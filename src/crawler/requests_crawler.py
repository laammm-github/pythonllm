import requests
from typing import Dict, Any, Optional
from loguru import logger
from .base_crawler import BaseCrawler
from fake_useragent import UserAgent

class RequestsCrawler(BaseCrawler):
    """
    基于Requests库的爬虫实现
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Requests爬虫
        
        Args:
            config: 爬虫配置
        """
        super().__init__(config)
        
        # 创建会话对象
        self.session = requests.Session()
        
        # 设置默认请求头
        self.headers = {
            "User-Agent": config.get("browser", {}).get("user_agent", UserAgent().random),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        
        # 设置代理（如果有）
        proxy_url = config.get("proxy_url")
        if proxy_url:
            self.proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }
            logger.info(f"设置代理: {proxy_url}")
        else:
            self.proxies = None
        
        # 设置超时
        self.session.timeout = self.timeout
    
    def fetch(self, url: str, **kwargs) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            **kwargs: 额外参数
                headers: 自定义请求头
                proxies: 自定义代理
                params: URL参数
                data: POST数据
                cookies: Cookie字典
            
        Returns:
            网页内容字符串，如果失败返回None
        """
        def _request():
            # 合并请求头
            headers = {**self.headers, **kwargs.get("headers", {})}
            
            # 合并代理
            proxies = kwargs.get("proxies", self.proxies)
            
            # 发送请求
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxies,
                params=kwargs.get("params"),
                data=kwargs.get("data"),
                cookies=kwargs.get("cookies"),
                allow_redirects=True,
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 根据内容类型设置编码
            if "charset" in response.headers.get("Content-Type", ""):
                response.encoding = response.apparent_encoding
            else:
                response.encoding = "utf-8"
            
            logger.info(f"成功获取 {url}，状态码: {response.status_code}")
            return response.text
        
        return self._retry_request(_request)
    
    def fetch_json(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        获取JSON格式的响应
        
        Args:
            url: 目标URL
            **kwargs: 额外参数
                headers: 自定义请求头
                proxies: 自定义代理
                params: URL参数
                data: POST数据
                cookies: Cookie字典
            
        Returns:
            JSON数据字典，如果失败返回None
        """
        def _request():
            # 合并请求头
            headers = {**self.headers, **kwargs.get("headers", {})}
            headers["Accept"] = "application/json, text/plain, */*"
            
            # 合并代理
            proxies = kwargs.get("proxies", self.proxies)
            
            # 发送请求
            response = self.session.get(
                url,
                headers=headers,
                proxies=proxies,
                params=kwargs.get("params"),
                data=kwargs.get("data"),
                cookies=kwargs.get("cookies"),
                allow_redirects=True,
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            logger.info(f"成功获取JSON数据 {url}，状态码: {response.status_code}")
            return response.json()
        
        return self._retry_request(_request)
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()
        logger.info("Requests爬虫会话已关闭")

if __name__ == "__main__":
    # 测试爬虫
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    crawler = RequestsCrawler(config.get("crawler"))
    
    try:
        # 测试抓取拉勾网首页
        html = crawler.fetch("https://www.lagou.com")
        if html:
            logger.info(f"成功获取拉勾网首页，内容长度: {len(html)} 字符")
            logger.info(f"页面标题: {html[:100]}...")
    finally:
        crawler.close()