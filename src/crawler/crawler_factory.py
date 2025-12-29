from typing import Dict, Any, Optional
from loguru import logger
from .base_crawler import BaseCrawler
from .requests_crawler import RequestsCrawler
from .selenium_crawler import SeleniumCrawler

class CrawlerFactory:
    """
    爬虫工厂类，用于创建不同类型的爬虫实例
    """
    
    @staticmethod
    def create_crawler(config: Dict[str, Any]) -> BaseCrawler:
        """
        创建爬虫实例
        
        Args:
            config: 爬虫配置
            
        Returns:
            BaseCrawler实例
        """
        driver_type = config.get("driver", "requests")
        
        if driver_type == "requests":
            logger.info("创建Requests爬虫实例")
            return RequestsCrawler(config)
        elif driver_type == "selenium":
            logger.info("创建Selenium爬虫实例")
            return SeleniumCrawler(config)
        elif driver_type == "playwright":
            # 注意：Playwright实现需要额外安装依赖
            logger.info("创建Playwright爬虫实例")
            try:
                from .playwright_crawler import PlaywrightCrawler
                return PlaywrightCrawler(config)
            except ImportError:
                logger.error("Playwright模块未安装，请运行: pip install playwright && playwright install")
                raise
        else:
            logger.error(f"不支持的爬虫驱动类型: {driver_type}")
            raise ValueError(f"不支持的爬虫驱动类型: {driver_type}")

if __name__ == "__main__":
    # 测试爬虫工厂
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    
    # 测试创建Requests爬虫
    logger.info("=== 测试Requests爬虫 ===")
    try:
        config.update("crawler.driver", "requests")
        crawler = CrawlerFactory.create_crawler(config.get("crawler"))
        html = crawler.fetch("https://www.baidu.com")
        if html:
            logger.info(f"Requests爬虫成功获取页面内容")
        crawler.close()
    except Exception as e:
        logger.error(f"Requests爬虫测试失败: {e}")
    
    # 测试创建Selenium爬虫（可选，需要Chrome浏览器）
    logger.info("\n=== 测试Selenium爬虫 ===")
    try:
        config.update("crawler.driver", "selenium")
        crawler = CrawlerFactory.create_crawler(config.get("crawler"))
        html = crawler.fetch("https://www.baidu.com", wait_seconds=1)
        if html:
            logger.info(f"Selenium爬虫成功获取页面内容")
        crawler.close()
    except Exception as e:
        logger.error(f"Selenium爬虫测试失败: {e}")
        logger.info("注意：Selenium爬虫需要Chrome浏览器和ChromeDriver")