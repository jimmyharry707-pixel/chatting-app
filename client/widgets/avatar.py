"""Circular-style initials avatar built with QLabel."""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AvatarLabel(QLabel):
    def __init__(self,name="",size=42,parent=None):
        super().__init__(parent); self.setFixedSize(size,size)
        self.setAlignment(Qt.AlignCenter); self.set_name(name)
        self.setStyleSheet("background:#d8ebfa;color:#277eb9;border-radius:21px;font-weight:700;")
        self.setFont(QFont("Segoe UI",max(9,size//3),QFont.Bold))
    def set_name(self,name):
        words=[part for part in (name or "?").split() if part]
        initials="".join(word[0] for word in words[:2]).upper() or "?"
        self.setText(initials)
