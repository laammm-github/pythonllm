from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger
import time

class BaseCrawler(ABC):
    """
    爬虫基类，定义爬虫的基本接口
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化爬虫
        
        Args:
            config: 爬虫配置
        """
        self.config = config
        self.timeout = config.get("timeout", 30)
        self.retry_times = config.get("retry_times", 3)
        self.retry_delay = config.get("retry_delay", 5)
    
    @abstractmethod
    def fetch(self, url: str, **kwargs) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            **kwargs: 额外参数
            
        Returns:
            网页内容字符串，如果失败返回None
        """
        pass
    
    def _retry_request(self, func, *args, **kwargs) -> Optional[str]:
        """
        重试请求机制
        
        Args:
            func: 要执行的请求函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            请求结果，如果所有重试都失败返回None
        """
        for i in range(self.retry_times):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"请求失败 (尝试 {i+1}/{self.retry_times}): {e}")
                if i < self.retry_times - 1:
                    logger.info(f"等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"所有重试都失败: {e}")
        return None
    
    @abstractmethod
    def close(self):
        """
        关闭爬虫资源
        """
        pass