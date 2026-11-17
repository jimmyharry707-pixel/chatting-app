"""Message composer with send and attachment signals."""
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QLineEdit,QPushButton
from PyQt5.QtCore import pyqtSignal

class MessageComposer(QWidget):
    send_requested=pyqtSignal(str)
    attachment_requested=pyqtSignal()
    typing_changed=pyqtSignal(str)
    def __init__(self,parent=None):
        super().__init__(parent)
        layout=QHBoxLayout(self); layout.setContentsMargins(12,8,12,8)
        self.attach=QPushButton("Attach"); self.entry=QLineEdit()
        self.entry.setPlaceholderText("Write a message…")
        self.send=QPushButton("Send")
        self.attach.clicked.connect(self.attachment_requested.emit)
        self.send.clicked.connect(self._send)
        self.entry.returnPressed.connect(self._send)
        self.entry.textChanged.connect(self.typing_changed.emit)
        layout.addWidget(self.attach); layout.addWidget(self.entry,1); layout.addWidget(self.send)
        self.set_enabled(False)
    def _send(self):
        text=self.entry.text().strip()
        if text:
            self.send_requested.emit(text); self.entry.clear()
    def set_enabled(self,enabled):
        self.entry.setEnabled(enabled); self.send.setEnabled(enabled); self.attach.setEnabled(enabled)
    def clear(self): self.entry.clear()
