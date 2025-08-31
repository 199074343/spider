#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主爬虫入口文件
"""

import asyncio
import argparse
from spider import Spider
from mobile_spider import MobileSpider
from utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description='通用爬虫框架')
    parser.add_argument('--target', type=str, required=True, help='目标网站或任务名称')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径')
    parser.add_argument('--workers', type=int, default=5, help='并发数量')
    parser.add_argument('--mobile', action='store_true', help='使用移动端爬虫模式')
    parser.add_argument('--debug', action='store_true', help='开启调试模式')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(debug=args.debug)
    
    # 根据模式创建爬虫实例
    if args.mobile:
        spider = MobileSpider(
            target=args.target,
            config_path=args.config,
            workers=1,  # 移动端通常使用单线程
            logger=logger
        )
        logger.info("使用移动端爬虫模式")
    else:
        spider = Spider(
            target=args.target,
            config_path=args.config,
            workers=args.workers,
            logger=logger
        )
        logger.info("使用标准爬虫模式")
    
    try:
        # 运行爬虫
        asyncio.run(spider.run())
    except KeyboardInterrupt:
        logger.info("爬虫被用户中断")
    except Exception as e:
        logger.error(f"爬虫运行出错: {e}")

if __name__ == '__main__':
    main()