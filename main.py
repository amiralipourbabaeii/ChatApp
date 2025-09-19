from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import sys
import db
from Login import Ui_Login
from Signup import Ui_SignUp
from Chatapp import Ui_MessageBox
import shutil
import os


class ChatApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MessageBox()
        self.ui.setupUi(self)

        self.username = username
        self.receiver = None
        self.selected_group_id = None

        # دکمه‌ها
        self.ui.pushButton.clicked.connect(self.send_message)
        self.ui.pushButton_2.clicked.connect(self.select_file)
        self.ui.pushButton_3.clicked.connect(self.add_contact)
        self.ui.pushButton_4.clicked.connect(lambda: self.create_group_or_channel(is_channel=0))
        self.ui.pushButton_5.clicked.connect(lambda: self.create_group_or_channel(is_channel=1))

        # انتخاب آیتم لیست (کاربر یا گروه/کانال)
        self.ui.listWidget.itemClicked.connect(self.select_item)

        # لود اولیه
        self.load_all_items()

    # -------------------- لود همه کاربران و گروه‌ها --------------------
    def load_all_items(self):
        self.ui.listWidget.clear()

        # کاربران
        contacts = db.get_contacts(self.username)
        for c in contacts:
            self.ui.listWidget.addItem(c)

        # گروه‌ها / کانال‌ها
        groups = db.get_user_groups(self.username)
        for group_id, name, is_channel in groups:
            display_name = f"{name} (Channel)" if is_channel else f"{name} (Group)"
            self.ui.listWidget.addItem(display_name)

    # -------------------- انتخاب آیتم --------------------
    def select_item(self, item):
        text = item.text()
        if text.endswith("(Group)") or text.endswith("(Channel)"):
            # گروه یا کانال انتخاب شد
            group_name = text.rsplit(" ", 1)[0]  # اسم گروه
            group = db.get_group_by_name(group_name)
            if group:
                self.selected_group_id = group[0]
                self.receiver = None
                self.load_group_chat(self.selected_group_id)
        else:
            # کاربر انتخاب شد
            self.receiver = text
            self.selected_group_id = None
            self.ui.textBrowser.clear()
            self.ui.textBrowser.append(f"Chatting with {self.receiver}")
            self.load_chat()

    # -------------------- ارسال پیام --------------------
    def send_message(self):
        message = self.ui.lineEdit.text()
        if not message:
            return

        if self.receiver:
            db.send_message(self.username, self.receiver, message)
            self.ui.textBrowser.append(f"You: {message}")
            self.ui.lineEdit.clear()
        elif self.selected_group_id:
            success = db.send_group_message(self.selected_group_id, self.username, message)
            if success:
                self.load_group_chat(self.selected_group_id)
                self.ui.lineEdit.clear()
            else:
                QMessageBox.warning(self, "Error", "Only the creator can send messages in this channel.")
        else:
            QMessageBox.warning(self, "Warning", "Select a user or group first.")

    # -------------------- ارسال فایل --------------------
    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
        if file_path:
            file_name = file_path.split("/")[-1]
            content = f"[File] {file_name}"
            if self.receiver:
                db.send_message(self.username, self.receiver, content)
                self.ui.textBrowser.append(f"You: {content}")
            elif self.selected_group_id:
                db.send_group_message(self.selected_group_id, self.username, content)
                self.load_group_chat(self.selected_group_id)

    # -------------------- بارگذاری چت --------------------
    def load_chat(self):
        self.ui.textBrowser.clear()
        messages = db.get_messages(self.username, self.receiver)
        for sender, content, timestamp in messages:
            prefix = "You" if sender == self.username else sender
            self.ui.textBrowser.append(f"{prefix}: {content}")

    def load_group_chat(self, group_id):
        self.ui.textBrowser.clear()
        messages = db.get_group_messages(group_id)
        for sender, content, timestamp in messages:
            prefix = "You" if sender == self.username else sender
            self.ui.textBrowser.append(f"{prefix}: {content}")

    # -------------------- اضافه کردن مخاطب --------------------
    def add_contact(self):
        new_user, ok = QInputDialog.getText(self, "Add Contact", "Enter username:")
        if ok and new_user:
            if db.add_contact(self.username, new_user):
                QMessageBox.information(self, "Success", f"{new_user} added to contacts.")
                self.load_all_items()
            else:
                QMessageBox.warning(self, "Error", "User not found or already in contacts.")

    # -------------------- ساخت گروه یا کانال --------------------
    def create_group_or_channel(self, is_channel=0):
        name, ok = QInputDialog.getText(self, "Create Group/Channel", "Enter name:")
        if not ok or not name:
            return

        group_id = db.create_group(name, self.username, is_channel)
        if group_id:
            kind = "Channel" if is_channel else "Group"
            QMessageBox.information(self, "Success", f"{kind} '{name}' created!")
            self.load_all_items()
        else:
            QMessageBox.warning(self, "Error", "Name already exists.")

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