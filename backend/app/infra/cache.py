import time
import threading
from typing import Any, Optional

class LocalTTLCache:
    def __init__(self):
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            exp, val = item
            if exp < now:
                # expirado
                self._data.pop(key, None)
                return None
            return val

    def set(self, key: str, value: Any, ttl_seconds: int):
        exp = time.time() + ttl_seconds
        with self._lock:
            self._data[key] = (exp, value)

# instancia única para todo el proceso
local_cache = LocalTTLCache()