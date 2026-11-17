"""Login and registration dialog."""
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QLabel,QLineEdit,QTabWidget,QWidget,QPushButton,QMessageBox
from PyQt5.QtCore import Qt
from client.api import APIClient

class AuthDialog(QDialog):
    def __init__(self,default_url,parent=None):
        super().__init__(parent); self.setWindowTitle("Northstar Messenger"); self.setMinimumWidth(420)
        self.api=None; self.user=None
        root=QVBoxLayout(self); title=QLabel("Northstar Messenger")
        title.setAlignment(Qt.AlignCenter); title.setStyleSheet("font-size:20pt;font-weight:700;color:#229ed9")
        root.addWidget(title); root.addWidget(QLabel("Server address"))
        self.url=QLineEdit(default_url); root.addWidget(self.url)
        self.tabs=QTabWidget(); self.tabs.addTab(self._tab(False),"Log in"); self.tabs.addTab(self._tab(True),"Register")
        root.addWidget(self.tabs)
    def _tab(self,register):
        widget=QWidget(); layout=QVBoxLayout(widget)
        self.username=QLineEdit(); self.username.setPlaceholderText("Username")
        self.password=QLineEdit(); self.password.setPlaceholderText("Password"); self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.username); layout.addWidget(self.password)
        self.confirm=None
        if register:
            self.confirm=QLineEdit(); self.confirm.setPlaceholderText("Confirm password")
            self.confirm.setEchoMode(QLineEdit.Password); layout.addWidget(self.confirm)
        button=QPushButton("Create account" if register else "Log in")
        button.clicked.connect(lambda:self._submit(register)); layout.addWidget(button)
        self.password.returnPressed.connect(button.click); return widget
    def _submit(self,register):
        try:
            self.api=APIClient(self.url.text())
            if register:
                if self.confirm.text()!=self.password.text(): raise ValueError("Passwords do not match.")
                result=self.api.register(self.username.text(),self.password.text())
            else: result=self.api.login(self.username.text(),self.password.text())
            self.user=result["user"]; self.accept()
        except Exception as exc: QMessageBox.warning(self,"Sign in failed",str(exc))
