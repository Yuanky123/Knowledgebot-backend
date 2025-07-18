#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from collections import defaultdict, deque

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
        # new_comments_phase = [random.choice([1, 2, 3])] * len(new_comments)
        # for i in range(len(new_comments)):
        #     if new_comments[i].get('parent_comment_id') is not None:
        #         new_comments_phase[i] = 2
        # new_comments_phase[0] = 1
        new_comments_phase = [1, 1, 1, 2, 2, 2, 2, 0, 3, 2]
        return new_comments_phase

    def analyze_connection(self, context, new_comment, past_comment):
        # randomly return true or false
        # return random.choice([True, False])
        print(past_comment.get('body'))
        if new_comment.get('id') == 406 and past_comment.get('id') in [397, 399]:
            return True
        return False

    def analyze_connection_with_tree(self, context, new_comment, tree_id):
        # randomly return true or false
        return random.choice([True, False])
    
    def add_to_graph(self, context, new_comments):
        graph = context['graph']
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        node_id_map = {node['id']: node for node in nodes}

        # 1. Drop all phase 0/4 comments
        filtered_comments = [c for c in new_comments if c.get('message_phase', 0) not in [0, 4]]

        # Find current max tree id
        existing_tree_ids = [node.get('tree_id', -1) for node in nodes if node.get('tree_id', -1) >= 0]
        max_tree_id = max(existing_tree_ids) if existing_tree_ids else 0
        # Build a lookup for all comments (old and new) by id
        all_comments = {c['id']: c for c in (context.get('comments', []) + new_comments)}
        for comment in filtered_comments:
            cid = comment['id']
            phase = comment.get('message_phase', 0)

            # append new node
            if cid not in node_id_map and phase != 0 and phase != 4:
                node = {'id': cid, 'phase': phase}
                nodes.append(node)
                node_id_map[cid] = node
            # PHASE 1: assign new tree id, no edge, no tree update
            if phase == 1:
                max_tree_id += 1
                node_id_map[cid]['tree_id'] = max_tree_id
                continue

            # PHASE 3: check connection with each tree
            if phase == 3:
                # Build current tree mapping
                adj = defaultdict(set)
                for e in edges:
                    adj[e['source']].add(e['target'])
                    adj[e['target']].add(e['source'])
                # Find all trees (connected components)
                visited = set()
                tree_id_map = {}
                component_nodes = {}
                tree_counter = 0
                for node in nodes:
                    nid = node['id']
                    if nid in visited:
                        continue
                    queue = deque([nid])
                    component = []
                    while queue:
                        curr = queue.popleft()
                        if curr in visited:
                            continue
                        visited.add(curr)
                        component.append(curr)
                        for neighbor in adj[curr]:
                            if neighbor not in visited:
                                queue.append(neighbor)
                    for n in component:
                        tree_id_map[n] = tree_counter
                    component_nodes[tree_counter] = component
                    tree_counter += 1
                found_connection = False
                for t_id, comp in component_nodes.items():
                    if self.analyze_connection_with_tree(context, comment, t_id):
                        node_id_map[cid]['tree_id'] = t_id
                        found_connection = True
                        break
                if not found_connection:
                    node_id_map[cid]['tree_id'] = -1
                continue

            # PHASE 2: add edges, then reconstruct trees
            if phase == 2:
                connected_tree_ids = set()
                parent_id = comment.get('parent_comment_id')
                if parent_id is not None and parent_id in node_id_map:
                    if not any(e for e in edges if e['source'] == parent_id and e['target'] == cid):
                        edges.append({'source': parent_id, 'target': cid})
                    parent_tree_id = node_id_map[parent_id].get('tree_id', None)
                    if parent_tree_id is not None and parent_tree_id >= 0:
                        connected_tree_ids.add(parent_tree_id)
                for past_node in nodes:
                    past_id = past_node['id']
                    if past_id == cid or past_id == parent_id:
                        continue
                    if past_node.get('phase', 0) not in [1, 2]:
                        continue
                    past_comment = all_comments.get(past_id, past_node)
                    if not any(e for e in edges if (e['source'] == past_id and e['target'] == cid) or (e['source'] == cid and e['target'] == past_id)):
                        if self.analyze_connection(context, comment, past_comment):
                            edges.append({'source': past_id, 'target': cid})
                            past_tree_id = node_id_map[past_id].get('tree_id', None)
                            if past_tree_id is not None and past_tree_id >= 0:
                                connected_tree_ids.add(past_tree_id)
                # Assign tree id
                if not connected_tree_ids:
                    max_tree_id += 1
                    node_id_map[cid]['tree_id'] = max_tree_id
                else:
                    min_tree_id = min(connected_tree_ids)
                    node_id_map[cid]['tree_id'] = min_tree_id
                    # Merge all other connected trees into min_tree_id
                    for merge_id in connected_tree_ids:
                        if merge_id == min_tree_id:
                            continue
                        for n in nodes:
                            if n.get('tree_id', -1) == merge_id:
                                n['tree_id'] = min_tree_id
        graph['nodes'] = nodes
        graph['edges'] = edges
        print(graph)
        return graph
    
    def check_discussion_sufficiency(self, context, new_comments):
        """检查当前阶段讨论是否充分"""
        current_phase = context['phase']
        # current_is_sufficient = context['is_sufficient']
        current_discussion_patience = context['discussion_patience']
        new_discussion_phase = current_phase
        new_discussion_patience = current_discussion_patience
        # new_is_sufficient = current_is_sufficient
        return {'phase': new_discussion_phase, 'patience': new_discussion_patience}