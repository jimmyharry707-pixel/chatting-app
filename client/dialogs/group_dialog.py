"""Create group dialog with multi-select member list."""
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QLabel,QLineEdit,QListWidget,QListWidgetItem,QDialogButtonBox,QAbstractItemView,QMessageBox
from PyQt5.QtCore import Qt

class GroupDialog(QDialog):
    def __init__(self,api,parent=None):
        super().__init__(parent); self.api=api; self.setWindowTitle("Create group"); self.resize(440,520)
        layout=QVBoxLayout(self); layout.addWidget(QLabel("Group name"))
        self.title=QLineEdit(); layout.addWidget(self.title)
        self.search=QLineEdit(); self.search.setPlaceholderText("Search users, press Enter")
        self.search.returnPressed.connect(self.load_users); layout.addWidget(self.search)
        self.people=QListWidget(); self.people.setSelectionMode(QAbstractItemView.MultiSelection); layout.addWidget(self.people,1)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
    def load_users(self):
        try: results=self.api.search_users(self.search.text())
        except Exception as exc:
            QMessageBox.warning(self,"Search failed",str(exc)); return
        self.people.clear()
        for user in results:
            item=QListWidgetItem(f"{user.get('display_name') or user['username']} (@{user['username']})")
            item.setData(Qt.UserRole,user["id"]); self.people.addItem(item)
    def values(self):
        return self.title.text().strip(),[int(i.data(Qt.UserRole)) for i in self.people.selectedItems()]
