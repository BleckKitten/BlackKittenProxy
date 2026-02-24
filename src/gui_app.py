#!/usr/bin/env python3
"""
BlackKittenproxy Desktop UI (local web app).
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import webbrowser
import socket
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "ui"
ASSETS_DIR = ROOT / "assets"
UNLOCKED_DIR = ROOT / "unlocked"
CONFIG_PATH = ROOT / "gui_config.json"
GUI_BLACKLIST_PATH = ROOT / "gui-blacklist.txt"
GUI_STATS_PATH = ROOT / "gui-stats.json"
GUI_RULES_PATH = ROOT / "gui-rules.json"
LOG_DIR = ROOT / "logs"
LOG_ACCESS_PATH = LOG_DIR / "gui-access.log"
LOG_ERROR_PATH = LOG_DIR / "gui-error.log"

SUBDOMAIN_PREFIXES = ["www", "cdn", "api", "static"]

DEFAULT_CONFIG = {
    "host": "127.0.0.1",
    "port": 8881,
    "language": "en",
    "selected_lists": [],
    "custom_domains": [],
    "fragment_method": "random",
    "domain_matching": "strict",
    "auto_blacklist": False,
    "no_blacklist": False,
    "rules": [],
}

_proxy_process = None
_proxy_lock = threading.Lock()


# -------------------------
# Config helpers
# -------------------------

def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    else:
        data = {}
    cfg = DEFAULT_CONFIG.copy()
    cfg.update({k: v for k, v in data.items() if k in cfg})
    cfg["selected_lists"] = list(cfg.get("selected_lists", []))
    cfg["custom_domains"] = list(cfg.get("custom_domains", []))
    cfg["rules"] = list(cfg.get("rules", []))
    if not cfg["selected_lists"] and UNLOCKED_DIR.exists():
        cfg["selected_lists"] = [p.stem for p in UNLOCKED_DIR.glob("*.txt")]
    return cfg


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def save_rules(rules: list) -> None:
    GUI_RULES_PATH.write_text(json.dumps(rules, indent=2), encoding="utf-8")


def normalize_rule(rule: dict) -> dict:
    pattern = str(rule.get("pattern", "")).strip().lower()
    action = str(rule.get("action", "auto")).strip().lower()
    method = rule.get("fragment_method")
    if method is not None:
        method = str(method).strip().lower()
    if action not in {"auto", "force", "bypass"}:
        action = "auto"
    if method not in {None, "", "random", "sni"}:
        method = None
    return {
        "pattern": pattern,
        "action": action,
        "fragment_method": method or None,
    }


def validate_host(value: str) -> bool:
    if not value:
        return False
    if len(value) > 255:
        return False
    if value == "localhost":
        return True
    # basic IPv4 check
    if re.fullmatch(r"(\\d{1,3}\\.){3}\\d{1,3}", value):
        parts = value.split(".")
        return all(0 <= int(p) <= 255 for p in parts)
    # basic hostname (letters, digits, dots, hyphens)
    return re.fullmatch(r"[a-zA-Z0-9.-]+", value) is not None


def validate_port(value: int) -> bool:
    try:
        v = int(value)
        return 1 <= v <= 65535
    except Exception:
        return False


def port_available(host: str, port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, int(port)))
        sock.close()
        return True
    except Exception:
        return False


def is_local_request(handler) -> bool:
    try:
        addr = handler.client_address[0]
        return addr in {"127.0.0.1", "::1"}
    except Exception:
        return False


def sanitize_list_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("List name is required")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", name):
        raise ValueError("List name contains invalid characters")
    return name


def list_path(name: str) -> Path:
    safe = sanitize_list_name(name)
    if not safe.endswith(".txt"):
        safe = f"{safe}.txt"
    return UNLOCKED_DIR / safe


def read_list_domains(path: Path) -> list:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    domains = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        domains.append(s)
    return domains


def _normalize_domain(raw: str) -> str:
    s = raw.strip().lower()
    if not s:
        return ""
    s = s.replace("http://", "").replace("https://", "")
    s = s.split("/")[0]
    return s


def _expand_domains(domains: list) -> list:
    expanded = []
    seen = set()
    for d in domains:
        if not d:
            continue
        if d.startswith("*."):
            if d not in seen:
                seen.add(d)
                expanded.append(d)
            continue
        if d not in seen:
            seen.add(d)
            expanded.append(d)
        for prefix in SUBDOMAIN_PREFIXES:
            if d.startswith(f"{prefix}."):
                continue
            pref = f"{prefix}.{d}"
            if pref not in seen:
                seen.add(pref)
                expanded.append(pref)
        wildcard = f"*.{d}"
        if wildcard not in seen:
            seen.add(wildcard)
            expanded.append(wildcard)
    return expanded


def write_list_domains(path: Path, domains_text: str) -> list:
    lines = []
    for line in domains_text.splitlines():
        s = _normalize_domain(line)
        if not s:
            continue
        lines.append(s)
    lines = _expand_domains(lines)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return lines


def list_entries(cfg: dict) -> list:
    UNLOCKED_DIR.mkdir(exist_ok=True)
    entries = []
    for path in sorted(UNLOCKED_DIR.glob("*.txt")):
        name = path.stem
        domains = read_list_domains(path)
        entries.append(
            {
                "name": name,
                "enabled": name in cfg["selected_lists"],
                "count": len(domains),
                "domains": domains,
            }
        )
    return entries


def build_blacklist(cfg: dict) -> list:
    UNLOCKED_DIR.mkdir(exist_ok=True)
    selected = set(cfg.get("selected_lists", []))
    lines = []
    seen = set()

    for path in sorted(UNLOCKED_DIR.glob("*.txt")):
        if path.stem not in selected:
            continue
        for domain in read_list_domains(path):
            d = domain.strip()
            if d and d not in seen:
                seen.add(d)
                lines.append(d)

    for domain in cfg.get("custom_domains", []):
        d = _normalize_domain(domain)
        if d and d not in seen:
            seen.add(d)
            lines.append(d)
    expanded_custom = _expand_domains(lines)
    if expanded_custom:
        lines = expanded_custom

    GUI_BLACKLIST_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return lines


def tail_lines(path: Path, limit: int = 200) -> list:
    if not path.exists():
        return []
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            block = 1024
            data = b""
            while size > 0 and data.count(b"\n") <= limit:
                step = min(block, size)
                f.seek(-step, os.SEEK_CUR)
                data = f.read(step) + data
                f.seek(-step, os.SEEK_CUR)
                size -= step
        lines = data.decode("utf-8", errors="ignore").splitlines()
        return lines[-limit:]
    except Exception:
        return []


def get_diagnostics(cfg: dict) -> dict:
    config_valid = validate_host(cfg.get("host", "")) and validate_port(cfg.get("port", 0))
    stats_age = None
    if GUI_STATS_PATH.exists():
        try:
            stats_age = time.time() - GUI_STATS_PATH.stat().st_mtime
        except Exception:
            stats_age = None

    blacklist_count = 0
    if GUI_BLACKLIST_PATH.exists():
        try:
            blacklist_count = sum(1 for _ in GUI_BLACKLIST_PATH.open("r", encoding="utf-8", errors="ignore"))
        except Exception:
            blacklist_count = 0

    lists_count = 0
    try:
        lists_count = len(list(UNLOCKED_DIR.glob("*.txt")))
    except Exception:
        lists_count = 0

    port_open = False
    try:
        with socket.create_connection((cfg.get("host", "127.0.0.1"), int(cfg.get("port", 8881))), timeout=1):
            port_open = True
    except Exception:
        port_open = False

    return {
        "config_valid": config_valid,
        "port_available": port_available(cfg.get("host", "127.0.0.1"), int(cfg.get("port", 8881))),
        "running": proxy_status().get("running", False),
        "port_open": port_open,
        "stats_age_sec": stats_age,
        "blacklist_entries": blacklist_count,
        "list_files": lists_count,
    }


# -------------------------
# Proxy control
# -------------------------

def start_proxy(cfg: dict) -> dict:
    global _proxy_process
    with _proxy_lock:
        if _proxy_process and _proxy_process.poll() is None:
            return {"running": True, "message": "Already running"}
        if not validate_host(cfg.get("host", "")) or not validate_port(cfg.get("port", 0)):
            return {"running": False, "message": "Invalid host/port"}
        if not port_available(cfg.get("host", "127.0.0.1"), int(cfg.get("port", 8881))):
            return {"running": False, "message": "Port is already in use"}
        build_blacklist(cfg)
        LOG_DIR.mkdir(exist_ok=True)
        command = [
            sys.executable,
            str(ROOT / "src" / "main.py"),
            "--host",
            cfg["host"],
            "--port",
            str(cfg["port"]),
            "--blacklist",
            str(GUI_BLACKLIST_PATH),
            "--stats-file",
            str(GUI_STATS_PATH),
            "--rules-file",
            str(GUI_RULES_PATH),
        ]
        if cfg.get("fragment_method"):
            command += ["--fragment-method", cfg["fragment_method"]]
        if cfg.get("domain_matching"):
            command += ["--domain-matching", cfg["domain_matching"]]
        if cfg.get("auto_blacklist"):
            command.append("--autoblacklist")
        if cfg.get("no_blacklist"):
            command.append("--no-blacklist")
        command += ["--log-access", str(LOG_ACCESS_PATH), "--log-error", str(LOG_ERROR_PATH)]
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW
        _proxy_process = subprocess.Popen(command, cwd=str(ROOT), creationflags=creationflags)
        return {"running": True, "message": f"Proxy started on {cfg['host']}:{cfg['port']}"}


def stop_proxy() -> dict:
    global _proxy_process
    with _proxy_lock:
        if not _proxy_process or _proxy_process.poll() is not None:
            _proxy_process = None
            return {"running": False, "message": "Proxy is not running"}
        _proxy_process.terminate()
        try:
            _proxy_process.wait(timeout=5)
        except Exception:
            _proxy_process.kill()
        _proxy_process = None
        return {"running": False, "message": "Proxy stopped"}


def proxy_status() -> dict:
    if _proxy_process and _proxy_process.poll() is None:
        return {"running": True, "pid": _proxy_process.pid, "message": "Proxy online"}
    return {"running": False, "pid": None, "message": "Proxy offline"}


# -------------------------
# OS helpers
# -------------------------

def open_path(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


# -------------------------
# HTTP server
# -------------------------

class UIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self._send_text("Not found", status=404)
            return
        content_type = "text/plain"
        if path.suffix == ".html":
            content_type = "text/html"
        elif path.suffix == ".css":
            content_type = "text/css"
        elif path.suffix == ".js":
            content_type = "application/javascript"
        elif path.suffix in {".png", ".jpg", ".jpeg", ".ico"}:
            if path.suffix == ".png":
                content_type = "image/png"
            elif path.suffix in {".jpg", ".jpeg"}:
                content_type = "image/jpeg"
            else:
                content_type = "image/x-icon"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _safe_path(self, base: Path, rel: str) -> Path:
        rel = unquote(rel)
        rel_path = Path(rel)
        # Prevent absolute paths or traversal
        if rel_path.is_absolute():
            raise ValueError("Invalid path")
        resolved = (base / rel_path).resolve()
        base_resolved = base.resolve()
        if base_resolved not in resolved.parents and resolved != base_resolved:
            raise ValueError("Invalid path")
        return resolved

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._handle_api_get()
            return

        if self.path == "/" or self.path == "":
            self._serve_file(UI_DIR / "index.html")
            return

        if self.path.startswith("/ui/"):
            rel = self.path.replace("/ui/", "", 1)
            try:
                safe = self._safe_path(UI_DIR, rel)
            except ValueError:
                self._send_text("Not found", status=404)
                return
            self._serve_file(safe)
            return

        if self.path.startswith("/assets/"):
            rel = self.path.replace("/assets/", "", 1)
            try:
                safe = self._safe_path(ASSETS_DIR, rel)
            except ValueError:
                self._send_text("Not found", status=404)
                return
            self._serve_file(safe)
            return

        self._send_text("Not found", status=404)

    def do_POST(self):
        if not self.path.startswith("/api/"):
            self._send_text("Not found", status=404)
            return
        self._handle_api_post()

    def do_DELETE(self):
        if not self.path.startswith("/api/"):
            self._send_text("Not found", status=404)
            return
        self._handle_api_delete()

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        data = self.rfile.read(length)
        try:
            return json.loads(data.decode("utf-8"))
        except Exception:
            return {}

    def _handle_api_get(self):
        cfg = load_config()
        if self.path == "/api/config":
            self._send_json(cfg)
            return
        if self.path == "/api/lists":
            self._send_json(list_entries(cfg))
            return
        if self.path == "/api/status":
            self._send_json(proxy_status())
            return
        if self.path == "/api/stats":
            if GUI_STATS_PATH.exists():
                try:
                    data = json.loads(GUI_STATS_PATH.read_text(encoding="utf-8"))
                    self._send_json(data)
                    return
                except Exception:
                    pass
            self._send_json({})
            return
        if self.path.startswith("/api/diagnostics"):
            self._send_json(get_diagnostics(cfg))
            return
        if self.path == "/api/rules":
            self._send_json(cfg.get("rules", []))
            return
        if self.path.startswith("/api/logs/"):
            if not is_local_request(self):
                self._send_text("Forbidden", status=403)
                return
            parsed = urlparse(self.path)
            parts = parsed.path.split("/")
            log_type = parts[-1]
            params = parse_qs(parsed.query)
            limit = 200
            try:
                limit = int(params.get("limit", [limit])[0])
            except Exception:
                pass
            if log_type == "access":
                self._send_json({"lines": tail_lines(LOG_ACCESS_PATH, limit)})
                return
            if log_type == "error":
                self._send_json({"lines": tail_lines(LOG_ERROR_PATH, limit)})
                return
            self._send_text("Not found", status=404)
            return
        self._send_text("Not found", status=404)

    def _handle_api_post(self):
        cfg = load_config()
        payload = self._read_json()
        path = self.path

        if path == "/api/config":
            host = payload.get("host")
            port = payload.get("port")
            language = payload.get("language")
            custom_domains = payload.get("custom_domains")
            fragment_method = payload.get("fragment_method")
            domain_matching = payload.get("domain_matching")
            auto_blacklist = payload.get("auto_blacklist")
            no_blacklist = payload.get("no_blacklist")
            rules = payload.get("rules")

            if host:
                if not validate_host(str(host)):
                    self._send_text("Invalid host", status=400)
                    return
                cfg["host"] = str(host)
            if port:
                try:
                    if not validate_port(port):
                        self._send_text("Invalid port", status=400)
                        return
                    cfg["port"] = int(port)
                except Exception:
                    pass
            if language:
                cfg["language"] = str(language)
            if fragment_method:
                cfg["fragment_method"] = str(fragment_method)
            if domain_matching:
                cfg["domain_matching"] = str(domain_matching)
            if isinstance(auto_blacklist, bool):
                cfg["auto_blacklist"] = auto_blacklist
            if isinstance(no_blacklist, bool):
                cfg["no_blacklist"] = no_blacklist
            if cfg.get("auto_blacklist") and cfg.get("no_blacklist"):
                # prefer explicit no_blacklist over auto
                cfg["auto_blacklist"] = False
            if custom_domains is not None:
                if isinstance(custom_domains, str):
                    cfg["custom_domains"] = [
                        line.strip() for line in custom_domains.splitlines() if line.strip()
                    ]
                elif isinstance(custom_domains, list):
                    cfg["custom_domains"] = [str(item).strip() for item in custom_domains if str(item).strip()]
            if isinstance(rules, list):
                cfg["rules"] = [normalize_rule(r) for r in rules if isinstance(r, dict)]
            save_config(cfg)
            save_rules(cfg.get("rules", []))
            build_blacklist(cfg)
            self._send_json(cfg)
            return

        if path == "/api/rules":
            rules = payload.get("rules", [])
            if not isinstance(rules, list):
                self._send_text("Invalid rules", status=400)
                return
            cfg["rules"] = [normalize_rule(r) for r in rules if isinstance(r, dict)]
            save_config(cfg)
            save_rules(cfg.get("rules", []))
            self._send_json({"ok": True, "rules": cfg["rules"]})
            return

        if path == "/api/lists":
            name = payload.get("name", "")
            domains = payload.get("domains", "")
            try:
                file_path = list_path(name)
            except ValueError as exc:
                self._send_text(str(exc), status=400)
                return
            if file_path.exists():
                self._send_text("List already exists", status=409)
                return
            write_list_domains(file_path, domains)
            if file_path.stem not in cfg["selected_lists"]:
                cfg["selected_lists"].append(file_path.stem)
            save_config(cfg)
            build_blacklist(cfg)
            self._send_json({"ok": True})
            return

        if path.startswith("/api/lists/"):
            parts = path.split("/")
            if len(parts) >= 4 and parts[-1] == "toggle":
                name = unquote(parts[-2])
                try:
                    file_path = list_path(name)
                except ValueError as exc:
                    self._send_text(str(exc), status=400)
                    return
                if not file_path.exists():
                    self._send_text("Not found", status=404)
                    return
                enabled = bool(payload.get("enabled"))
                if enabled and file_path.stem not in cfg["selected_lists"]:
                    cfg["selected_lists"].append(file_path.stem)
                if not enabled and file_path.stem in cfg["selected_lists"]:
                    cfg["selected_lists"].remove(file_path.stem)
                save_config(cfg)
                build_blacklist(cfg)
                self._send_json({"ok": True})
                return

            name = unquote(parts[-1])
            try:
                file_path = list_path(name)
            except ValueError as exc:
                self._send_text(str(exc), status=400)
                return
            if not file_path.exists():
                self._send_text("Not found", status=404)
                return
            domains = payload.get("domains", "")
            write_list_domains(file_path, domains)
            build_blacklist(cfg)
            self._send_json({"ok": True})
            return

        if path == "/api/proxy/start":
            result = start_proxy(cfg)
            self._send_json(result)
            return

        if path == "/api/proxy/stop":
            result = stop_proxy()
            self._send_json(result)
            return

        if path == "/api/open/unlocked":
            UNLOCKED_DIR.mkdir(exist_ok=True)
            open_path(UNLOCKED_DIR)
            self._send_json({"ok": True})
            return

        if path == "/api/open/blacklist":
            if not GUI_BLACKLIST_PATH.exists():
                build_blacklist(cfg)
            open_path(GUI_BLACKLIST_PATH)
            self._send_json({"ok": True})
            return

        self._send_text("Not found", status=404)

    def _handle_api_delete(self):
        cfg = load_config()
        if self.path.startswith("/api/lists/"):
            name = unquote(self.path.split("/")[-1])
            try:
                file_path = list_path(name)
            except ValueError as exc:
                self._send_text(str(exc), status=400)
                return
            if not file_path.exists():
                self._send_text("Not found", status=404)
                return
            file_path.unlink(missing_ok=True)
            if file_path.stem in cfg["selected_lists"]:
                cfg["selected_lists"].remove(file_path.stem)
            save_config(cfg)
            build_blacklist(cfg)
            self._send_json({"ok": True})
            return

        self._send_text("Not found", status=404)


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), UIHandler)


def serve_in_thread(server: ThreadingHTTPServer) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="UI host")
    parser.add_argument("--port", type=int, default=9797, help="UI port")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser")
    return parser.parse_args()


def main():
    args = parse_args()
    server = create_server(args.host, args.port)
    url = f"http://{args.host}:{args.port}/"

    if not args.no_browser:
        webbrowser.open(url)

    print(f"BlackKittenproxy UI running at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_proxy()


if __name__ == "__main__":
    main()
