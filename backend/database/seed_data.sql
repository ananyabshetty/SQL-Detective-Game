-- SQL Detective Game - Seed Data
-- Realistic crime investigation data for gameplay

-- ==============================================================
-- LOCATIONS - City locations where events occur
-- ==============================================================
INSERT INTO locations (name, type, address, latitude, longitude, description) VALUES
('Downtown Bank', 'bank', '123 Main Street', 40.7128, -74.0060, 'Central city bank, main branch'),
('Midnight Diner', 'restaurant', '456 Oak Avenue', 40.7135, -74.0055, '24-hour diner near downtown'),
('Central Park South', 'park', 'Central Park', 40.7650, -73.9760, 'Southern entrance of Central Park'),
('Harbor District', 'industrial', '789 Harbor Road', 40.6892, -74.0445, 'Industrial shipping area'),
('Riverside Apartments', 'residence', '321 River Drive', 40.7200, -74.0100, 'Upscale apartment complex'),
('Metro Station Central', 'transit', '100 Metro Plaza', 40.7150, -74.0080, 'Main subway station'),
('Eastside Mall', 'commercial', '555 East Boulevard', 40.7180, -73.9900, 'Large shopping center'),
('City Hospital', 'hospital', '888 Health Way', 40.7220, -74.0020, 'Main city hospital'),
('Police Precinct 12', 'government', '12 Justice Lane', 40.7140, -74.0070, 'Local police station'),
('The Golden Lounge', 'nightclub', '777 Party Street', 40.7160, -74.0040, 'Popular nightclub downtown');

-- ==============================================================
-- SUSPECTS - Persons of interest in the investigation
-- ==============================================================
INSERT INTO suspects (name, age, gender, occupation, address, phone_number, email, criminal_record, notes) VALUES
('Marcus Chen', 35, 'Male', 'Investment Banker', '45 Wall Street Apt 12B', '555-0101', 'mchen@email.com', 0, 'Works at Downtown Bank. Clean record.'),
('Elena Rodriguez', 28, 'Female', 'Software Developer', '321 River Drive #5A', '555-0102', 'erodriguez@email.com', 0, 'Lives near crime scene. Night owl.'),
('Viktor Petrov', 42, 'Male', 'Import/Export Business', '789 Harbor Road Unit 3', '555-0103', 'vpetrov@email.com', 1, 'Prior conviction for fraud. Known associate of criminal elements.'),
('Sarah Mitchell', 31, 'Female', 'Bank Manager', '123 Main Street', '555-0104', 'smitchell@bank.com', 0, 'Manager at Downtown Bank. Access to vault.'),
('James Wilson', 45, 'Male', 'Security Guard', '100 Metro Plaza Apt 2C', '555-0105', 'jwilson@email.com', 1, 'Previous theft charge. Works night shift at bank.'),
('Mei Lin', 29, 'Female', 'Accountant', '555 East Boulevard #8D', '555-0106', 'mlin@email.com', 0, 'Works at accounting firm. Handles large transactions.'),
('Carlos Reyes', 38, 'Male', 'Taxi Driver', '456 Oak Avenue Apt 3B', '555-0107', 'creyes@email.com', 0, 'Works night shift. Knows city well.'),
('Diana Foster', 33, 'Female', 'Lawyer', '321 River Drive #12A', '555-0108', 'dfoster@law.com', 0, 'Criminal defense attorney. Represents Viktor Petrov.'),
('Robert Blake', 50, 'Male', 'Retired Detective', '888 Health Way #1A', '555-0109', 'rblake@email.com', 0, 'Former police. Consulting on cold cases.'),
('Natasha Ivanova', 27, 'Female', 'Bartender', '777 Party Street', '555-0110', 'nivanova@email.com', 1, 'Works at Golden Lounge. Minor drug charges.');

-- ==============================================================
-- CRIME_SCENES - The main robbery case
-- ==============================================================
INSERT INTO crime_scenes (case_number, crime_type, location_id, date_time, description, status, evidence_collected) VALUES
('CASE-2024-0315', 'robbery', 1, '2024-03-15 23:45:00', 'Armed robbery at Downtown Bank. $2.5 million stolen from vault. Security disabled.', 'investigating', 'Fingerprints on vault, disabled camera footage, broken security panel'),
('CASE-2024-0310', 'fraud', 7, '2024-03-10 14:30:00', 'Credit card fraud reported at Eastside Mall. Multiple victims.', 'open', 'Transaction records, witness statements'),
('CASE-2024-0301', 'assault', 10, '2024-03-01 02:15:00', 'Assault reported outside Golden Lounge. Victim hospitalized.', 'closed', 'CCTV footage, witness statements');

