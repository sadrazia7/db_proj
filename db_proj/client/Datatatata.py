import sqlite3
import bcrypt
import random
#######inserting sample datas into database(samples are made by AI)
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_data():
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    categories = ['Math', 'Science', 'History', 'Geography', 'Literature']
    for cat in categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

    players = [
        ('alice', 'alice@example.com', 0, 0), 
        ('bob', 'bob@example.com', 0, 0),
        ('carol', 'carol@example.com', 1, 0),  
        ('dave', 'dave@example.com', 0, 1),   
        ('eve', 'eve@example.com', 0, 0),
        ('frank', 'frank@example.com', 0, 0),
        ('grace', 'grace@example.com', 0, 0),
        ('heidi', 'heidi@example.com', 0, 0),
        ('ivan', 'ivan@example.com', 1, 0), 
        ('judy', 'judy@example.com', 0, 0)
    ]
    for username, email, role, isbanned in players:
        password = hash_password("password123")
        cursor.execute("""
            INSERT OR IGNORE INTO players (username, password, email, xp, role, isbanned)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password, email, random.randint(0, 100), role, isbanned))

    # === 3. Questions ===
    sample_questions = [
        ('What is 5 + 3?', '6', '7', '8', '9', 'C', 1, 1),
        ('What is 9 x 9?', '81', '72', '99', '91', 'A', 1, 2),
        ('Which planet is the hottest?', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'A', 2, 1),
        ('What gas do we breathe in?', 'Oxygen', 'Carbon', 'Helium', 'Nitrogen', 'A', 2, 1),
        ('Who wrote Iliad?', 'Virgil', 'Homer', 'Shakespeare', 'Sophocles', 'B', 5, 3),
        ('What is the capital of Japan?', 'Seoul', 'Beijing', 'Tokyo', 'Bangkok', 'C', 4, 2),
        ('What year was WWII?', '1914', '1939', '1945', '1965', 'B', 3, 2),
        ('What is 2^5?', '16', '32', '64', '128', 'B', 1, 1),
        ('Which is a mammal?', 'Shark', 'Dolphin', 'Octopus', 'Trout', 'B', 2, 2),
        ('Who painted the Mona Lisa?', 'Michelangelo', 'Raphael', 'Da Vinci', 'Van Gogh', 'C', 5, 3),
        ('Which ocean is largest?', 'Atlantic', 'Indian', 'Pacific', 'Arctic', 'C', 4, 2),
        ('Who discovered gravity?', 'Newton', 'Einstein', 'Kepler', 'Galileo', 'A', 2, 3),
        ('When was the Cold War?', '1947-1991', '1920-1940', '2000-2020', '1800-1850', 'A', 3, 2),
        ('What is H2O?', 'Oxygen', 'Water', 'Hydrogen', 'Salt', 'B', 2, 1),
        ('Who is the author of 1984?', 'Orwell', 'Huxley', 'Bradbury', 'Atwood', 'A', 5, 3),
        ('Which continent is Egypt in?', 'Asia', 'Africa', 'Europe', 'Australia', 'B', 4, 2),
        ('What is 15 % of 200?', '20', '30', '25', '35', 'B', 1, 1),
        ('What’s the boiling point of water?', '90°C', '100°C', '110°C', '120°C', 'B', 2, 2),
        ('Who was Napoleon?', 'French King', 'General', 'President', 'Poet', 'B', 3, 3),
        ('Where is the Great Wall?', 'India', 'Japan', 'China', 'Korea', 'C', 4, 2),
    ]

    for text, a, b, c, d, correct, category_id, difficulty in sample_questions:
        author_id = random.randint(1, 10) 
        cursor.execute("""
            INSERT INTO questions (
                text, option_a, option_b, option_c, option_d,
                correct_option, category_id, difficulty, author_id, approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (text, a, b, c, d, correct, category_id, difficulty, author_id))

    conn.commit()
    conn.close()
    print("Sample data inserted successfully.")

if __name__ == "__main__":
    seed_data()
