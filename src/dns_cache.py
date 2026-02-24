"""DNS cache with TTL for outbound connections."""

import asyncio
import socket
import time
from typing import Dict, List, Tuple

from constants import DNS_CACHE_MAX, DNS_CACHE_TTL


class DNSCache:
    def __init__(self, ttl: float = DNS_CACHE_TTL, max_entries: int = DNS_CACHE_MAX):
        self.ttl = ttl
        self.max_entries = max_entries
        self._cache: Dict[str, Tuple[float, List[Tuple]]] = {}

    async def resolve(self, host: str, port: int) -> List[Tuple]:
        now = time.monotonic()
        key = f"{host}:{port}"
        entry = self._cache.get(key)
        if entry and entry[0] > now:
            return entry[1]
        loop = asyncio.get_running_loop()
        addrs = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        if len(self._cache) >= self.max_entries:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = (now + self.ttl, addrs)
        return addrs
