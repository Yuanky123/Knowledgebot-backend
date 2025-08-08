#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import e
import random
import json

from . import utils
import arg
from pprint import pprint

from openai import OpenAI

client = OpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key=arg.OPENAI_API_KEY
    )

class ResponseGenerator:
    """回复生成器"""
    
    def __init__(self):
        self.response_history = []
    
    def generate_custom_response(self, context, strategy):
        print(f"🟢: in function [generate_custom_response], current_phase = {context['phase']}")
        """根据策略生成回复"""

        intervention_style = context['style'] # 0: telling, 1: selling, 2: participating, 3: delegating
        current_phase = context['phase']

        post_information = f'''
            Post Title: {context['post']['title']}
            Post Body: {context['post']['body']}
            '''

        if current_phase == 1 or current_phase == 0:

            phase_1_comments = [comment for comment in context['comments'] if comment.get('message_phase', 1) == 1]
            if len(phase_1_comments) == 0:
                phase_1_comments_text = "(No comments yet)"
            else:
                phase_1_comments_text = '\n'.join([f"Comment {i+1}: {comment['body']}" for i, comment in enumerate(phase_1_comments)])

            parent_comment_id = None
            prompt = f'''
            You will be given a post and a list of comments expressing different opinions on the post.
            Your task is to:
            1. Extract the key aspects of all the comments. The "key aspects" should be concise, in a word or short phrase. It is not necessary to have a one-to-one correspondence between the key aspects and the comments. For example, two comments that are very similar in content can be summarized into one key aspect. However, you should not over-summarize the comments so that the key aspects are too few and too general.
            2. Based on the existing comments and the post, propose a new angle of discussion which is independent from all the existing arguments. The new angle of discussion should be concise, in no more than 3 words.
            3. Give a reason why this new angle is important to push the discussion forward.

            The post is:
            {post_information}

            The arguments are:
            {phase_1_comments_text}

            Respond with a JSON object containing:
            - "key_aspects": a list of key aspects of the arguments
            - "new_angle_of_discussion": string, the new angle of discussion
            - "reason": string, the reason why this new angle is important to push the discussion forward. The format should be "Because <reason>."
            '''

            response = client.chat.completions.create(
                model=arg.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts key aspects of arguments and proposes new angles of discussion."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            response = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content))
            existing_aspects = response.get('key_aspects', [])
            new_angle = response.get('new_angle_of_discussion', '')
            reason = response.get('reason', '')

            if intervention_style == 0: # telling
                intervention_message = strategy.format(
                    existing_aspects="We have discussed " + ', '.join(existing_aspects) if len(existing_aspects) > 0 else "Seems like we have not discussed much yet",
                    new_angle=new_angle
                )
            elif intervention_style == 1: # selling
                intervention_message = strategy.format(
                    existing_aspects="We have discussed " + ', '.join(existing_aspects) if len(existing_aspects) > 0 else "Seems like we have not discussed much yet",
                    new_angle=new_angle,
                    benefits=reason.replace('Because ', '')
                )
            elif intervention_style == 2: # participating
                prompt = f'''
                You will be given a post, existing comments expressing different opinions on the post, and a new angle of discussion.
                Your task is to, based on the new angle of discussion, generate a user-like comment proposing this new angle of discussion.

                The post is:
                {post_information}

                The existing arguments are:
                {phase_1_comments_text}

                The new angle of discussion is:
                {new_angle}

                Respond with a JSON object containing:
                - "comment": string, the user-like comment proposing the new angle of discussion.
                '''
                response = client.chat.completions.create(
                    model=arg.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing online discussions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                intervention_message = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
            elif intervention_style == 3: # delegating
                intervention_message = strategy
            else:
                raise ValueError(f"Invalid intervention style: {intervention_style}")

        elif current_phase == 2: # phase 2: exploration
            print(f"[generate_custom_response]🐞: current_phase = 2, select a tree where the argument is not sufficient")
            # select a tree (context['graph']['tree_scores'][tid]) where either the argument is not sufficient or the counterargument is not sufficient
            target_argument, missing_support = None, None
            for tid in random.sample(list(context['graph']['tree_scores'].keys()), len(context['graph']['tree_scores'])):
                score = context['graph']['tree_scores'][tid]
                # TODO: current loose sufficiency check
                if score.get('evidence', {}).get('score', 0) + score.get('reasoning', {}).get('score', 0) + score.get('qualifier', {}).get('score', 0) >= 2:
                    print(f"[generate_custom_response]🐞: Tree {tid} is sufficient, skip ...")
                    continue
                else:
                    print(f"[generate_custom_response]🐞: Tree {tid} is not sufficient, select it ...")

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
                    raise ValueError(f"Should not reach here")
                break

            print(f"[generate_custom_response]🐞: Intervention target (tid = {tid}, missing_support = {missing_support}): {target_argument}")

            # Not all arguments are sufficient in phase 2. So we should eventually find one that is insufficient.
            # get parent_comment_id from tid + argument/counterargument
            parent_comment_id = None
            argument_text = target_argument['text']
            for comment in context['comments']:
                if comment['body'] is None:
                    continue
                if argument_text in comment['body']:
                    parent_comment_id = comment['id']
                    break
            
            if intervention_style == 0: # telling
                intervention_message = strategy.format(
                    target_argument=target_argument['text'],
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
                    model=arg.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing online discussions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                benefits = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('benefits', '')
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
                
                Your task is to act like a user in this discussion, and provide support on the given missing dimension for the given argument.
                Note:
                - The comment should be based on current argument and semantically related to it. 
                
                The post is:
                {post_information}
                
                The argument is:
                {target_argument['text']}
                It is insufficient in the following dimension: {missing_support}.
                
                Respond with a JSON object containing:
                - "comment": string, the comment providing support on the given missing dimension. You should first show that you (more or less) agree with the argument, and then provide the required support.
                '''
                response = client.chat.completions.create(
                    model=arg.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert in analyzing online discussions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                intervention_message = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
            elif intervention_style == 3: # delegating
                intervention_message = strategy
            else:
                raise ValueError(f"Invalid intervention style: {intervention_style}")

        elif current_phase == 3: # phase 3: negotiation
            parent_comment_id = None
            # select unsolved conflict: first intra-tree, then inter-tree
            target_tree = None
            for tid in random.sample(list(context['graph']['conflicts']['intra_tree'].keys()), len(context['graph']['conflicts']['intra_tree'])):
                print(f"[generate_custom_response]🐞: Checking intra-tree conflict {tid} ...")
                pprint(context['graph']['conflicts']['intra_tree'][tid])
                if context['graph']['conflicts']['intra_tree'][tid].get('counterargument', "") != "" and \
                    context['graph']['conflicts']['intra_tree'][tid].get('consensus_rating', {}).get('score', 0) == 0:
                    target_tree = context['graph']['conflicts']['intra_tree'][tid]
                    print(f"[generate_custom_response]🐞: Found unresolved intra-tree conflict {tid}! The tree {tid} is:")
                    break
            if target_tree != None: # find a intra-tree conflict
                # TODO: if comment number < x: do original prompt, if comment number >= x: do new prompt that asks for clarified disagreements.
                if len(target_tree['comments']) < arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD: 
                    print(f"[generate_custom_response]🐞: Comments number < {arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD}, using strategy[0] ...")
                    strategy = strategy[0]
                    # first generate: under_addressed_conflicts, benefits
                    prompt = f'''
                    You will be given a post, and a pair of under-addressed conflicting arguments related to one same aspect.
                    Your task is to summarize the under-addressed conflicts in a concise way, like a short phrase. Also, shortly explain why resolving this conflict is important to the discussion.

                    The post is:
                    {post_information}
                    
                    The argument is:
                    {target_tree['argument']}
                    The counterargument is:
                    {target_tree['counterargument']}
                    
                    Respond with a JSON object containing:
                    - "conflicts": string, the under-addressed conflicts. 
                    - "benefits": string, the benefits of resolving this conflict. The format should be "Because <benefits>."
                    '''
                    response = client.chat.completions.create(
                        model=arg.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing online discussions."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1
                    )
                    conflicts = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('conflicts', '')
                    benefits = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('benefits', '')

                    if intervention_style == 0: # telling
                        intervention_message = strategy.format(
                            conflicts=conflicts,
                        )
                    elif intervention_style == 1: # selling
                        intervention_message = strategy.format(
                            conflicts=conflicts,
                            benefits=benefits.replace('Because', 'because')
                        )
                    elif intervention_style == 2: # participating
                        prompt = f'''
                        You will be given a post, and a pair of conflicting arguments related to one same aspect.
                        Your task is to act like a user in this discussion, and generate a comment trying to resolve the conflict.

                        The post is:
                        {post_information}
                        
                        The argument is:
                        {target_tree['argument']}
                        The counterargument is:
                        {target_tree['counterargument']}
                        
                        Respond with a JSON object containing:
                        - "comment": string, the user-like comment trying to resolve the conflict.
                        '''
                        response = client.chat.completions.create(
                            model=arg.OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.1
                        )
                        comment = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
                        intervention_message = comment
                    elif intervention_style == 3: # delegating
                        intervention_message = strategy
                    else:
                        raise ValueError(f"Invalid intervention style: {intervention_style}")
                else:
                    print(f"[generate_custom_response]🐞: Comments number >= {arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD}, using strategy[1] ...")
                    strategy = strategy[1]
                    # no longer try to reach consensus, and try to reach clarified disagreements.

                    if intervention_style in [0, 1]: # telling or selling, only need to summarize the conflict in one phrase
                        prompt = f'''
                        You will be given a post, and a pair of conflicting arguments related to one same aspect. 
                        Your task is to summarize the pair of conflicting arguments in a concise way, like a short phrase.

                        The post is:
                        {post_information}
                        
                        The argument is:
                        {target_tree['argument']}
                        The counterargument is:
                        {target_tree['counterargument']}
                        
                        Respond with a JSON object containing:
                        - "conflicts": string, the summary of the conflict with both sides. 
                        '''
                        response = client.chat.completions.create(
                            model=arg.OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.1
                        )
                        conflicts = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('conflicts', '')

                        intervention_message = strategy.format(
                            conflicts=conflicts,
                        ) # same for both telling and selling
                        
                        # TODO: delete this part after testing
                        # if intervention_style == 0: # telling
                        #     intervention_message = strategy.format(
                        #         conflicts=conflicts,
                        #     )
                        # elif intervention_style == 1: # selling
                        #     intervention_message = strategy.format(
                        #         conflicts=conflicts,
                        #     )
                        # else:
                        #     raise ValueError(f"Invalid intervention style: {intervention_style}")
                    elif intervention_style == 2: # participating
                        # comments_text: first sort by id, then join with \n
                        comments_text = '\n'.join([f"Comment {comment['id']}: {comment['body']}" for comment in sorted(target_tree['comments'], key=lambda x: x['id'])])
                        
                        prompt = f'''
                        You will be given a post, and a pair of conflicting arguments related to one same aspect, and comments related to this conflict.
                        This conflict has gone through a lot of discussions, but consensus still cannot be reached.
                        Your task is to act like a user in this discussion, and based on existing comments, generate a new comment clarifying the current disagreement between the two sides, and ask for additional comments from the members to further clarify the disagreement.

                        The post is:
                        {post_information}
                        
                        The argument is:
                        {target_tree['argument']}
                        The counterargument is:
                        {target_tree['counterargument']}

                        The comments related to this conflict are:
                        {comments_text}

                        Your comment should be structured as:
                        1) state that disagreement exists (e.g. "It seems that <the topic> has not been reached a consensus.")
                        2) summarize the current disagreement shown in the comments (e.g. "<A> thinks xxx under condition xxx, but <B> thinks yyy under condition yyy.")
                        3) ask for additional comments from the members to further clarify the disagreement. (e.g. "Do you have any thoughts or suggestions on this summary?")
                        
                        Respond with a JSON object containing:
                        - "comment": string, the user-like comment trying to clarify the current disagreement between the two sides.
                        '''
                        response = client.chat.completions.create(
                            model=arg.OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.1
                        )
                        comment = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
                        intervention_message = comment
                    elif intervention_style == 3: # delegating
                        intervention_message = strategy
                    else:
                        raise ValueError(f"Invalid intervention style: {intervention_style}")
            else: # inter-tree conflict
                print(f"[generate_custom_response]🐞: No intra-tree conflict found, checking inter-tree conflict which has not been covered...")
                dimensions = context['graph']['conflicts']['inter_tree']['dimensions']
                under_addressed_arguments = []
                for tid in dimensions:
                    if dimensions[tid].get('coverage_rating', {}).get('score', 0) == 0:
                        under_addressed_arguments.append(dimensions[tid].get('argument', ''))
                if len(under_addressed_arguments) > 0: # some trees has not been covered - do not count arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD
                    strategy = strategy[0]
                    print(f"[generate_custom_response]🐞: found under_addressed_arguments: {under_addressed_arguments}")
                    under_addressed_arguments_all = ''.join([f'Argument {i+1}: {arg}\n' for i, arg in enumerate(under_addressed_arguments)])

                    prompt = f'''
                    You will be given a post, and a list of under-addressed arguments related to the post.
                    Your task is to concisely summarize each under-addressed argument as a keyword or short phrase. Also, shortly explain why taking these under-addressed arguments into the negotiation process is important for the whole discussion.

                    The post is:
                    {post_information}

                    The under-addressed arguments are:
                    {under_addressed_arguments_all}

                    Respond with a JSON object containing:
                    - "under_addressed_arguments_keywords": a list of keywords or short phrases summarizing the under-addressed arguments.
                    - "reason": string, the reason why taking these under-addressed arguments into the negotiation process is important for the whole discussion. The format should be "Because <reason>."
                    '''
                    response = client.chat.completions.create(
                        model=arg.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": "You are an expert in analyzing online discussions."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1
                    )
                    under_addressed_arguments_keywords = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('under_addressed_arguments_keywords', [])
                    reason = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('reason', '')
                    
                    if intervention_style == 0: # telling
                        intervention_message = strategy.format(
                            conflicts='the tensions between ' + ', '.join(under_addressed_arguments_keywords) + " haven't been considered"
                        )
                    elif intervention_style == 1: # selling
                        intervention_message = strategy.format(
                            conflicts='the tensions between ' + ', '.join(under_addressed_arguments_keywords) + " haven't been considered",
                            benefits=reason.replace('Because', 'because')
                        )
                    elif intervention_style == 2: # participating
                        prompt = f'''
                        You will be given a post, and a list of under-addressed arguments related to the post.
                        Your task is to act like a user in this discussion, and generate a comment trying to include these under-addressed arguments into the negotiation process.

                        The post is:
                        {post_information}

                        The under-addressed arguments are:
                        {under_addressed_arguments_all}
                        
                        Respond with a JSON object containing:
                        - "comment": string, the user-like comment trying to include these under-addressed arguments into the negotiation process.
                        '''
                        response = client.chat.completions.create(
                            model=arg.OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.1
                        )
                        comment = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
                        intervention_message = comment
                        # TODO: 纯粹address某几个tree，生成的评论感觉有点不自然
                    elif intervention_style == 3: # delegating
                        intervention_message = strategy
                    else:
                        raise ValueError(f"Invalid intervention style: {intervention_style}")
                else: # all trees have been covered, but consensus has not been reached
                    print(f"[generate_custom_response]🐞: No under-addressed arguments found, checking inter-tree consensus score ... score = {context['graph']['conflicts']['inter_tree'].get('consensus_rating', {})}")
                    if len(context['graph']['conflicts']['inter_tree']['comments']) < arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD:
                        print(f"[generate_custom_response]🐞: Comments number < {arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD}, using strategy[0] ...")
                        strategy = strategy[0]

                        # prepare arguments_text
                        arguments_text = '\n'.join([f"Argument {i}: {arg['argument']}" for i, arg in dimensions.items()])

                        # comments_text: comments need to be sorted by id
                        comments_text = '\n'.join([f"Comment {i+1}: {comment['body']}" for i, comment in enumerate(sorted(context['graph']['conflicts']['inter_tree']['comments'], key=lambda x: x['id']))])

                        if intervention_style in [0, 1]: # telling or selling, only need to summarize the arguments in one phrase and give a reason
                            prompt = f'''
                            You will be given a post, a list of different arguments related to the post (each argument is related to one aspect), and comments that are trying to reach a consensus among these arguments.
                            Different arguments are competing with each other, and consensus has not been reached.
                            Your task is to summarize each argument in a concise way, like a short phrase. Also, to encourage members to reach a consensus among these arguments, give a reason why it is important to reach a consensus among them.
                            Note:
                            - The comments are trying to reach a consensus among these arguments, so they are related to the arguments.
                            - The comments are trying to reach a consensus among these arguments, so they are related to the arguments.

                            The post is:
                            {post_information}

                            The arguments are:
                            {arguments_text}

                            Respond with a JSON object containing:
                            - "arguments_keywords": a list of keywords or short phrases summarizing each argument.
                            - "reason": string, the reason why it is important to reach a consensus among these arguments. The format should be "Because <reason>."
                            '''

                            response = client.chat.completions.create(
                                model=arg.OPENAI_MODEL,
                                messages=[
                                    {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.1
                            )
                            arguments_keywords = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('arguments_keywords', [])
                            reason = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('reason', '')

                            if intervention_style == 0: # telling
                                intervention_message = strategy.format(
                                    conflicts='the tensions between ' + ', '.join(arguments_keywords),
                                )
                            elif intervention_style == 1: # selling
                                intervention_message = strategy.format(
                                    conflicts='the tensions between ' + ', '.join(arguments_keywords),
                                    benefits=reason.replace('Because', 'because')
                                )
                        elif intervention_style == 2: # participating

                            prompt = f'''
                            You will be given a post, and a list of different arguments related to the post, each argument is related to one aspect. 
                            Different arguments are competing with each other, and consensus has not been reached.
                            Your task is to act like a user in this discussion, and, based on existing comments, generate a new comment that is trying to reach a consensus among these arguments.

                            The post is:
                            {post_information}

                            The arguments are:
                            {arguments_text}

                            The comments related to this conflict are:
                            {comments_text}

                            Respond with a JSON object containing:
                            - "comment": string, the user-like comment trying to reach a consensus among these arguments.
                            '''
                            response = client.chat.completions.create(
                                model=arg.OPENAI_MODEL,
                                messages=[
                                    {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.1
                            )
                            comment = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
                            intervention_message = comment
                        elif intervention_style == 3: # delegating
                            intervention_message = strategy
                        else:
                            raise ValueError(f"Invalid intervention style: {intervention_style}")
                    else: # too many comments, just tell members to clarify the disagreement (telling, selling, delegating), or try to clarify the disagreement by the bot itself and ask for additional comments (participating)
                        print(f"[generate_custom_response]🐞: Comments number >= {arg.PHASE_3_CLARIFIED_DISAGREEMENT_THRESHOLD}, using strategy[1] ...")
                        strategy = strategy[1]

                        # prepare arguments_text
                        arguments_text = '\n'.join([f"Argument {i}: {arg['argument']}" for i, arg in dimensions.items()])

                        # comments_text: comments need to be sorted by id
                        comments_text = '\n'.join([f"Comment {i+1}: {comment['body']}" for i, comment in enumerate(sorted(context['graph']['conflicts']['inter_tree']['comments'], key=lambda x: x['id']))])

                        if intervention_style in [0, 1]: # telling or selling, only need to summarize the arguments in one phrase
                            prompt = f'''
                            You will be given a post, and a list of different arguments related to the post, each argument is related to one aspect. 
                            Different arguments are competing with each other, and consensus has not been reached.
                            Your task is to summarize each argument in a concise way, like a short phrase.

                            The post is:
                            {post_information}

                            The arguments are:
                            {arguments_text}

                            Respond with a JSON object containing:
                            - "arguments_keywords": a list of keywords or short phrases summarizing each argument.
                            '''
                            response = client.chat.completions.create(
                                model=arg.OPENAI_MODEL,
                                messages=[
                                    {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.1
                            )
                            arguments_keywords = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('arguments_keywords', [])
                            intervention_message = strategy.format(
                                conflicts='the tensions between ' + ', '.join(arguments_keywords),
                            )
                        elif intervention_style == 2: # participating
                            prompt = f'''
                            You will be given a post, and a list of different arguments related to the post (each argument is related to one aspect), and comments that are trying to reach a consensus among these arguments.
                            Different arguments are competing with each other, and consensus has not been reached.
                            Your task is to act like a user in this discussion, and, based on existing comments, generate a new comment clarifying the current disagreement, and ask for additional comments.

                            The post is:
                            {post_information}

                            The arguments are:
                            {arguments_text}

                            The comments related to this conflict are:
                            {comments_text}
                            
                            Your comment should be roughly structured as:
                            1) state that disagreement exists (e.g. "It seems that <the topic> has not been reached a consensus.")
                            2) summarize the current disagreement shown in the comments (e.g. "<A> thinks xxx under condition xxx, but <B> thinks yyy under condition yyy.")
                            3) ask for additional comments from the members to further clarify the disagreement. (e.g. "Do you have any thoughts or suggestions on this summary?")

                            Respond with a JSON object containing:
                            - "comment": string, the user-like comment trying to clarify the current disagreement between the two sides.
                            '''
                            response = client.chat.completions.create(
                                model=arg.OPENAI_MODEL,
                                messages=[
                                    {"role": "system", "content": "You are an expert in analyzing online discussions."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.1
                            )
                            comment = json.loads(utils.extract_json_from_markdown(response.choices[0].message.content)).get('comment', '')
                            intervention_message = comment
                        elif intervention_style == 3: # delegating
                            intervention_message = strategy
                        else:
                            raise ValueError(f"Invalid intervention style: {intervention_style}")

        # TODO: for phase 4: select unresolved conflict randomly and ask to resolve it.
        elif current_phase == 4: # phase 4: integration
            parent_comment_id = None
            intervention_message = 'test reply'
        # TODO: for phase 4.2, prompt users to post refliections directly.
        elif current_phase == 5: # phase 5: co-construction subphase 2
            parent_comment_id = None
            intervention_message = 'test reply'

        response = {
            'body': intervention_message,
            'post_id': context['post']['id'],
            'parent_comment_id': parent_comment_id,
        }
        return response