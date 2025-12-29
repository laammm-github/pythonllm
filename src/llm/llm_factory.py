from typing import Dict, Any, Optional
from loguru import logger
from .base_llm import BaseLLMClient

class LLMFactory:
    """
    LLM客户端工厂类，用于创建不同类型的LLM客户端实例
    """
    
    @staticmethod
    def create_client(config: Dict[str, Any], prompts: Optional[Dict[str, str]] = None) -> BaseLLMClient:
        """
        创建LLM客户端实例
        
        Args:
            config: LLM配置
            prompts: 提示词配置
            
        Returns:
            BaseLLMClient实例
        """
        provider = config.get("provider", "gpt")
        
        if provider == "gpt":
            logger.info("创建GPT客户端实例")
            try:
                from .gpt_client import GPTClient
                return GPTClient(config, prompts)
            except ImportError:
                logger.error("OpenAI库未安装，请运行: pip install openai")
                raise
        elif provider == "doubao":
            logger.info("创建豆包客户端实例")
            try:
                from .doubao_client import DoubaoClient
                return DoubaoClient(config, prompts)
            except ImportError:
                logger.error("豆包库未安装，请参考豆包API文档安装相应SDK")
                raise
        elif provider == "qwen":
            logger.info("创建千问客户端实例")
            try:
                from .qwen_client import QwenClient
                return QwenClient(config, prompts)
            except ImportError:
                logger.error("千问库未安装，请参考千问API文档安装相应SDK")
                raise
        elif provider == "deepseek":
            logger.info("创建DeepSeek客户端实例")
            try:
                from .deepseek_client import DeepSeekClient
                return DeepSeekClient(config, prompts)
            except ImportError:
                logger.error("DeepSeek库未安装，请参考DeepSeek API文档安装相应SDK")
                raise
        elif provider == "hunyuan":
            logger.info("创建混元客户端实例")
            try:
                from .hunyuan_client import HunyuanClient
                return HunyuanClient(config, prompts)
            except ImportError:
                logger.error("混元库未安装，请参考混元API文档安装相应SDK")
                raise
        else:
            logger.error(f"不支持的LLM提供商: {provider}")
            raise ValueError(f"不支持的LLM提供商: {provider}")

if __name__ == "__main__":
    # 测试LLM工厂
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    
    # 测试创建GPT客户端
    logger.info("=== 测试GPT客户端 ===")
    try:
        config.update("llm.provider", "gpt")
        client = LLMFactory.create_client(config.get("llm"))
        
        # 测试文本生成
        result = client.generate("请简单介绍一下人工智能")
        if result:
            logger.info(f"生成结果: {result[:100]}...")
    except Exception as e:
        logger.error(f"GPT客户端测试失败: {e}")