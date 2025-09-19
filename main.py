from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import sys
import db
from Login import Ui_Login
from Signup import Ui_SignUp
from Chatapp import Ui_MessageBox
import shutil
import os
from AddContact import Ui_AddContact


class ChatApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)
        self.username = username
        self.load_contacts()
        self.receiver = None
        self.ui.pushButton.clicked.connect(self.send_message)
        self.ui.pushButton_2.clicked.connect(self.select_file)
        self.ui.listWidget.itemClicked.connect(self.select_receiver)
        self.ui.pushButton_3.clicked.connect(self.add_contact)
        # usernames = db.get_all_usernames(self.username)
        # self.ui.listWidget.addItems(usernames)
        
    
    def load_contacts(self):
        self.ui.listWidget.clear()
        contacts = db.get_contacts(self.username)
        self.ui.listWidget.addItems(contacts)

    def add_contact(self):
        from PyQt5.QtWidgets import QInputDialog
        new_user, ok = QInputDialog.getText(self, "Add Contact", "Enter username:")
        if ok and new_user:
            if db.add_contact(self.username, new_user):
                QMessageBox.information(self, "Success", f"{new_user} added to contacts.")
                self.load_contacts()
            else:
                QMessageBox.warning(self, "Error", "User not found or already in contacts.")
    

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

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
        if file_path:
            self.send_file(file_path)

    def load_chat(self):
        self.ui.textBrowser.clear()
        messages = db.get_messages(self.username, self.receiver)
        for sender, content, timestamp in messages:
            prefix = "You" if sender == self.username else sender
            if content.startswith("[File]"):
                file_name = content.replace("[File]", "").strip()
                self.ui.textBrowser.append(f"{prefix}: [File]{file_name}")
            else:
                self.ui.textBrowser.append(f"{prefix}: {content}")

    def handle_contact(self):
        self.ContactUi = AddContactForm()
        self.ContactUi.show()
    
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
    def __init__(self):
        super().__init__()
        self.ui = Ui_AddContact()
        self.ui.setupUi(self)
        self.ui.pushButton_2.clicked.connect(self.close_app)
        
    def close_app(self):
        self.close()

# class AddContactForm(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.ui = Ui_AddContact()
#         self.ui.setupUi(self)
#         self.ui.pushButton_2.clicked.connect(self.close_app)
        
#     def close_app(self):
#         self.close()



app = QApplication(sys.argv)
LoginUi = LoginForm()
LoginUi.show()
sys.exit(app.exec_())