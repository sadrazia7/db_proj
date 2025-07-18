CREATE TABLE IF NOT EXISTS players (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL,
    email    TEXT    NOT NULL,
    xp       INTEGER DEFAULT 0,
    isbanned INTEGER DEFAULT 0, --boolean 0 for free users and 1 for banned users
    role     INTEGER DEFAULT 0 -- boolean 0 for normal users or 1 for admins
);


CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option CHAR(1) NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    category_id INTEGER REFERENCES categories(id),
    difficulty INTEGER CHECK (difficulty >= 1 AND difficulty <= 5),
    author_id INTEGER REFERENCES players(id),
    approved INTEGER DEFAULT 0 -- boolean: 0 = false, 1 = true
);


CREATE TABLE IF NOT EXISTS MATCHMAKING (
    id INTEGER PRIMARY KEY REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player1_id INTEGER REFERENCES players(id),
    player2_id INTEGER REFERENCES players(id),
    winner_id INTEGER REFERENCES players(id),
    loser_id  INTEGER REFERENCES players(id),
    status TEXT DEFAULT 'active',
    start_time TEXT DEFAULT CURRENT_TIMESTAMP,
    end_time TEXT
);


CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER REFERENCES games(id),
    round_number INTEGER NOT NULL,
    question_id INTEGER REFERENCES questions(id),
    player1_answer CHAR(1), -- NULL until answered
    player2_answer CHAR(1)  -- NULL until answered
);

CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES players(id) ON DELETE CASCADE,
    total_games INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_loses INTEGER DEFAULT 0,
    total_draws INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0
);

-- Trigger to update player_stats and player XP when a game finishes
CREATE TRIGGER IF NOT EXISTS after_game_finished
AFTER UPDATE OF status ON games
WHEN NEW.status = 'finished'
BEGIN
    -- Update stats for winner (if not a draw)
    -- If winner_id is not -1, it means a player won.
    UPDATE player_stats
    SET
        total_games = total_games + 1,
        total_wins = total_wins + 1,
        xp = xp + 10 -- XP for winning
    WHERE user_id = NEW.winner_id AND NEW.winner_id != -1;

    UPDATE players
    SET xp = xp + 10
    WHERE id = NEW.winner_id AND NEW.winner_id != -1;

    -- Update stats for loser (if not a draw)
    -- If loser_id is not -1, it means a player lost.
    UPDATE player_stats
    SET
        total_games = total_games + 1,
        total_loses = total_loses + 1
    WHERE user_id = NEW.loser_id AND NEW.loser_id != -1;

    -- Update stats for draws
    -- This applies to Player1 if winner_id is -1 (indicating a draw)
    UPDATE player_stats
    SET
        total_games = total_games + 1,
        total_draws = total_draws + 1,
        xp = xp + 5
    WHERE user_id = NEW.player1_id AND NEW.winner_id = -1;

    UPDATE players
    SET xp = xp + 5
    WHERE id = NEW.player1_id AND NEW.winner_id = -1;

    -- This applies to Player2 if winner_id is -1 (indicating a draw)
    UPDATE player_stats
    SET
        total_games = total_games + 1,
        total_draws = total_draws + 1,
        xp = xp + 5
    WHERE user_id = NEW.player2_id AND NEW.winner_id = -1;

    UPDATE players
    SET xp = xp + 5
    WHERE id = NEW.player2_id AND NEW.winner_id = -1;
END;