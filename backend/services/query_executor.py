"""
SQL Detective Game - Query Executor Service
Safely executes read-only SQL queries against the database
"""
import sqlite3
import time
from typing import Tuple, List, Dict, Any, Optional
from contextlib import contextmanager

from config import Config
from services.sql_validator import validate_query, sanitize_query


class QueryExecutor:
    """Handles safe execution of SQL queries"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.timeout = Config.QUERY_TIMEOUT
        self.max_rows = Config.MAX_RESULT_ROWS
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for read-only database connection.
        Uses URI mode with read-only flag for extra safety.
        """
        # Connect in read-only mode using URI
        conn = sqlite3.connect(
            f'file:{self.db_path}?mode=ro',
            uri=True,
            timeout=self.timeout
        )
        conn.row_factory = sqlite3.Row  # Enable column name access
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Executes a SQL query safely and returns results.
        
        Args:
            query: The SQL query to execute
            
        Returns:
            Tuple of (success, result_dict)
            result_dict contains:
                - columns: list of column names
                - rows: list of row data
                - row_count: number of rows
                - execution_time: time taken in ms
                - error: error message if failed
        """
        # Sanitize query
        query = sanitize_query(query)
        
        # Validate query
        is_valid, error_msg = validate_query(query)
        if not is_valid:
            return False, {
                'error': error_msg,
                'columns': [],
                'rows': [],
                'row_count': 0,
                'execution_time': 0
            }
        
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Get column names
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Fetch results (with limit for safety)
                rows = cursor.fetchmany(self.max_rows)
                
                # Convert Row objects to lists for JSON serialization
                rows_data = [list(row) for row in rows]
                
                execution_time = round((time.time() - start_time) * 1000, 2)
                
                return True, {
                    'columns': columns,
                    'rows': rows_data,
                    'row_count': len(rows_data),
                    'execution_time': execution_time,
                    'error': None,
                    'truncated': len(rows_data) == self.max_rows
                }
                
        except sqlite3.OperationalError as e:
            error_msg = str(e)
            # Make error messages more user-friendly
            if 'no such table' in error_msg:
                table_name = error_msg.split(':')[-1].strip() if ':' in error_msg else 'unknown'
                error_msg = f"Table not found: {table_name}. Check your table name spelling."
            elif 'no such column' in error_msg:
                error_msg = f"Column not found. Check your column names. {error_msg}"
            elif 'syntax error' in error_msg.lower():
                error_msg = f"SQL syntax error: {error_msg}. Check your query syntax."
            
            return False, {
                'error': error_msg,
                'columns': [],
                'rows': [],
                'row_count': 0,
                'execution_time': round((time.time() - start_time) * 1000, 2)
            }
            
        except sqlite3.Error as e:
            return False, {
                'error': f"Database error: {str(e)}",
                'columns': [],
                'rows': [],
                'row_count': 0,
                'execution_time': round((time.time() - start_time) * 1000, 2)
            }
        
        except Exception as e:
            return False, {
                'error': f"Unexpected error: {str(e)}",
                'columns': [],
                'rows': [],
                'row_count': 0,
                'execution_time': round((time.time() - start_time) * 1000, 2)
            }
    
    def get_table_schema(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Gets the schema information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column info dicts or None if table doesn't exist
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                if not columns:
                    return None
                
                return [
                    {
                        'name': col[1],
                        'type': col[2],
                        'nullable': not col[3],
                        'primary_key': bool(col[5])
                    }
                    for col in columns
                ]
        except:
            return None
    
    def get_all_tables(self) -> List[str]:
        """Returns list of all table names in the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                return [row[0] for row in cursor.fetchall()]
        except:
            return []
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> Tuple[bool, Dict[str, Any]]:
        """
        Gets sample data from a table for preview.
        
        Args:
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            Same format as execute_query
        """
        # Validate table name to prevent injection
        if not table_name.isidentifier():
            return False, {'error': 'Invalid table name'}
        
        query = f"SELECT * FROM {table_name} LIMIT {min(limit, 10)}"
        return self.execute_query(query)


# Singleton instance
query_executor = QueryExecutor()
