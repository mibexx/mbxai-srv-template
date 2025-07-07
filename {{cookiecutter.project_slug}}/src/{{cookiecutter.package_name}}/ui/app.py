"""Main Flask application."""

import os
import json
import logging
import requests
from flask import Flask, render_template, request, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm

from ..config import get_ui_config


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config = get_ui_config()
    app.config.from_object(config)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Configure logging
    if config.DEBUG:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        app.logger.setLevel(logging.INFO)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Add config and csrf_token to template context
    @app.context_processor
    def inject_config():
        from flask_wtf.csrf import generate_csrf
        return dict(config=config, csrf_token=generate_csrf)
    
    # Routes
    @app.route('/')
    def index():
        """Home page with CSV converter form."""
        return render_template('index.html', active_page='overview')
    
    
    @app.route('/api/hello', methods=['POST'])
    @csrf.exempt
    def hello_proxy():
        """Proxy the hello request to the backend API."""
        try:
            # Get the request data from the frontend
            request_data = request.get_json()
            
            if not request_data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Log the request data for debugging
            app.logger.info(f"Frontend request data: {json.dumps(request_data, indent=2)}")
            
            # Make the request to the actual API backend
            api_url = f"{config.API_URL}/api/hello"
            app.logger.info(f"Proxying hello request to: {api_url}")
            
            response = requests.post(
                api_url,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=300  # 5 minute timeout for AI hello
            )
            
            # Log the response for debugging
            app.logger.info(f"Backend API response status: {response.status_code}")
            if response.status_code != 200:
                app.logger.error(f"Backend API response body: {response.text}")
            
            # Return the response from the backend API
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                app.logger.error(f"Backend API error: {response.status_code} - {response.text}")
                try:
                    error_data = response.json()
                    return jsonify(error_data), response.status_code
                except json.JSONDecodeError:
                    return jsonify({
                        'error': f'Backend API error: {response.status_code}',
                        'detail': response.text
                    }), response.status_code
                    
        except requests.exceptions.Timeout:
            app.logger.error("Backend API request timed out")
            return jsonify({
                'error': 'Request timed out',
                'detail': 'The hello request took too long to complete. Please try again.'
            }), 504
            
        except requests.exceptions.ConnectionError as e:
            app.logger.error(f"Failed to connect to backend API: {str(e)}")
            return jsonify({
                'error': 'Backend API unavailable',
                'detail': 'Unable to connect to the hello service. Please try again later.'
            }), 503
            
        except Exception as e:
            app.logger.error(f"Unexpected error in hello proxy: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'detail': 'An unexpected error occurred while processing your request.'
            }), 500
    
    return app


def run_dev_server() -> None:
    """Run development server."""
    app = create_app()
    config = get_ui_config()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


def run_server() -> None:
    """Run production server."""
    app = create_app()
    config = get_ui_config()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=False
    )


if __name__ == "__main__":
    run_dev_server() 