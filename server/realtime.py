"""WebSocket connection manager and realtime event routing."""
import json
from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect
from server.repositories.chats import ChatRepository
from server.repositories.users import UserRepository
from server.services.presence import PresenceRegistry
from shared.timeutils import utc_iso

class RealtimeHub:
    def __init__(self):
        self.sockets=defaultdict(set)
        self.presence=PresenceRegistry()
        self.chats=ChatRepository()
        self.users=UserRepository()
    async def connect(self,user_id,socket):
        await socket.accept()
        connection_id=id(socket)
        self.sockets[user_id].add(socket)
        first=self.presence.connect(user_id,connection_id)
        if first: await self.broadcast_presence(user_id,True)
    async def disconnect(self,user_id,socket):
        self.sockets[user_id].discard(socket)
        if not self.sockets[user_id]: self.sockets.pop(user_id,None)
        last=self.presence.disconnect(user_id,id(socket))
        if last:
            self.users.set_last_seen(user_id,utc_iso())
            await self.broadcast_presence(user_id,False)
    async def send_user(self,user_id,event):
        for socket in list(self.sockets.get(user_id,set())):
            try: await socket.send_json(event)
            except Exception:
                self.sockets[user_id].discard(socket)
    async def send_many(self,user_ids,event,exclude=None):
        for user_id in set(user_ids):
            if user_id!=exclude: await self.send_user(user_id,event)
    async def broadcast_presence(self,user_id,is_online):
        # Presence fan-out is scoped to users who share a direct chat or group.
        from server.database import transaction
        with transaction() as db:
            rows=db.execute("""SELECT DISTINCT peer_id FROM (
                SELECT CASE WHEN user1_id=? THEN user2_id ELSE user1_id END peer_id
                FROM conversations WHERE user1_id=? OR user2_id=?
                UNION SELECT gm2.user_id FROM group_members gm1
                JOIN group_members gm2 ON gm1.group_id=gm2.group_id
                WHERE gm1.user_id=? AND gm2.user_id!=?)""",
                (user_id,user_id,user_id,user_id,user_id)).fetchall()
        await self.send_many([r["peer_id"] for r in rows],
            {"type":"presence","user_id":user_id,"is_online":is_online})
    async def route_client_event(self,user_id,payload):
        if payload.get("type")!="typing": return
        chat_type=payload.get("chat_type"); chat_id=payload.get("chat_id")
        try: chat_id=int(chat_id)
        except (TypeError,ValueError): return
        members=self.chats.direct_members(chat_id) if chat_type=="direct" else self.chats.group_members(chat_id) if chat_type=="group" else set()
        if user_id in members:
            await self.send_many(members,{"type":"typing","chat_type":chat_type,
                "chat_id":chat_id,"user_id":user_id,"username":payload.get("username","")},exclude=user_id)
    async def websocket(self,socket:WebSocket,user):
        await self.connect(user["id"],socket)
        try:
            while True:
                payload=await socket.receive_json()
                if isinstance(payload,dict): await self.route_client_event(user["id"],payload)
        except (WebSocketDisconnect,ValueError):
            pass
        finally:
            await self.disconnect(user["id"],socket)

hub=RealtimeHub()
