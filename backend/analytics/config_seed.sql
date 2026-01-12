-- ============================================
-- SQL Detective Analytics System
-- Default Configuration Values
-- ============================================

-- Suspect Scoring Weights
INSERT OR REPLACE INTO analytics_config (config_key, config_value, description) VALUES
('weight_criminal_record', 25.0, 'Points added for having criminal record'),
('weight_crime_calls', 15.0, 'Points per call made during crime window'),
('weight_high_transactions', 10.0, 'Points for transactions above threshold'),
('weight_bank_cctv', 20.0, 'Points for CCTV sighting at crime location'),
('weight_call_volume', 5.0, 'Points for above-average call volume'),
('weight_recent_activity', 10.0, 'Points for activity within 24h of crime');

-- Thresholds
INSERT OR REPLACE INTO analytics_config (config_key, config_value, description) VALUES
('high_transaction_threshold', 5000.0, 'Dollar amount to flag as high transaction'),
('crime_window_hours_before', 2.0, 'Hours before crime to consider as window'),
('crime_window_hours_after', 2.0, 'Hours after crime to consider as window');

-- Crime Reference Data
INSERT OR REPLACE INTO analytics_config (config_key, config_value, description) VALUES
('primary_case_number', 1.0, 'Reference to main crime case (CS-2024-001)'),
('crime_location_id', 1.0, 'Location ID of Downtown Bank');
