from auth import register, login
from gameplay import start_new_game , continue_pending_game , popular_categories 
# Import new functions
from stats import view_my_ranking, view_stats , top_10_players, get_xp_for_period, top_players_by_period 
import os
import sqlite3
import time
def AdminWantsYourGames(user_id):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM players WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        print("No such player.")
        conn.close()
        return

    username = user[0]
    print(f"\n Match History for {username} (ID: {user_id})")
    print("-" * 60)

    cursor.execute("""
        SELECT
            g.id,
            g.player1_id, p1.username,
            g.player2_id, p2.username,
            g.winner_id,
            g.loser_id,
            g.status,
            g.start_time,
            g.end_time
        FROM games g
        JOIN players p1 ON g.player1_id = p1.id
        JOIN players p2 ON g.player2_id = p2.id
        WHERE g.player1_id = ? OR g.player2_id = ?
        ORDER BY g.start_time DESC
    """, (user_id, user_id))

    games = cursor.fetchall()
    if not games:
        print("No matches found.")
    else:
        for game in games:
            winner_name = "N/A"
            loser_name = "N/A"
            if game[5] != -1: # winner_id is not -1
                cursor.execute("SELECT username FROM players WHERE id = ?", (game[5],))
                winner_name = cursor.fetchone()[0]
                cursor.execute("SELECT username FROM players WHERE id = ?", (game[6],))
                loser_name = cursor.fetchone()[0]
            elif game[5] == -1 and game[7] == 'finished': # It's a draw and finished
                winner_name = "Draw"
                loser_name = "Draw"


            print(f"Game ID: {game[0]} | Players: {game[2]} vs {game[4]} | Winner: {winner_name} | Loser: {loser_name} | Status: {game[7]} | Start: {game[8]} | End: {game[9]}")
    conn.close()
    input("\nPress Enter to return...")

