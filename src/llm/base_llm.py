from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from loguru import logger

class BaseLLMClient(ABC):
    """
    LLM客户端基类，定义统一的接口
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Optional[Dict[str, str]] = None):
        """
        初始化LLM客户端
        
        Args:
            config: LLM配置
            prompts: 提示词配置
        """
        self.config = config
        self.prompts = prompts or {}
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2000)
        
        if not self.api_key:
            raise ValueError("API密钥未配置")
        
        logger.info(f"初始化{self.__class__.__name__}客户端，模型: {self.model}")
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        生成文本
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数
                temperature: 温度参数
                max_tokens: 最大令牌数
                top_p: 核采样参数
                frequency_penalty: 频率惩罚
                presence_penalty: 存在惩罚
            
        Returns:
            生成的文本，如果失败返回None
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """
        聊天模式，支持多轮对话
        
        Args:
            messages: 消息列表，每个消息包含role和content字段
                role: 角色 (system, user, assistant)
                content: 消息内容
            **kwargs: 额外参数
                temperature: 温度参数
                max_tokens: 最大令牌数
                top_p: 核采样参数
                frequency_penalty: 频率惩罚
                presence_penalty: 存在惩罚
            
        Returns:
            生成的文本，如果失败返回None
        """
        pass
    
    def extract_recruitment_info(self, content: str, prompt_template: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        从招聘信息中提取结构化数据
        
        Args:
            content: 招聘信息文本
            prompt_template: 自定义提示词模板
            
        Returns:
            结构化的招聘信息字典，如果失败返回None
        """
        if not prompt_template:
            prompt_template = self._get_default_extract_prompt()
        
        prompt = prompt_template.format(content=content)
        
        try:
            response = self.generate(prompt, temperature=0.1, max_tokens=self.max_tokens)
            if response:
                return self._parse_extract_result(response)
            return None
        except Exception as e:
            logger.error(f"提取招聘信息失败: {e}")
            return None
    
    def _get_default_extract_prompt(self) -> str:
        """
        获取默认的招聘信息提取提示词模板
        
        Returns:
            提示词模板字符串
        """
        # 优先使用配置文件中的提示词
        if "extract_recruitment_info" in self.prompts:
            return self.prompts["extract_recruitment_info"]
        
        # 如果配置文件中没有，使用默认提示词
        return """
        你是一位专业的招聘信息分析员，请从以下招聘信息中提取结构化数据。
        请严格按照JSON格式输出，不要添加任何解释或额外内容。
        提取的字段包括：
        - job_title: 职位名称
        - company: 公司名称
        - industry: 行业领域
        - location: 工作地点
        - salary: 薪资范围
        - experience: 工作经验要求
        - education: 学历要求
        - job_type: 工作类型（全职、兼职、实习等）
        - department: 部门
        - description: 职位描述
        - requirements: 职位要求
        - benefits: 福利待遇
        - tags: 标签列表（数组格式）
        - post_date: 发布日期
        
        如果某些字段不存在，请使用null值。
        
        招聘信息内容：
        {content}
        """
    
    def _parse_extract_result(self, response: str) -> Dict[str, Any]:
        """
        解析LLM返回的提取结果
        
        Args:
            response: LLM返回的文本
            
        Returns:
            解析后的结构化数据字典
        """
        import json
        import re
        
        try:
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 尝试直接解析整个响应
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON响应失败: {e}")
            logger.error(f"原始响应: {response}")
            # 返回部分解析结果或空字典
            return {}