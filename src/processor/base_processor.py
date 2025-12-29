from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from loguru import logger
from ..crawler.base_crawler import BaseCrawler
from ..llm.base_llm import BaseLLMClient

class BaseProcessor(ABC):
    """
    处理器基类，定义数据处理的统一接口
    """
    
    def __init__(self, crawler: BaseCrawler, llm_client: BaseLLMClient):
        """
        初始化处理器
        
        Args:
            crawler: 爬虫实例
            llm_client: LLM客户端实例
        """
        self.crawler = crawler
        self.llm_client = llm_client
        logger.info(f"初始化{self.__class__.__name__}处理器")
    
    @abstractmethod
    def process(self, url: str, **kwargs) -> Optional[Any]:
        """
        处理指定URL的内容
        
        Args:
            url: 目标URL
            **kwargs: 额外参数
            
        Returns:
            处理结果，如果失败返回None
        """
        pass
    
    def batch_process(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        批量处理多个URL
        
        Args:
            urls: URL列表
            **kwargs: 额外参数
                max_workers: 最大工作线程数（默认: 1，单线程）
            
        Returns:
            处理结果列表，每个结果包含url和result字段
        """
        results = []
        max_workers = kwargs.get("max_workers", 1)
        
        if max_workers > 1:
            # 使用多线程处理
            from concurrent.futures import ThreadPoolExecutor
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {executor.submit(self.process, url, **kwargs): url for url in urls}
                
                for future in future_to_url:
                    url = future_to_url[future]
                    try:
                        result = future.result()
                        results.append({"url": url, "result": result})
                    except Exception as e:
                        logger.error(f"批量处理{url}失败: {e}")
                        results.append({"url": url, "result": None, "error": str(e)})
        else:
            # 单线程处理
            for url in urls:
                try:
                    result = self.process(url, **kwargs)
                    results.append({"url": url, "result": result})
                except Exception as e:
                    logger.error(f"批量处理{url}失败: {e}")
                    results.append({"url": url, "result": None, "error": str(e)})
        
        logger.info(f"批量处理完成，共{len(urls)}个URL，成功{sum(1 for r in results if r['result'] is not None)}个")
        return results