"""Rules engine for per-domain decisions."""

from typing import Dict, List, Optional, Tuple


class RuleEngine:
    def __init__(self, rules: List[Dict[str, object]]):
        self.rules = rules or []

    def _match(self, pattern: str, domain: str) -> bool:
        if not pattern:
            return False
        if pattern.startswith("*."):
            return domain.endswith(pattern[1:])
        return domain == pattern or domain.endswith("." + pattern)

    def decide(self, domain: str) -> Tuple[Optional[bool], Optional[str]]:
        d = domain.lower()
        for rule in self.rules:
            pattern = str(rule.get("pattern", "")).lower()
            if not self._match(pattern, d):
                continue
            action = str(rule.get("action", "auto")).lower()
            method = rule.get("fragment_method")
            method = str(method).lower() if method else None
            if action == "bypass":
                return False, method
            if action == "force":
                return True, method
            return None, method
        return None, None
