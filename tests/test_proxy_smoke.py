import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class TestProxySmoke(unittest.TestCase):
    def _get_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def test_proxy_starts_and_listens(self):
        port = self._get_free_port()
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            tmp.write("example.com\n")
            tmp_path = tmp.name

        proc = None
        try:
            proc = subprocess.Popen(
                [
                    PYTHON,
                    str(ROOT / "src" / "main.py"),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--blacklist",
                    tmp_path,
                    "--quiet",
                ],
                cwd=str(ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            deadline = time.time() + 5
            connected = False
            while time.time() < deadline:
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                        connected = True
                        break
                except Exception:
                    time.sleep(0.2)

            self.assertTrue(connected, "Proxy did not accept TCP connection")
        finally:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
