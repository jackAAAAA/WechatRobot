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

    # WeCom: Default app_secret and agent_id
    WECOM_APP_SECRET_DEFAULT=os.environ.get('WECOM_APP_SECRET_DEFAULT')
    WECOM_AGENT_ID_DEFAULT=os.environ.get('WECOM_AGENT_ID_DEFAULT')

    # WeCom: Groq/deepseek-r1-distill-llama-70b
    WECOM_APP_SECRET_GROQ_DEEPSEEK_R1_DISTILL_LLAMA_70B=os.environ.get('WECOM_APP_SECRET_GROQ_DEEPSEEK_R1_DISTILL_LLAMA_70B')
    WECOM_AGENT_ID_GROQ_DEEPSEEK_R1_DISTILL_LLAMA_70B=os.environ.get('WECOM_AGENT_ID_GROQ_DEEPSEEK_R1_DISTILL_LLAMA_70B')

    # WeCom: 通义千问/QWQ-Plus
    WECOM_APP_SECRET_TONGYIQIANWEN_QWQ_PLUS=os.environ.get('WECOM_APP_SECRET_TONGYIQIANWEN_QWQ_PLUS')
    WECOM_AGENT_ID_TONGYIQIANWEN_QWQ_PLUS=os.environ.get('WECOM_AGENT_ID_TONGYIQIANWEN_QWQ_PLUS')

    # WeCom: DeepSeek/deepseek-chat
    WECOM_APP_SECRET_DEEPSEEK_DS_V3=os.environ.get('WECOM_APP_SECRET_DEEPSEEK_DS_V3')
    WECOM_AGENT_ID_DEEPSEEK_DS_V3=os.environ.get('WECOM_AGENT_ID_DEEPSEEK_DS_V3')
    
    # WeCom: Tencent/deepseek-r1-671b
    WECOM_APP_SECRET_TENCENT_DS_R1_671B=os.environ.get('WECOM_APP_SECRET_TENCENT_DS_R1_671B')
    WECOM_AGENT_ID_TENCENT_DS_R1_671B=os.environ.get('WECOM_AGENT_ID_TENCENT_DS_R1_671B')

    # WeCom: GeekAI/gemma-3-27b-it:free
    WECOM_APP_SECRET_GEEKAI_GEMMA_3_27B_IT_FREE=os.environ.get('WECOM_APP_SECRET_GEEKAI_GEMMA_3_27B_IT_FREE')
    WECOM_AGENT_ID_GEEKAI_GEMMA_3_27B_IT_FREE=os.environ.get('WECOM_AGENT_ID_GEEKAI_GEMMA_3_27B_IT_FREE')

    # WeCom: GeekAI/mistral-small:free
    WECOM_APP_SECRET_GEEKAI_MISTRAL_SMALL_FREE=os.environ.get('WECOM_APP_SECRET_GEEKAI_MISTRAL_SMALL_FREE')
    WECOM_AGENT_ID_GEEKAI_MISTRAL_SMALL_FREE=os.environ.get('WECOM_AGENT_ID_GEEKAI_MISTRAL_SMALL_FREE')

    # AI API configuration
    # DeepSeek configurations
    DEEPSEEK_API_BASE = os.environ.get('DEEPSEEK_API_BASE')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_DS_V3 = os.environ.get('DEEPSEEK_DS_V3')
    # Groq configurations
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GROQ_DS_R1_70B_MODEL = os.environ.get('GROQ_DS_R1_70B_MODEL')
    # Geek configuration
    GEEK_API_KEY = os.environ.get('GEEK_API_KEY')
    GEEK_API_KEY_2 = os.environ.get('GEEK_API_KEY_2')
    GEEK_API_BASE = os.environ.get('GEEK_API_BASE')
    GEEK_MODEL_QWQ_PLUS = os.environ.get('GEEK_MODEL_QWQ_PLUS')
    GEEK_MODEL_GEMMA_27B = os.environ.get('GEEK_MODEL_GEMMA_27B')
    # Tencent configurations
    TENCENT_API_BASE = os.environ.get('TENCENT_API_BASE')
    TENCENT_API_KEY = os.environ.get('TENCENT_API_KEY')
    TENCENT_MODEL_DEEPSEEK_R1_671B = os.environ.get('TENCENT_MODEL_DEEPSEEK_R1_671B')
    
    # HTTP Proxy configuration (if needed)
    HTTP_PROXY = os.environ.get('HTTP_PROXY')
    
    # Tencent configurations
    TENCENT_API_KEY = os.environ.get('TENCENT_API_KEY')
    TENCENT_MODEL = os.environ.get('TENCENT_MODEL') 