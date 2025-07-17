#!/usr/bin/env python
# -*- coding: utf-8 -*-

class CommentAnalyzer:
    """评论分析器"""
    
    def __init__(self):
        self.discussion_phases = {
            'initiation': '初始阶段',
            'exploration': '探索阶段', 
            'negotiation': '协商阶段',
            'co_construction': '共同构建阶段'
        }
        
        self.phase_criteria = {
            'initiation': {
                'min_comments': 0,
                'max_comments': 2,
                'description': '多样化观点外化，建立讨论基础'
            },
            'exploration': {
                'min_comments': 3,
                'max_comments': 6,
                'description': '深入探讨，展开多维度分析'
            },
            'negotiation': {
                'min_comments': 7,
                'max_comments': 12,
                'description': '处理分歧，寻求共识'
            },
            'co_construction': {
                'min_comments': 13,
                'max_comments': float('inf'),
                'description': '共同构建知识，整合观点'
            }
        }
    
    def analyze_phase(self, context, new_comments):
        """判断当前评论的阶段"""
        # 目前使用简单逻辑，未来可以集成大语言模型
        # 使用大语言模型判断当前评论的阶段
        # 输入：当前评论
        # 输出：当前评论的阶段，并返回给前端
        # new_comments_phase = self.llm_model.predict(new_comments)
        new_comments_phase = [0] * len(new_comments)
        graph = context['graph']
        return new_comments_phase, graph
    
    def check_discussion_sufficiency(self, context, new_comments):
        """检查当前阶段讨论是否充分"""
        current_phase = context['phase']
        # current_is_sufficient = context['is_sufficient']
        current_discussion_patience = context['discussion_patience']
        new_discussion_phase = current_phase
        new_discussion_patience = current_discussion_patience
        # new_is_sufficient = current_is_sufficient
        return {'phase': new_discussion_phase, 'patience': new_discussion_patience}

