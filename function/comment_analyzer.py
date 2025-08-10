#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyexpat import model
import random
from tkinter import N
from openai import OpenAI
from collections import defaultdict, deque
import arg
import json
import traceback
from .utils import build_parent_chain, extract_json_from_markdown, extract_mentioned_user, formulate_tree, list_tree_ids
from pprint import pprint
import copy

# Configure OpenAI client
client = OpenAI(
    base_url='https://api.zhizengzeng.com/v1',
    api_key=arg.OPENAI_API_KEY
    )

local_client = OpenAI(
    base_url="http://0.0.0.0:8000/v1",
    api_key="0"
)

# client_gemini = OpenAI(
#     base_url='https://api.zhizengzeng.com/v1',
#     api_key="sk-zk23e12430a30075ee3d9858364a99d800867112483439ff"
# )

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
                'min_comments': 3,
                'description': '多样化观点外化，建立讨论基础'
            },
            'exploration': {
                'min_comments': 10, # TODO: Unused variable!!
                'description': '深入探讨，展开多维度分析'
            },
            'negotiation': {
                'min_coverage_rate': 0.5, # TODO: Unused variable!!
                'description': '处理分歧，寻求共识'
            },
            'co_construction': {
                'min_comments': 3, # TODO: Unused variable!!
                'description': '共同构建知识，整合观点'
            },
            'co_construction_subphase_2': {
                'min_comments': 3,
                'description': '反思及应用'
            }
        }
    


    def analyze_phase(self, context, new_comments):
        """判断当前评论的阶段"""
        # 使用大语言模型判断当前评论的阶段
        # 输入：当前新出现的评论list
        # 输出：当前评论的阶段(list)，并返回给前端

        # new_comments_phase = [1] * len(new_comments)
        
        new_comments_phase = []
        for i in range(len(new_comments)):
            print(f"**** Analyzing comment {new_comments[i]['id']}: {new_comments[i]['body']}")
            messages = [
                {"role": "system", "content": "You are a professional data classifier. Your task is, in a online knowledge community setting, given a comment in this community, decide, whether the it is a knowledge comment or not, and if it is, which knowledge co-construction stage the comment belongs to. \n\n# Classification of the comments:\nThe classes are: \n0. Non-knowledge comment\n    Typical examples: Joking around or off-topic banter; only expressing yes/no/thanks without any further opinion (or insufficient expression of opinion, e.g., \"I have never considered this aspect before\"); purely expressing emotions (even in a calm manner)/complaints; personal attacks; pure sarcasm.\n1. Initiation: Multiple viewpoints are proposed in the comments, but there is no interaction yet.\n    Typical examples: Introduces an entirely new topic, question or fact.\n2. Exploration: Referencing others' viewpoints, adding examples or personal experiences to existing ideas, asking and answering related questions — overall, the content becomes more in-depth.\n    Typical examples: Supporting or refuting a previous viewpoint; deepening/adding to/restating previous ideas; providing theoretical support for earlier points; raising variations or complementary questions to earlier ones; probing the details or logic of earlier viewpoints; pointing out logical fallacies in earlier ideas.\n3. Negotiation: Integration of viewpoints, defining scopes, clarifying differences and common ground, moving toward structured negotiation, and attempting to reach mechanisms or solutions.\n    Typical examples: Defining the scope of multiple viewpoints; analyzing differences and similarities among them; integrating multiple earlier ideas into one comprehensive viewpoint; proposing higher-level mechanisms/solutions by synthesizing several perspectives.\n4. Integration: Establishing clear consensus, summarizing principles, applying knowledge, and reflecting on the co-constructed outcomes.\n    Typical examples: Generalizing a shared principle or insight from earlier ideas; Applying a synthesized understanding to a new problem or situation; Reflecting on the learning process or how the discussion has advanced collective understanding; Proposing directions for future discussion based on established consensus.\n(Classes 1-4 comprise the knowledge co-construction stages.)\n\n# Tips\n- You can use some linguistic cues to help you classify the comments, especially distinguishing between Initiation (class 1) and Exploration (class 2). Below are definitions and examples for each cue:\n    - Raising questions: Comments that include direct or rhetorical questions, often seeking clarification, elaboration, or challenging previous statements.\n        - Examples: \"Why cannot ...?\", \"Right?\", \"So ...?\"\n    - Refuting or supporting others' viewpoints: Comments that explicitly agree or disagree with previous statements, or reinforce/contradict earlier points.\n        - Examples: \"Yes.\", \"No, it's not ...\", \"Exactly, it is ...\", \"But ...\", \"Or ...\"\n    - Mentioning others: Comments that refer directly to another participant’s statement or perspective, often using phrases like \"what you said\" or \"do you know ...\". \n        - Note: Not all uses of \"you\" are mentions of others. Only when \"you\" refers to another participant’s comment or cannot be inferred as generic should it be considered a mention.\n        - Examples: \"I agree with what you said.\", \"Do you know if ...?\"\n    - Explaining previous comments: Comments that provide reasons, justifications, or clarifications for earlier statements, often using explanatory phrases.\n        - Examples: \"It's because ...\", \"The reason is ...\"\n    - Abrupt numbers or concepts: Comments that introduce numbers, statistics, or concepts that are contextually linked to previous discussion, rather than being standalone facts.\n        - Examples: \"500 is not a precise estimate\", \"The XXX model is ...\" (where \"XXX\" refers to something mentioned earlier)\n    - Unclear references: Comments that use pronouns or comparative terms whose meaning depends on previous context, making them semantically dependent on earlier comments.\n        - Examples: \"It's better than this.\", \"That is ...\", \"This approach ...\"\n    - Explicit quote mark: Comments that directly quote previous statements, often using symbols like \">\" or quotation marks to indicate a reference to earlier content.\n        - Examples: \"> ...\", '\"As mentioned above, ...\" '\n    - Comparison with only one side: Comments that make a comparison but only provide detail for one side, implying the other side is understood from previous context.\n        - Examples: \"This is better than that.\", \"Similarly, ...\"\n    - The linguistic cues above are not exhaustive, and a comment may contain more than one cue. The presence of any of these cues is often enough to classify a comment as Exploration (class 2). Always consider the whole comment and its context.\n    - In summary, if the comment seems to be semantically dependent on previous comments (e.g., refuting or supporting others' viewpoints), it is likely an Exploration comment (class 2). If it stands alone, stating an independent viewpoint, it is likely to be an Initiation comment (class 1).\n\n\nYou should only output the class number. For example, if the comment belongs to class 1, you should output 1."},
                {"role": "user", "content": f"'comment': '{new_comments[i]['body']}'"}
            ]

            model_prediction_phase = None
            while model_prediction_phase is None:
                # response = rate_limited_local_client_call(messages)
                response = local_client.chat.completions.create(
                    messages=messages,
                    model="mistralai/Mistral-7B-Instruct-v0.3"
                )
                print(f"Comment Classifier Response: {response.choices[0].message.content}")
                try:
                    model_prediction_phase = int(response.choices[0].message.content)
                except:
                    print(f"Error parsing LLM response, retrying...")

            if model_prediction_phase == 0:
                final_prediction_phase = 0
            else: # final_prediction_phase = min(reply_phase, model_prediction_phase)
                parent_comment_id = new_comments[i].get('parent_comment_id')
                if parent_comment_id is None:
                    final_prediction_phase = model_prediction_phase
                else:
                    # find: parent_comment_phase; first from new_comments, then from context.get('comments', [])
                    parent_comment_phase = None
                    for c in new_comments:
                        if c.get('id') == parent_comment_id:
                            parent_comment_phase = c.get('message_phase', None)
                            break
                    if parent_comment_phase is None:
                        for c in context.get('comments', []):
                            if c.get('id') == parent_comment_id:
                                parent_comment_phase = c.get('message_phase', None)
                                break
                    if parent_comment_phase is None:
                        parent_comment_phase = 0
                    if parent_comment_phase == 1:
                        parent_comment_phase = 2 # comments replying to phase 1 should be at least phase 2; 
                        # but for other phases, comments replying to phase x should be at least phase x
                    final_prediction_phase = max(model_prediction_phase, parent_comment_phase) # fix bug: min -> max
                
            new_comments[i]['message_phase'] = final_prediction_phase
            new_comments_phase.append(final_prediction_phase)

        assert len(new_comments_phase) == len(new_comments)

        return new_comments_phase


    def analyze_connection_batch(self, context, new_comment, candidate_comments):
        print(f"🟢: In function [analyze_connection_batch]")
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
            {build_parent_chain(comment, id_to_comment)}
            {comment.get('body', 'No content')}
            """

            prompt = f"""
            Analyze which candidate comment the new comment is most likely replying to.
            
            New Comment (Author: {new_comment.get('author_name', 'Unknown')}):
            {build_parent_chain(new_comment, id_to_comment)}
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
            print(f"[analyze_connection_batch]🐞: Analyzing batch connection for comments...")
            print(f"[analyze_connection_batch]🐞: New comment: {new_comment.get('body', 'N/A')}")
            print(f"[analyze_connection_batch]🐞: Candidates: {candidate_text}")
            print(f"[analyze_connection_batch]🐞: Result: {result_text}")
            
            try:
                result_json = json.loads(extract_json_from_markdown(result_text))
                best_match_index = result_json.get('best_match_index', 0) - 1 # 1-based index to 0-based index
                connection_score = result_json.get('connection_score', 0)
                reason = result_json.get('reason', 'No reason provided')
                print(f"[analyze_connection_batch]🐞: Best match index: {best_match_index}\n\t\tcomment: {candidate_comments[best_match_index].get('body', 'N/A')}")
                print(f"[analyze_connection_batch]🐞: Connection score: {connection_score}")
                print(f"[analyze_connection_batch]🐞: Reason: {reason}")
                print(f"[analyze_connection_batch]🐞: {'-' * 10}")
                
                # Return the best matching comment if score is above threshold
                if best_match_index >= 0 and connection_score >= 5:
                    return candidate_comments[best_match_index]
                else:
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"[analyze_connection_batch]🐞: Error parsing JSON response: {e}")
                return None
            
        except Exception as e:
            print(f"[analyze_connection_batch]🐞: Error calling ChatGPT API: {e}")
            return None

    


        try:
            context_text = formulate_tree(context, tree_id)
            
            prompt = f"""
            Analyze if the new comment is related to part of the past discussion below. The past discussion consists of the following comments:
            {context_text}
            
            New Comment (Author: {new_comment.get('author_name', 'Unknown')}):
            {build_parent_chain(new_comment, id_to_comment)}
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

    def extract_argument_and_counterargument(self, context, tree_id):
        print(f"🟢: In function [extract_argument_and_counterargument], tree_id = {tree_id}")
        """
        Use GPT to extract the main argument and the main counterargument from a tree.
        Returns a dict with 'argument' and 'counterargument' fields, each containing 'text' and 'explanation'.
        """
        context_text = formulate_tree(context, tree_id)

        print(f"[extract_argument_and_counterargument]🐞: context_text = ")
        print(context_text)

        prompt = f"""
        You are an expert discussion analyst. Given the following discussion, identify:
        1. The main argument (the central claim or position that most comments support or build upon).
        2. The main counterargument (the most significant statement that challenges, refutes, or provides an alternative perspective to the main argument).
        If there are multiple counterarguments, focus on the most representative one.

        Note:
        - Among the comments, there might be some comments asking for evidence, reasoning, or qualifier for a specific argument. These comments do not count as counterarguments.

        For each, provide the extracted text and a brief explanation of why you selected it.
        Respond in the following JSON format:
        If there is a counterargument:
        {{
            "argument": {{"text": "...", "explanation": "..."}},
            "counterargument": {{"text": "...", "explanation": "..."}}
        }}
        If there is no counterargument:
        {{
            "argument": {{"text": "...", "explanation": "..."}},
            "counterargument": {{"text": "", "explanation": "No counterargument found."}}
        }}

        Note that:
        - Providing alternative perspectives is not viewed as a counterargument. We only consider counterarguments that explicitly refute the argument.

        Discussion:
        {context_text}
        """
        print(f"[extract_argument_and_counterargument]🐞: Dicussion (context_text) = {context_text}")
        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts arguments and counterarguments. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for argument/counterargument extraction: {e}")
            result_json = {
                "argument": {"text": "", "explanation": "No argument found."},
                "counterargument": {"text": "", "explanation": "No counterargument found."}
            }
        print(f"[extract_argument_and_counterargument]🐞: Argument and counterargument analysis result = {result_json}")
        return result_json

    def score_counterargument(self, context, tree_id, argument, counterargument):
        """
        For a given tree, find the counterargument(s) and use GPT to score their evidence, reasoning, and qualifier.
        Returns a dict with the scores and explanations for each dimension.
        """
        context_text = formulate_tree(context, tree_id)

        prompt = f"""
        You are an expert discussion analyst. Given the following discussion, the extracted main argument and counterargument. For the counterargument, assess the following three dimensions:
        - Evidence: Factual information, data, examples, or references that support the counterargument. Reply to other's comments is NOT evidence.
        - Reasoning: Logical connections, explanations, or justifications that link evidence to the counterargument or show how conclusions are drawn.
        - Qualifier: Words or phrases that indicate the strength, scope, or certainty of the counterargument (e.g., "usually", "sometimes", "might", "in most cases").
        For each dimension, provide a score of 0 or 1 (0 = not present, 1 = present), and a brief explanation for your score. 
        
        Discussion:
        {context_text}

        The extracted argument and counterargument are:
        Argument:
        {argument}
        Counterargument:
        {counterargument}

        Respond in the following JSON format:
        {{
            "evidence": {{"score": <0-1>, "explanation": "..."}},
            "reasoning": {{"score": <0-1>, "explanation": "..."}},
            "qualifier": {{"score": <0-1>, "explanation": "..."}}
        }}
        """
        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes counterarguments. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for counterargument quality: {e}")
            result_json = {
                "evidence": {"score": 0, "explanation": "Counterargument not present"},
                "reasoning": {"score": 0, "explanation": "Counterargument not present"},
                "qualifier": {"score": 0, "explanation": "Counterargument not present"}
            }
        return result_json

    def score_tree(self, context, tree_id, argument):
        """
        Use GPT to score a tree on the presence of evidence, reasoning, qualifier, and counterargument.
        Store the result in context['graph']['tree_scores'][tree_id] as a dict.
        """
        # Get all comments in the tree
        context_text = formulate_tree(context, tree_id)

        prompt = f"""
        You are an expert discussion analyst. Given the following discussion and the main claim or argument, assess whether the discussion contains the following 3 dimensions. For each dimension, provide a score of 0 or 1 (0 = not present, 1 = present), and a brief explanation for your score.

        Definitions:
        - Evidence: Factual information, data, examples, or references that support the main claim or argument in the discussion. Reply to other's comments is NOT evidence.
        - Reasoning: Logical connections, explanations, or justifications that link evidence to the main claim or argument, or show how conclusions of the main claim or argument are drawn.
        - Qualifier: Words or phrases that indicate the strength, scope, or certainty of the main claim or argument (e.g., "usually", "sometimes", "might", "in most cases").

        Discussion:
        {context_text}

        The extracted main argument is:
        Main Argument:
        {argument}

        Respond in the following JSON format:
        {{
            "evidence": {{"score": <0-1>, "explanation": "..."}},
            "reasoning": {{"score": <0-1>, "explanation": "..."}},
            "qualifier": {{"score": <0-1>, "explanation": "..."}},
        }}
        """
        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes discussion quality. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for tree scoring: {e}")
            result_json = {
                "evidence": {"score": -1, "explanation": "Error parsing response."},
                "reasoning": {"score": -1, "explanation": "Error parsing response."},
                "qualifier": {"score": -1, "explanation": "Error parsing response."},
            }

        return result_json

    def list_conflicts(self, context):
        graph = context['graph']
        # nodes = graph.get('nodes', [])
        tree_ids = list_tree_ids(context)
        # Ensure arguments are present
        if 'arguments' not in graph:
            graph['arguments'] = {}
        for tid in tree_ids:
            # INT2STR
            tid = str(tid)
            if tid not in graph['arguments']:
                graph['arguments'][tid] = self.extract_argument_and_counterargument(context, tid)
        # Intra-tree: argument vs counterargument for each tree
        intra_tree = {}
        for tid in tree_ids:
            # INT2STR
            tid = str(tid)
            arg = graph['arguments'][tid].get('argument', {}).get('text', '')
            ctr = graph['arguments'][tid].get('counterargument', {}).get('text', '')
            intra_tree[tid] = {'argument': arg, 'counterargument': ctr}
        # Inter-tree: all arguments across trees
        inter_tree = {}
        for tid1 in tree_ids:
            # INT2STR
            tid1 = str(tid1)
            arg1 = graph['arguments'][tid1].get('argument', {}).get('text', '')
            inter_tree[tid1] = {'argument': arg1}
        return {'intra_tree': intra_tree, 'inter_tree': { 'dimensions': inter_tree }}

    def extract_phase_x_comments(self, context, phase):
        return [
            {
                'id': c['id'],
                'body': c['body'],
                'author_name': c['author_name']
            } for c in context.get('comments', [])+context.get('new_added_comment', []) if c.get('message_phase', 0) == phase and c.get('author_isbot', 'false') == 'false']

    def map_phase3_comments_to_conflicts(self, phase3_comments, intra_tree_conflicts, inter_tree_conflicts):
        print(f"🟢: In function [map_phase3_comments_to_conflicts]")
        # Implement this function: compare each phase 3 comment against all tree comments. 
        # Params: phase3_comments: all phase 3 comments
        # intra_tree_conflicts: all intra tree conflicts. { 1: {'argument': '...', 'counterargument': '...' }, 2: {'argument': '...', 'counterargument': '...' }, ... }
        # inter_tree_conflicts: all dimensions of inter tree conflicts. { 'dimensions': { 1: {'argument': '...' ] }, 2: {'argument': '...' }, ... }, 'comments': [ {comment_1}, {comment_2}, ... ] }
        # For each intra tree conflict let GPT give a score of whether they are related or not (0 or 1) with a reason.
        # Each comment can only be in one conflict (including both intra and inter)
        # I suggest only query GPT once and let GPT rate all connections since it might hallucinate and give all 1 scores if you compare with only one conflict each time.
        # Return { "intra_tree": { 1: [ {comment_1}, {comment_2}, ... ] , 2: [ {comment_1}, {comment_2}, ... ] , ... } , "inter_tree": [ {comment_1}, {comment_2}, ... ] }
        # 
        
        # remove intra_tree_conflicts where the counterargument is empty (i.e. no conflicts at all)
        intra_tree_conflicts_reduced = {k: v for k, v in intra_tree_conflicts.items() if v.get('counterargument', '') != ''}

        print(f"[map_phase3_comments_to_conflicts]🐞: phase3_comments = ")
        pprint(phase3_comments)
        print(f"[map_phase3_comments_to_conflicts]🐞: intra_tree_conflicts_reduced = ")
        pprint(intra_tree_conflicts_reduced)
        print(f"[map_phase3_comments_to_conflicts]🐞: inter_tree_conflicts = ")
        pprint(inter_tree_conflicts)

        Prompt = f"""
            You are analyzing comments in a discussion to determine which conflicts they relate to. 
            Comments typically involve negotiation, integration of viewpoints, and attempting to reach consensus.

            You will be given a list of existing conflicts (including two types: intra-tree conflicts and inter-tree conflicts), and a list of comments. Each comment will be mapped to at most one of the conflicts.
            Intra-tree conflict is typically composed of two different viewpoints under the same aspect. For example, "I agree with <viewpoint 1>" and "I don't agree with <viewpoint 1>" form an intra-tree conflict.
            A comment related to the intra-tree conflict should be negotiating between <viewpoint 1> and counter-<viewpoint 1>.
            Inter-tree conflict is typically composed of multiple aspects under the same topic (post). It usually requires discussion members to choose one from them as the final answer, or trying to negotiate between them. For example, "<aspect 1> is the most important", "<aspect 2> is the most important", and "<aspect 3> is the most important" form an inter-tree conflict.
            A comment related to the inter-tree conflict should be addressing the relationships of <aspect 1>, <aspect 2>, and <aspect 3>.

            In this discussion, the available conflicts are:
            Intra-tree Conflicts:
            {intra_tree_conflicts_reduced}
            Each key corresponds to a conflict.

            Inter-tree Conflicts:
            {inter_tree_conflicts}
            This is only ONE conflict. Each key corresponds to a dimension of the conflict. Qualified comments should address the relationships of more than one dimensions.
            
            Comments to Analyze:
            {phase3_comments}
            
            For each comment, determine which conflict (if any) it most relates to. Consider:
            1. Does the comment explicitly address or reference the arguments/counterarguments in any conflict?
            2. Does the comment attempt to negotiate, integrate, or find common ground related to any specific conflict?
            3. Does the comment provide solutions or consensus-building content related to any conflict?
            
            Important rules:
            - Each comment must and can only be assigned to ONE conflict (either intra-tree or inter-tree)
            - Be strict - only assign if there's a clear, explicit connection
            
            Respond with a JSON object in this exact format:
            {{
                "comment_assignments": [
                    {{
                        "comment_id": "comment_1_id",
                        "assigned_conflict_type": "intra",
                        "assigned_conflict_id": 1 | 2 | ...,
                        "confidence_score": 0-10,
                        "reason": "brief explanation"
                    }},
                    {{
                        "comment_id": "comment_2_id", 
                        "assigned_conflict_type": "inter",
                        "confidence_score": 0-10,
                        "reason": "brief explanation"
                    }}
                ]
            }}
            Note: 
            - Each comment should only appear ONCE in this JSON object.
            - If a comment is related to the inter-tree conflict, no "assigned_conflict_id" should be provided.
        """

        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes comments in a discussion to determine which conflicts they relate to. Always respond with valid JSON format."},
                {"role": "user", "content": Prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
            print(f"[map_phase3_comments_to_conflicts]🐞: result_json = ")
            pprint(result_json)
        except Exception as e:
            print(f"Error parsing GPT response for comment assignment: {e}")
            result_json = { "comment_assignments": [] }
        return_result = { "intra_tree": {} , "inter_tree": []}
        for each_intra_conflict in intra_tree_conflicts_reduced.keys():
            return_result['intra_tree'][str(each_intra_conflict)] = [] # { '1': [ {comment_1}, {comment_2}, ... ] , '2': [ {comment_1}, {comment_2}, ... ] , ... }
        
        # Track which comments have been assigned to avoid duplicates
        assigned_comments = set()

        # First pass: process all 'intra' assignments (prioritized)
        for each_allocation in result_json['comment_assignments']:
            if each_allocation['assigned_conflict_type'] == 'intra':
                comment_id_be_added = int(each_allocation['comment_id']) # str to int
                if comment_id_be_added not in assigned_comments:
                    reason_to_be_added = each_allocation['reason']
                    for each_comment in phase3_comments:
                        if each_comment['id'] == comment_id_be_added: # each_comment['id'] is int
                            each_comment['reason'] = reason_to_be_added
                            return_result['intra_tree'][str(each_allocation['assigned_conflict_id'])].append(each_comment) # each_allocation['assigned_conflict_id'] is int
                            assigned_comments.add(comment_id_be_added)
                            break
        
        # Second pass: process 'inter' assignments only for comments not already assigned
        for each_allocation in result_json['comment_assignments']:
            if each_allocation['assigned_conflict_type'] == 'inter':
                comment_id_be_added = int(each_allocation['comment_id']) # str to int
                if comment_id_be_added not in assigned_comments:
                    reason_to_be_added = each_allocation['reason']
                    for each_comment in phase3_comments:
                        if each_comment['id'] == comment_id_be_added:
                            each_comment['reason'] = reason_to_be_added
                            return_result['inter_tree'].append(each_comment)
                            assigned_comments.add(comment_id_be_added)
                            break
        return return_result

    def map_phase3_comments_to_inter_conflict_dimensions(self, inter_tree_conflicts):
        # Implement this function: compare each phase 3 comment against all inter tree dimensions. 
        # Params: inter_tree_conflicts: all dimensions of inter tree conflicts. { 'dimensions': { 1: {'argument': '...' ] }, 2: {'argument': '...' }, ... }, 'comments': [ {comment_1}, {comment_2}, ... ] }
        # For each dimension of the conflict let GPT give a score of whether the comment is related to it or not (0 or 1) with a reason.
        # I suggest only query GPT once and let GPT rate all connections since it might hallucinate and give all 1 scores if you compare with only one dimension each time.
        # Return { 1: [ {comment_1}, {comment_2}, ... ] , 2: [ {comment_1}, {comment_2}, ... ] , ... }

        Prompt = f"""
        You are analyzing comments in a discussion. You will be given a list of dimensions of a conflict and a list of comments. Determine for each comment which dimension is related to it. 
        The conflict are:
        {inter_tree_conflicts['dimensions']}

        The comments are:
        {inter_tree_conflicts['comments']}

        Respond with a JSON object in this exact format:
        {{
            "comment_assignments": [
                {{
                    "comment_index": 0 | 1 | 2 | ..., # the order of the comment in the list
                    "assigned_dimension_id": [1, 2, ...], # the id of the conflict
                    "confidence_score": 0-10,
                    "reason": "brief explanation"
                }},
                {{
                    "comment_index": 0 | 1 | 2 | ..., # the order of the comment in the list
                    "assigned_dimension_id": [1, 2, ...], # the id of the conflict
                    "confidence_score": 0-10,
                    "reason": "brief explanation"
                }},
            ]
        }}
        """

        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes comments in a discussion to determine which conflicts they relate to. Always respond with valid JSON format."},
                {"role": "user", "content": Prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for comment assignment: {e}")
            result_json = { "comment_assignments": [] }
        return_result = {}

        for each_conflict in inter_tree_conflicts['dimensions'].keys():
            return_result[each_conflict] = []
        for each_allocation in result_json['comment_assignments']:
            for each_dimension_id in each_allocation['assigned_dimension_id']: # each_dimension_id is int
                return_result[str(each_dimension_id)].append(inter_tree_conflicts['comments'][each_allocation['comment_index']])
        return return_result
    
    def determine_consensus_of_intra_conflicts(self, intra_tree_conflicts):
        print(f"🟢: In function [determine_consensus_of_intra_conflicts], intra_tree_conflicts = ")
        pprint(intra_tree_conflicts)
        # Implemenet this function: for each conflict get all phase 3 comments related to this conflict and rate the degree of consensus.
        # Params: intra_tree_conflicts: all intra tree conflicts. { 1: [ "argument": "...", "counterargument": "...", "comments": [ {comment_1}, {comment_2}, ... ] ] , 2: [ "argument": "...", "counterargument": "...", "comments": [ {comment_1}, {comment_2}, ... ] ] , ... }
        # Score from 0 to 2 (0 = no consensus, 1 = partial consensus, 2 = complete consensus) and let GPT give a reason for the scoring.
        # Return { 1: { 'score': 0, 'reason': '...' } , 2: { 'score': 1, 'reason': '...' } , ... }
        
        return_result = {} # { '1': { 'score': 0, 'reason': '...' } , '2': { 'score': 1, 'reason': '...' } , ... }
        # One prompt per conflict

        for tid in intra_tree_conflicts.keys():

            if intra_tree_conflicts[tid]['counterargument'] == '':
                return_result[tid] = { 'score': 3, 'reason': "There is no counterargument, so the conflict is not a conflict." }
            elif intra_tree_conflicts[tid].get('comments', []) == []: # counterargument exists, but no comments related to this conflict
                return_result[tid] = { 'score': 0, 'reason': "No comments related to this conflict" }
            else:
                comments_text = '\n'.join([f"Comment {i+1}: {comment}" for i, comment in enumerate(intra_tree_conflicts[tid]['comments'])])

                Prompt = f"""
                You are evaluating the degree and type of consensus of a conflict, based on the comments related to this conflict.
                The conflict is composed of an argument and a counterargument. The comments are related to the conflict.
                
                Conflict:
                Argument: {intra_tree_conflicts[tid]['argument']}
                Counterargument: {intra_tree_conflicts[tid]['counterargument']}
                
                Comments related to this conflict:
                {comments_text}

                You need to provide a score that indicates the degree and type of the consensus of this conflict.
                The score is from 0 to 3. Each score has a type of consensus:
                0: No consensus: there are no consensus of any type reached, or the comments are not related to the conflict.
                1: Clarified disagreement: the comments indicate that it is impossible to reach agreement, and the area of disagreement is clarified.
                2: Conditional agreement: the comments indicate that agreementis reached, but different aspects apply under different conditions.
                3: Full agreement: the comments indicate that agreement is reached under all circumstances.
                The reason is a brief explanation for the scoring.

                Note:
                - Be strict if you want to give a score of "clarified disagreement". For example, only one comment supporting the argument and only one comment supporting the counterargument is usually not enough to form a "clarified disagreement". There should be further discussion to clarify the different perspectives.

                Respond with a JSON object in this exact format:
                {{
                    "score": 0 | 1 | 2 | 3 , # the score of the conflict
                    "reason": "brief explanation"
                }}
                """

                response = client.chat.completions.create(
                    model=arg.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes comments in a discussion to determine which conflicts they relate to. Always respond with valid JSON format."},
                        {"role": "user", "content": Prompt}
                    ],
                    max_tokens=400,
                    temperature=0.1
                )

                result_text = response.choices[0].message.content.strip()
                try:
                    result_json = json.loads(extract_json_from_markdown(result_text))
                except Exception as e:
                    print(f"Error parsing GPT response for conflict assignment: {e}")
                    result_json = { 'score': 0, 'reason': "Error parsing GPT response for conflict assignment" }
                return_result[tid] = { 'score': result_json['score'], 'reason': result_json['reason'] }
        print(f"[determine_consensus_of_intra_conflicts]🐞: return_result = ")
        pprint(return_result)
        return return_result

    def determine_consensus_of_inter_conflicts(self, inter_tree_conflicts):
        print(f"🟢: In function [determine_consensus_of_inter_conflicts], inter_tree_conflicts = ")
        pprint(inter_tree_conflicts)
        # Implemenet this function: for each conflict get all phase 3 comments related to this conflict and rate the degree of consensus.
        # Params: inter_tree_conflicts: all inter tree conflicts. { 'dimensions': { 1: {'argument': '...', 'comments': [ {comment_1}, {comment_2}, ... ] } , 2: {'argument': '...', 'comments': [ {comment_1}, {comment_2}, ... ] } , ... }, 'comments': [ {comment_1}, {comment_2}, ... ] }
        # Score from 0 to 2 (0 = no consensus, 1 = partial consensus, 2 = complete consensus) and let GPT give a reason for the scoring.
        # Return { 1: { 'score': 0, 'reason': '...' } , 2: { 'score': 1, 'reason': '...' } , ... }
        
        # if any dimension is not covered / have no comments, the score is 0 and the reason is "The comments do not cover all dimensions of the conflict".
        all_dimension_covered = True
        for tid in inter_tree_conflicts['dimensions'].keys():
            if inter_tree_conflicts['dimensions'][tid]['coverage_rating']['score'] == '0':
                all_dimension_covered = False
                break
        if not all_dimension_covered:
            return {'score': 0, 'reason': "The comments do not cover all dimensions of the conflict"}        

        # Preprocess the input, eg. remove duplicated comments using set(); decide what to show in prompts
        conflicts_text = '\n'.join([f"- Conflict {tid}: {inter_tree_conflicts['dimensions'][tid]['argument']}" for tid in inter_tree_conflicts['dimensions'].keys()])

        inter_tree_comments_id_set = set()
        inter_tree_comments = []
        for tid in inter_tree_conflicts['dimensions'].keys():
            for comment in inter_tree_conflicts['dimensions'][tid]['comments']:
                if comment['id'] not in inter_tree_comments_id_set:
                    inter_tree_comments_id_set.add(comment['id'])
                    inter_tree_comments.append(comment)
        comments_text = '\n'.join([f"- Comment {comment['id']}: {comment['body']}" for comment in inter_tree_comments])

        Prompt = f"""
        You are evaluating the degree and type of consensus of a conflict, based on the comments related to this conflict.
        All dimensions of the conflict are (the goal of the whole discussion is to negotiate between the different views represented by these dimensions):
        {conflicts_text}

        The comments related to the conflicts are:
        {comments_text}

        You need to provide a score that indicates the degree and type of the consensus of this conflict.
        The score is from 0 to 3. Each score has a type of consensus:
        0: No consensus: there are no consensus of any type reached, or the comments are not related to the conflict.
        1: Clarified disagreement: the comments indicate that it is impossible to reach agreement, and the area of disagreement is clarified.
        2: Conditional agreement: the comments indicate that agreementis reached, but different aspects apply under different conditions.
        3: Full agreement: the comments indicate that agreement is reached under all circumstances.
        The reason is a brief explanation for the scoring.

        Note: If any of the dimensions have no comments, the score is 0 and the reason is "The comments do not cover all dimensions of the conflict".

        Respond with a JSON object in this exact format:
        {{
            "score": 0 | 1 | 2 | 3 , # the score of the conflict
            "reason": "brief explanation"
        }}
        """

        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes comments in a discussion to determine which conflicts they relate to. Always respond with valid JSON format."},
                {"role": "user", "content": Prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for conflict assignment: {e}")
            result_json = []
        return_result = {'score': result_json['score'], 'reason': result_json['reason'] }
        print(f"[determine_consensus_of_inter_conflicts]🐞: return_result = ")
        pprint(return_result)
        return return_result


    def determine_coverage_of_inter_conflicts(self, inter_tree_conflicts):
        print(f"🟢: In function [determine_coverage_of_inter_conflicts], inter_tree_conflicts = ")
        pprint(inter_tree_conflicts)
        # Implemenet this function: get all phase 3 comments related to this conflict and for each dimension determine whether the phase 3 comments cover it.
        # Params: inter_tree_conflicts: all inter tree conflicts. { 'dimensions': { 1: {'argument': '...', 'comments': [ {comment_1}, {comment_2}, ... ] } , 2: {'argument': '...', 'comments': [ {comment_1}, {comment_2}, ... ] } , ... }, 'comments': [ {comment_1}, {comment_2}, ... ] }
        # Score from 0 to 1 (0 = not covered, 1 = covered) and let GPT give a reason for the scoring.
        # Return { 1: { 'score': 0, 'reason': '...' } , 2: { 'score': 1, 'reason': '...' } , ... }

        Prompt = f"""
        You are evaluating if all dimensions of a conflict is covered by the comments related to it.
        All dimensions of the conflict are:
        {inter_tree_conflicts['dimensions']}

        The comments related to the conflicts are:
        {inter_tree_conflicts['comments']}

        Note:
        - If there are no comments for one dimension, the score is 0 and the reason is "No comments related to this dimension".

        You need to score if the comments are related to a dimension of theconflict, and give a reason for the scoring.
        The score is from 0 to 1 (0 = not covered, 1 = covered).
        The reason is a brief explanation for the scoring.

        Respond with a JSON object in this exact format:
        [
            "dimension_order": 1 | 2 | ..., # the order of the conflict in the list
            "is_covered": 0 | 1, # 0 = not covered, 1 = covered
            "reason": "brief explanation"
        ]
        """

        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes comments in a discussion to determine which conflicts they relate to. Always respond with valid JSON format."},
                {"role": "user", "content": Prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for dimension coverage assignment: {e}")
            result_json = []
        return_result = {}  
        for each_evaluation in result_json:
            return_result[str(each_evaluation['dimension_order'])] = { 'score': each_evaluation['is_covered'], 'reason': each_evaluation['reason']}
        print(f"[determine_coverage_of_inter_conflicts]🐞: return_result = ")
        pprint(return_result)
        return return_result

    def consensus_generate(self, intra_tree_conflicts, inter_tree_conflicts):
        print(f"🟢: In function [consensus_generate], intra_tree_conflicts = ")
        pprint(intra_tree_conflicts)
        print(f"inter_tree_conflicts = ")
        pprint(inter_tree_conflicts)
        # Implement this function: generate consensus for each conflict.
        # Params: intra_tree_conflicts: all intra tree conflicts. { 1: [ "argument": "...", "counterargument": "...", "comments": [ {comment_1}, {comment_2}, ... ] ] , 2: [ "argument": "...", "counterargument": "...", "comments": [ {comment_1}, {comment_2}, ... ] ] , ... }, inter_tree_conflicts: all inter tree conflicts. { 'dimensions': { 1: {'argument': '...', 'comments': [ {comment_1}, {comment_2}, ... ] } , 2: {'argument': '...', 'comments': [ {comment_1}, {comment_2}, ... ] } , ... }, 'comments': [ {comment_1}, {comment_2}, ... ] }
        # Return: a list of consensus for each conflict. { 'intra_tree': {1: consensus, 2: consensus, ...}, 'inter_tree': consensus }
        # The consensus is a list of comments that are related to the conflict.

        # TODO: simplify the conflicts
        Prompt = f"""
        You are generating consensus for a conflict.
        The input is a list of conflicts and each conflict has a list of related comments:
        intra_tree_conflicts:
        {intra_tree_conflicts}

        inter_tree_conflict:
        {inter_tree_conflicts}
        This is only one conflict with multiple dimensions.

        You need to generate consensus for each conflict based on the comments related to the conflict.
        The consensus is a comprehensive summary of the conflict and the comments related to it.

        Respond with a JSON object in this exact format:
        {{
            "intra_tree": [
                {{
                    "conflict_order": 1 | 2 | ..., # the order of the conflict in the list
                    "consensus": "...", # the consensus of the conflict
                }},
                {{
                    "conflict_order": 1 | 2 | ..., # the order of the conflict in the list
                    "consensus": "...", # the consensus of the conflict
                }},
            ],
            "inter_tree": {{
                "consensus": "...", # the consensus of the conflict
            }}
        }}
        """

        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates consensus for a conflict. Always respond with valid JSON format."},
                {"role": "user", "content": Prompt}
            ],
            max_tokens=800,
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for consensus generation: {e}")
            result_json = { "intra_tree": [], "inter_tree": "" }
        return_result = { "intra_tree": {}, "inter_tree": "" }
        for each_consensus in result_json['intra_tree']:
            return_result['intra_tree'][str(each_consensus['conflict_order'])] = each_consensus['consensus']
        return_result['inter_tree'] = result_json['inter_tree']['consensus']
        print(f"[consensus_generate]🐞: return_result = ")
        pprint(return_result)
        # should be:
        # return_result = { "intra_tree": {'1': '...', '2': '...'}, 'inter_tree': '...' }
        return return_result

    def coverage_of_consensus(self, consensus, comments_in_phase_4):
        print(f"🟢: In function [coverage_of_consensus], comments_in_phase_4 = ")
        pprint(comments_in_phase_4)
        # Implement this function: determine if the comments in phase 4 cover the consensus.
        # Params: consensus:  list of consensus [consensus, 0:intra_tree/1:inter_tree]
        # Return: a list of coverage for each consensus. { 'intra_tree': {1: coverage, 2: coverage, ...}, 'inter_tree': {1: coverage, 2: coverage, ...}}
        # The coverage is a list of comments that are related to the consensus.
        intra_tree_consensus = []
        inter_tree_consensus = []
        for each_consensus in consensus:
            if each_consensus[1] == 0:
                intra_tree_consensus.append(each_consensus[0])
            else:
                inter_tree_consensus.append(each_consensus[0])

        intra_tree_consensus_text = '\n'.join([f"Consensus {i+1}: {each_consensus['consensus']}" for i, each_consensus in enumerate(intra_tree_consensus)])
        inter_tree_consensus_text = '\n'.join([f"Consensus {i+1}: {each_consensus['consensus']}" for i, each_consensus in enumerate(inter_tree_consensus)])

        print(f"[coverage_of_consensus]🐞: intra_tree_consensus_text = ")
        print(intra_tree_consensus_text)
        print(f"[coverage_of_consensus]🐞: inter_tree_consensus_text = ")
        print(inter_tree_consensus_text)

        Prompt = f"""
        You are determining if a selected list of comments cover the consensus.
        The consensus is a list of consensus with intra-tree conflicts and the inter-tree conflict.
        Consensus of intra-tree conflicts:
        {intra_tree_consensus_text}

        Consensus of the inter-tree conflict:
        {inter_tree_consensus_text}

        The comments are:
        {comments_in_phase_4}

        You need to determine if the comments cover the consensus and give a reason for the scoring.
        The score is from 0 to 1 (0 = not covered, 1 = covered).
        The reason is a brief explanation for the scoring.

        In your response, you must include evaluatio for EACH consensus.

        Respond with a JSON object in this exact format:
        {{
            "intra_tree": [
                {{
                    "conflict_order": 1 | 2 | ..., # the order of the conflict in the list
                    "score": 0 | 1, # the score of the consensus
                    "reason": "brief explanation"
                }},
                {{
                    "conflict_order": 1 | 2 | ..., # the order of the conflict in the list
                    "score": 0 | 1, # the score of the consensus
                    "reason": "brief explanation"
                }},
            ],
            "inter_tree": 
            {{
                "score": 0 | 1, # the score of the consensus
                "reason": "brief explanation"
            }}
        }}
        """
        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that determines if the comments cover the consensus. Always respond with valid JSON format."},
                {"role": "user", "content": Prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for coverage of consensus: {e}")
            result_json = { "intra_tree": [], "inter_tree": {} }
        return_result = { "intra_tree": {}, "inter_tree": {} }
        for each_evaluation in result_json['intra_tree']:
            return_result['intra_tree'][str(each_evaluation['conflict_order'])] = { 'score': each_evaluation['score'], 'reason': each_evaluation['reason']}
        if 'inter_tree' in result_json and result_json['inter_tree']:
            return_result['inter_tree'] = { 'score': result_json['inter_tree']['score'], 'reason': result_json['inter_tree']['reason']}
        else:
            return_result['inter_tree'] = { 'score': 0, 'reason': 'No inter-tree consensus coverage data' }
        print(f"[coverage_of_consensus]🐞: return_result = ")
        pprint(return_result)
        return return_result

    def extract_reflection_comments(self, context):
        print(f"🟢: In function [extract_reflection_comments]")
        # Implement this function: extract reflection comments from the context.
        # Params: context: the context of the discussion.
        # Return: a list of reflection comments.
        # Use ChatGPT to feed into all phase 4 comments and extract all comments that are reflection of the discussion process or future applications of the dicussion result.
        phase_4_comments = self.extract_phase_x_comments(context, 4)
        print(f"[extract_reflection_comments]🐞: phase_4_comments = ")
        pprint(phase_4_comments)
        prompt = f"""
        You are extracting reflection comments from a discussion. This includes: 
        - Reflection statements of the discussion process
        - Discussion of future applications of the ideas and consensus of the discussion

        You will be given a list of comments. For each comment, you need to determine if it is a reflection comment (0 = not reflection, 1 = reflection).

        The comments are:
        {phase_4_comments}

        Respond with a JSON object in this exact format:
        [
            {{
                "comment_id": 1 | 2 | ..., # the id of the comment
                "reflection_score": 0 | 1, # the score of the reflection comment
                "reason": "...", # the reason why this is a reflection comment
            }},
            {{
                "comment_id": 1 | 2 | ..., # the id of the comment
                "reflection_score": 0 | 1, # the score of the reflection comment
                "reason": "...", # the reason why this is a reflection comment
            }},
            ...
        ]
        """
        response = client.chat.completions.create(
            model=arg.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts reflection comments from a discussion."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()
        try:
            result_json = json.loads(extract_json_from_markdown(result_text))
        except Exception as e:
            print(f"Error parsing GPT response for reflection comments: {e}")
            result_json = []
        print(f"[extract_reflection_comments]🐞: result_json = ")
        pprint(result_json)

        # filter: only keep those with reflection_score = 1
        result_json_reflection = [each_comment for each_comment in result_json if each_comment['reflection_score'] == 1]
        print(f"[extract_reflection_comments]🐞: result_json_reflection = ")
        pprint(result_json_reflection)
        return result_json_reflection

    def add_to_graph(self, context, new_comments):
        print(f"🟢: In function [add_to_graph], new_comments (len={len(new_comments)}) = {new_comments}")

        # copy new_comments
        new_comments = copy.deepcopy(new_comments)
        # filter those comments that are < current phase
        new_comments = [each_comment for each_comment in new_comments if each_comment['message_phase'] >= context['phase']]

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
            if comment["author_isbot"] == "true":
                continue
            cid = comment['id']
            phase = comment.get('message_phase', 0)
            if phase in [0, 3, 4]:
                continue

            # append new node
            if cid not in node_id_map and phase != 0 and phase != 4:
                node = {'id': cid, 'phase': phase, 'tree_id': []}
                nodes.append(node)
                node_id_map[cid] = node

            print(f"[add_to_graph]🐞: newest node_id_map = ")
            pprint(node_id_map)
            
            # PHASE 1: assign new tree id, no edge, no tree update
            if phase == 1:
                max_tree_id += 1
                node_id_map[cid]['tree_id'] = [max_tree_id]
                continue
            
            # PHASE 2: add edges, then update tree ids efficiently
            elif phase == 2:
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
                    mentioned_user = extract_mentioned_user(comment.get('body', ''))
                    
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
                        print(f"[add_to_graph]🐞: Found {len(candidate_comments)} recent comments by mentioned user @{mentioned_user}")
                        print(f"[add_to_graph]🐞: candidate_comments = {candidate_comments}")
                    else:
                        # Get most recent 10 comments
                        recent_comments = []
                        for past_node in nodes:
                            past_id = past_node['id']
                            if past_id == cid:
                                continue
                            if past_node.get('phase', 0) not in [1, 2]:
                                continue
                            if past_node.get('author_isbot', 'false') == 'true':
                                continue
                            past_comment = all_comments.get(past_id, past_node)
                            recent_comments.append(past_comment)
                        
                        # Sort by ID (assuming higher ID = more recent) and get top 10
                        recent_comments.sort(key=lambda x: x.get('id', 0), reverse=True)
                        candidate_comments = recent_comments[:10]
                        print(f"[add_to_graph]🐞: Analyzing against {len(candidate_comments)} most recent comments")
                        print(f"[add_to_graph]🐞: candidate_comments = {candidate_comments}")
                    
                    # Use batch analysis to find best connection
                    if candidate_comments:
                        best_match = self.analyze_connection_batch(context, comment, candidate_comments)
                        print(f"[add_to_graph]🐞: best_match comment = {best_match}")
                        if best_match:
                            best_match_id = best_match.get('id')
                            print(f"[add_to_graph]🐞: best_match_(comment)_id = {best_match_id}")
                            if not any(e for e in edges if (e['source'] == best_match_id and e['target'] == cid) or (e['source'] == cid and e['target'] == best_match_id)):
                                edges.append({'source': best_match_id, 'target': cid})
                                print(f"[add_to_graph]🐞: node_id_map[best_match_id] = {node_id_map[best_match_id]}")
                                best_match_tree_ids = node_id_map[best_match_id].get('tree_id', [])
                                print(f"[add_to_graph]🐞: best_match_tree_ids = {best_match_tree_ids}")
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
        print(f"[add_to_graph]🐞: before exit, graph['nodes'] = {graph['nodes']}")
        print(f"[add_to_graph]🐞: before exit, graph['edges'] = {graph['edges']}")
        return graph

    def check_discussion_sufficiency(self, context, new_comments):
        print(f"🟢: In function [check_discussion_sufficiency]")
        """检查当前阶段讨论是否充分"""
        current_phase = context['phase']
        # current_is_sufficient = context['is_sufficient']
        current_discussion_patience = context['discussion_patience']
        new_discussion_phase = current_phase
        new_discussion_patience = current_discussion_patience
        # new_is_sufficient = current_is_sufficient
        while current_phase != 6:
            if current_phase == 0:
                if len(new_comments) > 0:
                    print(f"**************************************** Enter PHASE 1 ****************************************")
                    new_discussion_phase = 1
                    new_discussion_patience = arg.MAX_PATIENCE
                    print(f"[check_discussion_sufficiency]⏰: Enter PHASE 1, Discussion Patience: set back to {arg.MAX_PATIENCE}")
                else:
                    new_discussion_phase = 0
                    new_discussion_patience = current_discussion_patience - len(new_comments)
                    print(f"[check_discussion_sufficiency]⏰: Stay in PHASE 0, Discussion Patience -= {len(new_comments)}, Discussion Patience = {new_discussion_patience}")
                    break
            elif current_phase == 1:
                #判断阶段一的评论是不是足够多
                phase_1_comments = 0
                for comment in new_comments:
                    if comment.get('message_phase', -1) == 1:
                        phase_1_comments += 1
                for comment in context['comments']:
                    if comment.get('message_phase', -1) == 1:
                        phase_1_comments += 1
                print(f"[check_discussion_sufficiency]🐞: phase_1_comments = {phase_1_comments}")
                if phase_1_comments >= self.phase_criteria['initiation']['min_comments']:
                    print(f"**************************************** Enter PHASE 2 ****************************************")
                    new_discussion_phase = 2
                    new_discussion_patience = arg.MAX_PATIENCE
                    print(f"[check_discussion_sufficiency]⏰: Enter PHASE 2, Discussion Patience: set back to {arg.MAX_PATIENCE}")
                else:
                    new_discussion_phase = 1
                    new_discussion_patience = current_discussion_patience - len(new_comments)
                    print(f"[check_discussion_sufficiency]⏰: Stay in PHASE 1, Discussion Patience -= {len(new_comments)}, Discussion Patience = {new_discussion_patience}")
                    break
            elif current_phase == 2:
                #判断阶段二每个tree是否都有讨论的各个部分
                try:
                    # For each tree, score and store the table
                    tree_ids = list_tree_ids(context)
                    if 'arguments' not in context['graph']:
                        context['graph']['arguments'] = {}
                    if 'tree_scores' not in context['graph']:
                        context['graph']['tree_scores'] = {}

                    all_trees_full = True
                    for tid in tree_ids:
                        # INT2STR
                        tid = str(tid)
                        argument_analysis_result = self.extract_argument_and_counterargument(context, tid)
                        context['graph']['arguments'][tid] = argument_analysis_result
                        argument = argument_analysis_result['argument']['text']
                        counterargument = argument_analysis_result['counterargument']['text']
                        score = self.score_tree(context, tid, argument)
                        if counterargument and counterargument != "":
                            counter_scores = self.score_counterargument(context, tid, argument, counterargument)
                            score['counterargument'] = {
                                "score": 1,
                                "explanation": "Counterargument present"
                            }
                            score['counterargument_evidence'] = counter_scores['evidence']
                            score['counterargument_reasoning'] = counter_scores['reasoning']
                            score['counterargument_qualifier'] = counter_scores['qualifier']
                        else:
                            score['counterargument'] = {
                                "score": 0,
                                "explanation": "No counterargument found"
                            }
                            score['counterargument_evidence'] = {
                                "score": 0,
                                "explanation": "No counterargument found"   
                            }
                            score['counterargument_reasoning'] = {
                                "score": 0,
                                "explanation": "No counterargument found"
                            }
                            score['counterargument_qualifier'] = {  
                                "score": 0,
                                "explanation": "No counterargument found"
                            }
                        context['graph']['tree_scores'][tid] = score
                        # # Sufficiency check: Either no counterargument or has all dimensions of counterargument
                        # if not (
                        #     score.get('evidence', {}).get('score', 0) == 1 and
                        #     score.get('reasoning', {}).get('score', 0) == 1 and
                        #     score.get('qualifier', {}).get('score', 0) == 1 and (
                        #         score.get('counterargument', {}).get('score', 0) == 0 or 
                        #         (
                        #             score.get('counterargument', {}).get('score', 0) == 1 and
                        #             score.get('counterargument_evidence', {}).get('score', 0) == 1 and
                        #             score.get('counterargument_reasoning', {}).get('score', 0) == 1 and
                        #             score.get('counterargument_qualifier', {}).get('score', 0) == 1
                        #         )
                        #     )
                        # ):
                        #     all_trees_full = False
                        # sufficiency check: Two of the three dimensions of an argument are present; 2 of the 3 dimensions of counterargument are present (if counterargument is present)
                        if not (
                            ( # only argument is present, in this case we need 2 of the 3 dimensions to be present
                                score.get('evidence', {}).get('score', 0) + score.get('reasoning', {}).get('score', 0) + score.get('qualifier', {}).get('score', 0) >= 2
                            ) and (
                                (
                                    score.get('counterargument', {}).get('score', 0) == 0
                                ) or (
                                    score.get('counterargument_evidence', {}).get('score', 0) + score.get('counterargument_reasoning', {}).get('score', 0) + score.get('counterargument_qualifier', {}).get('score', 0) >= 2
                                )
                            )
                        ):
                            all_trees_full = False
                            print(f"[check_discussion_sufficiency]🐞: Tree {tid} is not full")


                        print(f"[check_discussion_sufficiency]🐞: Tree {tid}\tArguments: ") #{context['graph']['arguments'][tid]}\n\tTree scores: {context['graph']['tree_scores'][tid]}")
                        pprint(context['graph']['arguments'][tid])
                        print(f"[check_discussion_sufficiency]🐞: Tree {tid}\tTree scores: ")
                        pprint(context['graph']['tree_scores'][tid])
                    if all_trees_full:
                        print(f"**************************************** Enter PHASE 3 ****************************************")
                        new_discussion_phase = 3
                        new_discussion_patience = arg.MAX_PATIENCE
                        print(f"[check_discussion_sufficiency]⏰: Enter PHASE 3, Discussion Patience: set back to {arg.MAX_PATIENCE}")
                    else:
                        new_discussion_phase = 2
                        new_discussion_patience = current_discussion_patience - len(new_comments)
                        print(f"[check_discussion_sufficiency]⏰: Stay in PHASE 2, Discussion Patience -= {len(new_comments)}, Discussion Patience = {new_discussion_patience}")
                        break
                except Exception as e:
                    print("Error during sufficiency check of phase 2:", e)
            elif current_phase == 3:
                #判断阶段三的评论是否充分
                try:
                    conflicts = self.list_conflicts(context)
                    context['graph']['conflicts'] = conflicts
                    print(f"[check_discussion_sufficiency]🐞: context['graph']['conflicts'] = ")
                    pprint(context['graph']['conflicts'])

                    phase3_comments = self.extract_phase_x_comments(context, 3)
                    print(f"[check_discussion_sufficiency]🐞: phase3_comments = {phase3_comments}")

                    conflicts_mapping = self.map_phase3_comments_to_conflicts(phase3_comments, conflicts['intra_tree'], conflicts['inter_tree'])
                    intra_conflicts_mapping = conflicts_mapping['intra_tree']
                    inter_conflicts_mapping = conflicts_mapping['inter_tree']

                    print(f"[check_discussion_sufficiency]🐞: intra_conflicts_mapping = ")
                    pprint(intra_conflicts_mapping)
                    print(f"[check_discussion_sufficiency]🐞: inter_conflicts_mapping = ")
                    pprint(inter_conflicts_mapping)

                    for tid, comments in intra_conflicts_mapping.items():
                        context['graph']['conflicts']['intra_tree'][tid]['comments'] = comments
                    context['graph']['conflicts']['inter_tree']['comments'] = inter_conflicts_mapping # TOD: = or += ?; seems not very important since it will re-analyze all comments each time

                    inter_conflict_dimensions_mapping = self.map_phase3_comments_to_inter_conflict_dimensions(conflicts['inter_tree'])
                    for tid, comments in inter_conflict_dimensions_mapping.items():
                        # print(context['graph']['conflicts']['inter_tree'][tid]['comments'])
                        context['graph']['conflicts']['inter_tree']['dimensions'][tid]['comments'] = comments
                    
                    intra_conflicts_consensus_rating = self.determine_consensus_of_intra_conflicts(context['graph']['conflicts']['intra_tree'])
                    for tid, rating in intra_conflicts_consensus_rating.items():
                        context['graph']['conflicts']['intra_tree'][tid]['consensus_rating'] = rating

                    inter_conflicts_coverage_rating = self.determine_coverage_of_inter_conflicts(context['graph']['conflicts']['inter_tree'])
                    for tid, rating in inter_conflicts_coverage_rating.items():
                        context['graph']['conflicts']['inter_tree']['dimensions'][tid]['coverage_rating'] = rating
                    
                    # If all ratings are 1, do self.determine_consensus_of_inter_conflicts
                    if all(rating['score'] == 1 for rating in inter_conflicts_coverage_rating.values()):
                        inter_conflicts_consensus_rating = self.determine_consensus_of_inter_conflicts(context['graph']['conflicts']['inter_tree']) # {'score': int, 'reason': str}
                        context['graph']['conflicts']['inter_tree']['consensus_rating'] = inter_conflicts_consensus_rating
                    
                    print(f"[check_discussion_sufficiency]🐞: will check if PHASE 3 is sufficient ...")
                    pprint(context['graph']['conflicts'], width=200)
                    # Advance phase only if all intra and inter-tree conflicts have consensus score >= 1 and all inter-tree conflict dimensions have score == 1
                    all_ok = True
                    for tid in list_tree_ids(context):
                        # INT2STR
                        tid = str(tid)
                        # If any of the trees have unresolved conflicts, stay in phase 3
                        if context['graph']['conflicts']['intra_tree'].get(tid, {}).get('consensus_rating', {}).get('score', 0) < 1 \
                            or context['graph']['conflicts']['inter_tree']['dimensions'].get(tid, {}).get('coverage_rating', {}).get('score', 0) < 1: # 1. intra-tree must reach consensus; 2. inter-tree must be covered
                            all_ok = False
                            break
                    if context['graph']['conflicts']['inter_tree'].get('consensus_rating', {}).get('score', 0) < 1: # inter-tree must reach consensus
                        all_ok = False
                    if all_ok:
                        print(f"**************************************** Enter PHASE 4 ****************************************")
                        new_discussion_phase = 4
                        new_discussion_patience = arg.MAX_PATIENCE
                        print(f"[check_discussion_sufficiency]⏰: Enter PHASE 4, Discussion Patience: set back to {arg.MAX_PATIENCE}")
                        # 进入阶段四，准备consensus
                        consensus_list = self.consensus_generate(context['graph']['conflicts']['intra_tree'], context['graph']['conflicts']['inter_tree']['dimensions'])
                        for tid, consensus in consensus_list['intra_tree'].items():
                            context['graph']['conflicts']['intra_tree'][tid]['consensus'] = consensus
                        context['graph']['conflicts']['inter_tree']['consensus'] = consensus_list['inter_tree']
                    else:
                        new_discussion_phase = 3
                        new_discussion_patience = current_discussion_patience - len(new_comments)
                        print(f"[check_discussion_sufficiency]⏰: Stay in PHASE 3, Discussion Patience -= {len(new_comments)}, Discussion Patience = {new_discussion_patience}")
                        break
                except Exception as e:
                    print('Error during sufficiency check of phase 3:', traceback.format_exc())
            elif current_phase == 4:
                # 判断阶段四的评论是否充分
                consensus_list = []
                for tid, consensus_data in context['graph']['conflicts']['intra_tree'].items():
                    consensus_list.append([consensus_data, 0])
                consensus_list.append([context['graph']['conflicts']['inter_tree'], 1])

                comments_in_phase_4 = self.extract_phase_x_comments(context, 4)
                coverage_of_consensus = self.coverage_of_consensus(consensus_list, comments_in_phase_4)
                # coverage_of_consensus: { 'intra_tree': {1:{ 'score': 0 | 1, 'reason': '...' }, 2:{ 'score': 0 | 1, 'reason': '...' }, ...}, 'inter_tree': { 'score': 0 | 1, 'reason': '...' }}
                context['graph']['coverage_of_consensus'] = coverage_of_consensus # save for later use
                # 如果所有的consensus都覆盖了，则进入phase 5
                all_covered = True
                for tid, coverage in coverage_of_consensus['intra_tree'].items():
                    if coverage['score'] < 1 and context['graph']['conflicts']['intra_tree'][tid]['counterargument'] != "":
                        all_covered = False
                        break
                if coverage_of_consensus['inter_tree']['score'] < 1:
                    all_covered = False
                    break
                if all_covered:
                    print(f"**************************************** Enter PHASE 5 ****************************************")
                    new_discussion_phase = 5
                    new_discussion_patience = arg.MAX_PATIENCE
                    print(f"[check_discussion_sufficiency]⏰: Enter PHASE 5, Discussion Patience: set back to {arg.MAX_PATIENCE}")
                else:
                    new_discussion_phase = 4
                    new_discussion_patience = current_discussion_patience - len(new_comments)
                    print(f"[check_discussion_sufficiency]⏰: Stay in PHASE 4, Discussion Patience -= {len(new_comments)}, Discussion Patience = {new_discussion_patience}")
                    break
            elif current_phase == 5:
                reflection_comments = self.extract_reflection_comments(context)
                print(f"[check_discussion_sufficiency]🐞: reflection_comments = {reflection_comments}")
                context['reflection_comments'] = reflection_comments
                if len(reflection_comments) > self.phase_criteria['co_construction_subphase_2']['min_comments']:
                    print(f"**************************************** Finish PHASE 5 ****************************************")
                    new_discussion_phase = 6
                    new_discussion_patience = arg.MAX_PATIENCE
                    print(f"[check_discussion_sufficiency]⏰: Enter PHASE 5, Discussion Patience: set back to {arg.MAX_PATIENCE}")
                else:
                    new_discussion_phase = 5
                    new_discussion_patience = current_discussion_patience - len(new_comments)
                    print(f"[check_discussion_sufficiency]⏰: Stay in PHASE 5, Discussion Patience -= {len(new_comments)}, Discussion Patience = {new_discussion_patience}")
                    break
            current_phase = new_discussion_phase
        return {'phase': new_discussion_phase, 'patience': new_discussion_patience}
