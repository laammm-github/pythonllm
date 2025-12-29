#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DeepSeek LLM客户端实现

使用DeepSeek API进行文本生成和对话
"""

import os
from typing import Dict, Any, Optional, List
from openai import OpenAI
from loguru import logger
from .base_llm import BaseLLMClient

class DeepSeekClient(BaseLLMClient):
    """
    DeepSeek LLM客户端实现类
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Optional[Dict[str, str]] = None):
        """
        初始化DeepSeek客户端
        
        Args:
            config: 配置字典，包含以下键:
                - api_key: DeepSeek API密钥 (可选，若未提供则从环境变量DEEPSEEK_API_KEY读取)
                - model: 使用的模型名称 (默认: deepseek-chat)
                - temperature: 生成文本的随机性 (默认: 0.1)
                - max_tokens: 生成文本的最大长度 (默认: 1000)
            prompts: 提示词配置
        """
        super().__init__(config, prompts)
        
        # 获取API密钥
        api_key = config.get("api_key", os.environ.get("DEEPSEEK_API_KEY"))
        if not api_key:
            logger.error("DeepSeek API密钥未提供")
            raise ValueError("DeepSeek API密钥未提供")
        
        # 初始化OpenAI客户端（DeepSeek兼容OpenAI API）
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # 设置模型参数
        self.model = config.get("model", "deepseek-chat")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2000)
        
        logger.info(f"DeepSeek客户端已初始化，模型: {self.model}")
    
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
            # 合并默认参数和额外参数
            params = {
                "model": kwargs.get("model", self.model),
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取生成的文本
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                logger.warning("DeepSeek API返回空结果")
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
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
            # 合并默认参数和额外参数
            params = {
                "model": kwargs.get("model", self.model),
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": messages
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取生成的文本
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                logger.warning("DeepSeek API返回空结果")
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return None

if __name__ == "__main__":
    # 测试DeepSeek客户端
    import sys
    import os
    
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    config.update("llm.provider", "deepseek")
    
    client = DeepSeekClient(config.get("llm"))
    
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