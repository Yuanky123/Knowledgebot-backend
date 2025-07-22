#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from openai import OpenAI
from collections import defaultdict, deque
import arg
import json

# Configure OpenAI client
client = OpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key=arg.OPENAI_API_KEY
    )

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
                'min_comments': 10,
                'description': '多样化观点外化，建立讨论基础'
            },
            'exploration': {
                'min_comments': 10,
                'description': '深入探讨，展开多维度分析'
            },
            'negotiation': {
                'min_coverage_rate': 0.5,
                'description': '处理分歧，寻求共识'
            },
            'co_construction': {
                'min_comments': 10,
                'description': '共同构建知识，整合观点'
            }
        }
    

    def extract_mentioned_user(self, comment_text):
        """
        Extract mentioned username from comment text (e.g., @username)
        """
        import re
        # Look for @username pattern
        match = re.search(r'@(\w+)', comment_text)
        if match:
            return match.group(1)
        return None

    def build_parent_chain(self, comment, id_to_comment, depth=0, max_depth=1):
        """
        Recursively build parent chain string for a comment, up to max_depth.
        """
        if depth >= max_depth:
            return ''
        parent_id = comment.get('parent_comment_id')
        if parent_id is not None and parent_id in id_to_comment:
            parent = id_to_comment[parent_id]
            parent_str = self.build_parent_chain(parent, id_to_comment, depth+1, max_depth)
            return f"\n    (In reply to: Author: {parent.get('author_name', 'Unknown')}, Body: {parent.get('body', 'No content')}{parent_str})"
        return ''

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
        new_comments_phase = [1, 1, 1, 2, 2, 2, 2, 0, 3, 2, 2, 1, 1, 2, 2, 3, 3, 3]
        return new_comments_phase


    def analyze_connection(self, context, new_comment, past_comment):
        """
        Legacy function for single comment analysis - kept for backward compatibility
        """
        try:
            # Prepare the prompt for ChatGPT
            prompt = f"""
            Analyze if the new comment directly replies to the past comment.
            
            Past Comment (Author: {past_comment.get('author_name', 'Unknown')}):
            {past_comment.get('body', 'No content')}
            
            New Comment (Author: {new_comment.get('author_name', 'Unknown')}):
            {new_comment.get('body', 'No content')}
            
            Determine if the new comment is a direct reply to the past comment. Consider:
            1. Does the new comment explicitly reference or respond to points made in the past comment?
            2. Does the new comment explicitly agree with, disagree with, or question the past comment WITH EXPLANATION?
            3. Does the new comment mention or address the author of the past comment?

            Note that 
            - If either the new comment or past comment has no explanation or sufficient semantic information (for example, simply stating "I agree" or "I disagree" without any explanation), you should return false.
            - If the past commenet is too general or broad, or it contains unclear terms that may cause confusion, you should return false.
            - ALWAYS consider the semantic meaning of the new comment. The new comment may be expliciting expressing the author's opinion with a past comment, but this DOES NOT mean the new comment is replying to this specific past comment. You should consider the meaning of the new comment and the past comment. 
            - DO NOT infer the underlying meaning of the new comment and try to associate it with the past comment. If the new comment is not explicitly referencing the past comment (such as explicitly mentioning terms described in the past comment), their connection is insufficient.
            
            Respond with a JSON object containing:
            - "is_reply": true/false (whether the new comment directly replies to the past comment)
            - "reason": "brief explanation of your decision"
            
            Examples:
            New comment: Yeah I agree with you. Seems like a lot of graduate students are experiencing distress.
            Past comment: Mental health is also an important aspect where we should deliver help to graduate students.
            Response: {{
                "is_reply": true,
                "reason": "The new comment indicates that mental disorder is common among graduate students and agrees with the past comment that mental health is an important factor to consider when supporting graduate students. The new comment explicitly agrees with the past comment with explanation."
            }}

            New comment: Yeah that's a good point.
            Past comment: Career center can help students find interns, which is also a useful source of support.
            {{
                "is_reply": false,
                "reason": "The new comment indicates that the author agrees with a past comment, but no explanation is provided. The past comment discusses how career center can help students. Whether the new comment is agreeing with this specific past comment cannot be deteremined."
            }} 

            New comment: Yeah I think campus transportation can definitely help students to get around campus without stress.
            Past comment: I think we should build connections among different communities on campus.
            {{
                "is_reply": false,
                "reason": "The new comment agrees that campus transportation can help students travel within the campus. The past comment suggests building connections among different communities on campus. The term 'connection' in the past comment is not clearly defined, and it cannot be determined that it refers to physical connection and transportation, thus their relationship is unclear."
            }}           
            """
            
            # Call ChatGPT using the model from arg.py
            response = client.chat.completions.create(
                model=arg.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes comment relationships. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            # Extract the response
            result_text = response.choices[0].message.content.strip()
            print("Analyzing connection for comments...")
            print("New comment: ", new_comment.get('body', 'N/A'))
            print("Past comment: ", past_comment.get('body', 'N/A'))
            
            try:
                result_json = json.loads(result_text)
                is_reply = result_json.get('is_reply', False)
                reason = result_json.get('reason', 'No reason provided')
                print("Result: ", is_reply)
                print("Reason: ", reason)
                print('-' * 10)
                return is_reply
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                # Fallback: try to extract yes/no from text
                if 'true' in result_text.lower() or 'yes' in result_text.lower():
                    return True
                elif 'false' in result_text.lower() or 'no' in result_text.lower():
                    return False
                else:
                    return False
            
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")

    def analyze_connection_batch(self, context, new_comment, candidate_comments):
        """
        Analyze connection between new comment and multiple candidate comments, return the best match
        """
        try:
            all_comments = context.get('comments', [])
            id_to_comment = {c.get('id'): c for c in all_comments}
            # Prepare the prompt for ChatGPT
            candidate_text = ""
            for i, comment in enumerate(candidate_comments):
                candidate_text += f"""
            Candidate {i+1} (Author: {comment.get('author_name', 'Unknown')}):
            {self.build_parent_chain(comment, id_to_comment)}
            {comment.get('body', 'No content')}
            """

            prompt = f"""
            Analyze which candidate comment the new comment is most likely replying to.
            
            New Comment (Author: {new_comment.get('author_name', 'Unknown')}):
            {self.build_parent_chain(new_comment, id_to_comment)}
            {new_comment.get('body', 'No content')}
            
            {candidate_text}
            
            Determine which candidate comment the new comment is most likely replying to. Consider:
            1. Does the new comment explicitly reference or respond to points made in any candidate comment?
            2. Does the new comment explicitly agree with, disagree with, or question any candidate comment WITH EXPLANATION?
            3. Does the new comment mention or address the author of any candidate comment?

            Note that 
            - If either the new comment or candidate comment has no explanation or sufficient semantic information (for example, simply stating "I agree" or "I disagree" without any explanation), you should return false.
            - If the candidate comment is too general or broad, or it contains unclear terms that may cause confusion, you should return false.
            - ALWAYS consider the semantic meaning of the new comment. The new comment may be expliciting expressing the author's opinion with a candidate comment, but this DOES NOT mean the new comment is replying to this specific candidate comment. You should consider the meaning of the new comment and the candidate comment. 
            - DO NOT infer the underlying meaning of the new comment and try to associate it with the candidate comment. If the new comment is not explicitly referencing the candidate comment (such as explicitly mentioning terms described in the candidate comment), their connection is insufficient.
            
            Respond with a JSON object containing:
            - "best_match_index": 1-based index of the best matching candidate (or -1 if no good match)
            - "connection_score": 0-10 score indicating strength of connection (0 = no connection, 10 = perfect match)
            - "reason": "brief explanation of your decision"
            
            Examples:
            New comment: Yeah I agree with you. Seems like a lot of graduate students are experiencing distress.
            Candidate 1: Mental health is also an important aspect where we should deliver help to graduate students.
            Candidate 2: Career center can help students find interns.
            Response: {{
                "best_match_index": 1,
                "connection_score": 8,
                "reason": "The new comment explicitly agrees with Candidate 1 about mental health being important for graduate students, with clear explanation about distress."
            }}

            New comment: Yeah that's a good point.
            Candidate 1: Career center can help students find interns.
            Candidate 2: Campus transportation is important.
            Response: {{
                "best_match_index": -1,
                "connection_score": 0,
                "reason": "The new comment indicates agreement but provides no explanation about which specific point it agrees with."
            }}           
            """
            # print(prompt)
            # Call ChatGPT using the model from arg.py
            response = client.chat.completions.create(
                model=arg.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes comment relationships. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Extract the response
            result_text = response.choices[0].message.content.strip()
            print("Analyzing batch connection for comments...")
            print("New comment: ", new_comment.get('body', 'N/A'))
            print("Candidates: ", candidate_text)
            
            try:
                result_json = json.loads(result_text)
                best_match_index = result_json.get('best_match_index', 0)
                connection_score = result_json.get('connection_score', 0)
                reason = result_json.get('reason', 'No reason provided')
                print("Best match index: ", best_match_index)
                print("Connection score: ", connection_score)
                print("Reason: ", reason)
                print('-' * 10)
                
                # Return the best matching comment if score is above threshold
                if best_match_index > 0 and connection_score >= 5:
                    return candidate_comments[best_match_index]
                else:
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return None
            
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")
            return None



    def analyze_connection_with_tree(self, context, new_comment, tree_id):
        try:
            nodes = context['graph']['nodes']
            tree_nodes = [n for n in nodes if n.get('tree_id', []).count(tree_id) > 0]
            if not tree_nodes:
                print(f"No nodes found for tree_id {tree_id}")
                return False
            
            # Gather all comments in the tree as context (author, body, parent_comment_id only)
            all_comments = context.get('comments', [])
            id_to_comment = {c.get('id'): c for c in all_comments}
            tree_comments = []
            for n in tree_nodes:
                c = id_to_comment.get(n['id'])
                if c:
                    parent_chain = self.build_parent_chain(c, id_to_comment)
                    tree_comments.append(f"Author: {c.get('author_name', 'Unknown')}: {parent_chain} {c.get('body', 'No content')}")
            context_text = "\n".join(tree_comments)
            
            prompt = f"""
            Analyze if the new comment is related to part of the past discussion below. The past discussion consists of the following comments:
            {context_text}
            
            New Comment (Author: {new_comment.get('author_name', 'Unknown')}):
            {self.build_parent_chain(new_comment, id_to_comment)}
            {new_comment.get('body', 'No content')}
            
            Determine if the new comment is related to the past discussion. Consider:
            1. Does the new comment reference any points made in the past discussion?
            2. Is there a clear semantic or logical connection between the new comment and the points made in the past discussion?

            Note that:
            - DO NOT consider the "broader theme" or "implicit meaning" of the new comment. Only consider whether the new comment EXPLICITLY mentions ideas or topics in the past discussion. 
            - ONLY if the new comment explicitly mentions ideas in the past discussion, it is related to the past discussion. "Broader theme" or "Broader context" is not a valid reason to consider the new comment related to the past discussion.

            Respond with a JSON object containing:
            - "is_related": true/false (whether the new comment is related to the past discussion)
            - "reason": "summary of the new comment and the context, and brief explanation of your decision"
            
            Example:
            {{"is_related": true, "reason": "The new comment suggests that both physical and mental health issues are as important. This addresses the past discussion that graduate students' mental health should be supported. Part of the new comment is addressing the past discussion."}}
            {{"is_related: false, "reason": The new comment suggests that campus planning should consider both university development and students' convenience, while the past discussion is about campus transportation design. While campus transportation is part of campus planning, the new comment does not explicitly address transportation issues." }}
            """
            response = client.chat.completions.create(
                model=arg.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes comment relationships. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            print("Analyzing connection with tree...")
            print("New comment: ", new_comment.get('body', 'N/A'))
            print("Tree context: ", context_text)
            
            try:
                import json
                result_json = json.loads(result_text)
                is_related = result_json.get('is_related', False)
                reason = result_json.get('reason', 'No reason provided')
                print("Is related: ", is_related)
                print("Reason: ", reason)
                print('-' * 10)
                return is_related
            except Exception as e:
                print(f"Error parsing JSON response: {e}")
                return False
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")
            return False

    def rate_connection_with_all_trees(self, context, new_comment, tree_ids):
        """
        Use ChatGPT to rate the connection (0-10) between new_comment and each tree in tree_ids.
        Returns a dict: {tree_id: (score, reason)}
        """
        try:
            nodes = context['graph']['nodes']
            all_comments = context.get('comments', [])
            id_to_comment = {c.get('id'): c for c in all_comments}
            tree_contexts = []
            for idx, t_id in enumerate(tree_ids):
                tree_nodes = [n for n in nodes if n.get('tree_id', []).count(t_id) > 0]
                tree_comments = []
                for n in tree_nodes:
                    c = id_to_comment.get(n['id'])
                    if c:
                        parent_chain = self.build_parent_chain(c, id_to_comment)
                        tree_comments.append(f"Author: {c.get('author_name', 'Unknown')}: {parent_chain} {c.get('body', 'No content')}")
                context_text = "\n".join(tree_comments)
                tree_contexts.append(f"Tree {idx+1} (ID: {t_id}):\n{context_text}")
            all_trees_text = "\n\n".join(tree_contexts)
            prompt = f"""
            For each tree below, rate the connection between the new comment and the discussion tree representing part of the past discussion (0-10, 0 = no connection, 10 = perfect match).
            
            Consider:
            1. Does the new comment reference any points made in the tree?
            2. Is there a clear semantic or logical connection between the new comment and the points made in the tree?

            Note that:
            - The new comment does not have to be a continuation of the past discussion. It can be a combination of ideas proposed in the tree or new angles about the topic discussed in the tree.

            {all_trees_text}
            
            New Comment (Author: {new_comment.get('author_name', 'Unknown')}):
            {self.build_parent_chain(new_comment, id_to_comment)}
            {new_comment.get('body', 'No content')}
            
            Respond with a JSON object mapping tree index (starting from 1) to an object with 
            "score": integer between 0 and 10, 0 = no connection, 10 = perfect match
            "reason": summary of the new comment and the context, and brief explanation of your decision

            Example:
            {{
                "1": {{"score": 8, "reason": "The new comment suggests that both physical and mental health issues are as important. This addresses the past discussion that graduate students' mental health should be supported. Part of the new comment is addressing the past discussion."}},
                "2": {{"score": 0, "reason": "The new comment suggests that both physical and mental health issues are as important. The past discussion is about campus design. The new comment does not explicitly address campus design issues."}}
            }}
            """
            response = client.chat.completions.create(
                model=arg.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that rates comment relationships. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.1
            )
            result_text = response.choices[0].message.content.strip()
            try:
                import json
                result_json = json.loads(result_text)
                result = {}
                for idx, t_id in enumerate(tree_ids):
                    key = str(idx+1)
                    entry = result_json.get(key, {})
                    score = int(entry.get('score', 0))
                    reason = entry.get('reason', 'No reason provided')
                    result[t_id] = (score, reason)
                return result
            except Exception as e:
                print(f"Error parsing JSON response: {e}")
                return {t_id: (0, 'Error parsing response.') for t_id in tree_ids}
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")
            return {t_id: (0, 'Error calling API.') for t_id in tree_ids}


    def add_to_graph(self, context, new_comments):
        graph = context['graph']
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        node_id_map = {node['id']: node for node in nodes}


        # Find current max tree id
        existing_tree_ids = []
        for node in nodes:
            tids = node.get('tree_id', [])
            if isinstance(tids, int):
                tids = [tids]
            for tid in tids:
                if tid >= 0:
                    existing_tree_ids.append(tid)
        max_tree_id = max(existing_tree_ids) if existing_tree_ids else 0
        
        # Build a lookup for all comments (old and new) by id
        all_comments = {c['id']: c for c in (context.get('comments', []) + new_comments)}
        for comment in new_comments:
            cid = comment['id']
            phase = comment.get('message_phase', 0)
            context['comments'].append(comment)
            if phase in [0, 4]:
                continue

            # append new node
            if cid not in node_id_map and phase != 0 and phase != 4:
                node = {'id': cid, 'phase': phase, 'tree_id': []}
                nodes.append(node)
                node_id_map[cid] = node
            # PHASE 1: assign new tree id, no edge, no tree update
            if phase == 1:
                max_tree_id += 1
                node_id_map[cid]['tree_id'] = [max_tree_id]
                continue

            # PHASE 3: rate connection with all trees and assign to those above threshold
            if phase == 3:
                related_tree_ids = []
                threshold = 5
                parent_id = comment.get('parent_comment_id')
                parent_tree_ids = set()
                if parent_id is not None and parent_id in node_id_map:
                    parent_tree_ids = set(node_id_map[parent_id].get('tree_id', []))
                # Exclude parent trees from GPT scoring
                all_tree_ids = set(range(1, max_tree_id + 1))
                if all_tree_ids:
                    scores = self.rate_connection_with_all_trees(context, comment, all_tree_ids)
                    for t_id, (score, reason) in scores.items():
                        print(f"Phase 3: Comment {cid} - Tree {t_id} score: {score}, reason: {reason}")
                        if score >= threshold or t_id in parent_tree_ids:
                            if t_id in parent_tree_ids:
                                print("Adjusted score to 10 due to parent connection.")
                            related_tree_ids.append(t_id)
                if related_tree_ids:
                    node_id_map[cid]['tree_id'] = sorted(set(related_tree_ids))
                else:
                    node_id_map[cid]['tree_id'] = [-1]
                continue
            
            # PHASE 2: add edges, then update tree ids efficiently
            if phase == 2:
                connected_tree_ids = set()
                parent_id = comment.get('parent_comment_id')
                
                # If comment has parent_comment_id, just add edge to parent and skip other analysis
                if parent_id is not None and parent_id in node_id_map:
                    if not any(e for e in edges if e['source'] == parent_id and e['target'] == cid):
                        edges.append({'source': parent_id, 'target': cid})
                    parent_tree_ids = node_id_map[parent_id].get('tree_id', [])
                    if isinstance(parent_tree_ids, int):
                        parent_tree_ids = [parent_tree_ids]
                    for ptid in parent_tree_ids:
                        if ptid >= 0:
                            connected_tree_ids.add(ptid)
                else:
                    # No parent_comment_id, need to find best connection
                    candidate_comments = []
                    
                    # Check if comment mentions a user (@username)
                    mentioned_user = self.extract_mentioned_user(comment.get('body', ''))
                    
                    if mentioned_user:
                        # Find most recent 3 comments by mentioned user
                        user_comments = []
                        for past_node in nodes:
                            past_id = past_node['id']
                            if past_id == cid:
                                continue
                            past_comment = all_comments.get(past_id, past_node)
                            if past_comment.get('author_name') == mentioned_user:
                                user_comments.append(past_comment)
                        
                        # Get most recent 3 comments by this user
                        user_comments.sort(key=lambda x: x.get('id', 0), reverse=True)
                        candidate_comments = user_comments[:3]
                        print(f"Found {len(candidate_comments)} recent comments by mentioned user @{mentioned_user}")
                    else:
                        # Get most recent 5 comments
                        recent_comments = []
                        for past_node in nodes:
                            past_id = past_node['id']
                            if past_id == cid:
                                continue
                            if past_node.get('phase', 0) not in [1, 2]:
                                continue
                            past_comment = all_comments.get(past_id, past_node)
                            recent_comments.append(past_comment)
                        
                        # Sort by ID (assuming higher ID = more recent) and get top 5
                        recent_comments.sort(key=lambda x: x.get('id', 0), reverse=True)
                        candidate_comments = recent_comments[:5]
                        print(f"Analyzing against {len(candidate_comments)} most recent comments")
                    
                    # Use batch analysis to find best connection
                    if candidate_comments:
                        best_match = self.analyze_connection_batch(context, comment, candidate_comments)
                        if best_match:
                            best_match_id = best_match.get('id')
                            if not any(e for e in edges if (e['source'] == best_match_id and e['target'] == cid) or (e['source'] == cid and e['target'] == best_match_id)):
                                edges.append({'source': best_match_id, 'target': cid})
                                best_match_tree_ids = node_id_map[best_match_id].get('tree_id', [])
                                if isinstance(best_match_tree_ids, int):
                                    best_match_tree_ids = [best_match_tree_ids]
                                for btid in best_match_tree_ids:
                                    if btid >= 0:
                                        connected_tree_ids.add(btid)
                # Assign tree id
                if not connected_tree_ids:
                    max_tree_id += 1
                    node_id_map[cid]['tree_id'] = [max_tree_id]
                else:
                    min_tree_id = min(connected_tree_ids)
                    node_id_map[cid]['tree_id'] = list(sorted(connected_tree_ids))
                    # Merge all other connected trees into min_tree_id
                    for merge_id in connected_tree_ids:
                        if merge_id == min_tree_id:
                            continue
                        for n in nodes:
                            tids = n.get('tree_id', [])
                            if isinstance(tids, int):
                                tids = [tids]
                            if merge_id in tids:
                                # Remove merge_id and add min_tree_id if not present
                                tids = [tid for tid in tids if tid != merge_id]
                                if min_tree_id not in tids:
                                    tids.append(min_tree_id)
                                n['tree_id'] = list(sorted(set(tids)))
        graph['nodes'] = nodes
        graph['edges'] = edges
        return graph
    
    def check_discussion_sufficiency(self, context, new_comments):
        """检查当前阶段讨论是否充分"""
        current_phase = context['phase']
        # current_is_sufficient = context['is_sufficient']
        current_discussion_patience = context['discussion_patience']
        new_discussion_phase = current_phase
        new_discussion_patience = current_discussion_patience
        # new_is_sufficient = current_is_sufficient
        if current_phase == 0:
            new_discussion_patience = 0
            new_discussion_phase = current_discussion_patience - len(new_comments)
        elif current_phase == 1:
            #判断阶段一的评论是不是足够多
            phase_1_comments = 0
            for comment in new_comments:
                if comment.get('message_phase', 0) == 1:
                    phase_1_comments += 1
            for comment in context['comments']:
                if comment.get('message_phase', 0) == 1:
                    phase_1_comments += 1
            if phase_1_comments >= self.phase_criteria['initiation']['min_comments']:
                new_discussion_phase = 1
                new_discussion_patience = arg.MAX_PATIENCE
            else:
                new_discussion_phase = 0
                new_discussion_patience = current_discussion_patience - len(new_comments)
        elif current_phase == 2:
            #判断阶段二的评论是不是足够多
            phase_2_comments = 0
            for comment in new_comments:
                if comment.get('message_phase', 0) == 2:
                    phase_2_comments += 1
            for comment in context['comments']:
                if comment.get('message_phase', 0) == 2:
                    phase_2_comments += 1
            if phase_2_comments >= self.phase_criteria['exploration']['min_comments']:
                new_discussion_phase = 2
                new_discussion_patience = arg.MAX_PATIENCE
                # function: extract block from context_structure & extract the negotiation points
                # Negotiation_points_list = [[], [], ...]
                pass
            else:
                new_discussion_phase = 0
                new_discussion_patience = current_discussion_patience - len(new_comments)
        elif current_phase == 3:
            #判断阶段三的评论是否充分
            new_phase_3_block = []
            negotiation_points_list = [] #从原来的数据里提取
            # extract the negotiation points from the new_comments 提取新的谈判点
            new_negotiation_points = []
            # 判断新的谈判点对原来的谈判点的覆盖情况
            # function: 
            coverage_rate = 0
            if coverage_rate >= self.phase_criteria['negotiation']['min_coverage_rate']:
                new_discussion_phase = 3
                new_discussion_patience = arg.MAX_PATIENCE
                # 根据新的谈判点，获取潜在的共同构建点 potential_co_construction_points = []
                # function: 
                pass
            else:
                new_discussion_phase = 2
                new_discussion_patience = current_discussion_patience - len(new_comments)
        elif current_phase == 4:
            # 判断阶段四的评论是否充分
            potential_co_construction_points = [] #从原来的数据里提取
            # 根据新的谈判点，获取潜在的共同构建点 potential_co_construction_points = []
            # function: 
            new_co_construction_points = []
            # 判断新的共同构建点对原来的共同构建点的覆盖情况
            # function: 
            coverage_rate = 0
            if coverage_rate >= self.phase_criteria['co_construction']['min_coverage_rate']:
                new_discussion_phase = 4
                new_discussion_patience = arg.MAX_PATIENCE
            else:
                new_discussion_phase = 3
                new_discussion_patience = current_discussion_patience - len(new_comments)
        return {'phase': new_discussion_phase, 'patience': new_discussion_patience}