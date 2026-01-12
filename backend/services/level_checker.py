"""
SQL Detective Game - Level Checker Service
Validates player answers against expected results
"""
from typing import Dict, Any, Tuple, List, Set
import sqlite3

from services.query_executor import query_executor
from levels.level_config import get_level, Level


class LevelChecker:
    """Handles level answer verification"""
    
    def __init__(self):
        self.executor = query_executor
    
    def check_answer(self, level_id: int, user_query: str) -> Dict[str, Any]:
        """
        Check if user's query produces the correct answer for a level.
        
        Args:
            level_id: The level ID to check
            user_query: The user's SQL query
            
        Returns:
            Dictionary with:
                - correct: bool - whether answer is correct
                - message: str - feedback message
                - user_result: dict - user's query result
                - expected_result: dict - expected result (only if correct or for debugging)
                - hints: list - hints if incorrect
        """
        level = get_level(level_id)
        if not level:
            return {
                'correct': False,
                'message': f'Level {level_id} not found',
                'user_result': None,
                'hints': []
            }
        
        # Execute user's query
        success, user_result = self.executor.execute_query(user_query)
        
        if not success:
            return {
                'correct': False,
                'message': f"Query Error: {user_result.get('error', 'Unknown error')}",
                'user_result': user_result,
                'hints': self._get_error_hints(user_result.get('error', ''), level)
            }
        
        # Execute expected query to get expected result
        _, expected_result = self.executor.execute_query(level.expected_query)
        
        # Compare results
        is_correct, comparison_details = self._compare_results(
            user_result, 
            expected_result, 
            level
        )
        
        if is_correct:
            return {
                'correct': True,
                'message': self._get_success_message(level_id),
                'user_result': user_result,
                'next_level': level_id + 1 if level_id < 7 else None
            }
        else:
            return {
                'correct': False,
                'message': comparison_details['message'],
                'user_result': user_result,
                'hints': self._get_incorrect_hints(comparison_details, level)
            }
    
    def _compare_results(
        self, 
        user_result: Dict[str, Any], 
        expected_result: Dict[str, Any],
        level: Level
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Compare user result with expected result.
        
        Returns:
            Tuple of (is_correct, details_dict)
        """
        details = {'message': '', 'issues': []}
        
        # Check if user got any rows
        if user_result['row_count'] == 0 and expected_result['row_count'] > 0:
            details['message'] = "Your query returned no results, but there should be matching records."
            details['issues'].append('no_results')
            return False, details
        
        # Check row count
        if level.expected_row_count is not None:
            if user_result['row_count'] != expected_result['row_count']:
                details['message'] = f"Row count mismatch: Got {user_result['row_count']} rows, expected {expected_result['row_count']} rows."
                details['issues'].append('row_count')
                return False, details
        
        # Check required columns if specified
        if level.expected_columns:
            user_cols_lower = {col.lower() for col in user_result['columns']}
            expected_cols_lower = {col.lower() for col in level.expected_columns}
            
            missing_cols = expected_cols_lower - user_cols_lower
            if missing_cols:
                details['message'] = f"Missing required columns: {', '.join(missing_cols)}"
                details['issues'].append('missing_columns')
                return False, details
        
        # Compare actual data
        user_data = self._normalize_rows(user_result['rows'])
        expected_data = self._normalize_rows(expected_result['rows'])
        
        if level.order_matters:
            # Order matters - compare directly
            if user_data != expected_data:
                details['message'] = "Data or ordering doesn't match expected result."
                details['issues'].append('data_mismatch')
                return False, details
        else:
            # Order doesn't matter - compare as sets
            user_set = set(user_data)
            expected_set = set(expected_data)
            
            if user_set != expected_set:
                missing = expected_set - user_set
                extra = user_set - expected_set
                
                if missing and extra:
                    details['message'] = "Some rows are incorrect or missing."
                elif missing:
                    details['message'] = "Some expected rows are missing from your result."
                else:
                    details['message'] = "Your result contains extra rows not in the expected answer."
                
                details['issues'].append('data_mismatch')
                return False, details
        
        return True, details
    
    def _normalize_rows(self, rows: List[List[Any]]) -> List[Tuple]:
        """Convert rows to normalized tuple format for comparison"""
        normalized = []
        for row in rows:
            normalized_row = []
            for val in row:
                # Convert to string for comparison, handling None
                if val is None:
                    normalized_row.append(None)
                elif isinstance(val, float):
                    # Round floats for comparison
                    normalized_row.append(round(val, 2))
                else:
                    normalized_row.append(val)
            normalized.append(tuple(normalized_row))
        return normalized
    
    def _get_error_hints(self, error: str, level: Level) -> List[str]:
        """Generate hints based on error message"""
        hints = []
        error_lower = error.lower()
        
        if 'no such table' in error_lower:
            hints.append(f"Available tables for this level: {', '.join(level.tables_unlocked)}")
        elif 'no such column' in error_lower:
            hints.append("Check your column names. Use SELECT * FROM table_name to see available columns.")
        elif 'syntax error' in error_lower:
            hints.append("Check your SQL syntax. Common issues: missing commas, unmatched quotes, typos in keywords.")
        elif 'forbidden' in error_lower or 'not allowed' in error_lower:
            hints.append("Only SELECT queries are allowed. You cannot modify the database.")
        
        hints.append(f"Hint: {level.hint}")
        return hints
    
    def _get_incorrect_hints(self, details: Dict[str, Any], level: Level) -> List[str]:
        """Generate hints for incorrect but valid queries"""
        hints = []
        
        if 'no_results' in details.get('issues', []):
            hints.append("Your query syntax is correct but the filter conditions may be too restrictive.")
            hints.append("Double-check your WHERE clause values.")
        
        if 'row_count' in details.get('issues', []):
            hints.append("You're on the right track but getting different number of rows.")
            hints.append("Review the filter conditions in the objective carefully.")
        
        if 'missing_columns' in details.get('issues', []):
            hints.append("Make sure you're selecting all the required columns.")
        
        if 'data_mismatch' in details.get('issues', []):
            hints.append("The data doesn't match. Re-read the objective and check your conditions.")
        
        hints.append(f"Level hint: {level.hint}")
        return hints
    
    def _get_success_message(self, level_id: int) -> str:
        """Get success message based on level"""
        messages = {
            1: "🎉 Excellent work, Detective! You've identified the key suspects. The investigation deepens...",
            2: "🎉 Great analysis! Those midnight calls are suspicious. Let's dig deeper...",
            3: "🎉 You've connected the dots! Now we know who was at the scene.",
            4: "🎉 Pattern identified! One suspect was unusually active that night.",
            5: "🎉 Follow the money! These large transactions are very suspicious.",
            6: "🎉 The alibi is broken! Viktor's movements prove he was at the bank.",
            7: "🎉 CASE SOLVED! You've proven the financial conspiracy. Viktor Petrov and his accomplices are caught!"
        }
        return messages.get(level_id, "🎉 Level complete!")


# Singleton instance
level_checker = LevelChecker()
