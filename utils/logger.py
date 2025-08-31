#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志模块
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = 'spider', debug: bool = False, 
                log_file: str = 'logs/spider.log') -> logging.Logger:
    """设置日志器"""
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建日志目录
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger