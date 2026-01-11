CREATE TABLE universities (
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    ranking INTEGER,
    url TEXT,
    match_score FLOAT,
    notes TEXT
);

CREATE TABLE professors (
    id INTEGER PRIMARY KEY,
    uni_id INTEGER,
    name TEXT,
    email TEXT,
    department TEXT,
    research_areas TEXT,
    personal_page TEXT,
    match_score FLOAT,
    FOREIGN KEY (uni_id) REFERENCES universities(id)
);

CREATE TABLE email_history (
    id INTEGER PRIMARY KEY,
    professor_id INTEGER,
    email_draft TEXT,
    status TEXT, -- 'draft', 'sent', 'discarded'
    sent_date TIMESTAMP,
    response_received BOOLEAN,
    notes TEXT,
    FOREIGN KEY (professor_id) REFERENCES professors(id)
);