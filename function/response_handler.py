#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from flask import jsonify

class ResponseHandler:
    """统一的前端回复处理器"""
    
    def __init__(self):
        self.response_history = []
        self.stats = {
            'total_responses': 0,
            'success_responses': 0,
            'error_responses': 0,
            'start_time': datetime.now()
        }
    
    def success_response(self, message="操作成功", data=None):
        """成功响应"""
        response = {
            'success': True,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self._update_stats(True)
        self._log_response(response)
        
        return jsonify(response)
    
    def error_response(self, message="操作失败", error_code=None, status_code=500):
        """错误响应"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code,
            'timestamp': datetime.now().isoformat()
        }
        
        self._update_stats(False)
        self._log_response(response)
        
        return jsonify(response), status_code
    
    def data_response(self, data, message="数据获取成功"):
        """数据响应"""
        return self.success_response(message=message, data=data)
    
    def intervention_response(self, intervention_data, message="干预执行完成"):
        """干预响应"""
        return self.success_response(
            message=message,
            data={
                'intervention': intervention_data,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def timer_response(self, timer_data, message="计时器操作成功"):
        """计时器响应"""
        return self.success_response(
            message=message,
            data={'timer': timer_data}
        )
    
    def stats_response(self, stats_data, message="统计信息获取成功"):
        """统计响应"""
        return self.success_response(
            message=message,
            data={'stats': stats_data}
        )
    
    def _update_stats(self, success):
        """更新统计信息"""
        self.stats['total_responses'] += 1
        if success:
            self.stats['success_responses'] += 1
        else:
            self.stats['error_responses'] += 1
    
    def _log_response(self, response):
        """记录响应日志"""
        log_entry = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        self.response_history.append(log_entry)
        
        # 保持最近1000条记录
        if len(self.response_history) > 1000:
            self.response_history = self.response_history[-1000:]
    
    def get_response_stats(self):
        """获取响应统计信息"""
        return {
            'stats': self.stats,
            'history_count': len(self.response_history),
            'latest_responses': self.response_history[-5:] if self.response_history else []
        }
    
    def clear_stats(self):
        """清空统计数据"""
        self.response_history = []
        self.stats = {
            'total_responses': 0,
            'success_responses': 0,
            'error_responses': 0,
            'start_time': datetime.now()
        }
    
    def custom_response(self, success=True, message="", data=None, error_code=None, status_code=200):
        """自定义响应"""
        if success:
            return self.success_response(message=message, data=data)
        else:
            return self.error_response(message=message, error_code=error_code, status_code=status_code) 