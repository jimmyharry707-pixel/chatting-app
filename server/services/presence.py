"""In-process online presence registry.

For multi-worker deployments, replace this registry with Redis pub/sub and
shared expiring presence keys. This implementation is intentionally explicit
about its single-process scope.
"""
from collections import defaultdict
from threading import RLock

class PresenceRegistry:
    def __init__(self):
        self._connections=defaultdict(set); self._lock=RLock()
    def connect(self,user_id,connection_id):
        with self._lock:
            was_online=bool(self._connections[user_id])
            self._connections[user_id].add(connection_id)
            return not was_online
    def disconnect(self,user_id,connection_id):
        with self._lock:
            connections=self._connections.get(user_id,set())
            connections.discard(connection_id)
            if not connections:
                self._connections.pop(user_id,None)
                return True
            return False
    def is_online(self,user_id):
        with self._lock: return bool(self._connections.get(user_id))
    def online_users(self):
        with self._lock: return set(self._connections)
    def connection_count(self,user_id):
        with self._lock: return len(self._connections.get(user_id,set()))
