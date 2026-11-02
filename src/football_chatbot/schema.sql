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