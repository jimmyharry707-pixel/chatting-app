"""Safe HTML rendering for message history.

All user-controlled strings are escaped before they are inserted into QTextBrowser.
Links are restricted to the attachment scheme handled by the main window.
"""
import html
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtCore import QUrl
from shared.timeutils import local_clock

class MessageView(QTextBrowser):
    def __init__(self,parent=None):
        super().__init__(parent); self.setOpenLinks(False); self.setOpenExternalLinks(False)
        self.setStyleSheet("background:#e7eef4;border:0;padding:12px;")
    def render_messages(self,messages,current_user_id,chat_type):
        chunks=["<html><head><style>body{font-family:'Segoe UI';font-size:10pt;color:#202b36;}table{border-collapse:separate;}td{font-family:'Segoe UI';}</style></head><body>"]
        if not messages:
            chunks.append("<p style='text-align:center;color:#71808c;margin-top:180px'>No messages yet. Say hello!</p>")
        for message in messages:
            mine=message.get("sender_id")==current_user_id
            align="right" if mine else "left"
            color="#d8f4d0" if mine else "#fff"
            sender=""
            if chat_type=="group":
                sender=f"<b>{html.escape(message.get('sender_display_name') or message.get('sender_username',''))}</b><br>"
            if message.get("deleted_at"):
                body="<i>This message was deleted</i>"
            else:
                body=html.escape(message.get("body") or "").replace("\n","<br>")
                filename=message.get("attachment_filename")
                if filename:
                    body+=f"<br>📎 <a href='attachment://{chat_type}/{int(message['id'])}'>{html.escape(filename)}</a>"
                if message.get("edited_at"): body+=" <small>(edited)</small>"
            stamp=html.escape(local_clock(message.get("created_at")))
            receipt=" ✓✓" if mine and message.get("is_read") else (" ✓" if mine else "")
            chunks.append(f"<table width='100%' cellpadding='3'><tr><td align='{align}'>"
                f"<table cellpadding='8' bgcolor='{color}'><tr><td>{sender}{body}<br>"
                f"<small style='color:#71808c'>{stamp}{receipt}</small></td></tr></table>"
                "</td></tr></table>")
        chunks.append("</body></html>"); self.setHtml("".join(chunks))
        bar=self.verticalScrollBar(); bar.setValue(bar.maximum())
