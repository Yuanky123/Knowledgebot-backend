#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

        if current_phase == 1:
            # extract 1. existing aspects 2. one new angle from arguments
            post_information = f'''
            Post Title: {context['post']['title']}
            Post Body: {context['post']['body']}
            '''

            arguments_information = context['graph']['arguments']

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
            # NOTE: passed simple unit test using 0.json
            # TODO: 要不要限制bot在这一阶段不要直接提出integrated的观点？
            existing_aspects = response.choices[0].message.content.get('key_aspects', [])
            new_angle = response.choices[0].message.content.get('new_angle_of_discussion', '')

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

        elif current_phase == 2: # phase 2: discussion
            

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