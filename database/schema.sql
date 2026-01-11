-- SQLite Schema for PhD Finder

-- Universities table
CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    ranking_qs INTEGER,
    ranking_the INTEGER,
    ranking_arwu INTEGER,
    website_url TEXT,
    department_url TEXT,
    research_areas TEXT, -- JSON list
    match_score INTEGER,
    match_reasoning TEXT,
    confidence_score REAL,
    data_completeness REAL,
    verification_status TEXT DEFAULT 'needs_check',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Professors table
CREATE TABLE IF NOT EXISTS professors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER,
    name TEXT NOT NULL,
    email TEXT,
    title TEXT,
    department TEXT,
    research_areas TEXT, -- JSON list
    personal_page TEXT,
    google_scholar TEXT,
    lab_website TEXT,
    profile_summary TEXT,
    match_score INTEGER,
    match_reasoning TEXT,
    confidence_score REAL,
    contact_priority INTEGER,
    accepting_students TEXT, -- 'yes', 'no', 'unknown'
    data_completeness REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities (id)
);

-- Sources table (Tracking every piece of data)
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL, -- 'university' or 'professor'
    entity_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT, -- 'official', 'ranking', 'scholar', etc.
    extracted_value TEXT,
    context_snippet TEXT,
    reliability_score REAL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emails table
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor_id INTEGER,
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'draft', -- 'draft', 'sent', 'replied', 'discarded'
    quality_score INTEGER,
    personalization_score INTEGER,
    generation_reasoning TEXT,
    sent_at TIMESTAMP,
    response_received_at TIMESTAMP,
    FOREIGN KEY (professor_id) REFERENCES professors (id)
);

-- Agent Decisions (Audit trail)
CREATE TABLE IF NOT EXISTS agent_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    task TEXT NOT NULL,
    decision TEXT NOT NULL,
    reasoning TEXT,
    confidence REAL,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scrape Cache (Avoid redundant scraping)
CREATE TABLE IF NOT EXISTS scrape_cache (
    url TEXT PRIMARY KEY,
    content TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Preferences (Learning Agent)
CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT -- JSON or simple string
);