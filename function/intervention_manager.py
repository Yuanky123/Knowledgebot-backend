#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

class InterventionManager:
    """干预管理器"""
    
    def __init__(self, strategies):
        self.strategies = strategies
        self.intervention_history = []
        self.phase_names = {
            0: 'start',
            1: 'initiation', 
            2: 'exploration',
            3: 'negotiation',
            4: 'co_construction'
        }
        self.style_names = {
            0: 'telling',
            1: 'selling', 
            2: 'participating',
            3: 'delegating'
        }
    
    def should_intervene(self, phase, is_sufficient):
        """判断是否需要干预"""
        # 讨论不充分或处于初始阶段时需要干预
        return not is_sufficient or phase <= 1
    
    def select_strategy(self, phase, is_sufficient, style=None):
        """选择干预策略"""
        if not self.should_intervene(phase, is_sufficient):
            return None
        
        # 根据阶段和充分性选择策略类型
        if phase <= 1:
            strategy_type = 'initiation'
        elif phase == 2:
            strategy_type = 'exploration'
        elif phase == 3:
            strategy_type = 'negotiation'
        elif phase >= 4:
            strategy_type = 'co_construction'
        else:
            strategy_type = 'initiation'
        
        # 如果没有指定风格，使用默认风格选择逻辑
        if style is None:
            if not is_sufficient:
                style_key = 'participating'  # 讨论不充分时用参与式
            else:
                style_key = 'telling'  # 讨论充分时用告知式
        else:
            style_key = self.style_names.get(style, 'participating')
        
        # 获取对应的策略列表
        strategies = self.strategies.get(strategy_type, {}).get(style_key, [])
        if strategies:
            selected_strategy = random.choice(strategies)
            # 记录干预历史
            self.intervention_history.append({
                'phase': strategy_type,
                'style': style_key,
                'strategy_type': f"{strategy_type}_{style_key}",
                'strategy': selected_strategy,
                'timestamp': None,  # 在调用时会添加时间戳
                'trigger_type': 'normal'
            })
            return selected_strategy
        return None
    
    def intervene(self, current_phase, style=None, timeout=False):
        """执行干预操作"""
        if timeout:
            # 超时干预，使用特殊的timeout策略
            timeout_strategies = self.strategies.get('timeout', [])
            if timeout_strategies:
                strategy = random.choice(timeout_strategies)
                self.intervention_history.append({
                    'phase': f"timeout_from_{self.phase_names.get(current_phase, 'unknown')}",
                    'style': 'timeout',
                    'strategy_type': 'timeout',
                    'strategy': strategy,
                    'timestamp': None,
                    'trigger_type': 'timeout'
                })
                return {
                    'intervention_type': 'timeout',
                    'strategy': strategy,
                    'response': strategy.get('prompt', '请继续讨论...'),
                    'phase': current_phase,
                    'style': 'timeout'
                }
            else:
                return {
                    'intervention_type': 'timeout',
                    'response': '讨论似乎暂停了，让我们继续吧！',
                    'phase': current_phase,
                    'style': 'timeout'
                }
        
        # 正常干预逻辑
        phase_key = self.phase_names.get(current_phase, 'initiation')
        
        # 选择策略风格
        if style is None:
            # 默认策略选择逻辑
            if current_phase <= 1:
                style_key = 'participating'  # 初始阶段用参与式
            elif current_phase == 2:
                style_key = 'telling'  # 探索阶段用告知式
            elif current_phase == 3:
                style_key = 'participating'  # 协商阶段用参与式
            else:
                style_key = 'delegating'  # 共同构建阶段用委托式
        else:
            style_key = self.style_names.get(style, 'participating')
        
        # 获取策略
        strategies = self.strategies.get(phase_key, {}).get(style_key, [])
        if strategies:
            strategy = random.choice(strategies)
            self.intervention_history.append({
                'phase': phase_key,
                'style': style_key,
                'strategy_type': f"{phase_key}_{style_key}",
                'strategy': strategy,
                'timestamp': None,
                'trigger_type': 'phase_transition' if style is not None else 'normal'
            })
            
            return {
                'intervention_type': 'normal',
                'strategy': strategy,
                'response': strategy.get('prompt', '让我们继续讨论...'),
                'phase': current_phase,
                'phase_name': phase_key,
                'style': style_key,
                'criteria': strategy.get('criteria', '')
            }
        else:
            # 没有找到合适的策略，返回默认响应
            return {
                'intervention_type': 'default',
                'response': f'我们现在处于{phase_key}阶段，让我们继续深入讨论吧！',
                'phase': current_phase,
                'phase_name': phase_key,
                'style': style_key
            }
    
    def get_intervention_stats(self):
        """获取干预统计信息"""
        if not self.intervention_history:
            return {
                'total_interventions': 0,
                'by_phase': {},
                'by_style': {},
                'by_trigger_type': {}
            }
        
        total_interventions = len(self.intervention_history)
        by_phase = {}
        by_style = {}
        by_trigger_type = {}
        
        for intervention in self.intervention_history:
            phase = intervention['phase']
            style = intervention['style']
            trigger_type = intervention.get('trigger_type', 'normal')
            
            by_phase[phase] = by_phase.get(phase, 0) + 1
            by_style[style] = by_style.get(style, 0) + 1
            by_trigger_type[trigger_type] = by_trigger_type.get(trigger_type, 0) + 1
        
        return {
            'total_interventions': total_interventions,
            'by_phase': by_phase,
            'by_style': by_style,
            'by_trigger_type': by_trigger_type
        }
    
    def update_strategies(self, new_strategies):
        """更新策略数据库"""
        self.strategies = new_strategies
        return True
    
    def get_available_strategies(self, phase, style=None):
        """获取指定阶段和风格的可用策略"""
        phase_key = self.phase_names.get(phase, 'initiation')
        
        if style is None:
            # 返回该阶段所有风格的策略
            return self.strategies.get(phase_key, {})
        else:
            style_key = self.style_names.get(style, 'participating')
            return self.strategies.get(phase_key, {}).get(style_key, [])
    
    def get_phase_progression_suggestion(self, current_phase):
        """获取阶段推进建议"""
        if current_phase >= 4:
            return {
                'can_progress': False,
                'suggestion': '已达到最终阶段：共同构建阶段',
                'next_phase': None
            }
        
        next_phase = current_phase + 1
        next_phase_name = self.phase_names.get(next_phase, 'unknown')
        
        return {
            'can_progress': True,
            'suggestion': f'可以推进到下一阶段：{next_phase_name}',
            'next_phase': next_phase,
            'next_phase_name': next_phase_name
        } 