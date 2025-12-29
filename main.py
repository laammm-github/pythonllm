#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能招聘信息聚合与分析系统主脚本

Usage:
  python main.py --url <URL> [--config <CONFIG_PATH>] [--format <FORMAT>] [--output <OUTPUT_DIR>]
  python main.py --file <FILE_PATH> [--config <CONFIG_PATH>] [--format <FORMAT>] [--output <OUTPUT_DIR>]
  python main.py --help

Options:
  -u, --url <URL>            单个招聘信息URL
  -f, --file <FILE_PATH>     包含多个URL的文件路径（每行一个URL）
  -c, --config <CONFIG_PATH> 配置文件路径 [default: src/config/config.yaml]
  -o, --format <FORMAT>      输出格式 (json, markdown, csv) [default: json]
  -d, --output <OUTPUT_DIR>  输出目录 [default: data/output]
  -h, --help                 显示帮助信息
"""

import argparse
import sys
import os
from typing import List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.config_loader import ConfigLoader
from src.crawler.crawler_factory import CrawlerFactory
from src.llm.llm_factory import LLMFactory
from src.processor.recruitment_processor import RecruitmentProcessor
from src.processor.recruitment_analyzer import RecruitmentAnalyzer
from src.utils.logger import Logger
from src.utils.output_formatter import OutputFormatter
from loguru import logger

def parse_args() -> argparse.Namespace:
    """
    解析命令行参数
    
    Returns:
        解析后的参数命名空间
    """
    parser = argparse.ArgumentParser(
        description="智能招聘信息聚合与分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # 功能选择
    function_group = parser.add_mutually_exclusive_group(required=True)
    
    # 爬取功能参数
    function_group.add_argument(
        "-u", "--url", 
        type=str, 
        help="单个招聘信息URL"
    )
    function_group.add_argument(
        "-f", "--file", 
        type=str, 
        help="包含多个URL的文件路径（每行一个URL）"
    )
    
    # 分析功能参数
    function_group.add_argument(
        "-a", "--analyze",
        type=str,
        help="分析指定的招聘信息JSON文件"
    )
    
    # 其他参数
    parser.add_argument(
        "-c", "--config", 
        type=str, 
        default="src/config/config.yaml",
        help="配置文件路径 [default: src/config/config.yaml]"
    )
    parser.add_argument(
        "-o", "--format", 
        type=str, 
        choices=["json", "markdown", "csv"],
        default="json",
        help="输出格式 (json, markdown, csv) [default: json]"
    )
    parser.add_argument(
        "-d", "--output", 
        type=str, 
        default="data/output",
        help="输出目录 [default: data/output]"
    )
    
    return parser.parse_args()

def load_urls_from_file(file_path: str) -> List[str]:
    """
    从文件中加载URL列表
    
    Args:
        file_path: 包含URL的文件路径
        
    Returns:
        URL列表
    """
    urls = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith("#"):
                    urls.append(url)
        
        logger.info(f"从文件{file_path}加载了{len(urls)}个URL")
        return urls
        
    except FileNotFoundError:
        logger.error(f"URL文件不存在: {file_path}")
        raise
    except Exception as e:
        logger.error(f"加载URL文件失败: {e}")
        raise

def main():
    """
    主函数
    """
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 加载配置
        logger.info(f"加载配置文件: {args.config if hasattr(args, 'config') else 'src/config/config.yaml'}")
        config_path = args.config if hasattr(args, 'config') else "src/config/config.yaml"
        config = ConfigLoader(config_path)
        
        # 配置日志
        Logger.configure(config.get("logging"))
        
        # 分析功能
        if hasattr(args, 'analyze') and args.analyze:
            logger.info(f"开始分析招聘信息文件: {args.analyze}")
            
            # 创建招聘信息分析器
            analyzer = RecruitmentAnalyzer(config)
            
            # 执行分析
            report_path = analyzer.analyze_from_file(args.analyze)
            
            logger.success(f"分析完成！分析报告已保存至: {report_path}")
            return
        
        # 爬取功能
        # 更新配置（根据命令行参数）
        config.update("output.format", args.format)
        config.update("output.directory", args.output)
        
        # 创建爬虫实例
        crawler = CrawlerFactory.create_crawler(config.get("crawler"))
        
        # 创建LLM客户端实例
        llm_client = LLMFactory.create_client(config.get("llm"), config.prompts)
        
        # 创建招聘信息处理器
        processor = RecruitmentProcessor(
            crawler=crawler,
            llm_client=llm_client,
            website_rules=config.get("websites")
        )
        
        # 获取URL列表
        if args.url:
            urls = [args.url]
        else:
            urls = load_urls_from_file(args.file)
        
        # 处理URL
        if len(urls) == 1:
            # 处理单个URL
            logger.info(f"开始处理单个URL: {urls[0]}")
            result = processor.process(urls[0])
            if result:
                results = [result]
            else:
                results = []
        else:
            # 批量处理多个URL
            logger.info(f"开始批量处理{len(urls)}个URL")
            batch_results = processor.batch_process(urls, max_workers=1)
            results = [r["result"] for r in batch_results if r["result"] is not None]
        
        # 保存结果
        if results:
            logger.info(f"成功处理{len(results)}个招聘信息，正在保存结果...")
            OutputFormatter.format_and_save(results, config.get("output"))
            logger.success("爬取任务完成！")
        else:
            logger.warning("没有成功处理任何招聘信息")
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 关闭资源
        if 'crawler' in locals():
            crawler.close()

if __name__ == "__main__":
    main()