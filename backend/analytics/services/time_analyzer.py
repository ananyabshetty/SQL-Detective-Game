"""
Time-Based Behavioral Analysis Module
Analyzes how suspect behavior changes over time and identifies abnormal patterns
"""

import sqlite3
from typing import List, Dict, Any
from datetime import datetime


class TimeAnalyzer:
    """
    Analyzes temporal patterns in crime data including:
    - Hourly activity aggregations
    - Before/After crime comparisons
    - Activity spike detection
    - Timeline generation
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_hourly_activity(self, date: str = '2024-03-15') -> Dict[str, Any]:
        """
        Get hourly activity breakdown for a given date.
        Returns phone calls, transactions, and CCTV sightings per hour.
        """
        conn = self._get_connection()
        try:
            query = """
            WITH RECURSIVE hours(n) AS (
                SELECT 0
                UNION ALL
                SELECT n + 1 FROM hours WHERE n < 23
            ),
            hour_range AS (
                SELECT 
                    n AS hour_num,
                    datetime(:date || ' ' || printf('%02d', n) || ':00:00') AS hour_start,
                    datetime(:date || ' ' || printf('%02d', n) || ':59:59') AS hour_end
                FROM hours
            ),
            phone_counts AS (
                SELECT 
                    CAST(strftime('%H', timestamp) AS INTEGER) AS hour_num,
                    COUNT(*) AS count
                FROM phone_records
                WHERE DATE(timestamp) = :date
                GROUP BY hour_num
            ),
            trans_counts AS (
                SELECT 
                    CAST(strftime('%H', timestamp) AS INTEGER) AS hour_num,
                    COUNT(*) AS count,
                    SUM(amount) AS volume
                FROM bank_transactions
                WHERE DATE(timestamp) = :date
                GROUP BY hour_num
            ),
            cctv_counts AS (
                SELECT 
                    CAST(strftime('%H', timestamp) AS INTEGER) AS hour_num,
                    COUNT(*) AS count
                FROM cctv_logs
                WHERE DATE(timestamp) = :date
                GROUP BY hour_num
            )
            SELECT 
                h.hour_num,
                printf('%02d:00', h.hour_num) AS hour_label,
                COALESCE(p.count, 0) AS phone_calls,
                COALESCE(t.count, 0) AS transactions,
                COALESCE(t.volume, 0) AS transaction_volume,
                COALESCE(c.count, 0) AS cctv_sightings
            FROM hour_range h
            LEFT JOIN phone_counts p ON h.hour_num = p.hour_num
            LEFT JOIN trans_counts t ON h.hour_num = t.hour_num
            LEFT JOIN cctv_counts c ON h.hour_num = c.hour_num
            ORDER BY h.hour_num;
            """
            
            cursor = conn.execute(query, {'date': date})
            rows = cursor.fetchall()
            
            return {
                'date': date,
                'labels': [row['hour_label'] for row in rows],
                'phone_calls': [row['phone_calls'] for row in rows],
                'transactions': [row['transactions'] for row in rows],
                'transaction_volume': [row['transaction_volume'] for row in rows],
                'cctv_sightings': [row['cctv_sightings'] for row in rows],
                'total_calls': sum(row['phone_calls'] for row in rows),
                'total_transactions': sum(row['transactions'] for row in rows),
                'total_sightings': sum(row['cctv_sightings'] for row in rows)
            }
        finally:
            conn.close()
    
    def get_suspect_timeline(self, suspect_id: int) -> Dict[str, Any]:
        """
        Get a complete timeline of activities for a specific suspect.
        """
        conn = self._get_connection()
        try:
            # Get suspect info
            cursor = conn.execute(
                "SELECT name, occupation FROM suspects WHERE id = ?",
                (suspect_id,)
            )
            suspect = cursor.fetchone()
            if not suspect:
                return {'error': 'Suspect not found'}
            
            # Get all activities merged into timeline
            query = """
            SELECT * FROM (
                SELECT 
                    'phone_call' AS activity_type,
                    timestamp,
                    'Called ID: ' || receiver_id || ' (' || duration || 's)' AS description
                FROM phone_records
                WHERE caller_id = :suspect_id
                
                UNION ALL
                
                SELECT 
                    'phone_received' AS activity_type,
                    timestamp,
                    'Received from ID: ' || caller_id || ' (' || duration || 's)' AS description
                FROM phone_records
                WHERE receiver_id = :suspect_id
                
                UNION ALL
                
                SELECT 
                    'transaction' AS activity_type,
                    timestamp,
                    transaction_type || ': $' || amount AS description
                FROM bank_transactions
                WHERE account_id = :suspect_id
                
                UNION ALL
                
                SELECT 
                    'cctv' AS activity_type,
                    c.timestamp,
                    'Seen at ' || l.name || ' (' || c.confidence || '% confidence)' AS description
                FROM cctv_logs c
                JOIN locations l ON c.location_id = l.id
                WHERE c.person_id = :suspect_id
            )
            ORDER BY timestamp;
            """
            
            cursor = conn.execute(query, {'suspect_id': suspect_id})
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'type': row['activity_type'],
                    'timestamp': row['timestamp'],
                    'description': row['description']
                })
            
            return {
                'suspect_id': suspect_id,
                'name': suspect['name'],
                'occupation': suspect['occupation'],
                'activities': activities,
                'total_activities': len(activities)
            }
        finally:
            conn.close()
    
    def get_before_after_comparison(self) -> Dict[str, Any]:
        """
        Compare suspect activity before and after the crime.
        Identifies spikes, drops, and new activity patterns.
        """
        conn = self._get_connection()
        try:
            query = """
            WITH crime_time AS (
                SELECT datetime('2024-03-15 23:30:00') AS crime_dt
            ),
            -- Phone activity before crime (24 hours)
            calls_before AS (
                SELECT 
                    caller_id AS suspect_id,
                    COUNT(*) AS count
                FROM phone_records, crime_time
                WHERE timestamp BETWEEN 
                    datetime(crime_time.crime_dt, '-24 hours') AND crime_time.crime_dt
                GROUP BY caller_id
            ),
            -- Phone activity after crime (24 hours)
            calls_after AS (
                SELECT 
                    caller_id AS suspect_id,
                    COUNT(*) AS count
                FROM phone_records, crime_time
                WHERE timestamp BETWEEN 
                    crime_time.crime_dt AND datetime(crime_time.crime_dt, '+24 hours')
                GROUP BY caller_id
            ),
            -- Transactions before
            trans_before AS (
                SELECT 
                    account_id AS suspect_id,
                    COUNT(*) AS count,
                    SUM(amount) AS total
                FROM bank_transactions, crime_time
                WHERE timestamp BETWEEN 
                    datetime(crime_time.crime_dt, '-24 hours') AND crime_time.crime_dt
                GROUP BY account_id
            ),
            -- Transactions after
            trans_after AS (
                SELECT 
                    account_id AS suspect_id,
                    COUNT(*) AS count,
                    SUM(amount) AS total
                FROM bank_transactions, crime_time
                WHERE timestamp BETWEEN 
                    crime_time.crime_dt AND datetime(crime_time.crime_dt, '+24 hours')
                GROUP BY account_id
            )
            SELECT 
                s.id,
                s.name,
                COALESCE(cb.count, 0) AS calls_before,
                COALESCE(ca.count, 0) AS calls_after,
                COALESCE(ca.count, 0) - COALESCE(cb.count, 0) AS call_change,
                COALESCE(tb.count, 0) AS trans_before,
                COALESCE(ta.count, 0) AS trans_after,
                COALESCE(ta.count, 0) - COALESCE(tb.count, 0) AS trans_change,
                CASE 
                    WHEN COALESCE(cb.count, 0) = 0 AND COALESCE(ca.count, 0) > 0 THEN 'NEW_ACTIVITY'
                    WHEN COALESCE(ca.count, 0) > COALESCE(cb.count, 0) * 2 THEN 'SPIKE'
                    WHEN COALESCE(ca.count, 0) < COALESCE(cb.count, 0) * 0.5 THEN 'DROP'
                    ELSE 'NORMAL'
                END AS call_pattern,
                CASE 
                    WHEN COALESCE(tb.count, 0) = 0 AND COALESCE(ta.count, 0) > 0 THEN 'NEW_ACTIVITY'
                    WHEN COALESCE(ta.count, 0) > COALESCE(tb.count, 0) * 2 THEN 'SPIKE'
                    WHEN COALESCE(ta.count, 0) < COALESCE(tb.count, 0) * 0.5 THEN 'DROP'
                    ELSE 'NORMAL'
                END AS trans_pattern
            FROM suspects s
            LEFT JOIN calls_before cb ON s.id = cb.suspect_id
            LEFT JOIN calls_after ca ON s.id = ca.suspect_id
            LEFT JOIN trans_before tb ON s.id = tb.suspect_id
            LEFT JOIN trans_after ta ON s.id = ta.suspect_id
            ORDER BY ABS(COALESCE(ca.count, 0) - COALESCE(cb.count, 0)) DESC;
            """
            
            cursor = conn.execute(query)
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'calls': {
                        'before': row['calls_before'],
                        'after': row['calls_after'],
                        'change': row['call_change'],
                        'pattern': row['call_pattern']
                    },
                    'transactions': {
                        'before': row['trans_before'],
                        'after': row['trans_after'],
                        'change': row['trans_change'],
                        'pattern': row['trans_pattern']
                    }
                })
            
            return {
                'crime_reference': '2024-03-15 23:30:00',
                'window': '24 hours',
                'suspects': results,
                'anomalies': [s for s in results if s['calls']['pattern'] != 'NORMAL' or s['transactions']['pattern'] != 'NORMAL']
            }
        finally:
            conn.close()
    
    def get_activity_heatmap_data(self) -> Dict[str, Any]:
        """
        Get data for activity heatmap visualization.
        Shows activity intensity by suspect and hour.
        """
        conn = self._get_connection()
        try:
            query = """
            SELECT 
                s.id AS suspect_id,
                s.name,
                CAST(strftime('%H', p.timestamp) AS INTEGER) AS hour,
                COUNT(*) AS activity_count
            FROM suspects s
            JOIN phone_records p ON s.id = p.caller_id
            WHERE DATE(p.timestamp) = '2024-03-15'
            GROUP BY s.id, hour
            ORDER BY s.id, hour;
            """
            
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            
            # Build heatmap matrix
            suspects = {}
            for row in rows:
                if row['suspect_id'] not in suspects:
                    suspects[row['suspect_id']] = {
                        'name': row['name'],
                        'hours': [0] * 24
                    }
                suspects[row['suspect_id']]['hours'][row['hour']] = row['activity_count']
            
            return {
                'suspects': list(suspects.values()),
                'hours': [f'{h:02d}:00' for h in range(24)]
            }
        finally:
            conn.close()
