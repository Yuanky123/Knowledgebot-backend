#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ResponseGenerator:
    """回复生成器"""
    
    def __init__(self):
        self.response_history = []
    
    def generate_custom_response(self, context, strategy):
        """根据策略生成回复"""
        response = {
            'body': 'test reply',
            'post_id': context['post']['id'],
            'parent_comment_id': None,
        }
        return response