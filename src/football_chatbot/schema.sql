CREATE TABLE IF NOT EXISTS matches (
    id           INTEGER PRIMARY KEY,   -- the API's match id
    utc_date     TEXT    NOT NULL,      -- ISO string, sorts correctly as text
    status       TEXT    NOT NULL,      -- SCHEDULED, FINISHED, ...
    competition  TEXT    NOT NULL,      -- PD or CL
    stage        TEXT,                  -- LEAGUE_STAGE, ROUND_OF_16, ...
    matchday     INTEGER,
    home_team    TEXT,                  -- NULL for knockout slots not decided yet
    away_team    TEXT,
    home_goals   INTEGER,               -- NULL until the match is played
    away_goals   INTEGER,
    last_updated TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS articles (
    id           INTEGER PRIMARY KEY,
    url          TEXT NOT NULL UNIQUE,   -- dedupe key
    source       TEXT NOT NULL,
    title        TEXT NOT NULL,
    published_at TEXT NOT NULL,
    body         TEXT NOT NULL,
    fetched_at   TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    title, body, content='articles', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;