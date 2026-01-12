-- SQL Detective Game - Database Schema
-- A crime investigation database for teaching SQL skills

-- ==============================================================
-- LOCATIONS TABLE
-- Stores all locations in the city where events can occur
-- ==============================================================
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'bank', 'restaurant', 'street', 'residence', etc.
    address VARCHAR(200),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    description TEXT
);

-- ==============================================================
-- SUSPECTS TABLE
-- Contains profiles of all persons of interest
-- ==============================================================
CREATE TABLE IF NOT EXISTS suspects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20),
    occupation VARCHAR(100),
    address VARCHAR(200),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    criminal_record INTEGER DEFAULT 0,  -- 0 = No, 1 = Yes
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================
-- CRIME_SCENES TABLE
-- Details of reported crimes
-- ==============================================================
CREATE TABLE IF NOT EXISTS crime_scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number VARCHAR(20) UNIQUE NOT NULL,
    crime_type VARCHAR(50) NOT NULL,  -- 'robbery', 'assault', 'fraud', etc.
    location_id INTEGER NOT NULL,
    date_time TIMESTAMP NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',  -- 'open', 'investigating', 'closed'
    evidence_collected TEXT,
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- ==============================================================
-- PHONE_RECORDS TABLE
-- Call and SMS logs between persons
-- ==============================================================
CREATE TABLE IF NOT EXISTS phone_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,
    receiver_id INTEGER,
    receiver_number VARCHAR(20),  -- For external numbers
    call_type VARCHAR(10) NOT NULL,  -- 'call', 'sms'
    timestamp TIMESTAMP NOT NULL,
    duration INTEGER,  -- Duration in seconds (NULL for SMS)
    tower_location_id INTEGER,  -- Cell tower location
    FOREIGN KEY (caller_id) REFERENCES suspects(id),
    FOREIGN KEY (receiver_id) REFERENCES suspects(id),
    FOREIGN KEY (tower_location_id) REFERENCES locations(id)
);

-- ==============================================================
-- BANK_TRANSACTIONS TABLE
-- Financial transaction records
-- ==============================================================
CREATE TABLE IF NOT EXISTS bank_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  -- 'withdrawal', 'deposit', 'transfer'
    amount DECIMAL(12, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    location_id INTEGER,  -- ATM/Branch location
    recipient_account VARCHAR(50),  -- For transfers
    description TEXT,
    FOREIGN KEY (account_id) REFERENCES suspects(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- ==============================================================
-- CCTV_LOGS TABLE
-- Surveillance footage records showing person sightings
-- ==============================================================
CREATE TABLE IF NOT EXISTS cctv_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    camera_id VARCHAR(20),
    confidence_score DECIMAL(5, 2),  -- Facial recognition confidence
    image_path VARCHAR(200),
    notes TEXT,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    FOREIGN KEY (person_id) REFERENCES suspects(id)
);

-- ==============================================================
-- CASE_PROGRESS TABLE
-- Tracks player progress through levels
-- ==============================================================
CREATE TABLE IF NOT EXISTS case_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id VARCHAR(50) NOT NULL,  -- Session/Player identifier
    current_level INTEGER DEFAULT 1,
    level_1_completed INTEGER DEFAULT 0,
    level_2_completed INTEGER DEFAULT 0,
    level_3_completed INTEGER DEFAULT 0,
    level_4_completed INTEGER DEFAULT 0,
    level_5_completed INTEGER DEFAULT 0,
    level_6_completed INTEGER DEFAULT 0,
    level_7_completed INTEGER DEFAULT 0,
    total_queries_executed INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================
-- INDEXES for better query performance
-- ==============================================================
CREATE INDEX IF NOT EXISTS idx_phone_records_timestamp ON phone_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_phone_records_caller ON phone_records(caller_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_timestamp ON bank_transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_account ON bank_transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_cctv_logs_timestamp ON cctv_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_cctv_logs_location ON cctv_logs(location_id);
CREATE INDEX IF NOT EXISTS idx_cctv_logs_person ON cctv_logs(person_id);
