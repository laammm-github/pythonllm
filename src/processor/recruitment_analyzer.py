#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘信息分析工具
负责对已提取的招聘信息进行多维度分析并生成报告
"""

import json
import os
from typing import Dict, List, Any
from loguru import logger
import datetime

from src.config.config_loader import ConfigLoader
from src.llm.llm_factory import LLMFactory

class RecruitmentAnalyzer:
    """
    招聘信息分析器
    """
    
    def __init__(self, config: ConfigLoader):
        """
        初始化招聘信息分析器
        
        Args:
            config: 配置加载器实例
        """
        self.config = config
        self.analysis_config = config.get("analysis")
        self.llm_client = LLMFactory.create_client(config.get("llm"), config.prompts)
        
    def analyze_from_file(self, file_path: str) -> str:
        """
        从JSON文件加载招聘信息并进行分析
        
        Args:
            file_path: 招聘信息JSON文件路径
            
        Returns:
            生成的分析报告文件路径
        """
        logger.info(f"开始分析文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 加载JSON数据
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                recruitment_data = json.load(f)
            logger.info(f"成功加载{len(recruitment_data)}条招聘信息")
        except Exception as e:
            logger.error(f"加载JSON文件失败: {e}")
            raise
        
        # 执行分析
        return self.analyze(recruitment_data, file_path)
    
    def analyze(self, recruitment_data: List[Dict[str, Any]], source_file: str = None) -> str:
        """
        对招聘信息进行分析并生成报告
        
        Args:
            recruitment_data: 招聘信息列表
            source_file: 数据源文件路径（可选）
            
        Returns:
            生成的分析报告文件路径
        """
        logger.info(f"开始分析{len(recruitment_data)}条招聘信息")
        
        # 检查分析功能是否启用
        if not self.analysis_config.get("enabled", False):
            logger.warning("分析功能未启用，请在配置文件中开启")
            return None
        
        # 准备提示词参数
        prompt_params = {
            "recruitment_data": json.dumps(recruitment_data, ensure_ascii=False, indent=2)
        }
        
        # 获取分析提示词
        analysis_prompt = self.llm_client.prompts.get("analyze_recruitment_info", "")
        if not analysis_prompt:
            logger.error("未找到分析提示词，请检查配置文件")
            raise ValueError("未找到分析提示词")
        
        # 填充提示词参数
        formatted_prompt = analysis_prompt.format(**prompt_params)
        
        # 调用LLM进行分析
        try:
            logger.info("调用大模型进行招聘信息分析...")
            # 使用通用生成方法
            analysis_result = self.llm_client.generate(formatted_prompt)
            logger.info("招聘信息分析完成")
        except Exception as e:
            logger.error(f"大模型分析失败: {e}")
            raise
        
        # 保存分析报告
        return self._save_analysis_report(analysis_result, recruitment_data, source_file)
    
    def _save_analysis_report(self, analysis_content: str, recruitment_data: List[Dict[str, Any]], source_file: str = None) -> str:
        """
        保存分析报告
        
        Args:
            analysis_content: 分析报告内容
            recruitment_data: 招聘信息列表
            source_file: 数据源文件路径（可选）
            
        Returns:
            生成的分析报告文件路径
        """
        # 获取报告配置
        report_config = self.analysis_config.get("report", {})
        output_dir = report_config.get("output_dir", "data/output")
        output_format = report_config.get("format", "markdown")
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"创建输出目录: {output_dir}")
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        if source_file:
            # 从源文件名提取部分信息
            source_name = os.path.splitext(os.path.basename(source_file))[0]
            filename = f"{source_name}_analysis_{timestamp}"
        else:
            filename = f"recruitment_analysis_{timestamp}"
        
        # 确定文件扩展名
        if output_format == "markdown":
            file_ext = ".md"
        else:
            logger.warning(f"不支持的报告格式: {output_format}，使用Markdown格式")
            file_ext = ".md"
            output_format = "markdown"
        
        # 完整文件路径
        file_path = os.path.join(output_dir, filename + file_ext)
        
        # 保存报告
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(analysis_content)
            
            logger.info(f"分析报告已保存到: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
            raise

if __name__ == "__main__":
    """
    测试招聘信息分析器
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python recruitment_analyzer.py <recruitment_json_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 加载配置
    config = ConfigLoader()
    
    # 创建分析器
    analyzer = RecruitmentAnalyzer(config)
    
    # 执行分析
    try:
        report_path = analyzer.analyze_from_file(file_path)
        print(f"分析完成，报告保存至: {report_path}")
    except Exception as e:
        print(f"分析失败: {e}")
        sys.exit(1)