from celery import Celery
from flask import Flask

# Global Celery instance to be used throughout the application
celery = Celery('wechat_robot')

def init_celery(app: Flask):
    """Initialize Celery with Flask app configuration
    
    This should be called once during application startup.
    """
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer=app.config['CELERY_TASK_SERIALIZER'],
        accept_content=app.config['CELERY_ACCEPT_CONTENT'],
        result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
        timezone=app.config['CELERY_TIMEZONE'],
        enable_utc=app.config['CELERY_ENABLE_UTC']
    )
    
    # Register task modules - corrected paths to match actual project structure
    celery.autodiscover_tasks([
        'app.adapters.source_adapters.wechat_adapter',
        'app.adapters.source_adapters.wecom_adapter',
        'app.services.provider_services.groq_service',
        'app.services.provider_services.tongyiqianwen_service',
        'app.services.provider_services.deepseek_service',
    ], force=True)
    
    # Apply Flask app context to Celery tasks
    TaskBase = celery.Task
    
    class ContextTask(TaskBase):
        abstract = True
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    
    celery.Task = ContextTask
    
    return celery 