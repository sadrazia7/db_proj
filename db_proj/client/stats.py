import sqlite3
import time
from datetime import datetime, timedelta

def view_my_ranking(user_id):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, xp FROM players ORDER BY xp DESC")
    players = cursor.fetchall()
    rank = 1
    for pid, name, xp in players:
        if pid == user_id:
            print(f"\nYour Rank: {rank}")
            print(f"Name: {name}")
            print(f"XP: {xp}")
            break
        rank += 1
    print()
    conn.close()
    input("\nPress Enter to return...")

def view_stats(user):
    print("\nYour Stats:")
    print(f"Username: {user[1]}")
    print(f"Email: {user[3]}")
    print(f"XP: {user[4]}") # This is total XP from players table
    print(f"Role: {'Admin' if user[6] else 'User'}")

    con = sqlite3.connect("dd.db")
    cursor = con.cursor()

    # Fetch total games, wins, losses, and draws from player_stats
    cursor.execute("SELECT total_games, total_wins, total_loses, total_draws FROM player_stats WHERE user_id = ?", (user[0],))
    stats = cursor.fetchone()

    if stats:
        total_games, total_wins, total_loses, total_draws = stats

        win_loss_ratio_str = "N/A"
        if total_loses == 0:
            if total_wins > 0:
                win_loss_ratio_str = "N/A (No losses yet)"
            else:
                win_loss_ratio_str = "N/A (No games played yet)"
        else:
            win_loss_ratio_str = f"{total_wins / total_loses:.2f}"

        print(f"Total games: {total_games}")
        print(f"Wins: {total_wins} | Losses: {total_loses} | Draws: {total_draws}")
        print(f"Win/Loss Ratio: {win_loss_ratio_str}")
    else:
        print("No stats found for this user.")

    cursor.close()
    con.close()

    input("\nPress Enter to return...")

def top_10_players():
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, xp , role FROM players ORDER BY xp DESC LIMIT 10")
    rows = cursor.fetchall()
    print("\n--- Top 10 Players (All-time Stored XP) ---") # Clarified title
    changiz=0
    if not rows:
        print("No players found.")
    else:
        for i, row in enumerate(rows, 1):
            if row[2]==0: # Check if role is 0 (normal user)
                print(f"{i-changiz}. {row[0]} - {row[1]} XP")
            else:
                changiz+=1 # Adjust ranking for admin roles
    conn.close()
    input("\nPress Enter to return...")

# Function to get XP for a specific period for a single user
def get_xp_for_period(user_id, period_type):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    if period_type == 'total':
        # For 'total' XP, directly fetch from player_stats as it's the authoritative source for overall XP
        cursor.execute("SELECT xp FROM player_stats WHERE user_id = ?", (user_id,))
        xp_result = cursor.fetchone()
        conn.close()
        return xp_result[0] if xp_result else 0

    end_timestamp = datetime.now()
    start_timestamp = None

    if period_type == 'weekly':
        start_timestamp = end_timestamp - timedelta(days=end_timestamp.weekday())
        start_timestamp = start_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period_type == 'monthly':
        start_timestamp = end_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        print("Invalid period type.")
        conn.close()
        return None

    start_time_str = start_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        SELECT
            SUM(
                CASE
                    WHEN g.winner_id = ? THEN 10
                    WHEN g.winner_id = -1 AND (g.player1_id = ? OR g.player2_id = ?) THEN 5
                    ELSE 0
                END
            ) AS period_xp
        FROM games g
        WHERE (g.player1_id = ? OR g.player2_id = ?)
          AND g.status = 'finished'
          AND g.end_time >= ?
          AND g.end_time <= ?;
    """, (user_id, user_id, user_id, user_id, user_id, start_time_str, end_time_str))

    xp_result = cursor.fetchone()[0]
    conn.close()

    return xp_result if xp_result is not None else 0

# New function to get top players for a specific period
def top_players_by_period(period_type):
    conn = sqlite3.connect("dd.db")
    cursor = conn.cursor()

    end_timestamp = datetime.now()
    start_timestamp = None
    period_name = ""

    if period_type == 'weekly':
        start_timestamp = end_timestamp - timedelta(days=end_timestamp.weekday())
        start_timestamp = start_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "Weekly"
    elif period_type == 'monthly':
        start_timestamp = end_timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_name = "Monthly"
    elif period_type == 'total_calculated': # Use this for calculating total from all games
        start_timestamp = datetime(2000, 1, 1) # Arbitrarily old date to cover all games
        period_name = "Total (All Time - Calculated)"
    else:
        print("Invalid period type.")
        conn.close()
        return

    start_time_str = start_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # SQL query to calculate XP for each player within the period and order them
    cursor.execute(f"""
        SELECT
            p.username,
            SUM(
                CASE
                    WHEN g.winner_id = p.id THEN 10
                    WHEN g.winner_id = -1 AND (g.player1_id = p.id OR g.player2_id = p.id) THEN 5
                    ELSE 0
                END
            ) AS period_xp
        FROM players p
        JOIN games g ON (p.id = g.player1_id OR p.id = g.player2_id)
        WHERE g.status = 'finished'
          AND g.end_time >= ?
          AND g.end_time <= ?
        GROUP BY p.id, p.username
        ORDER BY period_xp DESC
        LIMIT 10;
    """, (start_time_str, end_time_str))

    rows = cursor.fetchall()

    print(f"\n--- Top 10 Players by {period_name} XP ---")
    if not rows:
        print(f"No games finished in the {period_name.lower()} period.")
    else:
        for i, row in enumerate(rows, 1):
            print(f"{i}. {row[0]} - {row[1]} XP")
    conn.close()
    input("\nPress Enter to return...")