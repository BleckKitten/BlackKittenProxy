"""Application entrypoint for the proxy core."""

import argparse
import asyncio
import logging
import os
import sys

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except Exception:
    pass

from autostart import WindowsAutostartManager, LinuxAutostartManager
from blacklist import BlacklistManagerFactory
from config import ConfigLoader
from connection import ConnectionHandler
from json_utils import json_loads
from logger import ProxyLogger
from server import ProxyServer
from stats import Statistics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="Proxy host")
    parser.add_argument("--port", type=int, default=8881, help="Proxy port")
    parser.add_argument("--out-host", help="Outgoing proxy host")
    bl_group = parser.add_mutually_exclusive_group()
    bl_group.add_argument("--blacklist", default="blacklist.txt", help="Path to blacklist file")
    bl_group.add_argument("--no-blacklist", action="store_true", help="Use fragmentation for all domains")
    bl_group.add_argument("--autoblacklist", action="store_true", help="Automatic detection of blocked domains")
    parser.add_argument("--fragment-method", default="random", choices=["random", "sni", "split", "split-jitter"], help="Fragmentation method")
    parser.add_argument("--domain-matching", default="strict", choices=["loose", "strict"], help="Domain matching mode")
    parser.add_argument("--log-access", required=False, help="Path to the access control log")
    parser.add_argument("--log-error", required=False, help="Path to log file for errors")
    parser.add_argument("--stats-file", required=False, help="Path to stats JSON file")
    parser.add_argument("--rules-file", required=False, help="Path to rules JSON file")
    parser.add_argument("--connect-timeout", type=float, required=False, help="Connect timeout in seconds")
    parser.add_argument("--initial-read-timeout", type=float, required=False, help="Initial read timeout in seconds")
    parser.add_argument("-q", "--quiet", action="store_true", help="Remove UI output")
    as_group = parser.add_mutually_exclusive_group()
    as_group.add_argument("--install", action="store_true", help="Add proxy to autostart")
    as_group.add_argument("--uninstall", action="store_true", help="Remove proxy from autostart")
    return parser


async def run() -> None:
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    args = build_parser().parse_args()

    if args.install or args.uninstall:
        if getattr(sys, "frozen", False):
            mgr = WindowsAutostartManager if sys.platform == "win32" else LinuxAutostartManager
            action = "install" if args.install else "uninstall"
            mgr.manage_autostart(action)
            raise SystemExit(0)
        print("\033[91m[ERROR]: Autostart works only in executable version\033[0m")
        raise SystemExit(1)

    config = ConfigLoader.load_from_args(args)
    logger = ProxyLogger(config.log_access_file, config.log_error_file, config.quiet)
    blacklist = BlacklistManagerFactory.create(config, logger)
    stats = Statistics()
    logger.set_error_counter_callback(stats.increment_error_connections)
    if config.rules_file and os.path.exists(config.rules_file):
        try:
            with open(config.rules_file, "r", encoding="utf-8") as f:
                config.rules = json_loads(f.read())
        except Exception:
            config.rules = []

    server = ProxyServer(config, blacklist, stats, logger)
    server.connection_handler = ConnectionHandler(config, blacklist, stats, logger)
    try:
        await server.run()
    except asyncio.CancelledError:
        await server.shutdown()
        logger.info("\n" * 6 + "\033[92m[INFO]:\033[97m Shutting down proxy...")
        try:
            if sys.platform == "win32":
                os.system("mode con: lines=3000")
            raise SystemExit(0)
        except asyncio.CancelledError:
            pass


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
