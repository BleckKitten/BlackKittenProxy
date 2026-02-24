"""Autostart managers for desktop builds."""

import os
import subprocess
import sys
from pathlib import Path

from interfaces import IAutostartManager

if sys.platform == "win32":
    import winreg


class WindowsAutostartManager(IAutostartManager):
    @staticmethod
    def manage_autostart(action: str = "install") -> None:
        app_name = "BlackKittenproxy"
        exe_path = sys.executable
        try:
            key = winreg.HKEY_CURRENT_USER
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            if action == "install":
                with winreg.OpenKey(key, reg_path, 0, winreg.KEY_WRITE) as regkey:
                    winreg.SetValueEx(
                        regkey,
                        app_name,
                        0,
                        winreg.REG_SZ,
                        f'"{exe_path}" --blacklist "{os.path.dirname(exe_path)}/blacklist.txt"',
                    )
                print(f"\033[92m[INFO]:\033[97m Added to autostart: {exe_path}")
            elif action == "uninstall":
                try:
                    with winreg.OpenKey(key, reg_path, 0, winreg.KEY_WRITE) as regkey:
                        winreg.DeleteValue(regkey, app_name)
                    print("\033[92m[INFO]:\033[97m Removed from autostart")
                except FileNotFoundError:
                    print("\033[91m[ERROR]: Not found in autostart\033[0m")
        except PermissionError:
            print("\033[91m[ERROR]: Access denied. Run as administrator\033[0m")
        except Exception as e:
            print(f"\033[91m[ERROR]: Autostart operation failed: {e}\033[0m")


class LinuxAutostartManager(IAutostartManager):
    @staticmethod
    def manage_autostart(action: str = "install") -> None:
        app_name = "BlackKittenproxy"
        exec_path = sys.executable
        service_name = f"{app_name.lower()}.service"
        user_service_dir = Path.home() / ".config" / "systemd" / "user"
        service_file = user_service_dir / service_name
        blacklist_path = f"{os.path.dirname(exec_path)}/blacklist.txt"

        if action == "install":
            try:
                user_service_dir.mkdir(parents=True, exist_ok=True)
                service_content = f"""[Unit]
Description=BlackKittenproxy Service
After=network.target graphical-session.target
Wants=network.target

[Service]
Type=simple
ExecStart={exec_path} --blacklist "{blacklist_path}" --quiet
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0
Environment=XAUTHORITY=%h/.Xauthority

[Install]
WantedBy=default.target
"""
                service_file.write_text(service_content, encoding="utf-8")
                subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
                subprocess.run(["systemctl", "--user", "enable", service_name], check=True)
                subprocess.run(["systemctl", "--user", "start", service_name], check=True)
                print(f"\033[92m[INFO]:\033[97m Service installed and started: {service_name}")
                print("\033[93m[NOTE]:\033[97m Service will auto-start on login")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[ERROR]: Systemd command failed: {e}\033[0m")
            except Exception as e:
                print(f"\033[91m[ERROR]: Autostart operation failed: {e}\033[0m")
        elif action == "uninstall":
            try:
                subprocess.run(["systemctl", "--user", "stop", service_name], capture_output=True, check=True)
                subprocess.run(["systemctl", "--user", "disable", service_name], capture_output=True, check=True)
                if service_file.exists():
                    service_file.unlink()
                subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
                print("\033[92m[INFO]:\033[97m Service removed from autostart")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[ERROR]: Systemd command failed: {e}\033[0m")
            except Exception as e:
                print(f"\033[91m[ERROR]: Autostart operation failed: {e}\033[0m")
