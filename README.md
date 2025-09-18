💬 ChatApp
📌 Introduction

ChatApp is a simple local messenger built with Python (PyQt5 + SQLite).
It allows users to sign up, log in, and send/receive messages on a local environment without the need for an internet connection.

⚙️ Requirements

Python 3.x

PyQt5

SQLite3 (comes built-in with Python)

Install dependencies:

pip install -r requirements.txt

🚀 How to Run

Clone the repository:

git clone https://github.com/amiralipourbabaeii/ChatApp.git
cd ChatApp


Initialize the database:

python db.py


Run the application:

python main.py

🎯 Features

User registration (Sign Up)

User login (Sign In)

Local message sending/receiving

SQLite database for storing user info and messages

Simple and clean PyQt5 GUI

📂 Project Structure
📦 ChatApp
 ┣ 📜 main.py          # Main entry point
 ┣ 📜 Chatapp.py       # Core chat logic
 ┣ 📜 Login.py         # Login form (PyQt5)
 ┣ 📜 Signup.py        # Signup form (PyQt5)
 ┣ 📜 db.py            # Database setup
 ┣ 📜 Database.db      # SQLite database
 ┣ 📂 form             # UI forms
 ┣ 📜 requirements.txt # Dependencies
 ┗ 📜 README.md        # Project description

🤝 Contributing

Contributions are welcome!
Feel free to fork the project and submit pull requests.

📜 License

This project is licensed under the MIT License.