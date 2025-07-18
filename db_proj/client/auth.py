import bcrypt
import sqlite3
import time
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
        time.sleep(2)
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
    cursor.execute("SELECT id FROM players WHERE username = ?", (u,))
    

    
    i=cursor.fetchone()
    cursor.execute("""
        INSERT INTO player_stats (user_id) VALUES (?)
""" , (i[0],))

    print("Registration successful!")
    conn.commit()
    conn.close()
    return u 
 
def login():
    username = input("Username: ")
    password = input("Password: ")

    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password, email FROM players WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row is None:
        print("Username not found.")
        conn.close()
        time.sleep(2)
        return None

    stored_hash, email = row
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        print(f"Welcome back, {username}!")
        conn.close()
        return username

    else:
        print("Incorrect password.")
        print("\nForgot Password?")
        print("1. Reset password via email")
        print("2. Cancel login")
        choice = input("Enter choice (1/2): ")

        if choice.strip() == "1":
            entered_email = input("Enter your registered email: ").strip()
            if entered_email == email:
                new_password = input("Enter your new password: ")
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("UPDATE players SET password = ? WHERE username = ?", (new_hash, username))
                conn.commit()
                print("Password updated successfully. You can now log in.")
            else:
                print("Email does not match our records.")
        else:
            print("Returning to main menu.")

    conn.close()
    time.sleep(2)
    return None
