import logging
import time
from typing import Dict, Any
from flask import Request, Response, make_response

from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.enterprise import parse_message, WeChatClient

from app.adapters.source_adapters.base_adapter import BaseSourceAdapter
from app.config.config import Config
from app.utils.celery_utils import celery

logger = logging.getLogger(__name__)

class WecomAdapter(BaseSourceAdapter):
    """Adapter for handling WeCom (Enterprise WeChat) requests"""
    
    def __init__(self, provider=None, model=None):
        """Initialize the WeCom adapter with its crypto instance
        
        Args:
            provider: The AI provider name (e.g., 'Groq', 'Tongyiqianwen')
            model: The model name (e.g., 'deepseek-r1-distill-llama-70b', 'QWQ-Plus')
        """
        self.token = Config.WECOM_TOKEN
        self.encoding_aes_key = Config.WECOM_ENCODING_AES_KEY
        self.corp_id = Config.WECOM_CORP_ID
        
        # Set default agent_id and app_secret
        self.app_secret = Config.WECOM_APP_SECRET_DEFAULT
        self.agent_id = Config.WECOM_AGENT_ID_DEFAULT
        
        # If provider and model are specified, try to get the corresponding credentials
        if provider and model:
            # Create a key for environment variable lookup
            # Replace special characters that might not be valid in env var names
            env_key = f"{provider}_{model}".upper().replace("-", "_").replace(".", "_").replace("－", "_")
            
            # Try to get app_secret for this provider/model combination
            app_secret_var = f"WECOM_APP_SECRET_{env_key}"
            agent_id_var = f"WECOM_AGENT_ID_{env_key}"
            
            if hasattr(Config, app_secret_var) and getattr(Config, app_secret_var):
                self.app_secret = getattr(Config, app_secret_var)
                logger.info(f"Using custom app_secret for {provider}/{model}")
            
            if hasattr(Config, agent_id_var) and getattr(Config, agent_id_var):
                self.agent_id = getattr(Config, agent_id_var)
                logger.info(f"Using custom agent_id for {provider}/{model}")
        
        # Initialize crypto
        self.crypto = WeChatCrypto(self.token, self.encoding_aes_key, self.corp_id)
        
        # Save the provider and model for reference
        self.provider = provider
        self.model = model
    
    def verify(self, request: Request) -> Response:
        """Handle WeCom verification (GET requests)
        
        Args:
            request: The Flask request object
            
        Returns:
            The verification response
        """
        try:
            msg_signature = request.args.get('msg_signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            echostr = request.args.get('echostr', '')
            
            # Decrypt the echostr to verify the request
            decrypted_echostr = self.crypto.check_signature(
                msg_signature,
                timestamp,
                nonce,
                echostr
            )

            return decrypted_echostr
        except Exception as e:
            logger.error(f"WeCom verification error: {str(e)}")
            return make_response("Verification error", 500)
    
    def extract_params(self, request: Request) -> Dict[str, Any]:
        """Extract parameters from WeCom request
        
        Args:
            request: The Flask request object
            
        Returns:
            Dictionary of extracted parameters
        """
        try:
            # Get request parameters
            msg_signature = request.args.get('msg_signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            
            # Decrypt the XML
            encrypted_xml = request.data
            decrypted_xml = self.crypto.decrypt_message(
                encrypted_xml,
                msg_signature,
                timestamp,
                nonce
            )
            
            # Parse the XML to get message object
            msg = parse_message(decrypted_xml)
            
            # Extract parameters based on message type
            params = {
                'msg_type': msg.type,
                'from_user': msg.source,
                'to_user': msg.target,
                'create_time': msg.create_time,
            }
            
            # Handle different message types
            if msg.type == 'text':
                params['content'] = msg.content
            elif msg.type == 'image':
                params['media_id'] = msg.media_id
            elif msg.type == 'event':
                params['event'] = msg.event
                params['event_key'] = getattr(msg, 'key', '')
            
            logger.info(f"Extracted WeCom parameters: {params}")
            return params
            
        except Exception as e:
            logger.error(f"Error extracting WeCom parameters: {str(e)}")
            # Return empty params if error occurred
            return {'error': str(e)}
    
    def format_response(self, result: Dict[str, Any], params: Dict[str, Any]) -> Response:
        """Format the response for WeCom
        
        Args:
            result: The result from the AI provider
            params: The original request parameters
            
        Returns:
            XML response for WeCom
        """
        try:
            # For WeCom, we always respond immediately with a simple message
            # and then process the AI response asynchronously
            reply_xml = f"""<xml>
                <ToUserName><![CDATA[{params['from_user']}]]></ToUserName>
                <FromUserName><![CDATA[{params['to_user']}]]></FromUserName>
                <CreateTime>{int(time.time())}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[正在思考，请稍候...]]></Content>
            </xml>"""
            
            # Encrypt the response
            encrypted_xml = self.crypto.encrypt_message(
                reply_xml,
                nonce=params.get('nonce', str(int(time.time()))),
                timestamp=str(int(time.time()))
            )
            
            return make_response(encrypted_xml)
            
        except Exception as e:
            logger.error(f"Error formatting WeCom response: {str(e)}")
            return make_response("Error processing request", 500)
    
    def send_message(self, user_id: str, message: str, model: str = "Unknown") -> bool:
        """Send a message to a WeCom user
        
        Args:
            user_id: The WeCom user ID
            message: The message content
            model: The model name used for the message prefix
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = WeChatClient(
                self.corp_id,
                self.app_secret  # Using the instance-specific app_secret
            )
            # 分段发送
            for index, chunk in enumerate(self.split_content(message, 2000)):
                client.message.send_text(
                    agent_id=self.agent_id,  # Using the instance-specific agent_id
                    user_ids=[user_id],  # Wrap user_id in a list
                    content=f"{model}（{index+1}）: {chunk}"
                )
                time.sleep(1)  # 避免发送频率过高
            return True
        except Exception as e:
            logger.error(f"Error sending WeCom message: {str(e)}")
            return False