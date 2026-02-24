import json
import os
import socket
import sys
import time
import unittest
from pathlib import Path
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gui_app import create_server, serve_in_thread


class TestGuiApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = "127.0.0.1"
        cls.port = cls._get_free_port()
        cls.server = create_server(cls.host, cls.port)
        cls.thread = serve_in_thread(cls.server)
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    @staticmethod
    def _get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def _get(self, path):
        url = f"http://{self.host}:{self.port}{path}"
        with urlopen(url, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path, payload=None):
        url = f"http://{self.host}:{self.port}{path}"
        data = json.dumps(payload or {}).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_get_config(self):
        cfg = self._get("/api/config")
        self.assertIn("host", cfg)
        self.assertIn("port", cfg)

    def test_add_toggle_list(self):
        list_name = "testsite"
        unlocked_dir = ROOT / "unlocked"
        list_path = unlocked_dir / f"{list_name}.txt"
        if list_path.exists():
            list_path.unlink()

        try:
            self._post("/api/lists", {"name": list_name, "domains": "example.com"})
            lists = self._get("/api/lists")
            names = [item["name"] for item in lists]
            self.assertIn(list_name, names)

            self._post(f"/api/lists/{list_name}/toggle", {"enabled": False})
            lists = self._get("/api/lists")
            entry = next(item for item in lists if item["name"] == list_name)
            self.assertFalse(entry["enabled"])
        finally:
            if list_path.exists():
                list_path.unlink()


if __name__ == "__main__":
    unittest.main()
