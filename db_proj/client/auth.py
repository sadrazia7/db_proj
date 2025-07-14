import bcrypt
import sqlite3
import re
def register():
    u = input("Your username: ")
    conn = sqlite3.connect("dd.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE username = ?", (u,))
    existing_user = cursor.fetchone()
    if existing_user:
        print("Username is already taken")
        conn.close()
        return None

    e = input("Your Email: ")
    while not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', e):
        print("Please enter a valid email")
        e = input("Your Email: ")

    p = input("Password: ")
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("""
        INSERT INTO players (username, email, password)
        VALUES (?, ?, ?)
    """, (u, e, hashed))
    conn.commit()
    print("✅ Registration successful!")

    conn.close()
    return u 
 
def login():
    username = input("Username: ")
    password = input("Password: ")

    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM players WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row is None:
        print("Username not found.")
        conn.close()
        return None

    stored_hash = row[0]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        print(f"Welcome back, {username}!")
        conn.close()
        return username
    else:
        print("Incorrect password.")
        conn.close()
        return None

