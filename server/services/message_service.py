"""Message validation and business rules."""
from server.repositories.messages import MessageRepository
from server.repositories.chats import ChatRepository
from shared.validators import validate_message
from shared.errors import PermissionDenied, ResourceNotFound

class MessageService:
    def __init__(self):
        self.messages=MessageRepository(); self.chats=ChatRepository()
    def send(self, chat_type, chat_id, sender_id, body, attachment=None):
        body=validate_message(body) if body.strip() else ""
        if chat_type=="direct":
            if sender_id not in self.chats.direct_members(chat_id): raise ResourceNotFound("Conversation not found.")
        elif chat_type=="group":
            if sender_id not in self.chats.group_members(chat_id): raise ResourceNotFound("Group not found.")
        else: raise ValueError("Unknown chat type.")
        if not body and not attachment: raise ValueError("Message needs text or an attachment.")
        return self.messages.create(chat_type,chat_id,sender_id,body,attachment)
    def history(self, chat_type, chat_id, user_id, limit=100, before_id=None):
        members=self.chats.direct_members(chat_id) if chat_type=="direct" else self.chats.group_members(chat_id)
        if user_id not in members: raise ResourceNotFound("Conversation not found.")
        result=self.messages.list(chat_type,chat_id,limit,before_id)
        self.messages.mark_read(chat_type,chat_id,user_id)
        return result
    def edit(self, chat_type, chat_id, message_id, user_id, body):
        return self.messages.edit(chat_type,chat_id,message_id,user_id,validate_message(body))
    def delete(self, chat_type, chat_id, message_id, user_id):
        admin=False
        if chat_type=="group":
            with __import__("server.database",fromlist=["transaction"]).transaction() as db:
                row=db.execute("SELECT role FROM group_members WHERE group_id=? AND user_id=?",(chat_id,user_id)).fetchone()
                admin=bool(row and row["role"]=="admin")
        return self.messages.soft_delete(chat_type,chat_id,message_id,user_id,admin)
