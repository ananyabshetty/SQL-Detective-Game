"""
SQL Detective Game - Query Routes
Handles SQL query execution and answer checking
"""
import time
import uuid
from flask import Blueprint, jsonify, request, session
from services.query_executor import query_executor
from services.sql_validator import validate_query, get_blocked_keywords
from services.level_checker import level_checker
from levels import get_tables_for_level
import config

# Import player analytics for logging
try:
    from analytics.services import PlayerAnalytics
    ANALYTICS_ENABLED = True
except ImportError:
    ANALYTICS_ENABLED = False

query_bp = Blueprint('query', __name__, url_prefix='/api/query')


def get_or_create_session_id():
    """Get or create a unique session ID for analytics"""
    if 'analytics_session_id' not in session:
        session['analytics_session_id'] = str(uuid.uuid4())
        # Log session start if analytics enabled
        if ANALYTICS_ENABLED:
            try:
                analytics = PlayerAnalytics(config.DATABASE_PATH)
                analytics.log_session_start(
                    session['analytics_session_id'],
                    request.headers.get('User-Agent')
                )
            except Exception:
                pass
    return session['analytics_session_id']


def log_query_attempt(level_id, query, is_valid, is_correct=None, 
                      execution_time_ms=None, error_message=None):
    """Log a query attempt to analytics"""
    if not ANALYTICS_ENABLED:
        return
    
    try:
        session_id = get_or_create_session_id()
        analytics = PlayerAnalytics(config.DATABASE_PATH)
        analytics.log_query_attempt(
            session_id=session_id,
            level_id=level_id,
            query_text=query,
            is_valid=is_valid,
            is_correct=is_correct,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
    except Exception as e:
        print(f"Analytics logging error: {e}")


def log_error(level_id, error_type, error_detail=None, query_fragment=None):
    """Log an error to analytics"""
    if not ANALYTICS_ENABLED:
        return
    
    try:
        session_id = get_or_create_session_id()
        analytics = PlayerAnalytics(config.DATABASE_PATH)
        analytics.log_error(
            session_id=session_id,
            level_id=level_id,
            error_type=error_type,
            error_detail=error_detail,
            query_fragment=query_fragment[:100] if query_fragment else None
        )
    except Exception:
        pass


def log_level_completion(level_id, attempts_count, time_spent_seconds=None):
    """Log a level completion to analytics"""
    if not ANALYTICS_ENABLED:
        return
    
    try:
        session_id = get_or_create_session_id()
        analytics = PlayerAnalytics(config.DATABASE_PATH)
        analytics.log_level_completion(
            session_id=session_id,
            level_id=level_id,
            attempts_count=attempts_count,
            time_spent_seconds=time_spent_seconds
        )
    except Exception:
        pass


@query_bp.route('/execute', methods=['POST'])
def execute_query():
    """Execute a SQL query and return results"""
    data = request.get_json()
    level_id = data.get('level_id', session.get('current_level', 1))
    
    if not data or 'query' not in data:
        log_error(level_id, 'EMPTY_REQUEST', 'No query provided')
        return jsonify({
            'success': False,
            'error': 'No query provided'
        }), 400
    
    query = data.get('query', '').strip()
    
    if not query:
        log_error(level_id, 'EMPTY_QUERY', 'Query was empty')
        return jsonify({
            'success': False,
            'error': 'Query cannot be empty'
        }), 400
    
    # Track total queries in session
    session['total_queries'] = session.get('total_queries', 0) + 1
    
    # Execute the query with timing
    start_time = time.time()
    success, result = query_executor.execute_query(query)
    execution_time_ms = int((time.time() - start_time) * 1000)
    
    # Log to analytics
    if success:
        log_query_attempt(
            level_id=level_id,
            query=query,
            is_valid=True,
            execution_time_ms=execution_time_ms
        )
    else:
        error_msg = result.get('error', 'Unknown error')
        # Categorize error type
        error_type = categorize_error(error_msg)
        log_query_attempt(
            level_id=level_id,
            query=query,
            is_valid=False,
            execution_time_ms=execution_time_ms,
            error_message=error_msg
        )
        log_error(level_id, error_type, error_msg, query)
    
    return jsonify({
        'success': success,
        'columns': result.get('columns', []),
        'rows': result.get('rows', []),
        'row_count': result.get('row_count', 0),
        'execution_time': result.get('execution_time', 0),
        'error': result.get('error'),
        'truncated': result.get('truncated', False)
    })


def categorize_error(error_msg):
    """Categorize error message into error type"""
    error_lower = error_msg.lower()
    
    if 'syntax' in error_lower:
        return 'SYNTAX_ERROR'
    elif 'no such table' in error_lower:
        return 'TABLE_NOT_FOUND'
    elif 'no such column' in error_lower:
        return 'COLUMN_NOT_FOUND'
    elif 'blocked' in error_lower or 'not allowed' in error_lower:
        return 'BLOCKED_KEYWORD'
    elif 'timeout' in error_lower:
        return 'TIMEOUT'
    elif 'ambiguous' in error_lower:
        return 'AMBIGUOUS_COLUMN'
    elif 'group by' in error_lower or 'aggregate' in error_lower:
        return 'AGGREGATION_ERROR'
    else:
        return 'OTHER_ERROR'


@query_bp.route('/check', methods=['POST'])
def check_answer():
    """Check if query answer is correct for current level"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({
            'success': False,
            'error': 'No query provided'
        }), 400
    
    query = data.get('query', '').strip()
    level_id = data.get('level_id', session.get('current_level', 1))
    
    # Initialize level tracking
    level_key = f'level_{level_id}_attempts'
    level_start_key = f'level_{level_id}_start'
    
    # Track attempts for this level
    session[level_key] = session.get(level_key, 0) + 1
    attempts = session[level_key]
    
    # Track level start time
    if level_start_key not in session:
        session[level_start_key] = time.time()
    
    # Track total queries
    session['total_queries'] = session.get('total_queries', 0) + 1
    
    # Check the answer
    result = level_checker.check_answer(level_id, query)
    
    # Log the attempt
    log_query_attempt(
        level_id=level_id,
        query=query,
        is_valid=True,
        is_correct=result['correct']
    )
    
    if result['correct']:
        # Calculate time spent
        time_spent = int(time.time() - session.get(level_start_key, time.time()))
        
        # Log completion
        log_level_completion(level_id, attempts, time_spent)
        
        # Update progress
        session['correct_answers'] = session.get('correct_answers', 0) + 1
        completed = session.get('completed_levels', [])
        if level_id not in completed:
            completed.append(level_id)
            session['completed_levels'] = completed
        
        # Unlock next level
        current = session.get('current_level', 1)
        if level_id >= current and level_id < 7:
            session['current_level'] = level_id + 1
        
        # Reset level tracking for next attempt
        session.pop(level_key, None)
        session.pop(level_start_key, None)
    
    return jsonify({
        'success': True,
        'correct': result['correct'],
        'message': result['message'],
        'user_result': result.get('user_result'),
        'hints': result.get('hints', []),
        'next_level': result.get('next_level'),
        'current_level': session.get('current_level', 1)
    })


@query_bp.route('/validate', methods=['POST'])
def validate_query_syntax():
    """Validate a SQL query without executing it"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({
            'success': False,
            'error': 'No query provided'
        }), 400
    
    query = data.get('query', '').strip()
    is_valid, error_msg = validate_query(query)
    
    # Log validation errors
    if not is_valid:
        level_id = data.get('level_id', session.get('current_level', 1))
        log_error(level_id, 'VALIDATION_ERROR', error_msg, query)
    
    return jsonify({
        'success': True,
        'valid': is_valid,
        'error': error_msg if not is_valid else None
    })


@query_bp.route('/blocked-keywords', methods=['GET'])
def get_blocked():
    """Get list of blocked SQL keywords"""
    return jsonify({
        'success': True,
        'blocked_keywords': get_blocked_keywords()
    })

