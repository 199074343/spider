#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试配置管理器
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class TestConfigManager:
    """测试配置管理器"""
    
    def __init__(self, config_path: str = "tests/test_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载测试配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认测试配置"""
        return {
            "test_settings": {
                "timeout": 30,
                "max_retries": 3,
                "log_level": "DEBUG",
                "temp_dir": "temp_test_data",
                "mock_delay": 0.01,
                "cleanup_after_test": True
            },
            "test_data": {
                "sample_urls": [
                    "https://test1.example.com",
                    "https://test2.example.com"
                ],
                "sample_html": {
                    "title": "Default Test Title",
                    "content": "Default test content"
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_test_settings(self) -> Dict[str, Any]:
        """获取测试设置"""
        return self.get('test_settings', {})
    
    def get_test_data(self) -> Dict[str, Any]:
        """获取测试数据"""
        return self.get('test_data', {})
    
    def get_mobile_test_config(self) -> Dict[str, Any]:
        """获取移动端测试配置"""
        return self.get('mobile_test_config', {})
    
    def create_temp_dir(self) -> Path:
        """创建临时测试目录"""
        temp_dir = Path(self.get('test_settings.temp_dir', 'temp_test_data'))
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def cleanup_temp_dir(self):
        """清理临时测试目录"""
        if self.get('test_settings.cleanup_after_test', True):
            temp_dir = Path(self.get('test_settings.temp_dir', 'temp_test_data'))
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)


# 全局测试配置实例
test_config = TestConfigManager()