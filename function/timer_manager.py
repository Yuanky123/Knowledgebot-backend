#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

class TimerManager:
    """计时器管理器"""
    
    def __init__(self, timeout_seconds=30, callback_func=None):
        """
        初始化计时器管理器
        
        Args:
            timeout_seconds: 超时时间（秒）
            callback_func: 超时回调函数
        """
        self.timeout_seconds = timeout_seconds
        self.callback_func = callback_func
        self.timer = None
        self.is_active = False
        self.last_activity_time = None
        self.timeout_count = 0
        self.total_timeouts = 0
        
    def set_timeout(self, timeout_seconds):
        """设置超时时间"""
        self.timeout_seconds = timeout_seconds
        print(f"计时器超时时间设置为 {timeout_seconds} 秒")
    
    def set_callback(self, callback_func):
        """设置超时回调函数"""
        self.callback_func = callback_func
        print("计时器回调函数已设置")
    
    def start_timer(self):
        """启动计时器"""
        if self.is_active:
            self.stop_timer()
        
        self.is_active = True
        self.last_activity_time = datetime.now()
        self.timer = threading.Timer(self.timeout_seconds, self._on_timeout)
        self.timer.start()
        print(f"计时器已启动，{self.timeout_seconds}秒后超时")
    
    def stop_timer(self):
        """停止计时器"""
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        self.is_active = False
        print("计时器已停止")
    
    def reset_timer(self):
        """重置计时器"""
        if self.is_active:
            self.stop_timer()
            self.start_timer()
            print("计时器已重置")
    
    def update_activity(self):
        """更新活动时间（收到新评论时调用）"""
        self.last_activity_time = datetime.now()
        self.reset_timer()
        print(f"活动时间已更新: {self.last_activity_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _on_timeout(self):
        """超时回调处理"""
        self.timeout_count += 1
        self.total_timeouts += 1
        self.is_active = False
        
        timeout_info = {
            'timeout_time': datetime.now(),
            'last_activity_time': self.last_activity_time,
            'timeout_seconds': self.timeout_seconds,
            'timeout_count': self.timeout_count,
            'total_timeouts': self.total_timeouts
        }
        
        print(f"计时器超时！超时次数: {self.timeout_count}")
        print(f"最后活动时间: {self.last_activity_time}")
        print(f"超时时间: {timeout_info['timeout_time']}")
        
        # 调用回调函数
        if self.callback_func:
            try:
                self.callback_func(timeout_info)
            except Exception as e:
                print(f"执行超时回调函数时出错: {e}")
        
        # 重新启动计时器以持续监控
        self.start_timer()
    
    def get_status(self):
        """获取计时器状态"""
        if not self.is_active:
            return {
                'is_active': False,
                'timeout_seconds': self.timeout_seconds,
                'timeout_count': self.timeout_count,
                'total_timeouts': self.total_timeouts,
                'last_activity_time': self.last_activity_time.isoformat() if self.last_activity_time else None
            }
        
        # 计算剩余时间
        if self.last_activity_time:
            elapsed_time = (datetime.now() - self.last_activity_time).total_seconds()
            remaining_time = max(0, self.timeout_seconds - elapsed_time)
        else:
            remaining_time = self.timeout_seconds
        
        return {
            'is_active': self.is_active,
            'timeout_seconds': self.timeout_seconds,
            'remaining_time': round(remaining_time, 2),
            'timeout_count': self.timeout_count,
            'total_timeouts': self.total_timeouts,
            'last_activity_time': self.last_activity_time.isoformat() if self.last_activity_time else None
        }
    
    def get_timer_stats(self):
        """获取计时器统计信息"""
        return {
            'timeout_seconds': self.timeout_seconds,
            'is_active': self.is_active,
            'timeout_count': self.timeout_count,
            'total_timeouts': self.total_timeouts,
            'last_activity_time': self.last_activity_time.isoformat() if self.last_activity_time else None,
            'has_callback': self.callback_func is not None
        }
    
    def clear_stats(self):
        """清空统计数据"""
        self.timeout_count = 0
        self.total_timeouts = 0
        print("计时器统计数据已清空")
    
    def is_timeout_likely(self, warning_threshold=0.8):
        """判断是否即将超时"""
        if not self.is_active or not self.last_activity_time:
            return False
        
        elapsed_time = (datetime.now() - self.last_activity_time).total_seconds()
        warning_time = self.timeout_seconds * warning_threshold
        
        return elapsed_time >= warning_time 