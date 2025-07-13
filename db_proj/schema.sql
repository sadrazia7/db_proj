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
    name TEXT NOT NULL UNIQUE
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
    player1_answer CHAR(1),
    player2_answer CHAR(1)
);

CREATE TABLE IF NOT EXISTS player_stats (
    user_id INTEGER PRIMARY KEY REFERENCES players(id),
    total_games INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_loses INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0
);
