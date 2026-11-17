"""Compact connection and application status widget."""
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QLabel
from PyQt5.QtCore import Qt

class StatusBar(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); layout=QHBoxLayout(self)
        layout.setContentsMargins(12,3,12,3)
        self.connection=QLabel("Offline"); self.detail=QLabel("Northstar Messenger")
        self.detail.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.connection.setStyleSheet("color:#71808c;font-size:9pt")
        self.detail.setStyleSheet("color:#71808c;font-size:9pt")
        layout.addWidget(self.connection); layout.addStretch(1); layout.addWidget(self.detail)
    def set_connection(self,value):
        self.connection.setText(value)
        color="#229e67" if "connected" in value.lower() else "#71808c"
        self.connection.setStyleSheet(f"color:{color};font-size:9pt")
    def set_detail(self,value): self.detail.setText(value)
