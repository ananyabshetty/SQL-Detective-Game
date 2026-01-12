"""
SQL Detective: The Data Crime Investigation Game
================================================
Main Flask Application

An immersive SQL learning game where players solve crimes using database queries
in a 3D noir detective environment.
"""
import os
import sqlite3
from flask import Flask, send_from_directory, session
from flask_cors import CORS

from config import Config
from routes.game import game_bp
from routes.query import query_bp
from analytics.routes import analytics_bp


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Enable CORS for development
    CORS(app, supports_credentials=True)
    
    # Initialize database if needed
    init_database(app)
    
    # Initialize analytics tables
    init_analytics(app)
    
    # Register blueprints
    app.register_blueprint(game_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(analytics_bp)
    
    # Serve frontend
    @app.route('/')
    def serve_frontend():
        return send_from_directory(app.static_folder, 'index.html')
    
    # Serve analytics dashboard
    @app.route('/analytics')
    def serve_analytics():
        return send_from_directory(app.static_folder, 'analytics/analytics.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'game': 'SQL Detective', 'analytics': 'enabled'}
    
    return app


def init_database(app):
    """Initialize the database with schema and seed data if it doesn't exist"""
    db_path = app.config['DATABASE_PATH']
    schema_path = os.path.join(os.path.dirname(db_path), 'schema.sql')
    seed_path = os.path.join(os.path.dirname(db_path), 'seed_data.sql')
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Check if database already exists and has tables
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suspects'")
        if cursor.fetchone():
            conn.close()
            print("✓ Database already initialized")
            return
        conn.close()
    
    print("Initializing database...")
    
    # Create and populate database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            cursor.executescript(f.read())
        print("✓ Schema created")
    else:
        print("✗ Schema file not found!")
    
    # Execute seed data
    if os.path.exists(seed_path):
        with open(seed_path, 'r') as f:
            cursor.executescript(f.read())
        print("✓ Seed data inserted")
    else:
        print("✗ Seed data file not found!")
    
    conn.commit()
    conn.close()
    print("✓ Database initialization complete")


def init_analytics(app):
    """Initialize analytics tables and configuration"""
    db_path = app.config['DATABASE_PATH']
    analytics_dir = os.path.join(os.path.dirname(__file__), 'analytics')
    schema_path = os.path.join(analytics_dir, 'schema.sql')
    config_path = os.path.join(analytics_dir, 'config_seed.sql')
    
    # Check if analytics tables exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analytics_config'")
    if cursor.fetchone():
        conn.close()
        print("✓ Analytics tables already initialized")
        return
    
    print("Initializing analytics tables...")
    
    # Create analytics schema
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            cursor.executescript(f.read())
        print("✓ Analytics schema created")
    
    # Insert default config
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cursor.executescript(f.read())
        print("✓ Analytics config loaded")
    
    conn.commit()
    conn.close()
    print("✓ Analytics initialization complete")


# Create the application
app = create_app()


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🔍 SQL Detective: The Data Crime Investigation Game 🔍      ║
    ║                                                               ║
    ║   An immersive SQL learning experience                        ║
    ║   + Analytics Dashboard Enabled                               ║
    ║                                                               ║
    ║   Game:       http://localhost:5000                           ║
    ║   Analytics:  http://localhost:5000/analytics                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)

