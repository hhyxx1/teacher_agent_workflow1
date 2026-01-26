"""
日志工具
提供统一的日志配置和记录功能
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from config_agentscope import LOG_LEVEL

# 日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, "teacher_agent.log")

# 配置日志
def setup_logger(name: str = "teacher_agent") -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器（支持日志轮转）
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 设置格式化器
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认日志记录器
logger = setup_logger()

# 日志装饰器
def log_function_call(func):
    """
    日志装饰器，用于记录函数调用
    
    Args:
        func: 要装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        logger.info(f"调用函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
    return wrapper