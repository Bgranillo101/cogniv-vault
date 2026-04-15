"""Process-local TTL-LRU store for agent query results.

In-memory only — results are lost on restart. Forward-compatible placeholder until
Phase 4 swaps the poll for a live WebSocket stream.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any

_TTL_SECONDS = 5 * 60
_MAX_ENTRIES = 100


class _JobStore:
    def __init__(self) -> None:
        self._items: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()
        self._lock = threading.Lock()

    def put(self, job_id: str, result: dict[str, Any]) -> None:
        now = time.monotonic()
        with self._lock:
            self._evict(now)
            self._items[job_id] = (now, result)
            if len(self._items) > _MAX_ENTRIES:
                self._items.popitem(last=False)

    def pop(self, job_id: str) -> dict[str, Any] | None:
        now = time.monotonic()
        with self._lock:
            self._evict(now)
            item = self._items.pop(job_id, None)
            return item[1] if item is not None else None

    def _evict(self, now: float) -> None:
        expired = [k for k, (ts, _) in self._items.items() if now - ts > _TTL_SECONDS]
        for k in expired:
            self._items.pop(k, None)


_store = _JobStore()


def put(job_id: str, result: dict[str, Any]) -> None:
    _store.put(job_id, result)


def pop(job_id: str) -> dict[str, Any] | None:
    return _store.pop(job_id)
