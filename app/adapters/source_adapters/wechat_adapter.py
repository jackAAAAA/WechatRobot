import xml.etree.ElementTree as ET
import time
import hashlib
import logging
from typing import Dict, Any
from flask import Request, Response, make_response

from app.adapters.source_adapters.base_adapter import BaseSourceAdapter
from app.config.config import Config
from app.utils.celery_utils import celery

logger = logging.getLogger(__name__)

class WechatAdapter(BaseSourceAdapter):
    """Adapter for handling WeChat Official Account requests"""
    
    def verify(self, request: Request) -> Response:
        """Handle WeChat signature verification (GET requests)
        
        Args:
            request: The Flask request object
            
        Returns:
            The verification response
        """
        try:
            signature = request.args.get('signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            echostr = request.args.get('echostr', '')
            
            # Sort token, timestamp, and nonce lexicographically
            token = Config.WECHAT_TOKEN
            temp_list = [token, timestamp, nonce]
            temp_list.sort()
            
            # Join the list into a string and hash it
            temp_str = ''.join(temp_list)
            hashcode = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
            
            # Verify the signature
            if hashcode == signature:
                return echostr
            else:
                logger.warning("WeChat signature verification failed")
                return make_response("Verification failed", 403)
        except Exception as e:
            logger.error(f"WeChat verification error: {str(e)}")
            return make_response("Verification error", 500)
    
    def extract_params(self, request: Request) -> Dict[str, Any]:
        """Extract parameters from WeChat request
        
        Args:
            request: The Flask request object
            
        Returns:
            Dictionary of extracted parameters
        """
        xml_data = request.data
        root = ET.fromstring(xml_data)
        
        params = {
            'msg_type': root.find('MsgType').text,
            'from_user': root.find('FromUserName').text,
            'to_user': root.find('ToUserName').text,
            'create_time': int(root.find('CreateTime').text)
        }
        
        # Handle different message types
        if params['msg_type'] == 'text':
            params['content'] = root.find('Content').text
        elif params['msg_type'] == 'image':
            params['pic_url'] = root.find('PicUrl').text
            params['media_id'] = root.find('MediaId').text
        elif params['msg_type'] == 'event':
            params['event'] = root.find('Event').text
            
        logger.info(f"Extracted WeChat parameters: {params}")
        return params
    
    def format_response(self, result: Dict[str, Any], params: Dict[str, Any]) -> Response:
        """Format the response for WeChat"""
        if result.get('async', False):
            # For async responses, return an immediate reply and process in background
            initial_response = self._build_text_response(
                params['to_user'], 
                params['from_user'], 
                "正在思考，请稍候..."
            )
            
            return make_response(initial_response)
        else:
            # For synchronous responses, return the result directly
            response_text = result.get('content', 'No response from AI provider')
            xml_response = self._build_text_response(
                params['to_user'], 
                params['from_user'], 
                response_text
            )
            return make_response(xml_response)
    
    def _build_text_response(self, from_user: str, to_user: str, content: str) -> str:
        """Build a text response in WeChat XML format
        
        Args:
            from_user: The official account ID
            to_user: The user ID
            content: The message content
            
        Returns:
            XML string in WeChat format
        """
        # 立即返回文本
#         return f"""
# <xml>
#     <ToUserName><![CDATA[{to_user}]]></ToUserName>
#     <FromUserName><![CDATA[{from_user}]]></FromUserName>
#     <CreateTime>{int(time.time())}</CreateTime>
#     <MsgType><![CDATA[text]]></MsgType>
#     <Content><![CDATA[{content}]]></Content>
# </xml>"""
        # 立即返回图片
        return f"""
<xml>
    <ToUserName><![CDATA[{to_user}]]></ToUserName>
    <FromUserName><![CDATA[{from_user}]]></FromUserName>
    <CreateTime>{int(time.time())}</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <Image>
        <MediaId><![CDATA[kaMSmt1j23Az0YO9YonIwAxlsBmITjQUf_7ggkVu4E3rpxhJqXjBhefOBho46nIJ]]></MediaId>
    </Image>
</xml>"""
    
    def send_message(self, user_id: str, message: str, model: str = "Unknown") -> bool:
        """Send a message to a WeChat user
        
        Args:
            user_id: The WeChat user ID
            message: The message content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from wechatpy import WeChatClient
            client = WeChatClient(Config.WECHAT_APP_ID, Config.WECHAT_APP_SECRET)
            # 分段发送
            for index, chunk in enumerate(self.split_content(message, 2000)):
                client.message.send_text(
                    user_id,
                    f"{model}（{index+1}）: {chunk}"
                )
                time.sleep(1)  # 避免发送频率过高
            # 测试发送图片
            client.message.send_image(user_id, "kaMSmt1j23Az0YO9YonIwAxlsBmITjQUf_7ggkVu4E3rpxhJqXjBhefOBho46nIJ")
            # 测试发送图文
            articles = [{
                "title": "标题（可选）",
                "description": "描述（可选）",
                "url": "https://example.com",  # 用户点击后跳转的链接
                "image": "https://static.geekai.co/image/2025/03/28/ac761527b9215fa167be41a4559bcb0b.png"  # 图片网络URL
            }]
            client.message.send_articles(user_id, articles)
            return True
        except Exception as e:
            logger.error(f"Error sending WeChat message: {str(e)}")
            return False