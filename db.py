import sqlite3
import hashlib

conn = sqlite3.connect('Database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Firstname TEXT,
    Lastname TEXT,
    Username TEXT UNIQUE,
    Password TEXT
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Message (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Sender TEXT,
    Receiver TEXT,
    Content TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def Signup_db(Firstname, Lastname, Username, Password):
    hashed = hash_password(Password)
    try:
        cursor.execute('INSERT INTO User(Firstname, Lastname, Username, Password) VALUES (?, ?, ?, ?)',
                       (Firstname, Lastname, Username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def Login_db(Username, Password):
    hashed = hash_password(Password)
    cursor.execute('SELECT * FROM User WHERE Username = ? AND Password = ?', (Username, hashed))
    user = cursor.fetchone()
    return user is not None

def send_message(sender, receiver, content):
    cursor.execute('INSERT INTO Message(Sender, Receiver, Content) VALUES (?, ?, ?)',
                   (sender, receiver, content))
    conn.commit()

def get_messages(user1, user2):
    cursor.execute('''
        SELECT Sender, Content, Timestamp FROM Message
        WHERE (Sender = ? AND Receiver = ?) OR (Sender = ? AND Receiver = ?)
        ORDER BY Timestamp ASC
    ''', (user1, user2, user2, user1))
    return cursor.fetchall()

def get_all_usernames(exclude_username=None):
    if exclude_username:
        cursor.execute("SELECT username FROM User WHERE username != ?", (exclude_username,))
    else:
        cursor.execute("SELECT username FROM User")
    return [row[0] for row in cursor.fetchall()]