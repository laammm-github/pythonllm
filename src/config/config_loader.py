import yaml
import os
from dotenv import load_dotenv
from loguru import logger
from typing import Dict, Any, Optional

class ConfigLoader:
    """
    配置加载器，负责读取和验证配置文件
    """
    
    def __init__(self, config_path: str = "src/config/config.yaml", prompts_path: str = "src/config/prompts.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
            prompts_path: 提示词配置文件路径
        """
        self.config_path = config_path
        self.prompts_path = prompts_path
        self.config: Dict[str, Any] = {}
        self.prompts: Dict[str, str] = {}
        # LLM默认配置映射
        self.llm_defaults = {
            "gpt": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "doubao": {
                "model": "ERNIE-Bot-4",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "qwen": {
                "model": "qwen-turbo",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "deepseek": {
                "model": "deepseek-chat",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "hunyuan": {
                "model": "hunyuan-pro",
                "temperature": 0.1,
                "max_tokens": 2000
            }
        }
        self._load_env()
        self._load_config()
        self._load_prompts()
    
    def _load_env(self):
        """
        加载环境变量文件
        """
        try:
            # 尝试加载.env文件，如果存在
            if os.path.exists(".env"):
                load_dotenv()
                logger.info("成功加载.env文件")
            else:
                logger.warning(".env文件不存在，使用系统环境变量")
        except Exception as e:
            logger.error(f"加载环境变量失败: {e}")
    
    def _load_config(self):
        """
        加载YAML配置文件
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            logger.info(f"成功加载配置文件: {self.config_path}")
            self._validate_config()
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _load_prompts(self):
        """
        加载提示词配置文件
        """
        try:
            with open(self.prompts_path, "r", encoding="utf-8") as f:
                self.prompts = yaml.safe_load(f)
            logger.info(f"成功加载提示词配置文件: {self.prompts_path}")
        except FileNotFoundError:
            logger.warning(f"提示词配置文件不存在: {self.prompts_path}")
            self.prompts = {}
        except yaml.YAMLError as e:
            logger.error(f"解析提示词配置文件失败: {e}")
            self.prompts = {}
        except Exception as e:
            logger.error(f"加载提示词配置文件失败: {e}")
            self.prompts = {}
    
    def _validate_config(self):
        """
        验证配置文件的完整性和正确性
        """
        required_sections = ["llm", "crawler", "websites", "output", "logging"]
        
        for section in required_sections:
            if section not in self.config:
                logger.error(f"配置文件缺少必要部分: {section}")
                raise ValueError(f"配置文件缺少必要部分: {section}")
        
        # 验证LLM配置
        llm_config = self.config["llm"]
        if "provider" not in llm_config:
            logger.error("LLM配置缺少provider字段")
            raise ValueError("LLM配置缺少provider字段")
        
        # 应用默认配置
        provider = llm_config["provider"]
        if provider in self.llm_defaults:
            # 合并默认配置和用户配置，用户配置优先级更高
            for key, default_value in self.llm_defaults[provider].items():
                if key not in llm_config:
                    llm_config[key] = default_value
                    logger.debug(f"应用默认配置: {key} = {default_value}")
        
        # 根据provider加载对应API密钥
        if provider == "gpt":
            api_key = os.getenv("OPENAI_API_KEY", llm_config.get("api_key"))
        elif provider == "doubao":
            api_key = os.getenv("DOUBAO_API_KEY", llm_config.get("api_key"))
        elif provider == "qwen":
            api_key = os.getenv("QWEN_API_KEY", llm_config.get("api_key"))
        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY", llm_config.get("api_key"))
        elif provider == "hunyuan":
            api_key = os.getenv("HUNYUAN_API_KEY", llm_config.get("api_key"))
        else:
            api_key = llm_config.get("api_key")
        
        if not api_key:
            logger.error(f"{provider}的API密钥未配置")
            raise ValueError(f"{provider}的API密钥未配置")
        
        self.config["llm"]["api_key"] = api_key
        logger.info(f"成功加载{provider}的API配置")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，可以使用点号分隔多层键 (如 "llm.provider")
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def update(self, key: str, value: Any):
        """
        更新配置值
        
        Args:
            key: 配置键，可以使用点号分隔多层键
            value: 新的配置值
        """
        keys = key.split(".")
        config_dict = self.config
        
        for k in keys[:-1]:
            if k not in config_dict:
                config_dict[k] = {}
            config_dict = config_dict[k]
        
        config_dict[keys[-1]] = value
        logger.info(f"更新配置: {key} = {value}")
    
    def get_prompt(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取提示词配置
        
        Args:
            key: 提示词键名
            default: 默认值
            
        Returns:
            提示词字符串或默认值
        """
        return self.prompts.get(key, default)

if __name__ == "__main__":
    # 测试配置加载
    try:
        config = ConfigLoader()
        logger.info(f"LLM提供商: {config.get('llm.provider')}")
        logger.info(f"爬虫驱动: {config.get('crawler.driver')}")
        logger.info(f"支持的网站: {list(config.get('websites').keys())}")
    except Exception as e:
        logger.error(f"测试配置加载失败: {e}")