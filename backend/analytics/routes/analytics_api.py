"""
Analytics API Routes
Provides endpoints for the analytics dashboard (Admin Only)
"""

from flask import Blueprint, jsonify, request, session
from analytics.services import SuspectScorer, TimeAnalyzer, PlayerAnalytics
import config

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


def get_db_path():
    """Get database path from config"""
    return config.DATABASE_PATH


# ==========================================
# Module 1: Suspect Intelligence Engine
# ==========================================

@analytics_bp.route('/suspects/rankings', methods=['GET'])
def get_suspect_rankings():
    """Get all suspects ranked by suspicion score"""
    try:
        scorer = SuspectScorer(get_db_path())
        rankings = scorer.get_suspect_rankings()
        return jsonify({
            'success': True,
            'rankings': rankings,
            'count': len(rankings)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/suspects/chart-data', methods=['GET'])
def get_suspect_chart_data():
    """Get data formatted for Chart.js stacked bar chart"""
    try:
        scorer = SuspectScorer(get_db_path())
        data = scorer.get_score_breakdown_chart_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/suspects/top', methods=['GET'])
def get_top_suspects():
    """Get top N suspects by score"""
    limit = request.args.get('limit', 3, type=int)
    try:
        scorer = SuspectScorer(get_db_path())
        suspects = scorer.get_top_suspects(limit)
        return jsonify({
            'success': True,
            'suspects': suspects
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/suspects/<int:suspect_id>', methods=['GET'])
def get_suspect_detail(suspect_id):
    """Get detailed analytics for a single suspect"""
    try:
        scorer = SuspectScorer(get_db_path())
        detail = scorer.get_suspect_detail(suspect_id)
        if detail:
            return jsonify({'success': True, 'suspect': detail})
        return jsonify({'success': False, 'error': 'Suspect not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/config', methods=['GET'])
def get_analytics_config():
    """Get current analytics configuration"""
    try:
        scorer = SuspectScorer(get_db_path())
        config_data = scorer.get_config()
        return jsonify({
            'success': True,
            'config': config_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/config', methods=['POST'])
def update_analytics_config():
    """Update analytics configuration value"""
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    
    if not key or value is None:
        return jsonify({'success': False, 'error': 'Missing key or value'}), 400
    
    try:
        scorer = SuspectScorer(get_db_path())
        success = scorer.update_config(key, float(value))
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# Module 2: Time-Based Behavioral Analysis
# ==========================================

@analytics_bp.route('/timeline/hourly', methods=['GET'])
def get_hourly_timeline():
    """Get hourly activity breakdown for a date"""
    date = request.args.get('date', '2024-03-15')
    try:
        analyzer = TimeAnalyzer(get_db_path())
        data = analyzer.get_hourly_activity(date)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/timeline/suspect/<int:suspect_id>', methods=['GET'])
def get_suspect_timeline(suspect_id):
    """Get activity timeline for a specific suspect"""
    try:
        analyzer = TimeAnalyzer(get_db_path())
        data = analyzer.get_suspect_timeline(suspect_id)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/timeline/comparison', methods=['GET'])
def get_before_after_comparison():
    """Compare suspect activity before and after crime"""
    try:
        analyzer = TimeAnalyzer(get_db_path())
        data = analyzer.get_before_after_comparison()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/timeline/heatmap', methods=['GET'])
def get_activity_heatmap():
    """Get activity heatmap data"""
    try:
        analyzer = TimeAnalyzer(get_db_path())
        data = analyzer.get_activity_heatmap_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# Module 3: Player Behavior Analytics
# ==========================================

@analytics_bp.route('/players/funnel', methods=['GET'])
def get_player_funnel():
    """Get level progression funnel analysis"""
    try:
        analytics = PlayerAnalytics(get_db_path())
        data = analytics.get_funnel_analysis()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/players/errors', methods=['GET'])
def get_error_analysis():
    """Get common error analysis"""
    try:
        analytics = PlayerAnalytics(get_db_path())
        data = analytics.get_error_analysis()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/players/learning-curve', methods=['GET'])
def get_learning_curve():
    """Get learning curve analysis"""
    try:
        analytics = PlayerAnalytics(get_db_path())
        data = analytics.get_learning_curve()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/players/sessions', methods=['GET'])
def get_session_summary():
    """Get session statistics"""
    try:
        analytics = PlayerAnalytics(get_db_path())
        data = analytics.get_session_summary()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/players/queries', methods=['GET'])
def get_query_stats():
    """Get query attempt statistics"""
    try:
        analytics = PlayerAnalytics(get_db_path())
        data = analytics.get_query_stats()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/players/dashboard', methods=['GET'])
def get_player_dashboard():
    """Get complete player analytics dashboard data"""
    try:
        analytics = PlayerAnalytics(get_db_path())
        data = analytics.get_dashboard_summary()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# Combined Summary Endpoint
# ==========================================

@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    """Get combined analytics summary for dashboard overview"""
    try:
        scorer = SuspectScorer(get_db_path())
        analyzer = TimeAnalyzer(get_db_path())
        player_analytics = PlayerAnalytics(get_db_path())
        
        return jsonify({
            'success': True,
            'data': {
                'top_suspects': scorer.get_top_suspects(3),
                'anomalies': analyzer.get_before_after_comparison().get('anomalies', []),
                'player_sessions': player_analytics.get_session_summary(),
                'query_stats': player_analytics.get_query_stats()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