-- ==============================================================
-- PHONE_RECORDS - Calls made around the crime date (March 15, 2024)
-- ==============================================================
-- Normal daytime calls
INSERT INTO phone_records (caller_id, receiver_id, receiver_number, call_type, timestamp, duration, tower_location_id) VALUES
(1, 4, NULL, 'call', '2024-03-15 09:15:00', 180, 1),
(4, 1, NULL, 'call', '2024-03-15 10:30:00', 240, 1),
(2, 6, NULL, 'call', '2024-03-15 11:00:00', 120, 5),
(3, 8, NULL, 'call', '2024-03-15 12:00:00', 600, 4),
(5, NULL, '555-9999', 'call', '2024-03-15 14:00:00', 90, 6);

-- Suspicious night calls (crime window: 11 PM - 2 AM)
INSERT INTO phone_records (caller_id, receiver_id, receiver_number, call_type, timestamp, duration, tower_location_id) VALUES
(3, 5, NULL, 'call', '2024-03-15 22:45:00', 45, 4),
(5, 3, NULL, 'call', '2024-03-15 23:00:00', 30, 1),
(3, NULL, '555-8888', 'call', '2024-03-15 23:15:00', 60, 1),
(5, 3, NULL, 'sms', '2024-03-15 23:30:00', NULL, 1),
(3, 5, NULL, 'call', '2024-03-15 23:45:00', 120, 1),
(10, 3, NULL, 'call', '2024-03-16 00:15:00', 180, 10),
(3, 10, NULL, 'call', '2024-03-16 00:45:00', 90, 4),
(5, NULL, '555-7777', 'call', '2024-03-16 01:00:00', 45, 6),
(3, 8, NULL, 'call', '2024-03-16 01:30:00', 300, 4),
(7, 3, NULL, 'call', '2024-03-16 01:45:00', 60, 4);

-- More calls from Viktor (suspect 3) - showing pattern
INSERT INTO phone_records (caller_id, receiver_id, receiver_number, call_type, timestamp, duration, tower_location_id) VALUES
(3, 5, NULL, 'sms', '2024-03-15 20:00:00', NULL, 4),
(3, 10, NULL, 'call', '2024-03-15 20:30:00', 120, 4),
(3, NULL, '555-6666', 'call', '2024-03-15 21:00:00', 180, 4),
(3, 5, NULL, 'call', '2024-03-15 21:30:00', 90, 4),
(3, 8, NULL, 'sms', '2024-03-15 22:00:00', NULL, 4),
(3, NULL, '555-5555', 'call', '2024-03-15 22:15:00', 60, 4);

-- Normal calls from others
INSERT INTO phone_records (caller_id, receiver_id, receiver_number, call_type, timestamp, duration, tower_location_id) VALUES
(1, 2, NULL, 'call', '2024-03-15 19:00:00', 300, 5),
(6, 2, NULL, 'call', '2024-03-15 18:00:00', 180, 7),
(9, 4, NULL, 'call', '2024-03-15 16:00:00', 420, 8),
(8, 3, NULL, 'call', '2024-03-15 15:00:00', 600, 5);

-- ==============================================================
-- BANK_TRANSACTIONS - Financial activity around crime date
-- ==============================================================
-- Normal transactions
INSERT INTO bank_transactions (account_id, transaction_type, amount, timestamp, location_id, recipient_account, description) VALUES
(1, 'deposit', 5000.00, '2024-03-14 10:00:00', 1, NULL, 'Salary deposit'),
(2, 'withdrawal', 200.00, '2024-03-14 14:30:00', 1, NULL, 'ATM withdrawal'),
(4, 'transfer', 1500.00, '2024-03-14 16:00:00', 1, 'SAVINGS-001', 'Savings transfer'),
(6, 'deposit', 3000.00, '2024-03-14 11:00:00', 7, NULL, 'Client payment');

-- Suspicious transactions (large amounts, unusual timing)
INSERT INTO bank_transactions (account_id, transaction_type, amount, timestamp, location_id, recipient_account, description) VALUES
(3, 'withdrawal', 15000.00, '2024-03-15 18:00:00', 1, NULL, 'Large cash withdrawal'),
(3, 'transfer', 50000.00, '2024-03-16 06:00:00', NULL, 'OFFSHORE-XXX', 'International transfer'),
(5, 'deposit', 8000.00, '2024-03-16 08:00:00', 1, NULL, 'Cash deposit - source unknown'),
(10, 'withdrawal', 5000.00, '2024-03-16 09:00:00', 7, NULL, 'Cash withdrawal');

