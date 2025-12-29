#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
混元(Hunyuan) LLM客户端实现

使用腾讯混元API进行文本生成和对话
"""

import os
from typing import Dict, Any, Optional, List
from loguru import logger
from .base_llm import BaseLLMClient

class HunyuanClient(BaseLLMClient):
    """
    混元(Hunyuan) LLM客户端实现类
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Optional[Dict[str, str]] = None):
        """
        初始化混元客户端
        
        Args:
            config: 配置字典，包含以下键:
                - secret_id: 腾讯云SecretId (可选，若未提供则从环境变量HUNYUAN_SECRET_ID读取)
                - secret_key: 腾讯云SecretKey (可选，若未提供则从环境变量HUNYUAN_API_KEY读取)
                - model: 使用的模型名称 (默认: hunyuan-chat)
                - temperature: 生成文本的随机性 (默认: 0.1)
                - max_tokens: 生成文本的最大长度 (默认: 1000)
            prompts: 提示词配置
        """
        super().__init__(config, prompts)
        
        # 获取API密钥
        secret_id = config.get("secret_id", os.environ.get("HUNYUAN_SECRET_ID"))
        secret_key = config.get("secret_key", os.environ.get("HUNYUAN_API_KEY"))
        
        if not secret_key:
            logger.error("混元API密钥未提供")
            raise ValueError("混元API密钥未提供")
        
        # 初始化腾讯云API客户端
        try:
            from tencentcloud.common import credential
            from tencentcloud.hunyuan.v20230901 import hunyuan_client
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.common.profile.client_profile import ClientProfile
            
            # 如果没有提供secret_id，尝试使用默认值
            if not secret_id:
                secret_id = "default_secret_id"
                logger.warning("未提供SecretId，使用默认值，可能会导致API调用失败")
            
            cred = credential.Credential(secret_id, secret_key)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            self.client = hunyuan_client.HunyuanClient(cred, "", clientProfile)
        except ImportError:
            logger.error("腾讯云SDK未安装，请运行: pip install tencentcloud-sdk-python")
            raise
        except Exception as e:
            logger.error(f"初始化混元客户端失败: {e}")
            raise
        
        # 设置模型参数
        self.model = config.get("model", "hunyuan-chat")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2000)
        
        logger.info(f"混元客户端已初始化，模型: {self.model}")
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        生成文本
        
        Args:
            prompt: 生成文本的提示词
            **kwargs: 额外参数，如temperature, max_tokens等
            
        Returns:
            生成的文本，失败则返回None
        """
        try:
            # 调用API
            from tencentcloud.hunyuan.v20230901 import models
            req = models.ChatCompletionsRequest()
            req.Model = kwargs.get("model", self.model)
            req.Messages = [{"Role": "user", "Content": prompt}]
            req.Temperature = kwargs.get("temperature", self.temperature)
            # 移除MaxTokens参数
            response = self.client.ChatCompletions(req)
            
            # 提取生成的文本
            if response and response.Choices:
                return response.Choices[0].Message.Content.strip()
            else:
                logger.warning("混元API返回空结果")
                return None
                
        except Exception as e:
            logger.error(f"混元API调用失败: {e}")
            return None
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """
        多轮对话
        
        Args:
            messages: 对话历史，每个元素是包含role和content的字典
            **kwargs: 额外参数，如temperature, max_tokens等
            
        Returns:
            生成的文本，失败则返回None
        """
        try:
            # 调用API
            from tencentcloud.hunyuan.v20230901 import models
            req = models.ChatCompletionsRequest()
            req.Model = kwargs.get("model", self.model)
            req.Messages = messages
            req.Temperature = kwargs.get("temperature", self.temperature)
            # 移除MaxTokens参数
            response = self.client.ChatCompletions(req)
            
            # 提取生成的文本
            if response and response.Choices:
                return response.Choices[0].Message.Content.strip()
            else:
                logger.warning("混元API返回空结果")
                return None
                
        except Exception as e:
            logger.error(f"混元API调用失败: {e}")
            return None

if __name__ == "__main__":
    # 测试混元客户端
    import sys
    import os
    
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    config.update("llm.provider", "hunyuan")
    
    client = HunyuanClient(config.get("llm"))
    
    # 测试文本生成
    logger.info("=== 测试文本生成 ===")
    prompt = "请简单介绍一下人工智能"
    result = client.generate(prompt)
    if result:
        logger.info(f"生成结果: {result}")
    else:
        logger.error("文本生成失败")
    
    # 测试多轮对话
    logger.info("\n=== 测试多轮对话 ===")
    messages = [
        {"role": "user", "content": "你好，我想了解一下Python"},
        {"role": "assistant", "content": "Python是一种高级编程语言，以其简洁性和易读性而闻名。它支持多种编程范式，包括面向对象、命令式和函数式编程。Python广泛应用于Web开发、数据科学、人工智能等领域。"},
        {"role": "user", "content": "Python有哪些主要的Web框架？"}
    ]
    result = client.chat(messages)
    if result:
        logger.info(f"对话结果: {result}")
    else:
        logger.error("多轮对话失败")