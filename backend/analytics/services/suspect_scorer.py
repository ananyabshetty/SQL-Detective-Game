"""
Suspect Intelligence Engine
Computes suspicion scores for suspects based on behavioral signals
"""

import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path


class SuspectScorer:
    """
    Rule-based analytics engine that ranks suspects using a dynamic Suspicion Score.
    All weights are configurable via the analytics_config table.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_config(self) -> Dict[str, float]:
        """Retrieve all configuration values"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT config_key, config_value FROM analytics_config")
            return {row['config_key']: row['config_value'] for row in cursor.fetchall()}
        finally:
            conn.close()
    
    def update_config(self, key: str, value: float) -> bool:
        """Update a configuration value"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "UPDATE analytics_config SET config_value = ?, updated_at = CURRENT_TIMESTAMP WHERE config_key = ?",
                (value, key)
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
    
    def get_suspect_rankings(self) -> List[Dict[str, Any]]:
        """
        Calculate and return suspect rankings with full score breakdown.
        Uses configurable weights from analytics_config table.
        """
        conn = self._get_connection()
        try:
            # Complex CTE query for suspect scoring
            query = """
            WITH config AS (
                SELECT 
                    MAX(CASE WHEN config_key = 'weight_criminal_record' THEN config_value END) AS w_criminal,
                    MAX(CASE WHEN config_key = 'weight_crime_calls' THEN config_value END) AS w_calls,
                    MAX(CASE WHEN config_key = 'weight_high_transactions' THEN config_value END) AS w_trans,
                    MAX(CASE WHEN config_key = 'weight_bank_cctv' THEN config_value END) AS w_cctv,
                    MAX(CASE WHEN config_key = 'weight_call_volume' THEN config_value END) AS w_volume,
                    MAX(CASE WHEN config_key = 'high_transaction_threshold' THEN config_value END) AS trans_threshold,
                    MAX(CASE WHEN config_key = 'crime_window_hours_before' THEN config_value END) AS window_before,
                    MAX(CASE WHEN config_key = 'crime_window_hours_after' THEN config_value END) AS window_after
                FROM analytics_config
            ),
            crime_info AS (
                SELECT 
                    cs.date_time as crime_time,
                    cs.location_id as crime_location
                FROM crime_scenes cs 
                WHERE cs.case_number = 'CS-2024-001' 
                LIMIT 1
            ),
            -- Score for criminal record
            criminal_score AS (
                SELECT 
                    id,
                    CASE WHEN criminal_record = 1 THEN (SELECT w_criminal FROM config) ELSE 0 END AS score
                FROM suspects
            ),
            -- Score for calls during crime window
            call_score AS (
                SELECT 
                    caller_id AS id,
                    COUNT(*) * (SELECT w_calls FROM config) AS score,
                    COUNT(*) AS call_count
                FROM phone_records p, crime_info ci, config
                WHERE p.timestamp BETWEEN 
                    datetime(ci.crime_time, '-' || config.window_before || ' hours') AND
                    datetime(ci.crime_time, '+' || config.window_after || ' hours')
                GROUP BY caller_id
            ),
            -- Score for high-value transactions
            transaction_score AS (
                SELECT 
                    account_id AS id,
                    COUNT(*) * (SELECT w_trans FROM config) AS score,
                    COUNT(*) AS trans_count,
                    SUM(amount) AS total_amount
                FROM bank_transactions, config
                WHERE amount > config.trans_threshold
                GROUP BY account_id
            ),
            -- Score for CCTV at crime location
            cctv_score AS (
                SELECT 
                    c.person_id AS id,
                    COUNT(*) * (SELECT w_cctv FROM config) AS score,
                    COUNT(*) AS sighting_count
                FROM cctv_logs c
                JOIN crime_info ci ON c.location_id = ci.crime_location
                GROUP BY c.person_id
            ),
            -- Total call volume (above average gets points)
            call_volume AS (
                SELECT 
                    caller_id AS id,
                    COUNT(*) AS total_calls,
                    CASE 
                        WHEN COUNT(*) > (SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM phone_records GROUP BY caller_id))
                        THEN (SELECT w_volume FROM config)
                        ELSE 0
                    END AS score
                FROM phone_records
                GROUP BY caller_id
            )
            SELECT 
                s.id,
                s.name,
                s.age,
                s.occupation,
                s.criminal_record,
                COALESCE(cr.score, 0) AS criminal_score,
                COALESCE(ca.score, 0) AS crime_window_call_score,
                COALESCE(ca.call_count, 0) AS crime_window_calls,
                COALESCE(tr.score, 0) AS high_transaction_score,
                COALESCE(tr.trans_count, 0) AS high_transactions,
                COALESCE(tr.total_amount, 0) AS high_transaction_total,
                COALESCE(cc.score, 0) AS cctv_score,
                COALESCE(cc.sighting_count, 0) AS bank_sightings,
                COALESCE(cv.score, 0) AS volume_score,
                COALESCE(cv.total_calls, 0) AS total_calls,
                ROUND(
                    COALESCE(cr.score, 0) + 
                    COALESCE(ca.score, 0) + 
                    COALESCE(tr.score, 0) + 
                    COALESCE(cc.score, 0) + 
                    COALESCE(cv.score, 0),
                    1
                ) AS total_score
            FROM suspects s
            LEFT JOIN criminal_score cr ON s.id = cr.id
            LEFT JOIN call_score ca ON s.id = ca.id
            LEFT JOIN transaction_score tr ON s.id = tr.id
            LEFT JOIN cctv_score cc ON s.id = cc.id
            LEFT JOIN call_volume cv ON s.id = cv.id
            ORDER BY total_score DESC;
            """
            
            cursor = conn.execute(query)
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'age': row['age'],
                    'occupation': row['occupation'],
                    'criminal_record': bool(row['criminal_record']),
                    'scores': {
                        'criminal': row['criminal_score'],
                        'crime_calls': row['crime_window_call_score'],
                        'transactions': row['high_transaction_score'],
                        'cctv': row['cctv_score'],
                        'volume': row['volume_score']
                    },
                    'details': {
                        'crime_window_calls': row['crime_window_calls'],
                        'high_transactions': row['high_transactions'],
                        'high_transaction_total': row['high_transaction_total'],
                        'bank_sightings': row['bank_sightings'],
                        'total_calls': row['total_calls']
                    },
                    'total_score': row['total_score'],
                    'rank': len(results) + 1
                })
            
            return results
        finally:
            conn.close()
    
    def get_suspect_detail(self, suspect_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed analytics for a single suspect"""
        rankings = self.get_suspect_rankings()
        for suspect in rankings:
            if suspect['id'] == suspect_id:
                return suspect
        return None
    
    def get_score_breakdown_chart_data(self) -> Dict[str, Any]:
        """Get data formatted for chart visualization"""
        rankings = self.get_suspect_rankings()
        
        return {
            'labels': [s['name'] for s in rankings],
            'datasets': [
                {
                    'label': 'Criminal Record',
                    'data': [s['scores']['criminal'] for s in rankings],
                    'backgroundColor': 'rgba(255, 99, 132, 0.7)'
                },
                {
                    'label': 'Crime Window Calls',
                    'data': [s['scores']['crime_calls'] for s in rankings],
                    'backgroundColor': 'rgba(54, 162, 235, 0.7)'
                },
                {
                    'label': 'High Transactions',
                    'data': [s['scores']['transactions'] for s in rankings],
                    'backgroundColor': 'rgba(255, 206, 86, 0.7)'
                },
                {
                    'label': 'CCTV at Bank',
                    'data': [s['scores']['cctv'] for s in rankings],
                    'backgroundColor': 'rgba(75, 192, 192, 0.7)'
                },
                {
                    'label': 'Call Volume',
                    'data': [s['scores']['volume'] for s in rankings],
                    'backgroundColor': 'rgba(153, 102, 255, 0.7)'
                }
            ],
            'total_scores': [s['total_score'] for s in rankings]
        }
    
    def get_top_suspects(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get top N suspects by score"""
        rankings = self.get_suspect_rankings()
        return rankings[:limit]
