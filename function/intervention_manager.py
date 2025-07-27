#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class InterventionManager:
    """干预管理器"""
    
    def __init__(self, strategies):
        self.strategies = strategies
        self.strategy_names = {
            0: 'initiation',
            1: 'exploration',
            2: 'negotiation',
            3: 'co_construction',
            4: 'co_construction_subphase_2'
        }
    
    def intervene(self, context):
        """执行干预操作"""
        # 根据context['phase']选择策略
        strategy = self.strategies[self.strategy_names[context['phase']]]
        return strategy
    