import json
import threading
from pathlib import Path
from typing import Any, Dict

_STORE_PATH = Path("tests") / "session_store.json"
_LOCK = threading.Lock()

class InMemorySessionService:
    """
    Very small session + memory store:
    - stores session_id -> dict
    - persists to tests/session_store.json on save
    """
    def __init__(self, persist: bool = True):
        self._store: Dict[str, Dict[str, Any]] = {}
        self.persist = persist
        if self.persist:
            self._load()

    def _load(self):
        if _STORE_PATH.exists():
            try:
                with _STORE_PATH.open("r", encoding="utf8") as f:
                    self._store = json.load(f)
            except Exception:
                self._store = {}

    def _save(self):
        if not self.persist:
            return
        with _LOCK:
            _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with _STORE_PATH.open("w", encoding="utf8") as f:
                json.dump(self._store, f, indent=2)

    def get(self, session_id: str):
        return self._store.get(session_id)

    def set(self, session_id: str, value: Dict[str, Any]):
        self._store[session_id] = value
        self._save()

    def merge(self, session_id: str, partial: Dict[str, Any]):
        existing = self._store.get(session_id, {})
        existing.update(partial)
        self._store[session_id] = existing
        self._save()

# single global instance you can import
session_service = InMemorySessionService(persist=True)
