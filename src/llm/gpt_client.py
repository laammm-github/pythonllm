from typing import Dict, Any, Optional, List
from loguru import logger
from .base_llm import BaseLLMClient

class GPTClient(BaseLLMClient):
    """
    OpenAI GPT客户端实现
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Optional[Dict[str, str]] = None):
        """
        初始化GPT客户端
        
        Args:
            config: LLM配置
            prompts: 提示词配置
        """
        super().__init__(config, prompts)
        
        # 导入OpenAI库
        try:
            from openai import OpenAI
        except ImportError:
            logger.error("OpenAI库未安装，请运行: pip install openai")
            raise
        
        # 初始化OpenAI客户端
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI GPT客户端初始化成功")
        except Exception as e:
            logger.error(f"OpenAI GPT客户端初始化失败: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        生成文本
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数
                temperature: 温度参数
                max_tokens: 最大令牌数
                top_p: 核采样参数
                frequency_penalty: 频率惩罚
                presence_penalty: 存在惩罚
            
        Returns:
            生成的文本，如果失败返回None
        """
        try:
            # 准备参数
            params = {
                "model": kwargs.get("model", self.model),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取结果
            result = response.choices[0].message.content.strip()
            logger.info(f"GPT生成成功，使用令牌数: {response.usage.total_tokens}")
            return result
        except Exception as e:
            logger.error(f"GPT生成失败: {e}")
            return None
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """
        聊天模式，支持多轮对话
        
        Args:
            messages: 消息列表，每个消息包含role和content字段
            **kwargs: 额外参数
            
        Returns:
            生成的文本，如果失败返回None
        """
        try:
            # 准备参数
            params = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取结果
            result = response.choices[0].message.content.strip()
            logger.info(f"GPT聊天成功，使用令牌数: {response.usage.total_tokens}")
            return result
        except Exception as e:
            logger.error(f"GPT聊天失败: {e}")
            return None

if __name__ == "__main__":
    # 测试GPT客户端
    from src.config.config_loader import ConfigLoader
    
    try:
        config = ConfigLoader()
        config.update("llm.provider", "gpt")
        
        client = GPTClient(config.get("llm"))
        
        # 测试生成文本
        logger.info("=== 测试文本生成 ===")
        prompt = "请介绍一下Python编程语言"
        result = client.generate(prompt)
        if result:
            logger.info(f"生成结果: {result[:200]}...")
        
        # 测试多轮对话
        logger.info("\n=== 测试多轮对话 ===")
        messages = [
            {"role": "system", "content": "你是一位友好的助手"},
            {"role": "user", "content": "你好，我想了解Python"},
            {"role": "assistant", "content": "Python是一种高级编程语言，以其简洁易读的语法而闻名。"},
            {"role": "user", "content": "Python适合做什么？"},
        ]
        result = client.chat(messages)
        if result:
            logger.info(f"聊天结果: {result[:200]}...")
            
    except Exception as e:
        logger.error(f"测试失败: {e}")