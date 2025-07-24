import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.config.app_config import app_config


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件名
        console_output: 是否输出到控制台
    """
    
    # 获取配置
    config = app_config.get_logging_config()
    log_level = level or config.get('level', 'INFO')
    
    # 确保日志目录存在
    logs_dir = app_config.get_path('logs')
    
    # 设置日志文件名
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"app_{timestamp}.log"
    
    log_path = os.path.join(logs_dir, log_file)
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # 创建格式化器
    formatter = logging.Formatter(
        config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器
    if config.get('file_rotation', True):
        # 使用旋转文件处理器
        max_bytes = _parse_file_size(config.get('max_file_size', '10MB'))
        backup_count = config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
    else:
        # 普通文件处理器
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
    
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)
    
    # 记录启动信息
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("应用程序启动")
    logger.info(f"日志文件: {log_path}")
    logger.info(f"日志级别: {log_level}")
    logger.info("=" * 60)


def _parse_file_size(size_str: str) -> int:
    """
    解析文件大小字符串
    
    Args:
        size_str: 文件大小字符串，如 "10MB", "1GB"
        
    Returns:
        int: 字节数
    """
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            try:
                return int(float(size_str[:-len(suffix)]) * multiplier)
            except ValueError:
                pass
    
    return 10 * 1024 * 1024  # 默认10MB


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, message: str, exc_info: bool = True) -> None:
    """
    记录异常信息
    
    Args:
        logger: 日志记录器
        message: 错误消息
        exc_info: 是否包含异常堆栈信息
    """
    logger.error(message, exc_info=exc_info)


# 模块初始化时设置默认日志
if __name__ != "__main__":
    setup_logging()