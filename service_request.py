#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务请求基类
提供HTTP请求的基础功能
"""

import requests
import json
from typing import Dict, Optional


class ServiceRequest:
    """服务请求基类"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化服务请求基类
        
        Args:
            base_url: 服务的基础URL
            api_key: API密钥（如果需要认证）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            data: 请求数据
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            raise