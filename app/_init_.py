from flask import Flask

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Import and register routes
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app