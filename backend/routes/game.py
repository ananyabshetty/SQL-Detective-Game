"""
SQL Detective Game - Game Routes
Handles level progression and game state
"""
from flask import Blueprint, jsonify, request, session
from levels import get_level, get_all_levels, get_level_count, get_tables_for_level
from services.query_executor import query_executor

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


@game_bp.route('/levels', methods=['GET'])
def get_levels():
    """Get all levels (without solutions)"""
    levels = get_all_levels()
    return jsonify({
        'success': True,
        'levels': [level.to_dict(include_solution=False) for level in levels.values()],
        'total_levels': get_level_count()
    })


@game_bp.route('/levels/<int:level_id>', methods=['GET'])
def get_level_details(level_id):
    """Get specific level details"""
    level = get_level(level_id)
    
    if not level:
        return jsonify({
            'success': False,
            'error': f'Level {level_id} not found'
        }), 404
    
    # Check if player has unlocked this level
    current_level = session.get('current_level', 1)
    if level_id > current_level:
        return jsonify({
            'success': False,
            'error': 'Level not yet unlocked',
            'current_level': current_level
        }), 403
    
    return jsonify({
        'success': True,
        'level': level.to_dict(include_solution=False)
    })


@game_bp.route('/progress', methods=['GET'])
def get_progress():
    """Get player's current progress"""
    return jsonify({
        'success': True,
        'current_level': session.get('current_level', 1),
        'completed_levels': session.get('completed_levels', []),
        'total_queries': session.get('total_queries', 0),
        'correct_answers': session.get('correct_answers', 0)
    })


@game_bp.route('/progress/reset', methods=['POST'])
def reset_progress():
    """Reset player progress"""
    session['current_level'] = 1
    session['completed_levels'] = []
    session['total_queries'] = 0
    session['correct_answers'] = 0
    
    return jsonify({
        'success': True,
        'message': 'Progress reset. Starting from Level 1.'
    })


@game_bp.route('/progress/unlock/<int:level_id>', methods=['POST'])
def unlock_level(level_id):
    """Unlock a specific level (for development/testing)"""
    if level_id < 1 or level_id > get_level_count():
        return jsonify({
            'success': False,
            'error': 'Invalid level ID'
        }), 400
    
    session['current_level'] = level_id
    return jsonify({
        'success': True,
        'message': f'Unlocked Level {level_id}'
    })


@game_bp.route('/tables', methods=['GET'])
def get_available_tables():
    """Get list of tables available for current level"""
    current_level = session.get('current_level', 1)
    tables = get_tables_for_level(current_level)
    
    # Get schema for each table
    table_schemas = {}
    for table in tables:
        schema = query_executor.get_table_schema(table)
        if schema:
            table_schemas[table] = schema
    
    return jsonify({
        'success': True,
        'level': current_level,
        'tables': tables,
        'schemas': table_schemas
    })


@game_bp.route('/tables/<table_name>/sample', methods=['GET'])
def get_table_sample(table_name):
    """Get sample data from a table"""
    current_level = session.get('current_level', 1)
    available_tables = get_tables_for_level(current_level)
    
    # Check if table is available for current level
    if table_name not in available_tables:
        return jsonify({
            'success': False,
            'error': f'Table {table_name} is not available for this level'
        }), 403
    
    success, result = query_executor.get_sample_data(table_name, limit=5)
    
    return jsonify({
        'success': success,
        'table': table_name,
        'columns': result.get('columns', []),
        'rows': result.get('rows', []),
        'error': result.get('error')
    })


@game_bp.route('/tables/<table_name>/schema', methods=['GET'])
def get_table_schema(table_name):
    """Get schema for a specific table"""
    current_level = session.get('current_level', 1)
    available_tables = get_tables_for_level(current_level)
    
    if table_name not in available_tables:
        return jsonify({
            'success': False,
            'error': f'Table {table_name} is not available for this level'
        }), 403
    
    schema = query_executor.get_table_schema(table_name)
    
    if schema is None:
        return jsonify({
            'success': False,
            'error': f'Table {table_name} not found'
        }), 404
    
    return jsonify({
        'success': True,
        'table': table_name,
        'schema': schema
    })
