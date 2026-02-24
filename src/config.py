"""Proxy configuration and CLI loader."""

from constants import CONNECT_TIMEOUT, INITIAL_READ_TIMEOUT


class ProxyConfig:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8881
        self.out_host = None
        self.blacklist_file = "blacklist.txt"
        self.fragment_method = "random"
        self.domain_matching = "strict"
        self.log_access_file = None
        self.log_error_file = None
        self.no_blacklist = False
        self.auto_blacklist = False
        self.quiet = False
        self.stats_file = None
        self.rules_file = None
        self.rules = []
        self.connect_timeout = CONNECT_TIMEOUT
        self.initial_read_timeout = INITIAL_READ_TIMEOUT


class ConfigLoader:
    @staticmethod
    def load_from_args(args) -> ProxyConfig:
        config = ProxyConfig()
        config.host = args.host
        config.port = args.port
        config.out_host = args.out_host
        config.blacklist_file = args.blacklist
        config.fragment_method = args.fragment_method
        config.domain_matching = args.domain_matching
        config.log_access_file = args.log_access
        config.log_error_file = args.log_error
        config.no_blacklist = args.no_blacklist
        config.auto_blacklist = args.autoblacklist
        config.quiet = args.quiet
        config.stats_file = args.stats_file
        config.rules_file = args.rules_file
        if args.connect_timeout:
            config.connect_timeout = args.connect_timeout
        if args.initial_read_timeout:
            config.initial_read_timeout = args.initial_read_timeout
        return config
