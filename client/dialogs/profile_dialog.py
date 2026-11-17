"""Profile editing dialog."""
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QLabel,QLineEdit,QPlainTextEdit,QDialogButtonBox

class ProfileDialog(QDialog):
    def __init__(self,profile,parent=None):
        super().__init__(parent); self.setWindowTitle("Edit profile")
        layout=QVBoxLayout(self); layout.addWidget(QLabel("Display name"))
        self.name=QLineEdit(profile.get("display_name") or profile.get("username",""))
        layout.addWidget(self.name); layout.addWidget(QLabel("Bio"))
        self.bio=QPlainTextEdit(); self.bio.setPlainText(profile.get("bio",""))
        self.bio.setMaximumBlockCount(4); layout.addWidget(self.bio)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
    def values(self): return self.name.text().strip(),self.bio.toPlainText().strip()