-- More transactions for average calculation
INSERT INTO bank_transactions (account_id, transaction_type, amount, timestamp, location_id, recipient_account, description) VALUES
(1, 'withdrawal', 100.00, '2024-03-10 10:00:00', 1, NULL, 'ATM'),
(2, 'deposit', 2500.00, '2024-03-11 09:00:00', 1, NULL, 'Paycheck'),
(4, 'withdrawal', 500.00, '2024-03-12 12:00:00', 1, NULL, 'ATM'),
(6, 'transfer', 800.00, '2024-03-13 14:00:00', 7, 'RENT-001', 'Rent payment'),
(7, 'deposit', 1200.00, '2024-03-13 16:00:00', 6, NULL, 'Tips deposit'),
(8, 'withdrawal', 300.00, '2024-03-14 18:00:00', 5, NULL, 'ATM'),
(9, 'deposit', 4500.00, '2024-03-10 11:00:00', 8, NULL, 'Pension'),
(1, 'transfer', 2000.00, '2024-03-15 09:00:00', 1, 'INV-001', 'Investment'),
(3, 'deposit', 25000.00, '2024-03-12 10:00:00', 4, NULL, 'Business income - cash'),
(3, 'withdrawal', 10000.00, '2024-03-13 15:00:00', 1, NULL, 'Large withdrawal');

-- ==============================================================
-- CCTV_LOGS - Surveillance sightings around crime scene
-- ==============================================================
-- Downtown Bank area sightings on crime night
INSERT INTO cctv_logs (location_id, person_id, timestamp, camera_id, confidence_score, notes) VALUES
(1, 5, '2024-03-15 22:30:00', 'CAM-BANK-01', 95.5, 'James Wilson entering bank - employee'),
(1, 4, '2024-03-15 22:45:00', 'CAM-BANK-01', 98.2, 'Sarah Mitchell leaving bank'),
(1, 3, '2024-03-15 23:30:00', 'CAM-BANK-02', 87.3, 'Viktor Petrov near bank entrance'),
(1, 5, '2024-03-15 23:40:00', 'CAM-BANK-01', 96.8, 'James Wilson at side door'),
(1, 3, '2024-03-16 00:15:00', 'CAM-BANK-03', 82.1, 'Viktor Petrov leaving area');

-- Other location sightings
INSERT INTO cctv_logs (location_id, person_id, timestamp, camera_id, confidence_score, notes) VALUES
(4, 3, '2024-03-15 18:00:00', 'CAM-HARBOR-01', 94.5, 'Viktor at Harbor District office'),
(4, 3, '2024-03-15 21:00:00', 'CAM-HARBOR-02', 91.2, 'Viktor leaving Harbor District'),
(6, 3, '2024-03-15 21:30:00', 'CAM-METRO-01', 88.7, 'Viktor at Metro Station'),
(6, 5, '2024-03-15 21:45:00', 'CAM-METRO-02', 93.1, 'James at Metro Station'),
(2, 7, '2024-03-15 22:00:00', 'CAM-DINER-01', 97.8, 'Carlos at Midnight Diner'),
(10, 10, '2024-03-15 22:30:00', 'CAM-LOUNGE-01', 99.1, 'Natasha working at lounge'),
(10, 3, '2024-03-15 20:00:00', 'CAM-LOUNGE-02', 85.4, 'Viktor at Golden Lounge'),
(4, 3, '2024-03-16 02:30:00', 'CAM-HARBOR-01', 79.3, 'Viktor returning to Harbor');

-- Movement trail for Level 6 (CTE level)
INSERT INTO cctv_logs (location_id, person_id, timestamp, camera_id, confidence_score, notes) VALUES
(5, 3, '2024-03-15 08:00:00', 'CAM-APT-01', 96.0, 'Morning departure'),
(7, 3, '2024-03-15 09:30:00', 'CAM-MALL-01', 92.3, 'Shopping at mall'),
(2, 3, '2024-03-15 12:00:00', 'CAM-DINER-01', 94.7, 'Lunch at diner'),
(4, 3, '2024-03-15 14:00:00', 'CAM-HARBOR-01', 95.1, 'Arrived at office'),
(8, 3, '2024-03-16 04:00:00', 'CAM-HOSP-01', 71.2, 'Near hospital - unclear purpose');

-- ==============================================================
-- Initial player progress (empty for new players)
-- ==============================================================
INSERT INTO case_progress (player_id, current_level) VALUES
('demo_player', 1);
