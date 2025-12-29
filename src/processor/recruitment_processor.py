from typing import Dict, Any, List, Optional
from loguru import logger
from bs4 import BeautifulSoup
import re
from .base_processor import BaseProcessor
from ..crawler.base_crawler import BaseCrawler
from ..llm.base_llm import BaseLLMClient

class RecruitmentProcessor(BaseProcessor):
    """
    招聘信息处理器，用于从网页中提取和分析招聘信息
    """
    
    def __init__(self, crawler: BaseCrawler, llm_client: BaseLLMClient, website_rules: Dict[str, Any]):
        """
        初始化招聘信息处理器
        
        Args:
            crawler: 爬虫实例
            llm_client: LLM客户端实例
            website_rules: 网站解析规则
        """
        super().__init__(crawler, llm_client)
        self.website_rules = website_rules
    
    def process(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        处理招聘信息URL
        
        Args:
            url: 招聘信息URL
            **kwargs: 额外参数
                website: 网站名称（自动检测如果不提供）
                clean_html: 是否清洗HTML（默认: True）
                extract_with_rules: 是否使用规则提取（默认: True）
            
        Returns:
            结构化的招聘信息字典，如果失败返回None
        """
        try:
            # 自动检测网站
            website = kwargs.get("website")
            if not website:
                website = self._detect_website(url)
                if not website:
                    logger.warning(f"无法检测URL所属网站: {url}")
                    website = "generic"
            
            logger.info(f"处理{website}招聘信息: {url}")
            
            # 获取网页内容
            # 为BOSS直聘添加特殊处理，等待页面完全加载
            if website == "boss":
                page_content = self.crawler.fetch(url, wait_for_element=".job-primary", wait_seconds=5, **kwargs)
            else:
                page_content = self.crawler.fetch(url, **kwargs)
            
            if not page_content:
                logger.error(f"无法获取网页内容: {url}")
                return None
            
            # 清洗HTML内容
            if kwargs.get("clean_html", True):
                clean_content = self._clean_html(page_content)
            else:
                clean_content = page_content
            
            # 使用规则提取（可选）
            rule_extracted_data = None
            if kwargs.get("extract_with_rules", True) and website in self.website_rules:
                rule_extracted_data = self._extract_with_rules(page_content, website)
            
            # 使用LLM提取结构化信息
            llm_extracted_data = self.llm_client.extract_recruitment_info(clean_content)
            
            # 合并结果（规则提取结果可能更准确，作为LLM结果的补充）
            final_data = {**(llm_extracted_data or {}), **(rule_extracted_data or {})}
            
            # 添加元数据
            final_data["url"] = url
            final_data["website"] = website
            
            logger.info(f"成功处理招聘信息: {final_data.get('job_title', '未知职位')} - {final_data.get('company', '未知公司')}")
            return final_data
            
        except Exception as e:
            logger.error(f"处理招聘信息失败 {url}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _detect_website(self, url: str) -> Optional[str]:
        """
        检测URL所属的招聘网站
        
        Args:
            url: 目标URL
            
        Returns:
            网站名称，如果无法检测返回None
        """
        for website, rules in self.website_rules.items():
            base_url = rules.get("base_url", "")
            if base_url in url:
                return website
        
        # 基于域名检测
        domain_patterns = {
            "lagou": r"lagou\.com",
            "zhaopin": r"zhaopin\.com",
            "51job": r"51job\.com",
            "liepin": r"liepin\.com",
            "boss": r"zhipin\.com",
        }
        
        for website, pattern in domain_patterns.items():
            if re.search(pattern, url, re.IGNORECASE):
                return website
        
        return None
    
    def _clean_html(self, html_content: str) -> str:
        """
        清洗HTML内容，提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            清洗后的纯文本
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            
            # 移除不需要的标签
            for tag in soup(["script", "style", "iframe", "img", "noscript", "form", "header", "footer", "nav"]):
                tag.decompose()
            
            # 移除注释
            for comment in soup.find_all(text=lambda text: isinstance(text, str) and text.strip().startswith("<!--")):
                comment.extract()
            
            # 获取文本内容
            text = soup.get_text(separator="\n", strip=True)
            
            # 清理空白行和多余空格
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s+', '\n', text)
            text = re.sub(r'\s+\n', '\n', text)
            
            # 移除重复的空行
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"清洗HTML失败: {e}")
            return html_content
    
    def _extract_with_rules(self, html_content: str, website: str) -> Optional[Dict[str, Any]]:
        """
        使用规则提取招聘信息
        
        Args:
            html_content: HTML内容
            website: 网站名称
            
        Returns:
            提取的结构化信息，如果失败返回None
        """
        try:
            if website not in self.website_rules:
                return None
            
            rules = self.website_rules[website]
            selectors = rules.get("selectors", {})
            
            soup = BeautifulSoup(html_content, "lxml")
            extracted_data = {}
            
            # 提取各个字段
            for field, selector in selectors.items():
                if not selector:
                    continue
                    
                try:
                    # 支持CSS选择器和XPath
                    if selector.startswith("//") or selector.startswith("/"):
                        # XPath选择器
                        from lxml import etree
                        tree = etree.HTML(html_content)
                        elements = tree.xpath(selector)
                        if elements:
                            extracted_data[field] = "\n".join([e.text.strip() if e.text else "" for e in elements])
                    else:
                        # CSS选择器
                        elements = soup.select(selector)
                        if elements:
                            extracted_data[field] = "\n".join([e.get_text(strip=True) for e in elements])
                    
                except Exception as e:
                    logger.debug(f"使用选择器{selector}提取{field}失败: {e}")
                    continue
            
            if extracted_data:
                logger.info(f"使用规则从{website}提取了{len(extracted_data)}个字段")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"使用规则提取信息失败: {e}")
            return None

if __name__ == "__main__":
    # 测试招聘信息处理器
    from src.config.config_loader import ConfigLoader
    from src.crawler.crawler_factory import CrawlerFactory
    from src.llm.llm_factory import LLMFactory
    
    try:
        config = ConfigLoader()
        
        # 创建爬虫实例
        crawler = CrawlerFactory.create_crawler(config.get("crawler"))
        
        # 创建LLM客户端实例
        llm_client = LLMFactory.create_client(config.get("llm"))
        
        # 创建处理器
        processor = RecruitmentProcessor(crawler, llm_client, config.get("websites"))
        
        # 测试URL（请替换为真实的招聘信息URL）
        test_url = "https://www.lagou.com/zhaopin/Python/1/"
        
        logger.info(f"测试处理招聘信息: {test_url}")
        result = processor.process(test_url)
        
        if result:
            logger.info("\n处理结果:")
            for key, value in result.items():
                if value and isinstance(value, str) and len(value) > 100:
                    logger.info(f"{key}: {value[:100]}...")
                else:
                    logger.info(f"{key}: {value}")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'crawler' in locals():
            crawler.close()