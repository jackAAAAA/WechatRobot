from app import create_app
from app.utils.celery_utils import celery

# Create the Flask application (initializes Celery)
app = create_app()

if __name__ == '__main__':
    # Start the Celery worker with the Flask application context
    with app.app_context():
        celery.worker_main(['worker', '--loglevel=info', '-P', 'solo']) 