#!/usr/bin/env python3
"""BlackKittenproxy Desktop App (pywebview wrapper)."""

import argparse
import logging
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw
import pystray
import webview

from gui_app import (
    create_server,
    serve_in_thread,
    stop_proxy,
    start_proxy,
    proxy_status,
    load_config,
    save_config,
    build_blacklist,
)

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_PATH = LOG_DIR / "desktop_app.log"
CONFIG_REFRESH_SEC = 2.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="UI host")
    parser.add_argument("--port", type=int, default=9797, help="UI port")
    parser.add_argument("--no-tray", action="store_true", help="Disable system tray icon")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen mode")
    return parser.parse_args()


def _build_tray_icon() -> Image.Image:
    size = 128
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse((24, 40, 104, 120), fill=(15, 15, 16, 255))
    draw.ellipse((18, 90, 110, 132), fill=(12, 12, 12, 255))

    draw.polygon([(32, 36), (52, 8), (68, 44)], fill=(12, 12, 12, 255))
    draw.polygon([(96, 36), (76, 8), (60, 44)], fill=(12, 12, 12, 255))

    draw.ellipse((44, 72, 56, 84), fill=(255, 183, 3, 255))
    draw.ellipse((72, 72, 84, 84), fill=(255, 183, 3, 255))
    draw.ellipse((49, 76, 53, 80), fill=(20, 20, 20, 255))
    draw.ellipse((77, 76, 81, 80), fill=(20, 20, 20, 255))

    draw.polygon([(64, 84), (58, 92), (70, 92)], fill=(255, 183, 3, 255))
    draw.line([(98, 108), (118, 120)], fill=(12, 12, 12, 255), width=10)
    return img


class AppApi:
    def __init__(self, window):
        self._window = window

    def toggle_fullscreen(self):
        try:
            self._window.toggle_fullscreen()
        except Exception:
            try:
                self._window.fullscreen = not getattr(self._window, "fullscreen", False)
            except Exception:
                pass

    def set_window_size(self, width: int, height: int):
        try:
            self._window.resize(width, height)
        except Exception:
            pass

    def reset_window(self):
        try:
            self._window.resize(1200, 800)
        except Exception:
            pass


class ConfigCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = None
        self._loaded_at = 0.0

    def get(self, force: bool = False) -> dict:
        now = time.time()
        with self._lock:
            if force or self._data is None or (now - self._loaded_at) > CONFIG_REFRESH_SEC:
                self._data = load_config()
                self._loaded_at = now
            return dict(self._data)

    def update(self, cfg: dict) -> None:
        with self._lock:
            self._data = dict(cfg)
            self._loaded_at = time.time()


def main():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    args = parse_args()
    logging.info("Starting BlackKittenproxy desktop app")
    server = create_server(args.host, args.port)
    serve_in_thread(server)

    url = f"http://{args.host}:{args.port}/"
    logging.info("UI server running at %s", url)
    api = AppApi(None)
    window = webview.create_window(
        "BlackKittenproxy",
        url,
        width=1200,
        height=800,
        min_size=(980, 640),
        js_api=api,
    )
    api._window = window
    if args.fullscreen:
        try:
            window.toggle_fullscreen()
        except Exception:
            pass

    tray_icon = None
    window_hidden = False
    tray_stop = threading.Event()
    cfg_cache = ConfigCache()

    def on_closed():
        logging.info("Window closed, stopping services")
        if tray_icon:
            tray_icon.stop()
        tray_stop.set()
        try:
            server.shutdown()
        except Exception:
            pass
        stop_proxy()

    window.events.closed += on_closed

    def run_tray():
        nonlocal tray_icon

        def status_title():
            cfg = cfg_cache.get()
            status = proxy_status()
            host = cfg.get("host", "127.0.0.1")
            port = cfg.get("port", 8881)
            if status.get("running"):
                return f"BlackKittenproxy - Running {host}:{port}"
            return f"BlackKittenproxy - Stopped ({host}:{port})"

        def toggle_window(_icon, _item):
            nonlocal window_hidden
            if window_hidden:
                logging.info("Tray action: show window")
                window.show()
                window_hidden = False
            else:
                logging.info("Tray action: hide window")
                window.hide()
                window_hidden = True

        def set_port(value: int):
            cfg = cfg_cache.get(force=True)
            cfg["port"] = int(value)
            cfg.setdefault("host", "127.0.0.1")
            save_config(cfg)
            build_blacklist(cfg)
            cfg_cache.update(cfg)
            if tray_icon:
                tray_icon.title = status_title()

        def set_host(value: str):
            cfg = cfg_cache.get(force=True)
            cfg["host"] = str(value)
            cfg.setdefault("port", 8881)
            save_config(cfg)
            build_blacklist(cfg)
            cfg_cache.update(cfg)
            if tray_icon:
                tray_icon.title = status_title()

        def start_stop_proxy_action(_icon, _item):
            status = proxy_status()
            if status.get("running"):
                logging.info("Tray action: stop proxy")
                stop_proxy()
            else:
                logging.info("Tray action: start proxy")
                cfg = cfg_cache.get(force=True)
                start_proxy(cfg)
            if tray_icon:
                tray_icon.title = status_title()

        def quit_app(_icon, _item):
            logging.info("Tray action: quit app")
            try:
                window.destroy()
            except Exception:
                pass

        port_menu = pystray.Menu(
            pystray.MenuItem("8881", lambda _i, _j: set_port(8881)),
            pystray.MenuItem("8882", lambda _i, _j: set_port(8882)),
            pystray.MenuItem("1080", lambda _i, _j: set_port(1080)),
        )

        host_menu = pystray.Menu(
            pystray.MenuItem("127.0.0.1", lambda _i, _j: set_host("127.0.0.1")),
            pystray.MenuItem("0.0.0.0", lambda _i, _j: set_host("0.0.0.0")),
            pystray.MenuItem("localhost", lambda _i, _j: set_host("localhost")),
        )

        menu = pystray.Menu(
            pystray.MenuItem("Show/Hide", toggle_window),
            pystray.MenuItem("Start/Stop Proxy", start_stop_proxy_action),
            pystray.MenuItem("Set Port", port_menu),
            pystray.MenuItem("Set Host", host_menu),
            pystray.MenuItem("Quit", quit_app),
        )
        tray_icon = pystray.Icon(
            "BlackKittenproxy",
            _build_tray_icon(),
            status_title(),
            menu,
        )

        def refresh_status():
            while not tray_stop.is_set():
                try:
                    if tray_icon:
                        tray_icon.title = status_title()
                except Exception:
                    pass
                time.sleep(CONFIG_REFRESH_SEC)

        status_thread = threading.Thread(target=refresh_status, daemon=True)
        status_thread.start()
        tray_icon.run()

    if not args.no_tray:
        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()

    webview.start()


if __name__ == "__main__":
    sys.exit(main())
