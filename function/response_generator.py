#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ResponseGenerator:
    """回复生成器"""
    
    def __init__(self):
        self.response_history = []
    
    def generate_custom_response(self, context, strategy):
        """根据策略生成回复"""

        intervention_style = context['style'] # 0: telling, 1: selling, 2: participating, 3: delegating
        current_phase = context['phase']

        if intervention_style == 0:
            pass
            intervention_message = ''
        elif intervention_style == 1:
            pass
            intervention_message = ''
        elif intervention_style == 2:
            pass
            intervention_message = ''
        elif intervention_style == 3: # delegating
            intervention_message = strategy

        response = {
            'body': 'test reply',
            'post_id': context['post']['id'],
            'parent_comment_id': None,
        }
        return response