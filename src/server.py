"""Proxy server orchestration."""

import asyncio
import os
import socket
from datetime import datetime

from constants import BUF_SIZE
from json_utils import json_dumps


class ProxyServer:
    def __init__(self, config, blacklist_manager, statistics, logger):
        self.config = config
        self.blacklist_manager = blacklist_manager
        self.statistics = statistics
        self.logger = logger
        self.connection_handler = None
        self.server = None
        self.stats_write_task = None
        logger.set_error_counter_callback(statistics.increment_error_connections)

    async def print_banner(self) -> None:
        self.logger.info("\033]0;BlackKittenproxy\007")
        if os.name == "nt":
            os.system("mode con: lines=33")

        console_width = os.get_terminal_size().columns if hasattr(os, "get_terminal_size") and os.get_terminal_size() else 80
        disclaimer = (
            "DISCLAIMER. The developer and/or supplier of this software "
            "shall not be liable for any loss or damage, including but "
            "not limited to direct, indirect, incidental, punitive or "
            "consequential damages arising out of the use of or inability "
            "to use this software, even if the developer or supplier has been "
            "advised of the possibility of such damages. The developer and/or "
            "supplier of this software shall not be liable for any legal "
            "consequences arising out of the use of this software. This includes, "
            "but is not limited to, violation of laws, rules or regulations, "
            "as well as any claims or suits arising out of the use of this software. "
            "The user is solely responsible for compliance with all applicable laws "
            "and regulations when using this software."
        )
        wrapped_text = []
        width = 70
        for i in range(0, len(disclaimer), width):
            wrapped_text.append(disclaimer[i:i + width])
        left_padding = (console_width - 76) // 2

        self.logger.info("\n\n\n")
        self.logger.info("\033[91m" + " " * left_padding + "â•”" + "â•" * 72 + "â•—" + "\033[0m")
        for line in wrapped_text:
            self.logger.info("\033[91m" + " " * left_padding + "â•‘ " + line.ljust(70) + " â•‘" + "\033[0m")
        self.logger.info("\033[91m" + " " * left_padding + "â•š" + "â•" * 72 + "â•" + "\033[0m")
        await asyncio.sleep(1)

        self.logger.info("\033[2J\033[H")
        self.logger.info("""
\033[92m  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ          â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ
 â–‘â–‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–‘â–‘â–ˆâ–ˆâ–ˆ          â–‘â–‘â–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–ˆâ–ˆâ–ˆ â–‘â–‘â–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–ˆâ–ˆâ–ˆâ–‘â–‘â–ˆâ–ˆâ–ˆ
  â–‘â–ˆâ–ˆâ–ˆâ–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–‘â–ˆâ–ˆâ–ˆ   â–‘â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ    â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ
  â–‘â–ˆâ–ˆâ–ˆâ–‘â–‘â–ˆâ–ˆâ–ˆâ–‘â–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–‘â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ    â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–‘â–ˆâ–ˆâ–ˆ
  â–‘â–ˆâ–ˆâ–ˆ â–‘â–‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ    â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘   â–‘â–ˆâ–ˆâ–ˆ
  â–‘â–ˆâ–ˆâ–ˆ  â–‘â–‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ â–‘â–ˆâ–ˆâ–ˆ    â–ˆâ–ˆâ–ˆ  â–‘â–ˆâ–ˆâ–ˆ         â–‘â–ˆâ–ˆâ–ˆ
  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–‘â–‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ        â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ
 â–‘â–‘â–‘â–‘â–‘    â–‘â–‘â–‘â–‘â–‘  â–‘â–‘â–‘â–‘â–‘â–‘  â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘   â–‘â–‘â–‘â–‘â–‘        â–‘â–‘â–‘â–‘â–‘\033[0m
        """)
        self.logger.info("\033[97m" + "Enjoy browsing! / ÐÐ°ÑÐ»Ð°Ð¶Ð´Ð°Ð¹Ñ‚ÐµÑÑŒ Ð¿Ñ€Ð¾ÑÐ¼Ð¾Ñ‚Ñ€Ð¾Ð¼!".center(50))
        self.logger.info("\n")

        self.logger.info(
            f"\033[92m[INFO]:\033[97m Proxy is running on {self.config.host}:{self.config.port} at "
            f"{datetime.now().strftime('%H:%M on %Y-%m-%d')}"
        )
        self.logger.info(f"\033[92m[INFO]:\033[97m The selected fragmentation method: {self.config.fragment_method}")
        self.logger.info("")
        if self.config.no_blacklist:
            self.logger.info("\033[92m[INFO]:\033[97m Blacklist is disabled. All domains will be subject to unblocking.")
        elif self.config.auto_blacklist:
            self.logger.info("\033[92m[INFO]:\033[97m Auto-blacklist is enabled")
        else:
            try:
                self.logger.info(f"\033[92m[INFO]:\033[97m Blacklist contains {len(self.blacklist_manager.blocked)} domains")
                self.logger.info(f"\033[92m[INFO]:\033[97m Path to blacklist: '{os.path.normpath(self.config.blacklist_file)}'")
            except Exception:
                pass

        self.logger.info("")
        if self.config.log_error_file:
            self.logger.info(f"\033[92m[INFO]:\033[97m Error logging is enabled. Path to error log: '{self.config.log_error_file}'")
        else:
            self.logger.info("\033[92m[INFO]:\033[97m Error logging is disabled")
        if self.config.log_access_file:
            self.logger.info(f"\033[92m[INFO]:\033[97m Access logging is enabled. Path to access log: '{self.config.log_access_file}'")
        else:
            self.logger.info("\033[92m[INFO]:\033[97m Access logging is disabled")
        self.logger.info("")
        self.logger.info("\033[92m[INFO]:\033[97m To stop the proxy, press Ctrl+C twice")
        self.logger.info("")

    async def display_stats(self) -> None:
        while True:
            await asyncio.sleep(1)
            self.statistics.update_speeds()
            if not self.config.quiet:
                print(self.statistics.get_stats_display())
                print("\033[5A", end="")

    async def write_stats(self) -> None:
        if not self.config.stats_file:
            return
        stats_path = self.config.stats_file
        while True:
            await asyncio.sleep(1)
            try:
                self.statistics.update_speeds()
                payload = self.statistics.snapshot()
                payload["fragment_method"] = self.config.fragment_method
                payload["host"] = self.config.host
                payload["port"] = self.config.port
                payload["timestamp"] = datetime.now().isoformat()
                with open(stats_path, "w", encoding="utf-8") as f:
                    f.write(json_dumps(payload))
            except Exception:
                pass

    async def run(self) -> None:
        if not self.config.quiet:
            await self.print_banner()

        try:
            self.server = await asyncio.start_server(
                self.connection_handler.handle_connection,
                self.config.host,
                self.config.port,
                limit=BUF_SIZE,
            )
        except OSError:
            self.logger.error(
                f"\033[91m[ERROR]: Failed to start proxy on this address ({self.config.host}:{self.config.port}). It looks like the port is already in use\033[0m"
            )
            raise SystemExit(1)

        try:
            for s in self.server.sockets or []:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception:
            pass

        if not self.config.quiet:
            asyncio.create_task(self.display_stats())
        if self.config.stats_file:
            self.stats_write_task = asyncio.create_task(self.write_stats())
        asyncio.create_task(self.connection_handler.cleanup_tasks())

        await self.server.serve_forever()

    async def shutdown(self) -> None:
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        if self.stats_write_task:
            self.stats_write_task.cancel()
        for task in self.connection_handler.tasks:
            task.cancel()
