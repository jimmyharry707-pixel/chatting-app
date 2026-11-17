"""Desktop application entry point."""
import sys
from PyQt5.QtWidgets import QApplication,QDialog,QMessageBox
from PyQt5.QtGui import QFont
from client.config import settings
from client.dialogs.auth_dialog import AuthDialog
from client.main_window import MainWindow

def main():
    app=QApplication(sys.argv); app.setStyle("Fusion"); app.setFont(QFont("Segoe UI",10))
    app.setStyleSheet("""
    QWidget{font-family:'Segoe UI';font-size:10pt;color:#202b36}
    QMainWindow,QDialog{background:#eef3f7}
    QLineEdit,QPlainTextEdit{background:#f1f4f6;border:1px solid #dfe6ec;border-radius:8px;padding:9px}
    QPushButton{background:#3390ec;color:white;border:0;border-radius:8px;padding:8px 14px;font-weight:600}
    QPushButton:hover{background:#2683df}
    QListWidget{background:white;border:0}
    QListWidget::item{padding:12px;border-bottom:1px solid #f0f2f4}
    QListWidget::item:selected{background:#e7f2fc}
    """)
    auth=AuthDialog(settings.server_url)
    if auth.exec_()!=QDialog.Accepted: return
    window=MainWindow(auth.api,auth.user); window.show()
    sys.exit(app.exec_())

if __name__=="__main__": main()