def addquestion(author_id):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    question_text = input("Enter the question text: ")
    option_a = input("Enter option A: ")
    option_b = input("Enter option B: ")
    option_c = input("Enter option C: ")
    option_d = input("Enter option D: ")
    correct_option = input("Enter the correct option (A, B, C, D): ").upper()
    while correct_option not in ['A', 'B', 'C', 'D']:
        correct_option = input("Invalid option. Enter A, B, C, or D: ").upper()

    cursor.execute("SELECT name FROM categories")
    categories = cursor.fetchall()
    print("\nAvailable Categories:")
    for i, cat in enumerate(categories):
        print(f"{i+1}. {cat[0]}")
    
    category_choice = int(input("Enter the number for the category: "))
    category_name = categories[category_choice-1][0]
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()[0]

    difficulty = int(input("Enter difficulty (1-5, 5 is hardest): "))
    while not (1 <= difficulty <= 5):
        difficulty = int(input("Invalid difficulty. Enter a number between 1 and 5: "))

    cursor.execute("""
        INSERT INTO questions (text, option_a, option_b, option_c, option_d, correct_option, category_id, difficulty, author_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (question_text, option_a, option_b, option_c, option_d, correct_option, category_id, difficulty, author_id))
    conn.commit()
    conn.close()
    print("Question added successfully! Awaiting admin approval.")
    time.sleep(2)

def approve_questions():
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("SELECT q.id, q.text, p.username FROM questions q JOIN players p ON q.author_id = p.id WHERE q.approved = 0")
    pending_questions = cursor.fetchall()

    if not pending_questions:
        print("No pending questions for approval.")
        time.sleep(2)
        conn.close()
        return

    print("\n--- Pending Questions for Approval ---")
    for q_id, q_text, author_name in pending_questions:
        print(f"Question ID: {q_id} | Author: {author_name} | Text: {q_text}")
        choice = input("Approve this question? (yes/no/skip): ").lower()
        if choice == 'yes':
            cursor.execute("UPDATE questions SET approved = 1 WHERE id = ?", (q_id,))
            conn.commit()
            print("Question approved.")
        elif choice == 'no':
            cursor.execute("DELETE FROM questions WHERE id = ?", (q_id,))
            conn.commit()
            print("Question rejected and deleted.")
        elif choice == 'skip':
            print("Skipping question.")
        else:
            print("Invalid input. Skipping question.")
    
    conn.close()
    input("\nPress Enter to return...")

def adminmenu(username):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    while True:
        os.system('clear')
        print(f"\nWelcome, Admin {username}!")
        print("--- Admin Menu ---")
        print("1. View All Players")
        print("2. Ban/Unban Player")
        print("3. Add Question")
        print("4. Approve Questions")
        print("5. View All Games (Admin)")
        print("0. Logout")

        choice = input("Choose an option: ")

        if choice == "1":
            AdminWantsAllPlayers()
        elif choice == "2":
            AdminWantsToBanPlayer()
        elif choice == "3":
            addquestion(user[0])
        elif choice == "4":
            approve_questions()
        elif choice == "5":
            AdminWantsYourGames(user[0]) # Assuming user[0] is admin's ID
        elif choice == "0":
            print("Logged out from admin panel.")
            time.sleep(1)
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def AdminWantsAllPlayers():
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, xp, isbanned, role FROM players")
    players = cursor.fetchall()
    conn.close()

    print("\n--- All Players ---")
    print("{:<5} {:<15} {:<25} {:<5} {:<10} {:<10}".format("ID", "Username", "Email", "XP", "Banned", "Role"))
    print("-" * 70)
    for player in players:
        banned_status = "Yes" if player[4] else "No"
        role_status = "Admin" if player[5] else "User"
        print(f"{player[0]:<5} {player[1]:<15} {player[2]:<25} {player[3]:<5} {banned_status:<10} {role_status:<10}")
    input("\nPress Enter to return...")

def AdminWantsToBanPlayer():
    player_id = input("Enter player ID to ban/unban: ")
    try:
        player_id = int(player_id)
    except ValueError:
        print("Invalid ID.")
        time.sleep(1)
        return

    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, isbanned FROM players WHERE id = ?", (player_id,))
    player = cursor.fetchone()

    if player:
        new_status = 1 if player[1] == 0 else 0
        status_text = "banned" if new_status == 1 else "unbanned"
        cursor.execute("UPDATE players SET isbanned = ? WHERE id = ?", (new_status, player_id))
        conn.commit()
        print(f"Player {player[0]} has been {status_text}.")
    else:
        print("Player not found.")
    conn.close()
    time.sleep(2)


def show_menu():
    print("\n--- Welcome to Quiz Game ---")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

def usermenu(username):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    while True:
        os.system('clear')
        print(f"\nWelcome, {username}!")
        print("--- Main Menu ---")
        print("1. Start New Game")
        print("2. Match History")
        print("3. Continue Pending Game")
        print("4. View My Stats") # Shows Total XP, Wins, Losses, Draws, Win/Loss Ratio
        print("5. Add Question (for admin approval)")
        print("6. Top 10 Players (by XP - All-time Stored)") # Existing global ranking
        print("7. Most Popular Categories")
        print("8. View XP by Period & Rankings") # COMBINED OPTION
        print("0. Logout")

        choice = input("Choose an option: ")

        if choice == "1":
            start_new_game(user[0])
        elif choice == "2":
            AdminWantsYourGames(user[0])
        elif choice == "3":
            conn = sqlite3.connect("dd.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, player1_id, player2_id, start_time FROM games
                WHERE status = 'active' AND (player1_id = ? OR player2_id = ?)
                ORDER BY start_time DESC
            """, (user[0], user[0]))
            active_games = cursor.fetchall()
            conn.close()

            if not active_games:
                print("No active games found.")
                time.sleep(1)
            else:
                print("\n--- Your Active Games ---")
                for game in active_games:
                    opponent_id = game[1] if game[1] != user[0] else game[2]
                    conn = sqlite3.connect("dd.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM players WHERE id = ?", (opponent_id,))
                    opponent_username = cursor.fetchone()[0]
                    conn.close()
                    print(f"  Game ID: {game[0]} | Opponent: {opponent_username} | Started: {game[3]}")

                try:
                    selected_game_id = int(input("Enter the Game ID of the game you want to continue (or 0 to cancel): "))
                    if selected_game_id == 0:
                        print("Game continuation cancelled.")
                        time.sleep(1)
                    else:
                        game_found = False
                        for game in active_games:
                            if game[0] == selected_game_id:
                                game_found = True
                                break
                        
                        if game_found:
                            continue_pending_game(user[0], selected_game_id)
                        else:
                            print("Invalid Game ID selected or game not active for you.")
                            time.sleep(1)

                except ValueError:
                    print("Invalid input. Please enter a number.")
                    time.sleep(1)

        elif choice == "4":
            view_stats(user)
        elif choice == "5":
            addquestion(user[0])
        elif choice == "6":
            top_10_players() # This is for total stored XP ranking
        elif choice == "7":
            popular_categories()
        elif choice == "8": # COMBINED View XP by Period & Rankings
            print("\n--- XP Stats by Period ---")
            print("1. Weekly")
            print("2. Monthly")
            print("3. Total (All time)")
            xp_choice = input("Select a period (1/2/3): ")

            period_type = None
            period_name_display = ""
            if xp_choice == "1":
                period_type = 'weekly'
                period_name_display = "Weekly"
            elif xp_choice == "2":
                period_type = 'monthly'
                period_name_display = "Monthly"
            elif xp_choice == "3":
                period_type = 'total' # For get_xp_for_period
                period_name_display = "Total (All Time)"
            else:
                print("Invalid period selection.")
                time.sleep(1)
                continue

            if period_type:
                # First, show current user's XP for the period
                my_xp = get_xp_for_period(user[0], period_type)
                print(f"\nYour {period_name_display} XP: {my_xp}")

                # Then, offer to show top players for that period
                # Map 'total' from get_xp_for_period to 'total_calculated' for top_players_by_period
                ranking_period_type = period_type
                if period_type == 'total':
                    ranking_period_type = 'total_calculated' 
                    
                view_ranking_choice = input(f"Do you want to see the Top 10 players for {period_name_display} XP? (yes/no): ").lower()
                if view_ranking_choice == 'yes':
                    top_players_by_period(ranking_period_type) # Call the new function
                else:
                    input("\nPress Enter to return...") # Return to menu after user's XP and optional ranking

        elif choice == "0":
            print("Logged out.")
            time.sleep(1)
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

def main():
    user_data = None  
    
    while True:
        os.system('clear')
        show_menu()
        choice = input("Choose an option (1–3): ")

        if choice == "1":
            username_registered = register()
            if username_registered:
                conn = sqlite3.connect("dd.db")
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM players WHERE username = ?", (username_registered,))
                user_data = cursor.fetchone()
                conn.close()
            else:
                user_data = None
        elif choice == "2":
            username_logged_in = login()
            if username_logged_in:
                conn = sqlite3.connect("dd.db")
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM players WHERE username = ?", (username_logged_in,))
                user_data = cursor.fetchone()
                conn.close()
            else:
                user_data = None
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")
            time.sleep(1)
            continue

        if user_data:
            print(f"Hello {user_data[1]}! You're now logged in.")
            if user_data[6]: # Role is at index 6
                adminmenu(user_data[1])
            else:
                usermenu(user_data[1])
        else:
            print("Login or registration failed. Please try again.")
            time.sleep(1)
if __name__ == "__main__":
    main()