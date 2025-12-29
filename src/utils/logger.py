from loguru import logger
import os
from typing import Dict, Any

class Logger:
    """
    日志配置工具类
    """
    
    @staticmethod
    def configure(config: Dict[str, Any]):
        """
        配置日志
        
        Args:
            config: 日志配置
                level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                file: 日志文件路径
                rotation: 日志文件轮换规则
                retention: 日志文件保留时间
        """
        # 移除默认的控制台日志
        logger.remove()
        
        # 添加控制台日志
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level=config.get("level", "INFO"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} - {message}",
            colorize=True,
        )
        
        # 添加文件日志
        log_file = config.get("file", "logs/app.log")
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"创建日志目录: {log_dir}")
        
        logger.add(
            sink=log_file,
            level=config.get("level", "INFO"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} - {message}",
            rotation=config.get("rotation", "1 day"),
            retention=config.get("retention", "30 days"),
            compression="zip",
            encoding="utf-8",
        )
        
        logger.info(f"日志配置完成，日志文件: {log_file}")

if __name__ == "__main__":
    # 测试日志配置
    from src.config.config_loader import ConfigLoader
    
    config = ConfigLoader()
    Logger.configure(config.get("logging"))
    
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")