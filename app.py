from flask import Flask, request, jsonify
import json
from datetime import datetime
import os
import arg

# 从function模块导入各个组件
from function import CommentAnalyzer, InterventionManager, ResponseGenerator, TimerManager

app = Flask(__name__)

# 加载策略数据库
def load_strategies(Current_style):
    try:
        if Current_style == 0:
            with open('Database/Strategy/telling.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        elif Current_style == 1:
            with open('Database/Strategy/selling.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        elif Current_style == 2:
            with open('Database/Strategy/participating.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        elif Current_style == 3:
            with open('Database/Strategy/delegating.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except FileNotFoundError:
        return {}

def update_context_to_database():
    # 更新Current_context到数据库
    with open(Current_context['discussion_database_path'], 'w', encoding='utf-8') as f:
        json.dump(Current_context, f, ensure_ascii=False, indent=4)

# 定义全局变量
Current_context = { 'post': '', 
                    'comments': [], 
                    'phase': 0, 
                    # 'is_sufficient': False, 
                    'discussion_patience': arg.MAX_PATIENCE,
                    'time_patience': arg.MAX_TIME_PATIENCE,
                    'style': arg.CURRENT_STYLE,
                    'topic': arg.CURRENT_TOPIC,
                    'token': '',
                    'discussion_database_path': arg.DATABASE_PATH + str(arg.CURRENT_STYLE) + '/' + str(arg.CURRENT_TOPIC) + '.json',
                    'graph':{
                        'nodes':[],
                        'edges':[]
                    }
                    }  # 当前上下文

# 策略数据库
strategies_db = load_strategies(Current_context['style'])
# 初始化干预管理器
intervention_manager = InterventionManager(strategies_db)
analyzer = CommentAnalyzer()
response_generator = ResponseGenerator()

@app.route('/api/init', methods=['POST'])
def init():
    """初始化讨论"""
    global Current_token
    # POST/users/login 
    # 设置登陆获得token，并设置token到全局变量
    # Current_token =
    # GET/posts
    # 获取当前讨论的post内容
    # Current_context['post'] = 
    # 更新Current_context到数据库
    pass

# 计时器超时回调函数
def on_timeout_callback():
    global Current_context, Current_phase, Current_is_sufficient
    # 获得当前post的评论
    # POST /comments 
    new_comments = request.json.get('comments', [])
    # 收到新评论时重置计时器
    timer_manager.update_activity()
    # 对比new_comments和Current_context['comments']，如果new_comments和Current_context['comments']数量相同，则进行超时干预
    if len(new_comments) == len(Current_context['comments']):
        # 如果时间阶段耐心值耗尽，则进行超时干预
        Current_context['time_patience'] = Current_context['time_patience'] - 1
        if Current_context['time_patience'] <= 0:
            # 恢复时间阶段耐心值
            Current_context['time_patience'] = arg.MAX_TIME_PATIENCE
            # 进行超时干预
            intervention_strategy = intervention_manager.intervene(Current_context)
            # 生成干预响应
            response = response_generator.generate_custom_response(Current_context, intervention_strategy)
            # 发送给前端
            # POST/comments
            # 更新上下文
            Current_context['comments'].append(response)
            # 更新数据库
            update_context_to_database()
        else:
            pass
    else:
        new_added_comments = new_comments[len(Current_context['comments']):]
        # 步骤1：分析最新评论阶段
        [new_added_comments_phase, graph] = analyzer.analyze_phase(Current_context, new_added_comments)
        for i in range(len(new_added_comments)):
            new_added_comments[i]['message_phase'] = new_added_comments_phase[i]
        Current_context['graph'] = graph
        
        # 步骤2：检查当前应该协助的阶段
        analysis_result = analyzer.check_discussion_sufficiency(Current_context, new_added_comments)
        Current_context['comments'] = Current_context['comments'] + new_added_comments
        # Current_context['is_sufficient'] = analysis_result['is_sufficient']
        Current_context['discussion_patience'] = analysis_result['discussion_patience']
        Current_context['phase'] = analysis_result['phase']

        # 步骤3：决定是否需要干预和如何干预
        # 如果耐心值耗尽，则进行促进干预，不然不干预
        if Current_context['discussion_patience'] <= 0:
            # 进行超时干预
            intervention_strategy = intervention_manager.intervene(Current_context)
            # 生成干预响应
            response = response_generator.generate_custom_response(Current_context, intervention_strategy)
            # 发送给前端
            # POST/comments
            # 更新上下文
            Current_context['comments'].append(response)
            # 更新数据库
            update_context_to_database()
        else:
            pass
    return response

# 初始化计时器管理器
timer_manager = TimerManager(timeout_seconds=arg.DEFAULT_TIMEOUT_SECONDS, callback_func=on_timeout_callback)

if __name__ == '__main__':
    # 启动计时器
    timer_manager.start_timer()
    
    # 使用arg.py中的环境变量配置
    app.run(debug=arg.FLASK_DEBUG, host=arg.FLASK_HOST, port=arg.FLASK_PORT) 