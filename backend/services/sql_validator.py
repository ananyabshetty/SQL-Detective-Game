"""
SQL Detective Game - SQL Validator Service
Ensures only safe SELECT queries are executed
"""
import re
from typing import Tuple

# Blocked SQL keywords that could modify data or schema
BLOCKED_KEYWORDS = [
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
    'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC',
    'EXECUTE', 'PRAGMA', 'ATTACH', 'DETACH', 'VACUUM',
    'REINDEX', 'REPLACE', 'UPSERT', 'MERGE'
]

# Pattern to detect multiple statements
MULTI_STATEMENT_PATTERN = re.compile(r';\s*\S', re.IGNORECASE)

# Pattern to detect comments that might hide malicious code
COMMENT_PATTERN = re.compile(r'(--.*$|/\*.*?\*/)', re.MULTILINE | re.DOTALL)


def validate_query(query: str) -> Tuple[bool, str]:
    """
    Validates a SQL query to ensure it's safe to execute.
    
    Args:
        query: The SQL query string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message will be empty string
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    # Normalize query for checking
    query = query.strip()
    
    # Remove comments for analysis (but keep original for execution)
    query_no_comments = COMMENT_PATTERN.sub('', query)
    query_upper = query_no_comments.upper().strip()
    
    # 1. Check if query starts with SELECT or WITH (for CTEs)
    if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
        return False, "Only SELECT queries are allowed. Your query must start with SELECT or WITH."
    
    # 2. Check for blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        # Use word boundary to avoid false positives (e.g., "UPDATED_AT" column)
        pattern = rf'\b{keyword}\b'
        if re.search(pattern, query_upper):
            return False, f"Forbidden keyword detected: {keyword}. Only SELECT queries are allowed."
    
    # 3. Check for multiple statements (prevent injection via second statement)
    if MULTI_STATEMENT_PATTERN.search(query):
        return False, "Multiple statements are not allowed. Please submit one query at a time."
    
    # 4. Check query length (prevent DoS via very long queries)
    if len(query) > 5000:
        return False, "Query is too long. Maximum 5000 characters allowed."
    
    # 5. Check for suspicious patterns
    suspicious_patterns = [
        (r'INTO\s+OUTFILE', "INTO OUTFILE is not allowed"),
        (r'INTO\s+DUMPFILE', "INTO DUMPFILE is not allowed"),
        (r'LOAD_FILE', "LOAD_FILE is not allowed"),
        (r'BENCHMARK\s*\(', "BENCHMARK is not allowed"),
        (r'SLEEP\s*\(', "SLEEP is not allowed"),
    ]
    
    for pattern, error_msg in suspicious_patterns:
        if re.search(pattern, query_upper):
            return False, error_msg
    
    return True, ""


def sanitize_query(query: str) -> str:
    """
    Sanitizes a query by removing leading/trailing whitespace
    and normalizing line endings.
    
    Args:
        query: The SQL query to sanitize
        
    Returns:
        Sanitized query string
    """
    if not query:
        return ""
    
    # Normalize line endings
    query = query.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove leading/trailing whitespace
    query = query.strip()
    
    # Remove trailing semicolon if present
    if query.endswith(';'):
        query = query[:-1].strip()
    
    return query


def get_blocked_keywords() -> list:
    """Returns list of blocked SQL keywords for frontend display"""
    return BLOCKED_KEYWORDS.copy()
