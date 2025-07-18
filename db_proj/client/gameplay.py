import sqlite3
import time
import os

def start_new_game(user_id):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM MATCHMAKING WHERE id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO MATCHMAKING (id) VALUES (?)", (user_id,))
        conn.commit()

    cursor.execute("SELECT id FROM MATCHMAKING WHERE id != ? ORDER BY rowid ASC LIMIT 1", (user_id,))
    opponent = cursor.fetchone()

    if opponent:
        opponent_id = opponent[0]
        cursor.execute("DELETE FROM MATCHMAKING WHERE id IN (?, ?)", (user_id, opponent_id))
        conn.commit()

        print(f"Matched with player : {opponent_id}! Starting game...")
        time.sleep(2)
        gg(user_id, opponent_id)
    else:
        print("Waiting for an opponent...")
        time.sleep(2)

    conn.close()

def gg(player1_id, player2_id):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM questions ORDER BY RANDOM() LIMIT 3") # راندها به 3 کاهش یافته
    questions = [row[0] for row in cursor.fetchall()]

    cursor.execute('''
        INSERT INTO games (player1_id, player2_id, winner_id, loser_id, status)
        VALUES (?, ?, -1, -1, 'active')
    ''', (player1_id, player2_id))
    game_id = cursor.lastrowid

    for i, qid in enumerate(questions):
        cursor.execute('''
            INSERT INTO rounds (game_id, round_number, question_id)
            VALUES (?, ?, ?)
        ''', (game_id, i + 1, qid))

    conn.commit()
    conn.close()

    print(f"\nGame {game_id} started between {player1_id} and {player2_id}!")
    print(f"{len(questions)} questions have been assigned to the game.")
    input("\nPress Enter to continue...")
    continue_pending_game(player1_id, game_id)

def continue_pending_game(user_identifier, game_id):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    current_user_id = None
    current_username_str = None

    if isinstance(user_identifier, str):
        cursor.execute("SELECT id, username FROM players WHERE username = ?", (user_identifier,))
        result = cursor.fetchone()
        if not result:
            print("Error: Current user (username) not found in database.")
            conn.close()
            return
        current_user_id = result[0]
        current_username_str = result[1]
    elif isinstance(user_identifier, int):
        cursor.execute("SELECT id, username FROM players WHERE id = ?", (user_identifier,))
        result = cursor.fetchone()
        if not result:
            print("Error: Current user (ID) not found in database.")
            conn.close()
            return
        current_user_id = result[0]
        current_username_str = result[1]
    else:
        print("Error: Invalid user identifier type passed to continue_pending_game.")
        conn.close()
        return

    cursor.execute("""
        SELECT id, player1_id, player2_id FROM games
        WHERE (id = ?) AND status = 'active'
    """, (game_id,))
    game = cursor.fetchone()
    if not game:
        print("No active games found or game finished.")
        time.sleep(2)
        conn.close()
        return

    game_id, p1_id, p2_id = game

    cursor.execute("SELECT id, round_number, question_id, player1_answer, player2_answer FROM rounds WHERE game_id = ? ORDER BY round_number ASC", (game_id,))
    rounds = cursor.fetchall()

    current_round_index = -1
    for i, rnd in enumerate(rounds):
        _, _, _, ans1, ans2 = rnd
        if ans1 is None or ans2 is None:
            current_round_index = i
            break
    
    if current_round_index == -1:
        _finish_game(conn, cursor, game_id, p1_id, p2_id, rounds)
        return

    round_id, round_number, qid, player1_ans, player2_ans = rounds[current_round_index]

    cursor.execute("SELECT text, option_a, option_b, option_c, option_d, correct_option FROM questions WHERE id = ?", (qid,))
    q_data = cursor.fetchone()

    print(f"\nGame ID: {game_id} | Round {round_number}/{len(rounds)}")
    print(f"Question: {q_data[0]}")
    print(f"A) {q_data[1]}  B) {q_data[2]}  C) {q_data[3]}  D) {q_data[4]}")

    player_to_answer_first = p1_id if round_number % 2 != 0 else p2_id

    if current_user_id == player_to_answer_first:
        if (current_user_id == p1_id and player1_ans is not None) or \
           (current_user_id == p2_id and player2_ans is not None):
            print("You have already answered this round. Waiting for opponent...")
            time.sleep(2)
            conn.close()
            return
        
        print(f"\nIt's your turn to answer first in Round {round_number}.")
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        while answer not in ["A", "B", "C", "D"]:
            answer = input("Invalid. Please enter A/B/C/D: ").strip().upper()

        if current_user_id == p1_id:
            cursor.execute("UPDATE rounds SET player1_answer = ? WHERE id = ?", (answer, round_id))
        else:
            cursor.execute("UPDATE rounds SET player2_answer = ? WHERE id = ?", (answer, round_id))
        conn.commit()
        print("Answer saved. Waiting for opponent to answer this round...")
        time.sleep(2)
        conn.close()
        return

    else: # این بازیکن باید دوم در این راند پاسخ دهد
        if (player_to_answer_first == p1_id and player1_ans is None) or \
           (player_to_answer_first == p2_id and player2_ans is None):
            print("Waiting for opponent to answer first in this round...")
            time.sleep(2)
            conn.close()
            return
        
        if (current_user_id == p1_id and player1_ans is not None) or \
           (current_user_id == p2_id and player2_ans is not None):
            print("You have already answered this round. Waiting for the game to proceed to next round...")
            time.sleep(2)
            conn.close()
            return

        print(f"\nOpponent has answered Round {round_number}. It's your turn to answer.")
        answer = input("Your answer (A/B/C/D): ").strip().upper()
        while answer not in ["A", "B", "C", "D"]:
            answer = input("Invalid. Please enter A/B/C/D: ").strip().upper()

        if current_user_id == p1_id:
            cursor.execute("UPDATE rounds SET player1_answer = ? WHERE id = ?", (answer, round_id))
        else:
            cursor.execute("UPDATE rounds SET player2_answer = ? WHERE id = ?", (answer, round_id))
        conn.commit()
        print("Answer saved. Round complete.")
        time.sleep(2)
        conn.close()
        return


