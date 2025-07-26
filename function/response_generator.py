#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import json
from . import utils

from openai import OpenAI

client = OpenAI(
    base_url='https://api.zhizengzeng.com/v1',
    api_key="sk-zk23e12430a30075ee3d9858364a99d800867112483439ff"
    )


class ResponseGenerator:
    """回复生成器"""
    
    def __init__(self):
        self.response_history = []
    
    def generate_custom_response(self, context, strategy):
        """根据策略生成回复"""

        intervention_style = context['style'] # 0: telling, 1: selling, 2: participating, 3: delegating
        current_phase = context['phase']

        post_information = f'''
            Post Title: {context['post']['title']}
            Post Body: {context['post']['body']}
            '''
        arguments_information = context['graph']['arguments']

        if current_phase == 1:
            # extract 1. existing aspects 2. one new angle from arguments
            prompt = f'''
            You will be given a post and a list of arguments extracted from the comments.
            Your task is to:
            1. For each argument, extract the key aspects of the argument. The "key aspects" should be concise, in no more than 3 words.
            2. Based on the existing arguments and the post, propose a new angle of discussion. The new angle of discussion should be concise, in no more than 3 words.
            3. Give a reason why this new angle is important to push the discussion forward.

            The post is:
            {post_information}

            The arguments are:
            {arguments_information}

            Respond with a JSON object containing:
            - "key_aspects": a list of key aspects of the arguments
            - "new_angle_of_discussion": string, the new angle of discussion
            - "reason": string, the reason why this new angle is important to push the discussion forward. The format should be "Because <reason>."
            '''

            response = client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts key aspects of arguments and proposes new angles of discussion."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            # TODO: 要不要限制bot在这一阶段不要直接提出integrated的观点？
            response = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content))
            existing_aspects = response.get('key_aspects', [])
            new_angle = response.get('new_angle_of_discussion', '')
            reason = response.get('reason', '')

            if intervention_style in [0, 1]: # telling, selling
                intervention_message = strategy.format(
                    existing_aspects=existing_aspects,
                    new_angle=new_angle
                )
            elif intervention_style == 2: # participating
                intervention_message = strategy.format(
                    existing_aspects=existing_aspects,
                    new_angle=new_angle,
                    reason=reason
                )
            elif intervention_style == 3: # delegating
                intervention_message = strategy
            else:
                raise ValueError(f"Invalid intervention style: {intervention_style}")

        elif current_phase == 2: # phase 2: exploration
            # select a tree (context['graph']['tree_scores'][tid]) where either the argument is not sufficient or the counterargument is not sufficient
            # Target: tree_id, argument/counterargument, dimension
            for tid in random.sample(list(context['graph']['tree_scores'].keys()), 1):
                score = context['graph']['tree_scores'][tid]
                # first check if the argument is sufficient
                if score.get('evidence', {}).get('score', 0) == 0:
                    target_argument = context['graph']['arguments'][tid]['argument']
                    missing_support = 'evidence'
                elif score.get('reasoning', {}).get('score', 0) == 0:
                    target_argument = context['graph']['arguments'][tid]['argument']
                    missing_support = 'reasoning'
                elif score.get('qualifier', {}).get('score', 0) == 0:
                    target_argument = context['graph']['arguments'][tid]['argument']
                    missing_support = 'qualifier'
                elif score.get('counterargument', {}).get('score', 0) == 1 and score.get('counterargument_evidence', {}).get('score', 0) == 0:
                    target_argument = context['graph']['arguments'][tid]['counterargument']
                    missing_support = 'evidence'
                elif score.get('counterargument', {}).get('score', 0) == 1 and score.get('counterargument_reasoning', {}).get('score', 0) == 0:
                    target_argument = context['graph']['arguments'][tid]['counterargument']
                    missing_support = 'reasoning'
                elif score.get('counterargument', {}).get('score', 0) == 1 and score.get('counterargument_qualifier', {}).get('score', 0) == 0:
                    target_argument = context['graph']['arguments'][tid]['counterargument']
                    missing_support = 'qualifier'
                else:
                    continue
            # Not all arguments are sufficient in phase 2. So we should eventually find one that is insufficient.
            # adapt to different intervention styles
            if intervention_style == 0: # telling
                intervention_message = strategy.format(
                    target_argument=target_argument,
                    missing_support=missing_support
                )
            elif intervention_style == 1: # selling
                # generate the benefits of the missing support
                prompt = f'''
                You will be given a post, and an argument in response to the post. However, the argument is insufficient in one of the following dimensions: evidence, reasoning, or qualifier.
                The meaning of each dimension is as follows:
                - Evidence: Factual information, data, examples, or references that support the argument.
                - Reasoning: Logical connections, explanations, or justifications that link evidence to the argument, or show how conclusions of the argument are drawn.
                - Qualifier: Words or phrases that indicate the strength, scope, or certainty of the argument (e.g., "usually", "sometimes", "might", "in most cases").

                Your task is to persuade the readers to provide more support on the missing dimension for the argument. 
                Specifically, you should output the benefits of adding this missing dimension to the argument.
                
                Note:
                - The benefits should be closely related to the discussion topic, but not hollow words.
                - The benefits should be based on current argument and show how can it be improved compared to the current version.

                The post is:
                {post_information}

                The argument is:
                {target_argument['text']}
                It is insufficient in the following dimension: {missing_support}.
                
                Respond with a JSON object containing:
                - "benefits": string, the benefits of adding {missing_support} to the argument. The format should be "Because this <benefits>." Please be concise, in no more than one sentence.
                '''
                response = client.chat.completions.create(
                    model="gemini-2.0-flash",
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing online discussions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                response = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content))
                benefits = response.get('benefits', '')
                intervention_message = strategy.format(
                    target_argument=target_argument['text'],
                    missing_support=missing_support,
                    benefits=benefits
                )
            elif intervention_style == 2: # participating
                # generate a user-like comment asking for more support on the missing dimension
                prompt = f'''
                You will be given a post, and an argument in response to the post. However, the argument is insufficient in one of the following dimensions: evidence, reasoning, or qualifier.
                The meaning of each dimension is as follows:
                - Evidence: Factual information, data, examples, or references that support the argument.
                - Reasoning: Logical connections, explanations, or justifications that link evidence to the argument, or show how conclusions of the argument are drawn.
                - Qualifier: Words or phrases that indicate the strength, scope, or certainty of the argument (e.g., "usually", "sometimes", "might", "in most cases").
                
                Your task is to act like a user in this discussion, and ask for more support on the missing dimension for the argument.
                Note:
                - The comment should be closely related to the discussion topic, but not hollow words. For example, you cannot just say "Could you provide more evidence/reasoning/qualifier?".
                - The comment should be based on current argument and semantically related to it. 
                
                The post is:
                {post_information}
                
                The argument is:
                {target_argument['text']}
                It is insufficient in the following dimension: {missing_support}.
                
                Respond with a JSON object containing:
                - "comment": string, the comment asking for more support on the missing dimension. 
                '''
                response = client.chat.completions.create(
                    model="gemini-2.0-flash",
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing online discussions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                response = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content))
                comment = response.get('comment', '')
                intervention_message = comment
            elif intervention_style == 3: # delegating
                intervention_message = strategy

        elif current_phase == 3: # phase 3: negotiation
            # select unsolved conflict: first intra-tree, then inter-tree
            target_tree = None
            for tid in random.sample(list(context['graph']['conflicts']['intra_tree'].keys()), 1):
                if context['graph']['conflicts']['intra_tree'][tid]['consensus_rating']['score'] == 0:
                    target_tree = context['graph']['conflicts']['intra_tree'][tid]
                    break
            if target_tree != None:
                if intervention_style in [0, 1, 2]:
                    if intervention_style == 0: # telling
                        prompt = f'''
                        You will be given a post, and two conflicting arguments related to one same aspect.
                        Your task is to find a direction to continue the discussion, which is helpful to resolve the conflict.

                        Note: 
                        - While guiding the users to resolve the conflict, you should focus on the original post. Do not be off-topic when resolving the conflict.

                        The post is:
                        {post_information}
                        
                        One of the arguments is:
                        {target_tree['argument']}
                        The other (conflicting) argument is:
                        {target_tree['counterargument']}
                        
                        Respond with a JSON object containing:
                        - "comment": string, the direction to continue the discussion. The format should be "There seems to be a conflict between <the two arguments>. Please <direction>."
                        '''
                    elif intervention_style == 1: # selling
                        prompt = f'''
                        You will be given a post, and two conflicting arguments related to one same aspect.
                        Your task is to find a direction to continue the discussion, which is helpful to resolve the conflict.

                        Note: 
                        - While guiding the users to resolve the conflict, you should focus on the original post. Do not be off-topic when resolving the conflict.

                        The post is:
                        {post_information}
                        
                        One of the arguments is:
                        {target_tree['argument']}
                        The other (conflicting) argument is:
                        {target_tree['counterargument']}
                        
                        Respond with a JSON object containing:
                        - "comment": string, the direction to continue the discussion. The format should be "There seems to be a conflict between <the two arguments>. Please <direction>, because <the benefits to discuss this direction>."
                        '''
                    elif intervention_style == 2: # participating
                        prompt = f'''
                        You will be given a post, and two conflicting arguments related to one same aspect.
                        Your task is to act like a user in this discussion, and generate a comment, which is supposed to be helpful to resolve the conflict.

                        Note: 
                        - While trying to resolve the conflict, you should keep your comment related to the original post. Do not be off-topic when resolving the conflict.

                        The post is:
                        {post_information}
                        
                        One of the arguments is:
                        {target_tree['argument']}
                        The other (conflicting) argument is:
                        {target_tree['counterargument']}

                        Respond with a JSON object containing:
                        - "comment": string, the user-like comment to resolve the conflict. 
                        '''
                    response = client.chat.completions.create(
                        model="gemini-2.0-flash",
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing online discussions."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1
                    )
                    response = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content))
                    intervention_message = response.get('comment', '')
                elif intervention_style == 3: # delegating
                    intervention_message = strategy
                else:
                    raise ValueError(f"Invalid intervention style: {intervention_style}")
            else: # inter-tree conflict
                dimensions = context['graph']['conflicts']['inter_tree']['dimensions']
                under_addressed_arguments = []
                for tid in dimensions:
                    if dimensions[tid].get('coverage_rating', {}).get('score', 1) == 0:
                        under_addressed_arguments.append(dimensions[tid].get('argument', ''))
                # we assume that len(under_addressed_arguments) must be greater than 0
                under_addressed_arguments_all = ''.join([f'Argument {i+1}: {arg}\n' for i, arg in enumerate(under_addressed_arguments)])
                
                if intervention_style in [0, 1, 2]:
                    if intervention_style == 0: # telling
                        prompt = f'''
                        You will be given a post, and a list of under-addressed arguments related to the post.
                        Your task is to generate a comment to address the under-addressed arguments. 
                        
                        Note:
                        - When mentioning the under-addressed arguments, you should summarize each argument as a keyword or short phrase. Do not copy the original argument text.
                        - While addressing the under-addressed arguments, you should focus on the original post. Do not be off-topic.

                        The post is:
                        {post_information}

                        The under-addressed arguments are:
                        {under_addressed_arguments_all}

                        Respond with a JSON object containing:
                        - "comment": string, the comment to address the under-addressed arguments. The format should be: "Considering the current discussion progress, here are ... other ... <under_addressed_arguments_keywords>. Please include them into the discussion."
                        '''
                    elif intervention_style == 1: # selling
                        prompt = f'''
                        You will be given a post, and a list of under-addressed arguments related to the post.
                        Your task is to generate a comment to address the under-addressed arguments, and tell the users the benefits of including them into the discussion.
                        
                        Note:
                        - When mentioning the under-addressed arguments, you should summarize each argument as a keyword or short phrase. Do not copy the original argument text.
                        - While addressing the under-addressed arguments, you should focus on the original post. Do not be off-topic. Focus on why including these arguments into the discussion is beneficial or important to the whole discussion.
                        - Be concise while ensuring the comment is concrete enough.

                        The post is:
                        {post_information}

                        The under-addressed arguments are:
                        {under_addressed_arguments_all}

                        Respond with a JSON object containing:
                        - "comment": string, the comment to address the under-addressed arguments. The format should be: "Considering the current discussion progress, here are ... other ... <under_addressed_arguments_keywords>. Please include them into the discussion because <the benefits of doing so>."
                        '''
                    elif intervention_style == 2: # participating
                        prompt = f'''
                        You will be given a post, and a list of under-addressed arguments related to the post.
                        Your task is to act like a user in this discussion, and generate a comment to address the under-addressed arguments.
                        Specifically, given the under-addressed arguments, you should generate a comment trying to include them into the discussion. 
                        
                        Note:
                        - When mentioning the under-addressed arguments, you should summarize each argument as a keyword or short phrase. Do not copy the original argument text.
                        - While addressing the under-addressed arguments, you should focus on the original post. Do not be off-topic.
                        - Be concise while ensuring the comment is concrete enough.
                        - Make the tone as natural as possible, like a real user. Do not use confusing opening words like "That's a good question!" because it requires someone to propose a question before you, otherwise it will seem unnatural.
                        - These under-addressed arguments are assumed to be conflicting with each other. Thus, you should try to negotiate and balance them.

                        The post is:
                        {post_information}

                        The under-addressed arguments are:
                        {under_addressed_arguments_all}

                        Respond with a JSON object containing:
                        - "comment": string, the user-like comment to address the under-addressed arguments."
                        '''
                        # TODO: test needed; using context closer to our final setting: "who is the most evil person in the world" instead of "how can we make people happy in cities"
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing online discussions."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1
                    )
                    response = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content))
                    intervention_message = response.get('comment', '')
                elif intervention_style == 3: # delegating
                    intervention_message = strategy
                else:
                    raise ValueError(f"Invalid intervention style: {intervention_style}")
        elif current_phase == 4: # phase 4: integration
            pass
                
            

        # if intervention_style == 0:
        #     pass
        #     intervention_message = ''
        # elif intervention_style == 1:
        #     pass
        #     intervention_message = ''
        # elif intervention_style == 2:
        #     pass
        #     intervention_message = ''
        # elif intervention_style == 3: # delegating
        #     intervention_message = strategy

        # response = {
        #     'body': 'test reply',
        #     'post_id': context['post']['id'],
        #     'parent_comment_id': None,
        # }
        return response