#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
千问API测试脚本
"""

import os
import sys
import logging

# 设置日志为DEBUG级别
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.append('.')

try:
    # 导入千问客户端
    from src.llm.qwen_client import QwenClient
    from src.config.config_loader import ConfigLoader
    
    # 加载配置
    config = ConfigLoader('src/config/config.yaml')
    llm_config = config.get('llm')
    llm_config['api_key'] = os.getenv('QWEN_API_KEY')
    
    # 初始化千问客户端
    logger.info("初始化千问客户端...")
    client = QwenClient(llm_config)
    
    # 测试简单的文本生成
    logger.info("测试简单的文本生成...")
    prompt = "请简单介绍一下你自己"
    result = client.generate(prompt)
    
    if result:
        logger.info(f"生成结果: {result}")
    else:
        logger.error("文本生成失败")
        
    # 测试结构化数据提取
    logger.info("\n测试结构化数据提取...")
    test_content = """
    职位名称：高级Python开发工程师
    公司名称：科技有限公司
    薪资范围：25K-35K
    工作地点：北京市朝阳区
    经验要求：3-5年
    学历要求：本科及以上
    """
    
    extract_prompt = f"请从以下文本中提取招聘信息，以JSON格式输出，包含job_title, company, salary字段：\n{test_content}"
    result = client.generate(extract_prompt)
    
    if result:
        logger.info(f"提取结果: {result}")
    else:
        logger.error("数据提取失败")
        
    logger.info("测试完成")
    
except Exception as e:
    logger.error(f"测试失败: {e}", exc_info=True)
    sys.exit(1)