import json
import os
import pandas as pd
from typing import Dict, Any, List
from loguru import logger
import datetime

class OutputFormatter:
    """
    输出格式化工具类，用于将数据保存为不同格式
    """
    
    @staticmethod
    def format_and_save(data: Any, config: Dict[str, Any], filename: str = None) -> str:
        """
        格式化数据并保存到文件
        
        Args:
            data: 要保存的数据
            config: 输出配置
                format: 输出格式 (json, markdown, csv)
                directory: 输出目录
                encoding: 编码格式
            filename: 自定义文件名（可选，默认使用时间戳）
            
        Returns:
            保存的文件路径
        """
        # 确保输出目录存在
        output_dir = config.get("directory", "data/output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"创建输出目录: {output_dir}")
        
        # 生成文件名
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"recruitment_info_{timestamp}"
        
        # 确定文件扩展名
        output_format = config.get("format", "json").lower()
        if output_format == "json":
            file_ext = ".json"
        elif output_format == "markdown":
            file_ext = ".md"
        elif output_format == "csv":
            file_ext = ".csv"
        else:
            logger.warning(f"不支持的输出格式: {output_format}，使用JSON格式")
            file_ext = ".json"
            output_format = "json"
        
        # 完整文件路径
        file_path = os.path.join(output_dir, filename + file_ext)
        
        # 保存文件
        try:
            if output_format == "json":
                OutputFormatter._save_json(data, file_path, config.get("encoding", "utf-8"))
            elif output_format == "markdown":
                OutputFormatter._save_markdown(data, file_path, config.get("encoding", "utf-8"))
            elif output_format == "csv":
                OutputFormatter._save_csv(data, file_path, config.get("encoding", "utf-8"))
            
            logger.info(f"数据已保存到: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise
    
    @staticmethod
    def _save_json(data: Any, file_path: str, encoding: str = "utf-8"):
        """
        保存为JSON格式
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            encoding: 编码格式
        """
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    @staticmethod
    def _save_markdown(data: Any, file_path: str, encoding: str = "utf-8"):
        """
        保存为Markdown格式
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            encoding: 编码格式
        """
        if isinstance(data, list):
            markdown_content = OutputFormatter._list_to_markdown(data)
        elif isinstance(data, dict):
            markdown_content = OutputFormatter._dict_to_markdown(data)
        else:
            markdown_content = str(data)
        
        with open(file_path, "w", encoding=encoding) as f:
            f.write(markdown_content)
    
    @staticmethod
    def _list_to_markdown(data_list: List[Dict[str, Any]]) -> str:
        """
        将列表转换为Markdown格式
        
        Args:
            data_list: 数据列表
            
        Returns:
            Markdown格式字符串
        """
        if not data_list:
            return ""
        
        content = "# 招聘信息汇总\n\n"
        content += f"共 {len(data_list)} 条招聘信息\n\n"
        
        for i, item in enumerate(data_list, 1):
            content += f"## 职位 {i}: {item.get('job_title', '未知职位')}\n\n"
            content += OutputFormatter._dict_to_markdown(item)
            content += "\n\n---\n\n"
        
        return content
    
    @staticmethod
    def _dict_to_markdown(data_dict: Dict[str, Any]) -> str:
        """
        将字典转换为Markdown格式
        
        Args:
            data_dict: 数据字典
            
        Returns:
            Markdown格式字符串
        """
        if not data_dict:
            return ""
        
        content = ""
        
        # 定义字段顺序
        field_order = [
            "job_title", "company", "industry", "location", "salary", 
            "experience", "education", "job_type", "department",
            "description", "requirements", "benefits", "tags", "post_date",
            "website", "url"
        ]
        
        # 添加有序字段
        for field in field_order:
            if field in data_dict and data_dict[field] is not None:
                content += OutputFormatter._field_to_markdown(field, data_dict[field])
        
        # 添加其他字段
        for field, value in data_dict.items():
            if field not in field_order and value is not None:
                content += OutputFormatter._field_to_markdown(field, value)
        
        return content
    
    @staticmethod
    def _field_to_markdown(field: str, value: Any) -> str:
        """
        将单个字段转换为Markdown格式
        
        Args:
            field: 字段名
            value: 字段值
            
        Returns:
            Markdown格式的字段字符串
        """
        # 字段名映射
        field_names = {
            "job_title": "职位名称",
            "company": "公司名称",
            "industry": "行业领域",
            "location": "工作地点",
            "salary": "薪资范围",
            "experience": "工作经验",
            "education": "学历要求",
            "job_type": "工作类型",
            "department": "部门",
            "description": "职位描述",
            "requirements": "职位要求",
            "benefits": "福利待遇",
            "tags": "标签",
            "post_date": "发布日期",
            "website": "来源网站",
            "url": "原文链接"
        }
        
        # 格式化值
        if isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                formatted_value = ", ".join(value)
            else:
                formatted_value = "\n- " + "\n- ".join(str(item) for item in value)
        elif isinstance(value, dict):
            formatted_value = "\n\n" + OutputFormatter._dict_to_markdown(value)
        else:
            formatted_value = str(value)
        
        # 长文本使用代码块
        if len(formatted_value) > 500:
            formatted_value = f"\n```\n{formatted_value}\n```"
        
        return f"**{field_names.get(field, field)}**: {formatted_value}\n\n"
    
    @staticmethod
    def _save_csv(data: Any, file_path: str, encoding: str = "utf-8"):
        """
        保存为CSV格式
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            encoding: 编码格式
        """
        if isinstance(data, list):
            # 如果是列表，转换为DataFrame
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # 如果是字典，转换为单列DataFrame
            df = pd.DataFrame.from_dict(data, orient="index", columns=["Value"])
        else:
            logger.error("CSV格式只支持列表或字典数据")
            raise ValueError("CSV格式只支持列表或字典数据")
        
        # 保存CSV
        df.to_csv(file_path, index=False, encoding=encoding)

if __name__ == "__main__":
    # 测试输出格式化工具
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    
    # 测试数据
    test_data = [
        {
            "job_title": "Python开发工程师",
            "company": "科技有限公司",
            "location": "北京",
            "salary": "20-30K",
            "experience": "3-5年",
            "education": "本科及以上",
            "description": "负责公司Python后端开发工作",
            "requirements": "熟悉Python，掌握Django或Flask框架",
            "benefits": "五险一金，带薪年假",
            "tags": ["Python", "后端", "Django"],
            "website": "lagou",
            "url": "https://www.lagou.com/jobs/123456.html"
        },
        {
            "job_title": "Java开发工程师",
            "company": "互联网公司",
            "location": "上海",
            "salary": "15-25K",
            "experience": "2-4年",
            "education": "本科及以上",
            "description": "负责公司Java后端系统开发",
            "requirements": "熟悉Java，掌握Spring Boot框架",
            "benefits": "六险一金，弹性工作制",
            "tags": ["Java", "后端", "Spring Boot"],
            "website": "zhaopin",
            "url": "https://www.zhaopin.com/jobs/654321.html"
        }
    ]
    
    # 测试保存为JSON
    logger.info("=== 测试保存为JSON ===")
    config.update("output.format", "json")
    OutputFormatter.format_and_save(test_data, config.get("output"))
    
    # 测试保存为Markdown
    logger.info("\n=== 测试保存为Markdown ===")
    config.update("output.format", "markdown")
    OutputFormatter.format_and_save(test_data, config.get("output"))
    
    # 测试保存为CSV
    logger.info("\n=== 测试保存为CSV ===")
    config.update("output.format", "csv")
    OutputFormatter.format_and_save(test_data, config.get("output"))