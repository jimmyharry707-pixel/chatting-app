"""Conversation list rendering and selection payload helpers."""
from PyQt5.QtWidgets import QListWidget,QListWidgetItem
from PyQt5.QtCore import Qt,QSize

class ChatList(QListWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.setSpacing(2); self.setUniformItemSizes(False)
    def populate(self,chats):
        self.clear()
        for chat in chats:
            title=chat.get("title","Conversation")
            preview=chat.get("last_message") or "Start a conversation"
            unread=int(chat.get("unread_count",0))
            suffix=f"   · {unread} unread" if unread else ""
            kind="GROUP" if chat.get("chat_type")=="group" else "DIRECT"
            item=QListWidgetItem(f"{title}{suffix}\n{kind}  ·  {preview[:80]}")
            item.setSizeHint(QSize(300,66)); item.setData(Qt.UserRole,chat)
            self.addItem(item)
    def selected_chat(self):
        item=self.currentItem()
        return item.data(Qt.UserRole) if item else None
    def find_chat(self,chat_id,chat_type=None):
        for index in range(self.count()):
            item=self.item(index); data=item.data(Qt.UserRole) or {}
            if data.get("id")==chat_id and (chat_type is None or data.get("chat_type")==chat_type):
                return item
        return None
