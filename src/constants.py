"""Constants and tuning values for BlackKittenproxy core."""

__version__ = "2.1"

# tuning
BUF_SIZE = 65536
DRAIN_HWM = 1 << 20  # 1MB
CONNECT_TIMEOUT = 5.0
INITIAL_READ_TIMEOUT = 5.0
DNS_CACHE_TTL = 60.0
DNS_CACHE_MAX = 512
