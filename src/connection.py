"""Connection handling and fragmentation logic."""

import asyncio
import random
import socket
import traceback
from datetime import datetime
from typing import Dict, List, Tuple

from constants import BUF_SIZE, DRAIN_HWM
from interfaces import IConnectionHandler
from blacklist import AutoBlacklistManager, NoBlacklistManager
from dns_cache import DNSCache
from rules import RuleEngine


class ConnectionInfo:
    __slots__ = ("src_ip", "dst_domain", "method", "start_time", "traffic_in", "traffic_out")

    def __init__(self, src_ip: str, dst_domain: str, method: str):
        self.src_ip = src_ip
        self.dst_domain = dst_domain
        self.method = method
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.traffic_in = 0
        self.traffic_out = 0


class ConnectionHandler(IConnectionHandler):
    def __init__(self, config, blacklist_manager, statistics, logger):
        self.config = config
        self.blacklist_manager = blacklist_manager
        self.statistics = statistics
        self.logger = logger
        self.out_host = config.out_host
        self.rule_engine = RuleEngine(config.rules)
        self.dns_cache = DNSCache()
        self.domain_failures: Dict[str, int] = {}

        self.active_connections: Dict[Tuple, ConnectionInfo] = {}
        self.connections_lock = asyncio.Lock()
        self.tasks: List[asyncio.Task] = []

        self._randrange = random.randrange

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        conn_key = ()
        try:
            peer = writer.get_extra_info("peername")
            if not peer:
                peer = ("unknown", 0)
            client_ip, client_port = peer[0], peer[1]

            try:
                http_data = await asyncio.wait_for(reader.read(BUF_SIZE), timeout=self.config.initial_read_timeout)
            except asyncio.TimeoutError:
                try:
                    writer.close()
                except Exception:
                    pass
                return
            if not http_data:
                try:
                    writer.close()
                except Exception:
                    pass
                return

            method, host, port = self._parse_http_request(http_data)
            conn_key = (client_ip, client_port)
            conn_info = ConnectionInfo(client_ip, host.decode(), method.decode())

            if method == b"CONNECT" and isinstance(self.blacklist_manager, AutoBlacklistManager):
                await self.blacklist_manager.check_domain(host)

            async with self.connections_lock:
                self.active_connections[conn_key] = conn_info

            self.statistics.update_traffic(0, len(http_data))
            conn_info.traffic_out += len(http_data)

            if method == b"CONNECT":
                await self._handle_https_connection(reader, writer, host, port, conn_key, conn_info)
            else:
                await self._handle_http_connection(reader, writer, http_data, host, port, conn_key)

        except Exception:
            await self._handle_connection_error(writer, conn_key)

    def _parse_http_request(self, http_data: bytes) -> Tuple[bytes, bytes, int]:
        first_crlf = http_data.find(b"\r\n")
        if first_crlf == -1:
            raise ValueError("Malformed HTTP request")
        first_line = http_data[:first_crlf]
        parts = first_line.split(b" ")
        method = parts[0]
        url = parts[1]

        if method == b"CONNECT":
            hp = url.split(b":", 1)
            host = hp[0]
            port = int(hp[1]) if len(hp) > 1 else 443
            return method, host, port

        host_pos = http_data.find(b"\r\nHost: ")
        if host_pos == -1:
            headers = http_data.split(b"\r\n")
            host_header = next((h for h in headers if h.startswith(b"Host: ")), None)
            if not host_header:
                raise ValueError("Missing Host header")
            host_port = host_header[6:].split(b":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 80
            return method, host, port

        start = host_pos + 8
        end = http_data.find(b"\r\n", start)
        host_line = http_data[start:end]
        hp = host_line.split(b":", 1)
        host = hp[0]
        port = int(hp[1]) if len(hp) > 1 else 80
        return method, host, port

    async def _handle_https_connection(self, reader, writer, host: bytes, port: int, conn_key: Tuple, conn_info: ConnectionInfo) -> None:
        established = b"HTTP/1.1 200 Connection Established\r\n\r\n"
        self.statistics.update_traffic(len(established), 0)
        conn_info.traffic_in += len(established)

        try:
            remote_reader, remote_writer = await asyncio.wait_for(
                self._open_connection(host.decode(), port),
                timeout=self.config.connect_timeout,
            )
        except Exception:
            await self._handle_connection_error(writer, conn_key)
            return

        writer.write(established)
        await writer.drain()

        await self._handle_initial_tls_data(reader, remote_writer, host, conn_info)
        await self._run_pipes(reader, writer, remote_reader, remote_writer, conn_key)

    async def _handle_http_connection(self, reader, writer, http_data: bytes, host: bytes, port: int, conn_key: Tuple) -> None:
        try:
            remote_reader, remote_writer = await asyncio.wait_for(
                self._open_connection(host.decode(), port),
                timeout=self.config.connect_timeout,
            )
        except Exception:
            await self._handle_connection_error(writer, conn_key)
            return
        remote_writer.write(http_data)
        await remote_writer.drain()

        self.statistics.increment_total_connections()
        self.statistics.increment_allowed_connections()

        await self._run_pipes(reader, writer, remote_reader, remote_writer, conn_key)

    async def _open_connection(self, host: str, port: int):
        loop = asyncio.get_running_loop()
        addrs = await self.dns_cache.resolve(host, port)
        last_exc = None
        for family, socktype, proto, _canon, sockaddr in addrs:
            sock = None
            try:
                sock = socket.socket(family, socktype, proto)
                sock.setblocking(False)
                if self.out_host and family == socket.AF_INET:
                    try:
                        sock.bind((self.out_host, 0))
                    except Exception:
                        pass
                await loop.sock_connect(sock, sockaddr)
                return await asyncio.open_connection(sock=sock, limit=BUF_SIZE)
            except Exception as exc:
                last_exc = exc
                try:
                    if sock:
                        sock.close()
                except Exception:
                    pass
                continue
        if last_exc:
            raise last_exc
        raise OSError("Failed to connect")

    def _extract_sni_position(self, data: bytes):
        pos = data.find(b"\x00\x00")
        while pos != -1 and pos + 9 <= len(data):
            try:
                ext_len = int.from_bytes(data[pos + 2:pos + 4], "big")
                list_len = int.from_bytes(data[pos + 4:pos + 6], "big")
                name_len = int.from_bytes(data[pos + 7:pos + 9], "big")
                if ext_len - list_len == 2 and list_len - name_len == 3:
                    sni_start = pos + 9
                    return sni_start, sni_start + name_len
            except Exception:
                pass
            pos = data.find(b"\x00\x00", pos + 1)
        return None

    async def _handle_initial_tls_data(self, reader, writer, host: bytes, conn_info: ConnectionInfo) -> None:
        try:
            head = await asyncio.wait_for(reader.read(5), timeout=self.config.initial_read_timeout)
            data = await asyncio.wait_for(reader.read(2048), timeout=self.config.initial_read_timeout)
        except Exception:
            try:
                self.logger.log_error(f"{host.decode()} : {traceback.format_exc()}")
            except Exception:
                pass
            return

        should_fragment = True
        if not isinstance(self.blacklist_manager, NoBlacklistManager):
            should_fragment = self.blacklist_manager.is_blocked(conn_info.dst_domain)

        rule_decision, rule_method = self.rule_engine.decide(conn_info.dst_domain)
        if rule_decision is not None:
            should_fragment = rule_decision

        if not should_fragment:
            self.statistics.increment_total_connections()
            self.statistics.increment_allowed_connections()
            combined = head + data
            writer.write(combined)
            await writer.drain()
            self.statistics.update_traffic(0, len(combined))
            conn_info.traffic_out += len(combined)
            return

        self.statistics.increment_total_connections()
        self.statistics.increment_blocked_connections()

        parts: List[bytes] = []
        hdr = bytes.fromhex("160304")

        method = rule_method or self.config.fragment_method
        failures = self.domain_failures.get(conn_info.dst_domain, 0)
        if failures >= 2 and method == "random":
            method = "sni"
        if method == "sni":
            sni_pos = self._extract_sni_position(data)
            if sni_pos:
                pre = data[:sni_pos[0]]
                sni = data[sni_pos[0]:sni_pos[1]]
                post = data[sni_pos[1]:]
                mid = (len(sni) + 1) // 2
                parts = [
                    hdr + len(pre).to_bytes(2, "big") + pre,
                    hdr + len(sni[:mid]).to_bytes(2, "big") + sni[:mid],
                    hdr + len(sni[mid:]).to_bytes(2, "big") + sni[mid:],
                    hdr + len(post).to_bytes(2, "big") + post,
                ]
            else:
                method = "split"
        if method == "split" or method == "split-jitter":
            chunk_size = 32
            idx = 0
            while idx < len(data):
                n = min(chunk_size, len(data) - idx)
                parts.append(hdr + n.to_bytes(2, "big") + data[idx:idx + n])
                idx += n
        if method not in {"sni", "split", "split-jitter"}:
            host_end = data.find(b"\x00")
            if host_end != -1:
                chunk = data[:host_end + 1]
                parts.append(hdr + (host_end + 1).to_bytes(2, "big") + chunk)
                data = data[host_end + 1:]
            append = parts.append
            randrange = self._randrange
            while data:
                n = randrange(1, len(data) + 1)
                append(hdr + n.to_bytes(2, "big") + data[:n])
                data = data[n:]

        if not parts:
            combined = head + data
            writer.write(combined)
            await writer.drain()
            self.statistics.update_traffic(0, len(combined))
            conn_info.traffic_out += len(combined)
            return

        if method == "split-jitter":
            total = 0
            for part in parts:
                writer.write(part)
                await writer.drain()
                total += len(part)
                await asyncio.sleep(self._randrange(1, 6) / 1000)
        else:
            combined = b"".join(parts)
            writer.write(combined)
            await writer.drain()
            total = len(combined)
        self.statistics.update_traffic(0, total)
        conn_info.traffic_out += total

    async def _run_pipes(self, client_reader, client_writer, remote_reader, remote_writer, conn_key: Tuple) -> None:
        t1 = asyncio.create_task(self._pipe(client_reader, remote_writer, True))
        t2 = asyncio.create_task(self._pipe(remote_reader, client_writer, False))
        await asyncio.gather(t1, t2, return_exceptions=True)

        for w in (client_writer, remote_writer):
            try:
                w.close()
                await w.wait_closed()
            except Exception:
                pass

        async with self.connections_lock:
            removed = self.active_connections.pop(conn_key, None)
        if removed:
            if removed.dst_domain in self.domain_failures:
                self.domain_failures[removed.dst_domain] = max(0, self.domain_failures[removed.dst_domain] - 1)
            try:
                self.logger.log_access(
                    f"{removed.start_time} {removed.src_ip} {removed.method} {removed.dst_domain} {removed.traffic_in} {removed.traffic_out}"
                )
            except Exception:
                pass

    async def _pipe(self, reader, writer, is_out: bool) -> None:
        stats = self.statistics
        local_vol = 0

        transport = getattr(writer, "transport", None)
        write = writer.write
        drain = writer.drain
        read = reader.read

        conn_info = None
        try:
            conn_key_approx = None
        except Exception:
            conn_info = None

        try:
            while True:
                data = await read(BUF_SIZE)
                if not data:
                    break
                write(data)
                local_vol += len(data)

                if transport and transport.get_write_buffer_size() > DRAIN_HWM:
                    await drain()

            await drain()

        except asyncio.CancelledError:
            pass
        except Exception:
            domain = conn_info.dst_domain if conn_info else "unknown"
            try:
                self.logger.log_error(f"{domain} : {traceback.format_exc()}")
            except Exception:
                pass
        finally:
            if is_out:
                stats.update_traffic(0, local_vol)
                if conn_info:
                    conn_info.traffic_out += local_vol
            else:
                stats.update_traffic(local_vol, 0)
                if conn_info:
                    conn_info.traffic_in += local_vol

    async def _handle_connection_error(self, writer, conn_key: Tuple) -> None:
        try:
            error_response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n"
            writer.write(error_response)
            await writer.drain()
            self.statistics.update_traffic(len(error_response), 0)
        except Exception:
            pass

        async with self.connections_lock:
            conn_info = self.active_connections.pop(conn_key, None)

        self.statistics.increment_total_connections()
        self.statistics.increment_error_connections()

        domain = conn_info.dst_domain if conn_info else "unknown"
        if conn_info:
            self.domain_failures[conn_info.dst_domain] = self.domain_failures.get(conn_info.dst_domain, 0) + 1
        try:
            self.logger.log_error(f"{domain} : {traceback.format_exc()}")
        except Exception:
            pass

        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

    async def cleanup_tasks(self) -> None:
        while True:
            await asyncio.sleep(60)
            self.tasks = [t for t in self.tasks if not t.done()]
