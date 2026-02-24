"""Traffic statistics tracking."""

import time
from typing import Dict

from interfaces import IStatistics


class Statistics(IStatistics):
    def __init__(self):
        self.total_connections = 0
        self.allowed_connections = 0
        self.blocked_connections = 0
        self.errors_connections = 0
        self.traffic_in = 0
        self.traffic_out = 0
        self.last_traffic_in = 0
        self.last_traffic_out = 0
        self.speed_in = 0
        self.speed_out = 0
        self.average_speed_in = (0.0, 1)
        self.average_speed_out = (0.0, 1)
        self.last_time = None

    def increment_total_connections(self) -> None:
        self.total_connections += 1

    def increment_allowed_connections(self) -> None:
        self.allowed_connections += 1

    def increment_blocked_connections(self) -> None:
        self.blocked_connections += 1

    def increment_error_connections(self) -> None:
        self.errors_connections += 1

    def update_traffic(self, incoming: int, outgoing: int) -> None:
        self.traffic_in += incoming
        self.traffic_out += outgoing

    def update_speeds(self) -> None:
        current_time = time.monotonic()
        if self.last_time is not None:
            dt = current_time - self.last_time
            if dt > 0:
                self.speed_in = (self.traffic_in - self.last_traffic_in) * 8 / dt
                self.speed_out = (self.traffic_out - self.last_traffic_out) * 8 / dt
                if self.speed_in > 0:
                    self.average_speed_in = (self.average_speed_in[0] + self.speed_in, self.average_speed_in[1] + 1)
                if self.speed_out > 0:
                    self.average_speed_out = (self.average_speed_out[0] + self.speed_out, self.average_speed_out[1] + 1)
        self.last_traffic_in = self.traffic_in
        self.last_traffic_out = self.traffic_out
        self.last_time = current_time

    @staticmethod
    def format_size(size: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        unit = 0
        s = float(size)
        while s >= 1024 and unit < len(units) - 1:
            s /= 1024
            unit += 1
        return f"{s:.1f} {units[unit]}"

    @staticmethod
    def format_speed(speed_bps: float) -> str:
        if speed_bps <= 0:
            return "0 b/s"
        units = ["b/s", "Kb/s", "Mb/s", "Gb/s"]
        unit = 0
        speed = speed_bps
        while speed >= 1000 and unit < len(units) - 1:
            speed /= 1000
            unit += 1
        return f"{speed:.0f} {units[unit]}"

    def get_stats_display(self) -> str:
        col_width = 30
        conns_stat = (
            f"\033[97mTotal: \033[93m{self.total_connections}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mMiss: \033[96m{self.allowed_connections}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mUnblock: \033[92m{self.blocked_connections}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mErrors: \033[91m{self.errors_connections}\033[0m".ljust(col_width)
        )
        traffic_stat = (
            f"\033[97mTotal: \033[96m{self.format_size(self.traffic_out + self.traffic_in)}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mDL: \033[96m{self.format_size(self.traffic_in)}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mUL: \033[96m{self.format_size(self.traffic_out)}\033[0m".ljust(col_width)
            + "\033[97m| "
        )
        avg_in = self.average_speed_in[0] / self.average_speed_in[1]
        avg_out = self.average_speed_out[0] / self.average_speed_out[1]
        speed_stat = (
            f"\033[97mDL: \033[96m{self.format_speed(self.speed_in)}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mUL: \033[96m{self.format_speed(self.speed_out)}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mAVG DL: \033[96m{self.format_speed(avg_in)}\033[0m".ljust(col_width)
            + "\033[97m| "
            + f"\033[97mAVG UL: \033[96m{self.format_speed(avg_out)}\033[0m"
        )
        title = "STATISTICS"
        top_border = f"\033[92m{'â•' * 36} {title} {'â•' * 36}\033[0m"
        line_conns = f"\033[92m   {'Conns'.ljust(8)}:\033[0m {conns_stat}\033[0m"
        line_traffic = f"\033[92m   {'Traffic'.ljust(8)}:\033[0m {traffic_stat}\033[0m"
        line_speed = f"\033[92m   {'Speed'.ljust(8)}:\033[0m {speed_stat}\033[0m"
        bottom = f"\033[92m{'â•' * (36 * 2 + len(title) + 2)}\033[0m"
        return f"{top_border}\n{line_conns}\n{line_traffic}\n{line_speed}\n{bottom}"

    def snapshot(self) -> Dict[str, object]:
        total = self.total_connections
        allowed = self.allowed_connections
        blocked = self.blocked_connections
        errors = self.errors_connections
        efficiency = (blocked / total) * 100 if total > 0 else 0.0
        avg_in = self.average_speed_in[0] / self.average_speed_in[1]
        avg_out = self.average_speed_out[0] / self.average_speed_out[1]
        return {
            "total_connections": total,
            "allowed_connections": allowed,
            "blocked_connections": blocked,
            "error_connections": errors,
            "traffic_in": self.traffic_in,
            "traffic_out": self.traffic_out,
            "speed_in_bps": self.speed_in,
            "speed_out_bps": self.speed_out,
            "avg_speed_in_bps": avg_in,
            "avg_speed_out_bps": avg_out,
            "efficiency": efficiency,
        }
