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
    
    def analyze_phase(self, comments):
        """判断当前评论的阶段"""
        # 目前使用简单逻辑，未来可以集成大语言模型
        # 使用大语言模型判断当前评论的阶段
        # 输入：当前评论
        # 输出：当前评论的阶段，并返回给前端
        # phase = self.llm_model.predict(comments)
        
        if not comments:
            return 'initiation'
        
        comment_count = len(comments)
        
        # 基于评论数量的简单阶段判断
        if comment_count <= 2:
            return 'initiation'
        elif comment_count <= 6:
            return 'exploration'
        elif comment_count <= 12:
            return 'negotiation'
        else:
            return 'co_construction'
    
    def check_discussion_sufficiency(self, comments, current_phase):
        """检查当前阶段讨论是否充分"""
        if not comments:
            return False
        
        comment_count = len(comments)
        
        # 计算平均评论长度
        total_length = 0
        for comment in comments:
            if isinstance(comment, dict):
                content = comment.get('message', '') or comment.get('content', '')
            elif isinstance(comment, list) and len(comment) >= 2:
                content = comment[1]
            else:
                content = str(comment)
            total_length += len(content)
        
        avg_length = total_length / len(comments) if comments else 0
        
        # 计算独立用户数
        unique_users = set()
        for comment in comments:
            if isinstance(comment, dict):
                user = comment.get('user', '') or comment.get('user_name', '')
            elif isinstance(comment, list) and len(comment) >= 1:
                user = comment[0]
            else:
                user = 'unknown'
            unique_users.add(user)
        
        unique_user_count = len(unique_users)
        
        # 根据当前阶段判断充分性
        phase_names = list(self.discussion_phases.keys())
        if current_phase >= len(phase_names):
            current_phase = len(phase_names) - 1
        
        phase_name = phase_names[current_phase] if current_phase < len(phase_names) else 'initiation'
        
        # 不同阶段的充分性标准
        if phase_name == 'initiation':
            # 初始阶段：需要至少2个用户，每个评论平均长度>10字符
            return unique_user_count >= 2 and avg_length >= 10 and comment_count >= 2
        elif phase_name == 'exploration':
            # 探索阶段：需要至少3个用户，深度讨论
            return unique_user_count >= 3 and avg_length >= 20 and comment_count >= 4
        elif phase_name == 'negotiation':
            # 协商阶段：需要体现不同观点和协商过程
            return unique_user_count >= 2 and avg_length >= 25 and comment_count >= 6
        elif phase_name == 'co_construction':
            # 共同构建阶段：需要深度整合和总结
            return unique_user_count >= 2 and avg_length >= 30 and comment_count >= 8
        else:
            return False
    
    def get_discussion_statistics(self, comments):
        """获取讨论统计信息"""
        if not comments:
            return {
                'total_comments': 0,
                'average_length': 0,
                'unique_users': 0,
                'latest_comment': None,
                'phase_analysis': None
            }
        
        total_comments = len(comments)
        
        # 计算平均长度
        total_length = 0
        for comment in comments:
            if isinstance(comment, dict):
                content = comment.get('message', '') or comment.get('content', '')
            elif isinstance(comment, list) and len(comment) >= 2:
                content = comment[1]
            else:
                content = str(comment)
            total_length += len(content)
        
        average_length = total_length / total_comments if total_comments > 0 else 0
        
        # 计算独立用户数
        unique_users = set()
        for comment in comments:
            if isinstance(comment, dict):
                user = comment.get('user', '') or comment.get('user_name', '')
            elif isinstance(comment, list) and len(comment) >= 1:
                user = comment[0]
            else:
                user = 'unknown'
            unique_users.add(user)
        
        unique_user_count = len(unique_users)
        latest_comment = comments[-1] if comments else None
        
        # 分析当前应该处于哪个阶段
        suggested_phase = self.analyze_phase(comments)
        
        return {
            'total_comments': total_comments,
            'average_length': round(average_length, 2),
            'unique_users': unique_user_count,
            'latest_comment': latest_comment,
            'suggested_phase': suggested_phase,
            'phase_analysis': self.phase_criteria.get(suggested_phase, {})
        }
    
    def get_phase_requirements(self, phase_name):
        """获取指定阶段的要求"""
        return self.phase_criteria.get(phase_name, {})
    
    def suggest_next_phase(self, current_comments, current_phase):
        """建议下一个阶段"""
        phase_names = list(self.discussion_phases.keys())
        
        if current_phase >= len(phase_names) - 1:
            return {
                'can_progress': False,
                'current_phase': phase_names[-1],
                'suggestion': '已达到最终阶段'
            }
        
        # 检查当前阶段是否完成
        is_sufficient = self.check_discussion_sufficiency(current_comments, current_phase)
        
        if is_sufficient:
            next_phase_index = min(current_phase + 1, len(phase_names) - 1)
            next_phase_name = phase_names[next_phase_index]
            
            return {
                'can_progress': True,
                'current_phase': phase_names[current_phase],
                'next_phase': next_phase_name,
                'suggestion': f'可以推进到{self.discussion_phases[next_phase_name]}',
                'requirements': self.phase_criteria.get(next_phase_name, {})
            }
        else:
            return {
                'can_progress': False,
                'current_phase': phase_names[current_phase],
                'suggestion': '当前阶段讨论尚未充分，建议继续深入',
                'requirements': self.phase_criteria.get(phase_names[current_phase], {})
            }
    
    def analyze_comment_quality(self, comment):
        """分析单条评论的质量"""
        if isinstance(comment, dict):
            content = comment.get('message', '') or comment.get('content', '')
            user = comment.get('user', '') or comment.get('user_name', '')
        elif isinstance(comment, list) and len(comment) >= 2:
            user, content = comment[0], comment[1]
        else:
            return {
                'quality_score': 0,
                'length': 0,
                'has_question': False,
                'has_reasoning': False
            }
        
        length = len(content)
        has_question = '？' in content or '?' in content
        # 简单检测是否包含推理词汇
        reasoning_words = ['因为', '所以', '但是', '然而', '因此', '由于', '如果', '那么']
        has_reasoning = any(word in content for word in reasoning_words)
        
        # 质量评分（简单版本）
        quality_score = 0
        if length >= 10:
            quality_score += 2
        if length >= 30:
            quality_score += 3
        if has_question:
            quality_score += 2
        if has_reasoning:
            quality_score += 3
        
        return {
            'quality_score': min(quality_score, 10),  # 最高10分
            'length': length,
            'has_question': has_question,
            'has_reasoning': has_reasoning,
            'user': user
        }
