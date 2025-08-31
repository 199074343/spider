#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据存储模块
"""

import json
import csv
import pandas as pd
import aiofiles
from pathlib import Path
from typing import List, Dict, Any

class Storage:
    """数据存储器"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    async def save(self, data: List[Dict[str, Any]], format: str = 'json', 
                  path: str = 'data', filename: str = 'results'):
        """保存数据"""
        # 确保目录存在
        Path(path).mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            await self._save_json(data, path, filename)
        elif format.lower() == 'csv':
            await self._save_csv(data, path, filename)
        elif format.lower() == 'excel':
            await self._save_excel(data, path, filename)
        else:
            if self.logger:
                self.logger.error(f"不支持的格式: {format}")
    
    async def _save_json(self, data: List[Dict[str, Any]], path: str, filename: str):
        """保存为JSON格式"""
        try:
            filepath = Path(path) / f"{filename}.json"
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            if self.logger:
                self.logger.info(f"数据已保存到: {filepath}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"JSON保存失败: {e}")
    
    async def _save_csv(self, data: List[Dict[str, Any]], path: str, filename: str):
        """保存为CSV格式"""
        try:
            if not data:
                return
                
            filepath = Path(path) / f"{filename}.csv"
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            if self.logger:
                self.logger.info(f"数据已保存到: {filepath}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"CSV保存失败: {e}")
    
    async def _save_excel(self, data: List[Dict[str, Any]], path: str, filename: str):
        """保存为Excel格式"""
        try:
            if not data:
                return
                
            filepath = Path(path) / f"{filename}.xlsx"
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            if self.logger:
                self.logger.info(f"数据已保存到: {filepath}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Excel保存失败: {e}")
    
    async def load_json(self, filepath: str) -> List[Dict[str, Any]]:
        """加载JSON数据"""
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            if self.logger:
                self.logger.error(f"JSON加载失败: {e}")
            return []