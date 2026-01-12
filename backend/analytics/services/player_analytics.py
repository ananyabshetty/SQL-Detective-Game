"""
Player Behavior Analytics Module
Analyzes player interactions with the SQL Detective Game
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class PlayerAnalytics:
    """
    Tracks and analyzes player behavior including:
    - Query attempts and success rates
    - Level completion funnel
    - Error frequency analysis
    - Learning curve metrics
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==========================================
    # Logging Methods (called during gameplay)
    # ==========================================
    
    def log_session_start(self, session_id: str, user_agent: str = None) -> bool:
        """Log a new player session"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO session_logs (session_id, user_agent)
                VALUES (?, ?)
            """, (session_id, user_agent))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error logging session: {e}")
            return False
        finally:
            conn.close()
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update last active timestamp for session"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                UPDATE session_logs 
                SET last_active_at = CURRENT_TIMESTAMP,
                    total_queries = total_queries + 1
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
    
    def log_query_attempt(self, session_id: str, level_id: int, query_text: str,
                          is_valid: bool, is_correct: bool = None,
                          execution_time_ms: int = None, error_message: str = None) -> bool:
        """Log a query attempt"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO query_attempts 
                (session_id, level_id, query_text, is_valid, is_correct, execution_time_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, level_id, query_text, is_valid, is_correct, execution_time_ms, error_message))
            conn.commit()
            
            # Update session activity
            self.update_session_activity(session_id)
            return True
        except Exception as e:
            print(f"Error logging query attempt: {e}")
            return False
        finally:
            conn.close()
    
    def log_level_completion(self, session_id: str, level_id: int, 
                             attempts_count: int, time_spent_seconds: int = None) -> bool:
        """Log a successful level completion"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO level_completions 
                (session_id, level_id, attempts_count, time_spent_seconds)
                VALUES (?, ?, ?, ?)
            """, (session_id, level_id, attempts_count, time_spent_seconds))
            
            # Update session levels completed
            conn.execute("""
                UPDATE session_logs 
                SET levels_completed = levels_completed + 1
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error logging level completion: {e}")
            return False
        finally:
            conn.close()
    
    def log_error(self, session_id: str, level_id: int, error_type: str,
                  error_detail: str = None, query_fragment: str = None) -> bool:
        """Log a categorized error"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO error_logs 
                (session_id, level_id, error_type, error_detail, query_fragment)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, level_id, error_type, error_detail, query_fragment))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()
    
    # ==========================================
    # Analytics Methods (for dashboard)
    # ==========================================
    
    def get_funnel_analysis(self) -> Dict[str, Any]:
        """
        Analyze player progression through levels.
        Shows drop-off at each level.
        """
        conn = self._get_connection()
        try:
            query = """
            WITH level_starts AS (
                SELECT level_id, COUNT(DISTINCT session_id) AS sessions_started
                FROM query_attempts
                GROUP BY level_id
            ),
            level_completions_agg AS (
                SELECT level_id, COUNT(DISTINCT session_id) AS sessions_completed
                FROM level_completions
                GROUP BY level_id
            )
            SELECT 
                ls.level_id,
                ls.sessions_started,
                COALESCE(lc.sessions_completed, 0) AS sessions_completed,
                ROUND(COALESCE(lc.sessions_completed, 0) * 100.0 / 
                    NULLIF(ls.sessions_started, 0), 1) AS completion_rate,
                LAG(ls.sessions_started) OVER (ORDER BY ls.level_id) AS prev_level_starts,
                CASE 
                    WHEN LAG(ls.sessions_started) OVER (ORDER BY ls.level_id) IS NULL THEN 0
                    ELSE ROUND(
                        (LAG(ls.sessions_started) OVER (ORDER BY ls.level_id) - ls.sessions_started) * 100.0 
                        / NULLIF(LAG(ls.sessions_started) OVER (ORDER BY ls.level_id), 0), 1
                    )
                END AS dropoff_rate
            FROM level_starts ls
            LEFT JOIN level_completions_agg lc ON ls.level_id = lc.level_id
            ORDER BY ls.level_id;
            """
            
            cursor = conn.execute(query)
            levels = []
            for row in cursor.fetchall():
                levels.append({
                    'level_id': row['level_id'],
                    'started': row['sessions_started'],
                    'completed': row['sessions_completed'],
                    'completion_rate': row['completion_rate'] or 0,
                    'dropoff_rate': row['dropoff_rate'] or 0
                })
            
            return {
                'levels': levels,
                'total_sessions': levels[0]['started'] if levels else 0,
                'fully_completed': levels[-1]['completed'] if levels else 0
            }
        finally:
            conn.close()
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """
        Analyze common SQL errors made by players.
        """
        conn = self._get_connection()
        try:
            # Error frequency
            cursor = conn.execute("""
                SELECT 
                    error_type,
                    COUNT(*) AS occurrence_count,
                    COUNT(DISTINCT session_id) AS affected_sessions
                FROM error_logs
                GROUP BY error_type
                ORDER BY occurrence_count DESC
                LIMIT 10;
            """)
            
            errors = []
            total_errors = 0
            for row in cursor.fetchall():
                errors.append({
                    'type': row['error_type'],
                    'count': row['occurrence_count'],
                    'sessions': row['affected_sessions']
                })
                total_errors += row['occurrence_count']
            
            # Add percentages
            for error in errors:
                error['percentage'] = round(error['count'] * 100 / total_errors, 1) if total_errors > 0 else 0
            
            # Errors by level
            cursor = conn.execute("""
                SELECT 
                    level_id,
                    COUNT(*) AS error_count
                FROM error_logs
                GROUP BY level_id
                ORDER BY level_id;
            """)
            
            by_level = [{
                'level_id': row['level_id'],
                'error_count': row['error_count']
            } for row in cursor.fetchall()]
            
            return {
                'top_errors': errors,
                'total_errors': total_errors,
                'by_level': by_level
            }
        finally:
            conn.close()
    
    def get_learning_curve(self) -> Dict[str, Any]:
        """
        Analyze learning curve - attempts and time per level.
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT 
                    level_id,
                    ROUND(AVG(attempts_count), 1) AS avg_attempts,
                    MIN(attempts_count) AS min_attempts,
                    MAX(attempts_count) AS max_attempts,
                    ROUND(AVG(time_spent_seconds), 0) AS avg_time_seconds,
                    COUNT(*) AS completions
                FROM level_completions
                GROUP BY level_id
                ORDER BY level_id;
            """)
            
            levels = []
            for row in cursor.fetchall():
                levels.append({
                    'level_id': row['level_id'],
                    'avg_attempts': row['avg_attempts'],
                    'min_attempts': row['min_attempts'],
                    'max_attempts': row['max_attempts'],
                    'avg_time_seconds': row['avg_time_seconds'],
                    'completions': row['completions']
                })
            
            return {
                'levels': levels,
                'difficulty_ranking': sorted(levels, key=lambda x: x['avg_attempts'], reverse=True)
            }
        finally:
            conn.close()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of all player sessions.
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) AS total_sessions,
                    SUM(levels_completed) AS total_completions,
                    SUM(total_queries) AS total_queries,
                    ROUND(AVG(levels_completed), 1) AS avg_levels_per_session,
                    ROUND(AVG(total_queries), 1) AS avg_queries_per_session
                FROM session_logs;
            """)
            
            row = cursor.fetchone()
            
            # Recent sessions
            cursor = conn.execute("""
                SELECT 
                    session_id,
                    started_at,
                    last_active_at,
                    levels_completed,
                    total_queries
                FROM session_logs
                ORDER BY started_at DESC
                LIMIT 10;
            """)
            
            recent = [{
                'session_id': r['session_id'][:8] + '...',
                'started': r['started_at'],
                'last_active': r['last_active_at'],
                'levels': r['levels_completed'],
                'queries': r['total_queries']
            } for r in cursor.fetchall()]
            
            return {
                'total_sessions': row['total_sessions'] or 0,
                'total_completions': row['total_completions'] or 0,
                'total_queries': row['total_queries'] or 0,
                'avg_levels_per_session': row['avg_levels_per_session'] or 0,
                'avg_queries_per_session': row['avg_queries_per_session'] or 0,
                'recent_sessions': recent
            }
        finally:
            conn.close()
    
    def get_query_stats(self) -> Dict[str, Any]:
        """
        Get statistics about query attempts.
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) AS total_queries,
                    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) AS valid_queries,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_queries,
                    ROUND(AVG(execution_time_ms), 0) AS avg_execution_time
                FROM query_attempts;
            """)
            
            row = cursor.fetchone()
            total = row['total_queries'] or 0
            valid = row['valid_queries'] or 0
            correct = row['correct_queries'] or 0
            
            return {
                'total_queries': total,
                'valid_queries': valid,
                'correct_queries': correct,
                'invalid_rate': round((total - valid) * 100 / total, 1) if total > 0 else 0,
                'success_rate': round(correct * 100 / total, 1) if total > 0 else 0,
                'avg_execution_time_ms': row['avg_execution_time'] or 0
            }
        finally:
            conn.close()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get complete dashboard summary with all metrics.
        """
        return {
            'sessions': self.get_session_summary(),
            'queries': self.get_query_stats(),
            'funnel': self.get_funnel_analysis(),
            'errors': self.get_error_analysis(),
            'learning_curve': self.get_learning_curve()
        }
