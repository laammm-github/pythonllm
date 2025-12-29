#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能招聘信息聚合与分析系统 - 简化运行脚本

Usage:
  python run.py <URL>                    # 爬取单个招聘信息URL
  python run.py --file <FILE_PATH>       # 批量爬取文件中的URL
  python run.py --analyze <JSON_FILE>    # 分析招聘信息文件
  python run.py --help                   # 显示帮助信息
"""

import sys
import os
import subprocess

def main():
    """简化运行脚本主函数"""
    if len(sys.argv) < 2:
        print("请提供至少一个参数")
        print(__doc__)
        sys.exit(1)
    
    # 构建命令
    cmd = [sys.executable, "main.py"]
    
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        cmd.append("--help")
    elif sys.argv[1] == "--file" or sys.argv[1] == "-f":
        if len(sys.argv) < 3:
            print("请提供文件路径")
            sys.exit(1)
        cmd.extend(["--file", sys.argv[2]])
    elif sys.argv[1] == "--analyze" or sys.argv[1] == "-a":
        if len(sys.argv) < 3:
            print("请提供要分析的JSON文件路径")
            sys.exit(1)
        cmd.extend(["--analyze", sys.argv[2]])
    else:
        # 默认作为URL处理
        cmd.extend(["--url", sys.argv[1]])
    
    # 运行命令
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()