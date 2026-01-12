-- ============================================
-- SQL Detective Analytics System
-- Schema for Player Tracking and Analytics
-- ============================================

-- Analytics Configuration Table
-- Stores configurable weights for suspect scoring
CREATE TABLE IF NOT EXISTS analytics_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value REAL NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query Attempts Log
-- Records every SQL query attempt by players
CREATE TABLE IF NOT EXISTS query_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    level_id INTEGER NOT NULL,
    query_text TEXT NOT NULL,
    is_valid BOOLEAN NOT NULL DEFAULT 0,
    is_correct BOOLEAN DEFAULT NULL,
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session Logs
-- Tracks player session information
CREATE TABLE IF NOT EXISTS session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,
    levels_completed INTEGER DEFAULT 0,
    total_queries INTEGER DEFAULT 0,
    user_agent TEXT
);

-- Level Completions
-- Records successful level completions
CREATE TABLE IF NOT EXISTS level_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    level_id INTEGER NOT NULL,
    attempts_count INTEGER NOT NULL DEFAULT 1,
    time_spent_seconds INTEGER,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Error Logs
-- Categorizes SQL errors for analysis
CREATE TABLE IF NOT EXISTS error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100),
    level_id INTEGER,
    error_type VARCHAR(50) NOT NULL,
    error_detail TEXT,
    query_fragment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_query_attempts_session ON query_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_query_attempts_level ON query_attempts(level_id);
CREATE INDEX IF NOT EXISTS idx_query_attempts_created ON query_attempts(created_at);
CREATE INDEX IF NOT EXISTS idx_level_completions_session ON level_completions(session_id);
CREATE INDEX IF NOT EXISTS idx_level_completions_level ON level_completions(level_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_type ON error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_session_logs_session ON session_logs(session_id);
