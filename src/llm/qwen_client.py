#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
千问(Qwen) LLM客户端实现

使用通义千问API进行文本生成和对话
"""

import os
from typing import Dict, Any, Optional, List
from loguru import logger
from .base_llm import BaseLLMClient

class QwenClient(BaseLLMClient):
    """
    千问(Qwen) LLM客户端实现类
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Optional[Dict[str, str]] = None):
        """
        初始化千问客户端
        
        Args:
            config: 配置字典，包含以下键:
                - api_key: 千问API密钥 (可选，若未提供则从环境变量QWEN_API_KEY读取)
                - model: 使用的模型名称 (默认: qwen-turbo)
                - temperature: 生成文本的随机性 (默认: 0.1)
                - max_tokens: 生成文本的最大长度 (默认: 1000)
            prompts: 提示词配置
        """
        super().__init__(config, prompts)
        
        # 获取API密钥
        api_key = config.get("api_key", os.environ.get("QWEN_API_KEY"))
        if not api_key:
            logger.error("千问API密钥未提供")
            raise ValueError("千问API密钥未提供")
        
        # 初始化阿里云DashScope客户端
        try:
            import dashscope
            dashscope.api_key = api_key
            self.dashscope = dashscope
        except ImportError:
            logger.error("dashscope库未安装，请运行: pip install dashscope")
            raise
        except Exception as e:
            logger.error(f"初始化千问客户端失败: {e}")
            raise
        
        # 设置模型参数
        self.model = config.get("model", "qwen-turbo")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2000)
        
        logger.info(f"千问客户端已初始化，模型: {self.model}")
    
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
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens)
            }
            
            # 调用API
            response = self.dashscope.Generation.call(**params)
            
            # 打印完整响应信息
            logger.debug(f"千问API完整响应: {response}")
            
            # 提取生成的文本
            if response.status_code == 200:
                # 处理不同版本的响应格式
                if hasattr(response, 'output'):
                    # 优先检查旧版格式 (output.text)
                    if hasattr(response.output, 'text'):
                        return response.output.text.strip()
                    # 检查新版格式 (output.choices)
                    elif hasattr(response.output, 'choices') and response.output.choices:
                        if hasattr(response.output.choices[0], 'message') and hasattr(response.output.choices[0].message, 'content'):
                            return response.output.choices[0].message.content.strip()
                    # 检查其他可能的格式
                    elif hasattr(response.output, 'result'):
                        return response.output.result.strip()
                
                # 尝试直接从response中提取
                if hasattr(response, 'result'):
                    return response.result.strip()
                    
                logger.warning(f"千问API返回200但无有效内容: {response}")
                return None
            else:
                logger.warning(f"千问API返回错误: {response.status_code} - {getattr(response, 'message', '未知错误')}")
                return None
                
        except Exception as e:
            logger.error(f"千问API调用失败: {e}")
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
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens)
            }
            
            # 调用API
            response = self.dashscope.Generation.call(**params)
            
            # 打印完整响应信息
            logger.debug(f"千问API完整响应: {response}")
            
            # 提取生成的文本
            if response.status_code == 200:
                if hasattr(response, 'output') and hasattr(response.output, 'text'):
                    # 旧版API格式
                    return response.output.text.strip()
                elif hasattr(response, 'output') and hasattr(response.output, 'choices') and response.output.choices:
                    # 新版API格式
                    return response.output.choices[0].message.content.strip()
                else:
                    logger.warning(f"千问API返回200但无有效内容: {response}")
                    return None
            else:
                logger.warning(f"千问API返回错误: {response.status_code} - {getattr(response, 'message', '未知错误')}")
                return None
                
        except Exception as e:
            logger.error(f"千问API调用失败: {e}")
            return None

if __name__ == "__main__":
    # 测试千问客户端
    import sys
    import os
    
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    config.update("llm.provider", "qwen")
    
    client = QwenClient(config.get("llm"))
    
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