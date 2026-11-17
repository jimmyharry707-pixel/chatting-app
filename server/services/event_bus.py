"""Async websocket fan-out abstraction."""
from collections import defaultdict
from fastapi import WebSocket

class EventBus:
    def __init__(self):
        self._sockets=defaultdict(set)
    async def attach(self,user_id,socket:WebSocket):
        await socket.accept()
        self._sockets[user_id].add(socket)
    async def detach(self,user_id,socket):
        sockets=self._sockets.get(user_id)
        if sockets is not None:
            sockets.discard(socket)
            if not sockets: self._sockets.pop(user_id,None)
    async def publish_user(self,user_id,event):
        for socket in list(self._sockets.get(user_id,set())):
            try: await socket.send_json(event)
            except Exception: await self.detach(user_id,socket)
    async def publish_many(self,user_ids,event,exclude=None):
        for user_id in set(user_ids):
            if user_id!=exclude: await self.publish_user(user_id,event)
    def is_online(self,user_id):
        return bool(self._sockets.get(user_id))
    def online_ids(self):
        return set(self._sockets)
