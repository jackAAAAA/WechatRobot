import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    
    # WeChat Official Account configuration
    WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN')
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID')
    WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET')
    
    # WeCom (Enterprise WeChat) configuration
    WECOM_TOKEN = os.environ.get('WECOM_TOKEN')
    WECOM_ENCODING_AES_KEY = os.environ.get('WECOM_ENCODING_AES_KEY')
    WECOM_CORP_ID = os.environ.get('WECOM_CORP_ID')
    WECOM_APP_SECRET = os.environ.get('WECOM_APP_SECRET')
    WECOM_AGENT_ID = os.environ.get('WECOM_AGENT_ID')
    
    # AI API configuration
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_CHAT = os.environ.get('DEEPSEEK_CHAT')
    
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GROQ_DS_R1_70B_MODEL = os.environ.get('GROQ_DS_R1_70B_MODEL')
    
    GEEK_API_KEY = os.environ.get('GEEK_API_KEY')
    GEEK_API_KEY_2 = os.environ.get('GEEK_API_KEY_2')
    GEEK_API_BASE = os.environ.get('GEEK_API_BASE')
    GEEK_MODEL_QWQ_PLUS = os.environ.get('GEEK_MODEL_QWQ_PLUS')
    
    # HTTP Proxy configuration (if needed)
    HTTP_PROXY = os.environ.get('HTTP_PROXY')
    
    # Tencent configurations
    TENCENT_API_KEY = os.environ.get('TENCENT_API_KEY')
    TENCENT_MODEL = os.environ.get('TENCENT_MODEL') 