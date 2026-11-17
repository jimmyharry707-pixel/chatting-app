"""Main desktop window assembled from small reusable widgets."""
import os
from PyQt5.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QFrame,QLabel,QPushButton,QSplitter,QListWidgetItem,QFileDialog,QMessageBox,QInputDialog,QLineEdit
from PyQt5.QtCore import Qt,QTimer
from client.widgets.chat_list import ChatList
from client.widgets.message_view import MessageView
from client.widgets.composer import MessageComposer
from client.widgets.status_bar import StatusBar
from client.dialogs.profile_dialog import ProfileDialog
from client.dialogs.group_dialog import GroupDialog
from client.realtime import RealtimeWorker

class MainWindow(QMainWindow):
    def __init__(self,api,user,parent=None):
        super().__init__(parent); self.api=api; self.user=user
        self.chat_id=None; self.chat_type=None; self.chat_title=""
        self.messages=[]; self.realtime=None
        self.setWindowTitle("Northstar Messenger"); self.resize(1280,820); self.setMinimumSize(960,620)
        self._build(); self.refresh_chats()
        self.realtime=RealtimeWorker(api.websocket_url(),parent=self)
        self.realtime.event_received.connect(self.on_event)
        self.realtime.status_changed.connect(self.status.set_connection); self.realtime.start()
    def _build(self):
        splitter=QSplitter(Qt.Horizontal)
        sidebar=QFrame(); sidebar.setStyleSheet("background:white")
        left=QVBoxLayout(sidebar); left.setContentsMargins(16,16,16,12)
        heading=QHBoxLayout(); title=QLabel("Northstar"); title.setStyleSheet("font-size:19pt;font-weight:700;color:#229ed9")
        profile=QPushButton("Profile"); profile.clicked.connect(self.edit_profile)
        heading.addWidget(title); heading.addStretch(1); heading.addWidget(profile); left.addLayout(heading)
        left.addWidget(QLabel(f"Signed in as @{user['username']}"))
        self.search=QLineEdit(); self.search.setPlaceholderText("Search people"); self.search.returnPressed.connect(self.search_people); left.addWidget(self.search)
        actions=QHBoxLayout(); group=QPushButton("+ Group"); group.clicked.connect(self.create_group)
        find=QPushButton("Find messages"); find.clicked.connect(self.search_messages)
        actions.addWidget(group); actions.addWidget(find); left.addLayout(actions)
        self.chats=ChatList(); self.chats.itemClicked.connect(self.open_selected); left.addWidget(self.chats,1)
        panel=QFrame(); panel.setStyleSheet("background:#e7eef4")
        right=QVBoxLayout(panel); right.setContentsMargins(0,0,0,0); right.setSpacing(0)
        header=QFrame(); header.setStyleSheet("background:white;border-bottom:1px solid #dce4ea")
        hl=QHBoxLayout(header); self.heading=QLabel("Welcome"); self.heading.setStyleSheet("font-size:14pt;font-weight:650")
        self.subtitle=QLabel("Choose a conversation"); self.subtitle.setStyleSheet("color:#71808c")
        labels=QVBoxLayout(); labels.addWidget(self.heading); labels.addWidget(self.subtitle); hl.addLayout(labels,1)
        self.edit=QPushButton("Edit last"); self.edit.clicked.connect(self.edit_last)
        self.delete=QPushButton("Delete last"); self.delete.clicked.connect(self.delete_last)
        hl.addWidget(self.edit); hl.addWidget(self.delete); right.addWidget(header)
        self.view=MessageView(); self.view.anchorClicked.connect(self.download_attachment); right.addWidget(self.view,1)
        self.composer=MessageComposer(); self.composer.send_requested.connect(self.send_message)
        self.composer.attachment_requested.connect(self.attach_file); self.composer.typing_changed.connect(self.typing)
        right.addWidget(self.composer); self.status=StatusBar(); right.addWidget(self.status)
        splitter.addWidget(sidebar); splitter.addWidget(panel); splitter.setSizes([350,930]); self.setCentralWidget(splitter)
    def refresh_chats(self):
        try: self.chats.populate(self.api.chats())
        except Exception as exc: self.status.set_detail(str(exc))
    def search_people(self):
        term=self.search.text().strip()
        if not term: self.refresh_chats(); return
        try: people=self.api.search_users(term)
        except Exception as exc: QMessageBox.warning(self,"Search failed",str(exc)); return
        self.chats.clear()
        for person in people:
            item=QListWidgetItem(f"{person.get('display_name') or person['username']} (@{person['username']})")
            item.setData(Qt.UserRole,{"chat_type":"user","peer":person,"user_id":person["id"]})
            self.chats.addItem(item)
    def open_selected(self,item):
        data=item.data(Qt.UserRole) or {}
        try:
            if data.get("chat_type")=="user":
                chat=self.api.open_direct(data["user_id"]); chat["peer"]=data["peer"]
            else: chat=data
            self.open_chat(chat)
        except Exception as exc: QMessageBox.warning(self,"Could not open chat",str(exc))
    def open_chat(self,chat):
        self.chat_id=int(chat["id"]); self.chat_type=chat.get("chat_type","direct")
        self.chat_title=chat.get("title") or (chat.get("peer") or {}).get("display_name","Conversation")
        self.heading.setText(self.chat_title); self.subtitle.setText("Group conversation" if self.chat_type=="group" else "Direct message")
        self.composer.set_enabled(True); self.refresh_messages()
    def refresh_messages(self):
        if self.chat_id is None: return
        try:
            self.messages=self.api.messages(self.chat_type,self.chat_id)
            self.view.render_messages(self.messages,self.user["id"],self.chat_type)
            self.refresh_chats()
        except Exception as exc: self.status.set_detail(str(exc))
    def send_message(self,body):
        if self.chat_id is None: return
        try: self.api.send(self.chat_type,self.chat_id,body); self.refresh_messages()
        except Exception as exc: QMessageBox.warning(self,"Message not sent",str(exc))
    def attach_file(self):
        if self.chat_id is None: return
        path,_=QFileDialog.getOpenFileName(self,"Attach file","","Images and documents (*.*)")
        if not path: return
        try: self.api.upload(self.chat_type,self.chat_id,path); self.refresh_messages()
        except Exception as exc: QMessageBox.warning(self,"Upload failed",str(exc))
    def download_attachment(self,url):
        if url.scheme()!="attachment": return
        kind=url.host()
        try: message_id=int(url.path().strip("/"))
        except ValueError: return
        path,_=QFileDialog.getSaveFileName(self,"Save attachment",f"attachment_{message_id}")
        if not path: return
        try: self.api.download(kind,message_id,path); self.status.set_detail(f"Saved {path}")
        except Exception as exc: QMessageBox.warning(self,"Download failed",str(exc))
    def edit_last(self):
        own=[m for m in self.messages if m["sender_id"]==self.user["id"] and not m.get("deleted_at") and m.get("body")]
        if not own: return
        msg=own[-1]; body,ok=QInputDialog.getMultiLineText(self,"Edit message","Message",msg["body"])
        if ok and body.strip():
            try: self.api.edit(self.chat_type,self.chat_id,msg["id"],body); self.refresh_messages()
            except Exception as exc: QMessageBox.warning(self,"Edit failed",str(exc))
    def delete_last(self):
        own=[m for m in self.messages if m["sender_id"]==self.user["id"] and not m.get("deleted_at")]
        if not own: return
        msg=own[-1]
        if QMessageBox.question(self,"Delete message","Delete your latest message?")!=QMessageBox.Yes: return
        try: self.api.delete(self.chat_type,self.chat_id,msg["id"]); self.refresh_messages()
        except Exception as exc: QMessageBox.warning(self,"Delete failed",str(exc))
    def create_group(self):
        dialog=GroupDialog(self.api,self)
        if dialog.exec_()!=dialog.Accepted: return
        title,ids=dialog.values()
        try:
            chat=self.api.create_group(title,ids); chat["chat_type"]="group"; self.open_chat(chat); self.refresh_chats()
        except Exception as exc: QMessageBox.warning(self,"Group failed",str(exc))
    def search_messages(self):
        term,ok=QInputDialog.getText(self,"Find messages","Search text")
        if not ok or not term.strip(): return
        try:
            results=self.api.search_messages(term); self.chats.clear()
            for result in results:
                item=QListWidgetItem(f"{result['chat_type']} #{result['chat_id']}\n{result.get('body','')[:100]}")
                item.setData(Qt.UserRole,result); self.chats.addItem(item)
            self.status.set_detail(f"{len(results)} results")
        except Exception as exc: QMessageBox.warning(self,"Search failed",str(exc))
    def edit_profile(self):
        dialog=ProfileDialog(self.user,self)
        if dialog.exec_()!=dialog.Accepted: return
        name,bio=dialog.values()
        try: self.user=self.api.update_profile(name,bio); self.status.set_detail("Profile updated")
        except Exception as exc: QMessageBox.warning(self,"Profile failed",str(exc))
    def typing(self,text):
        if text.strip() and self.realtime and self.chat_id:
            self.realtime.send_event({"type":"typing","chat_type":self.chat_type,"chat_id":self.chat_id,"username":self.user["username"]})
    def on_event(self,event):
        kind=event.get("type")
        if kind in {"new_message","message_updated","presence","group_added","group_removed"}:
            self.refresh_chats()
            if event.get("chat_id")==self.chat_id or event.get("group_id")==self.chat_id: self.refresh_messages()
        elif kind=="typing" and event.get("chat_id")==self.chat_id:
            self.subtitle.setText(f"@{event.get('username','Someone')} is typing…")
    def closeEvent(self,event):
        if self.realtime: self.realtime.stop()
        event.accept()
