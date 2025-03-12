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
    
    def __init__(self):
        """Initialize the WeCom adapter with its crypto instance"""
        self.token = Config.WECOM_TOKEN
        self.encoding_aes_key = Config.WECOM_ENCODING_AES_KEY
        self.corp_id = Config.WECOM_CORP_ID
        self.agent_id = Config.WECOM_AGENT_ID
        self.crypto = WeChatCrypto(self.token, self.encoding_aes_key, self.corp_id)
    
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
                <Content><![CDATA[收到您的请求，正在处理中...]]></Content>
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
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = WeChatClient(
                self.corp_id,
                Config.WECOM_APP_SECRET
            )
            
            # Send the message
            client.message.send_text(
                agent_id=self.agent_id,
                user_ids=[user_id],
                content=message
            )
            return True
        except Exception as e:
            logger.error(f"Error sending WeCom message: {str(e)}")
            return False