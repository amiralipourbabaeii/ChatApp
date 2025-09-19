import sqlite3
import hashlib

conn = sqlite3.connect('Database.db')
cursor = conn.cursor()

# جدول یوزرها
cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Firstname TEXT,
    Lastname TEXT,
    Username TEXT UNIQUE,
    Password TEXT
);
''')

# جدول کانتکت‌ها
cursor.execute('''
CREATE TABLE IF NOT EXISTS Contacts (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1 TEXT,
    user2 TEXT
);
''')

# جدول پیام‌ها
cursor.execute('''
CREATE TABLE IF NOT EXISTS Message (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Sender TEXT,
    Receiver TEXT,
    Content TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS GroupChat (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT UNIQUE,
    IsChannel INTEGER,
    Creator TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS GroupMessage (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    GroupId INTEGER,
    Sender TEXT,
    Content TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS GroupMembers (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    GroupId INTEGER,
    Username TEXT
)
''')

conn.commit()


# ---------------------- توابع ----------------------

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
        cursor.execute("SELECT Username FROM User WHERE Username != ?", (exclude_username,))
    else:
        cursor.execute("SELECT Username FROM User")
    return [row[0] for row in cursor.fetchall()]

def add_contact(user1, user2):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    
    # اول چک کنیم که user2 وجود داشته باشه
    cur.execute("SELECT * FROM User WHERE Username=?", (user2,))
    if not cur.fetchone():
        conn.close()
        return False

    # بعد چک کنیم که قبلاً اضافه نشده
    cur.execute("SELECT * FROM Contacts WHERE user1=? AND user2=?", (user1, user2))
    if cur.fetchone():
        conn.close()
        return False
    
    # اضافه کردن دوطرفه
    cur.execute("INSERT INTO Contacts (user1, user2) VALUES (?, ?)", (user1, user2))
    cur.execute("INSERT INTO Contacts (user1, user2) VALUES (?, ?)", (user2, user1))
    conn.commit()
    conn.close()
    return True


def get_contacts(username):
    cursor.execute('''
        SELECT user2 FROM Contacts WHERE user1=?
        UNION
        SELECT user1 FROM Contacts WHERE user2=?
    ''', (username, username))
    return [row[0] for row in cursor.fetchall()]

def create_group(name, creator, is_channel=0):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO GroupChat (Name, Creator, IsChannel) VALUES (?, ?, ?)", 
                    (name, creator, is_channel))
        group_id = cur.lastrowid
        # خود سازنده هم عضو گروه بشه
        cur.execute("INSERT INTO GroupMembers (GroupId, Username) VALUES (?, ?)", (group_id, creator))
        conn.commit()
        conn.close()
        return group_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def add_user_to_group(group_id, username):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM GroupMembers WHERE GroupId=? AND Username=?", (group_id, username))
    if cur.fetchone():
        conn.close()
        return False
    cur.execute("INSERT INTO GroupMembers (GroupId, Username) VALUES (?, ?)", (group_id, username))
    conn.commit()
    conn.close()
    return True

def send_group_message(group_id, sender, content):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute("SELECT IsChannel, Creator FROM GroupChat WHERE Id=?", (group_id,))
    row = cur.fetchone()
    if row and row[0] == 1 and row[1] != sender:
        conn.close()
        return False
    cur.execute("INSERT INTO GroupMessage (GroupId, Sender, Content) VALUES (?, ?, ?)", 
                (group_id, sender, content))
    conn.commit()
    conn.close()
    return True


def get_group_messages(group_id):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute("SELECT Sender, Content, Timestamp FROM GroupMessage WHERE GroupId=? ORDER BY Timestamp ASC", 
                (group_id,))
    messages = cur.fetchall()
    conn.close()
    return messages

def get_user_groups(username):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT GroupChat.Id, GroupChat.Name, GroupChat.IsChannel 
        FROM GroupChat 
        INNER JOIN GroupMembers ON GroupChat.Id = GroupMembers.GroupId
        WHERE GroupMembers.Username=?
    """, (username,))
    groups = cur.fetchall()
    conn.close()
    return groups  # [(id, name, is_channel), ...]

def get_all_groups():
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute("SELECT Id, Name, IsChannel FROM GroupChat")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_group_by_name(name):
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute("SELECT Id, Name, IsChannel, Creator FROM GroupChat WHERE Name=?", (name,))
    row = cur.fetchone()
    conn.close()
    return row
