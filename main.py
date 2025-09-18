import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow
import db
from Login import Ui_Login
from Signup import Ui_SignUp
from PyQt5.QtWidgets import QMainWindow
from Chatapp import Ui_MessageBox

class ChatApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)
        self.ui.listWidget.itemClicked.connect(self.select_receiver)
        self.receiver = None
        self.username = username
        self.ui.pushButton.clicked.connect(self.send_message)
        usernames = db.get_all_usernames(self.username)
        self.ui.listWidget.addItems(usernames)  

    def select_receiver(self, item):
        self.receiver = item.text()
        self.ui.textBrowser.append(f"Chatting with {self.receiver}")
        self.load_chat()

    def send_message(self):
        message = self.ui.lineEdit.text()
        if message and self.receiver:
            db.send_message(self.username, self.receiver, message)
            self.ui.textBrowser.append(f"You: {message}")
            self.ui.lineEdit.clear()
        elif not self.receiver:
            QMessageBox.warning(self, "Warning", "Please select a user to chat with.")

    def load_chat(self):
        self.ui.textBrowser.clear()
        messages = db.get_messages(self.username, self.receiver)
        for sender, content, timestamp in messages:
            prefix = "You" if sender == self.username else sender
            self.ui.textBrowser.append(f"{prefix}: {content}")




class LoginForm(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.ui.pushButton_2.clicked.connect(self.SignupApp)
        self.ui.pushButton_3.clicked.connect(self.close)
        self.ui.pushButton.clicked.connect(self.handle_login)

    def handle_login(self):
        self.username = self.ui.lineEdit.text()
        self.password = self.ui.lineEdit_2.text()
        if not self.username or not self.password:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return
        if db.Login_db(self.username, self.password):
            QMessageBox.information(self, "Login", "Login successful!")
            self.chat_window = ChatApp(self.username)
            self.chat_window.show()
            self.close()

        else:
            QMessageBox.warning(self, "Login Failed", "Username or password is incorrect.")

    def SignupApp(self):
        self.signup_window = SignupForm()
        self.signup_window.show()

class SignupForm(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SignUp()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.handle_Signup)
        self.ui.pushButton_2.clicked.connect(self.close)

    def handle_Signup(self):
        self.firstname = self.ui.lineEdit.text()
        self.lastname = self.ui.lineEdit_2.text()
        self.username = self.ui.lineEdit_3.text()
        self.password = self.ui.lineEdit_4.text()
        self.confirm_password = self.ui.lineEdit_5.text()

        if not all([self.firstname, self.lastname, self.username, self.password, self.confirm_password]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        if self.password != self.confirm_password:
            QMessageBox.warning(self, "Warning", "Passwords do not match.")
            return

        success = db.Signup_db(self.firstname, self.lastname, self.username, self.password)
        if success:
            QMessageBox.information(self, 'Information', "Signup successful, welcome.")
            self.close()
        else:
            QMessageBox.warning(self, "Warning", "Username already exists.")

app = QApplication(sys.argv)
LoginUi = LoginForm()
LoginUi.show()
sys.exit(app.exec_())