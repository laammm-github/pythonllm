from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, Any, Optional
from loguru import logger
from .base_crawler import BaseCrawler
import time

class SeleniumCrawler(BaseCrawler):
    """
    基于Selenium的爬虫实现，用于处理动态加载页面
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Selenium爬虫
        
        Args:
            config: 爬虫配置
        """
        super().__init__(config)
        
        # 浏览器配置
        browser_config = config.get("browser", {})
        
        # 创建Chrome选项
        self.options = Options()
        
        # 设置无头模式
        if browser_config.get("headless", True):
            self.options.add_argument("--headless")
            logger.info("启用无头模式")
        
        # 设置用户代理
        user_agent = browser_config.get("user_agent")
        if user_agent:
            self.options.add_argument(f"--user-agent={user_agent}")
        
        # 添加其他Chrome选项
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--lang=zh-CN")
        
        # 禁用图片加载（提高性能）
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        self.options.add_experimental_option("prefs", prefs)
        
        # 设置代理（如果有）
        proxy_url = config.get("proxy_url")
        if proxy_url:
            self.options.add_argument(f"--proxy-server={proxy_url}")
            logger.info(f"设置代理: {proxy_url}")
        
        # 初始化WebDriver
        try:
            # 使用WebDriverManager自动管理ChromeDriver
            self.service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.set_script_timeout(self.timeout)
            
            logger.info("Selenium WebDriver初始化成功")
        except Exception as e:
            logger.error(f"Selenium WebDriver初始化失败: {e}")
            raise
    
    def fetch(self, url: str, wait_for_element: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            wait_for_element: 等待的元素选择器（CSS或XPath）
            **kwargs: 额外参数
                wait_seconds: 额外等待时间（秒）
            
        Returns:
            网页内容字符串，如果失败返回None
        """
        def _request():
            # 导航到URL
            self.driver.get(url)
            logger.info(f"成功导航到: {url}")
            
            # 等待元素加载
            if wait_for_element:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                
                try:
                    # 自动检测选择器类型（XPath或CSS）
                    if wait_for_element.startswith("//") or wait_for_element.startswith("/"):
                        locator = (By.XPATH, wait_for_element)
                    else:
                        locator = (By.CSS_SELECTOR, wait_for_element)
                    
                    # 等待元素可见
                    WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(locator))
                    logger.info(f"元素 {wait_for_element} 已加载")
                except Exception as e:
                    logger.warning(f"等待元素 {wait_for_element} 失败: {e}")
            
            # 额外等待时间
            wait_seconds = kwargs.get("wait_seconds", 0)
            if wait_seconds > 0:
                logger.info(f"额外等待 {wait_seconds} 秒")
                time.sleep(wait_seconds)
            
            # 获取页面源码
            page_source = self.driver.page_source
            logger.info(f"成功获取页面源码，长度: {len(page_source)} 字符")
            return page_source
        
        return self._retry_request(_request)
    
    def scroll_to_bottom(self, scroll_pause_time: float = 1.0) -> None:
        """
        滚动到页面底部（用于加载动态内容）
        
        Args:
            scroll_pause_time: 每次滚动后的暂停时间（秒）
        """
        try:
            # 获取初始页面高度
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # 等待新内容加载
                time.sleep(scroll_pause_time)
                
                # 获取新的页面高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # 如果高度没有变化，说明已到页面底部
                if new_height == last_height:
                    break
                
                last_height = new_height
                logger.info(f"页面已滚动，新高度: {last_height}")
        except Exception as e:
            logger.error(f"滚动页面失败: {e}")
    
    def execute_script(self, script: str, *args) -> Any:
        """
        执行JavaScript脚本
        
        Args:
            script: JavaScript脚本
            *args: 脚本参数
        
        Returns:
            脚本执行结果
        """
        try:
            result = self.driver.execute_script(script, *args)
            logger.info(f"JavaScript脚本执行成功")
            return result
        except Exception as e:
            logger.error(f"JavaScript脚本执行失败: {e}")
            return None
    
    def close(self):
        """
        关闭WebDriver和服务
        """
        try:
            self.driver.quit()
            self.service.stop()
            logger.info("Selenium WebDriver已关闭")
        except Exception as e:
            logger.error(f"关闭Selenium WebDriver失败: {e}")

if __name__ == "__main__":
    # 测试爬虫
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    crawler = SeleniumCrawler(config.get("crawler"))
    
    try:
        # 测试抓取拉勾网首页，等待职位列表加载
        html = crawler.fetch("https://www.lagou.com", wait_for_element=".job_list", wait_seconds=2)
        if html:
            logger.info(f"成功获取拉勾网首页，内容长度: {len(html)} 字符")
    finally:
        crawler.close()