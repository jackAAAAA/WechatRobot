from flask import Flask, Blueprint, request, jsonify
from app.core.source_processor import SourceProcessor

# Main blueprint for API routes
api_bp = Blueprint('api', __name__)

def register_routes(app: Flask):
    """Register all routes with the Flask application.
    
    Args:
        app: The Flask application instance.
    """
    # Register the API blueprint
    app.register_blueprint(api_bp)
    
    # Log the registered routes
    app.logger.info("Routes registered successfully")
    
    for rule in app.url_map.iter_rules():
        app.logger.debug(f"Route: {rule}")

@api_bp.route('/<source>/<provider>', methods=['GET', 'POST'], defaults={'model': None})
@api_bp.route('/<source>/<provider>/<model>', methods=['GET', 'POST'])
def handle_request(source, provider, model):
    """Main route handler that processes requests based on path parameters.
    
    Args:
        source: The source of the request (wechat/wecom/etc.)
        provider: The AI provider to use (Groq/Tencent/etc.)
        model: Optional specific model to use
        
    Returns:
        The appropriate response based on the request.
    """
    # Initialize the source processor
    processor = SourceProcessor(source)
    
    # Process the request based on the method (GET for verification, POST for messages)
    if request.method == 'GET':
        return processor.verify(request)
    elif request.method == 'POST':
        # Extract source-specific parameters
        params = processor.extract_params(request)
        
        # Process with the specified provider and model
        return processor.process(params, provider, model)
    else:
        return jsonify({"error": "Method not allowed"}), 405 