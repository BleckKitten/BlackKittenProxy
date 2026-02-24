"""Blacklist managers and factory."""

import os
import ssl
from typing import List
from urllib.error import URLError
from urllib.request import Request, urlopen

from interfaces import IBlacklistManager


class FileBlacklistManager(IBlacklistManager):
    def __init__(self, config):
        self.config = config
        self.blacklist_file = config.blacklist_file
        self.blocked: List[str] = []
        self._blocked_set: set = set()
        self.load_blacklist()

    def load_blacklist(self) -> None:
        if not os.path.exists(self.blacklist_file):
            raise FileNotFoundError(f"File {self.blacklist_file} not found")
        with open(self.blacklist_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                s = line.strip()
                if len(s) < 2 or s[0] == "#":
                    continue
                d = s.lower().replace("www.", "")
                self.blocked.append(d)
                self._blocked_set.add(d)

    def is_blocked(self, domain: str) -> bool:
        d = domain.replace("www.", "")
        if self.config.domain_matching == "loose":
            for bd in self._blocked_set:
                if bd in d:
                    return True
        if d in self._blocked_set:
            return True
        parts = d.split(".")
        for i in range(1, len(parts)):
            if ".".join(parts[i:]) in self._blocked_set:
                return True
        return False

    async def check_domain(self, domain: bytes) -> None:
        return


class AutoBlacklistManager(IBlacklistManager):
    def __init__(self, config):
        self.blacklist_file = config.blacklist_file
        self._blocked_set: set = set()
        self._whitelist_set: set = set()

    def is_blocked(self, domain: str) -> bool:
        return domain in self._blocked_set

    async def check_domain(self, domain: bytes) -> None:
        dec = domain.decode()
        if dec in self._blocked_set or dec in self._whitelist_set:
            return
        try:
            req = Request(f"https://{dec}", headers={"User-Agent": "Mozilla/5.0"})
            ctx = ssl._create_unverified_context()
            from asyncio import get_running_loop

            loop = get_running_loop()

            def probe():
                with urlopen(req, timeout=4, context=ctx):
                    pass

            await loop.run_in_executor(None, probe)
            self._whitelist_set.add(dec)
        except URLError as e:
            try:
                reason = str(e.reason)
            except Exception:
                reason = ""
            if "handshake operation timed out" in reason:
                self._blocked_set.add(dec)
                try:
                    with open(self.blacklist_file, "a", encoding="utf-8") as f:
                        f.write(dec + "\n")
                except Exception:
                    pass
        except Exception:
            self._whitelist_set.add(dec)


class NoBlacklistManager(IBlacklistManager):
    def is_blocked(self, domain: str) -> bool:
        return True

    async def check_domain(self, domain: bytes) -> None:
        return


class BlacklistManagerFactory:
    @staticmethod
    def create(config, logger):
        if config.no_blacklist:
            return NoBlacklistManager()
        if config.auto_blacklist:
            return AutoBlacklistManager(config)
        try:
            return FileBlacklistManager(config)
        except FileNotFoundError as e:
            logger.error(f"\033[91m[ERROR]: {e}\033[0m")
            raise SystemExit(1)
