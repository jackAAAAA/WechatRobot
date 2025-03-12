import logging
from flask import Flask

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat.log'),
        logging.StreamHandler()
    ]
)

def create_app(config_class=None):
    """Create and configure the Flask application.
    
    Args:
        config_class: The configuration class to use. If None, uses the default Config.
        
    Returns:
        The configured Flask application.
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from app.config.config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    # Initialize Celery
    from app.utils.celery_utils import init_celery
    init_celery(app)
    
    # Register blueprints
    from app.core.router import register_routes
    register_routes(app)
    
    # Log app startup
    app.logger.info("Application initialized successfully")
    
    return app 