def _finish_game(conn, cursor, game_id, p1_id, p2_id, all_rounds_data):
    score1 = 0
    score2 = 0

    for _, _, qid, ans1, ans2 in all_rounds_data:
        cursor.execute("SELECT correct_option, difficulty FROM questions WHERE id = ?", (qid,))
        row = cursor.fetchone()
        if not row:
            continue
        correct_option, difficulty = row
        if ans1 == correct_option:
            score1 += difficulty
        if ans2 == correct_option:
            score2 += difficulty

    winner, loser = -1, -1

    if score1 > score2:
        winner, loser = p1_id, p2_id
        print(f"Player {p1_id} wins!")
    elif score2 > score1:
        winner, loser = p2_id, p1_id
        print(f"Player {p2_id} wins!")
    else: # It's a draw
        print("It's a draw!")
        # For draws, winner_id and loser_id remain -1. Trigger will handle stats for draws.

    # این UPDATE بازی را به 'finished' تغییر می‌دهد و Triggerها را فعال می‌کند
    cursor.execute("""
        UPDATE games
        SET winner_id = ?, loser_id = ?, status = 'finished', end_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (winner, loser, game_id))

    conn.commit()
    conn.close()

    print("\nGame finished!")
    print(f"Score - Player {p1_id}: {score1} | Player {p2_id}: {score2}")
    input("\nPress Enter to return...")


def popular_categories():
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT categories.name, COUNT(questions.id) as question_count
        FROM questions
        JOIN categories ON questions.category_id = categories.id
        GROUP BY questions.category_id
        ORDER BY question_count DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()

    print("\n\U0001F4DA Top 5 Most Popular Categories:")
    print("----------------------------------")
    if not rows:
        print("No categories found.")
    else:
        for idx, (name, count) in enumerate(rows, 1):
            print(f"{idx}. {name} — {count} questions")

    conn.close()
    input("\nPress Enter to return...")