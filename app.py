from flask import Flask, request, jsonify
import json
from datetime import datetime
import os
import arg
import requests

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
Current_context = { 
                    'post': {
                        'title': '',
                        'body': '',
                        'id': '',
                        'author_name': ''
                    }, 
                    'comments': [], 
                    'phase': 0, 
                    # 'is_sufficient': False, 
                    'discussion_patience': arg.MAX_PATIENCE,
                    'time_patience': arg.MAX_TIME_PATIENCE,
                    'style': arg.CURRENT_STYLE,
                    'topic': arg.CURRENT_TOPIC,
                    'token': '',
                    'discussion_database_path': arg.DATABASE_PATH + '/' + str(arg.CURRENT_TOPIC) + '.json',
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

def make_api_request(method, url, headers=None, json_data=None, retry_on_auth_error=True):
    print(f"Making {method} request to {url}")
    global Current_context
    
    # Set default headers if not provided
    if headers is None:
        headers = {}
    
    # Add authorization header if token exists
    if Current_context.get('token'):
        headers['Authorization'] = f'Bearer {Current_context["token"]}'
    
    # Make the initial request
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=json_data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Check for authentication errors
        if retry_on_auth_error and response.status_code in [401, 403]:
            print(f"Authentication error ({response.status_code}), attempting to re-login...")
            
            # Try to re-login
            login()
            
            # If we have a new token, retry the request
            if Current_context.get('token'):
                headers['Authorization'] = f'Bearer {Current_context["token"]}'
                
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=json_data)
                elif method.upper() == 'PUT':
                    response = requests.put(url, headers=headers, json=json_data)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, headers=headers)
                
                print(f"Re-authenticated request completed with status: {response.status_code}")
            else:
                print("Re-login failed, cannot retry request")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise

def login():
    print("Logging in...")
    global Current_context
    
    # POST /users/login - 设置登录获得token
    login_payload = {
        'username': arg.USERNAME,
        'password': arg.PASSWORD
    }
    
    try:
        login_response = requests.post(f"{arg.FRONTEND_URL}/users/login", json=login_payload)
        login_response.raise_for_status()  # Raise an exception for bad status codes
        
        result = login_response.json()
        
        # Extract and print the required fields
        if 'user' in result and 'selectedsubreddit' in result['user']:
            print(f"Selected Subreddit: {result['user']['selectedsubreddit']}")
        
        if 'token' in result:
            print(f"Token: {result['token']}")
            Current_context['token'] = result['token']
        
        
        
    

        
    except requests.exceptions.RequestException as e:
        print(f"Error making login request: {e}")

@app.route('/api/init', methods=['POST'])
def init():
    """初始化讨论"""
    global Current_context
    print('Starting initialization...')
    
    try:
        # First, perform login to get token
        login()
        
        # GET/posts - 获取当前讨论的post内容
        post_response = make_api_request('GET', f"{arg.FRONTEND_URL}/posts")
        
        if post_response.status_code == 200:
            post_data = post_response.json()
            if len(post_data) > 0:
                Current_context['post']['title'] = post_data[0]['title']
                Current_context['post']['body'] = post_data[0]['body']
                Current_context['post']['id'] = post_data[0]['id']
                Current_context['post']['author_name'] = post_data[0]['author_name']
                print(f"Post loaded: {Current_context['post']['title']}")
            else:
                print("No post found in response")
        else:
            print(f"Failed to get posts, status code: {post_response.status_code}")
        
        # 更新Current_context到数据库
        update_context_to_database()
        
    except Exception as e:
        print(f"Error during initialization: {e}")



# 计时器超时回调函数
def on_timeout_callback(timeout_info=None):
    global Current_context, Current_phase, Current_is_sufficient
    # 获得当前post的评论
    # GET /comments 
    
    # Check if we have a post ID, if not fetch posts again
    if not Current_context['post']['id']:
        print("No post ID found, fetching posts again...")
        post_response = make_api_request('GET', f"{arg.FRONTEND_URL}/posts")
        if post_response.status_code == 200:
            post_data = post_response.json()
            # print(post_data)
            if len(post_data) > 0:
                Current_context['post']['title'] = post_data[0]['title']
                Current_context['post']['body'] = post_data[0]['body']
                Current_context['post']['id'] = post_data[0]['id']
                Current_context['post']['author_name'] = post_data[0]['author_name']
                print(f"Updated post: {Current_context['post']['title']}")
            else:
                print("No post found in response")
                return
    
    new_comments_response = make_api_request('GET', f"{arg.FRONTEND_URL}/comments/{Current_context['post']['id']}")
    new_comments = new_comments_response.json().get('comments', [])
    # print(new_comments)
    # 收到新评论时重置计时器
    timer_manager.update_activity()
    # 对比new_comments和Current_context['comments']，如果new_comments和Current_context['comments']数量相同，说明没有新的评论，则进行超时干预
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
            # comment_response = make_api_request('POST', f"{arg.FRONTEND_URL}/comments", json_data=response)
            # comment_response_data = comment_response.json()
            # # print(comment_response_data)
            # if comment_response.status_code == 200:
            #     print("Comment posted successfully")
            # else:
            #     print("Failed to post comment")
            # # 更新上下文
            # Current_context['comments'].append(comment_response_data)
            # 更新数据库
            update_context_to_database()
        else:
            print(f"Current patience: {Current_context['discussion_patience']}")
            pass
    else:
        new_added_comments = new_comments[len(Current_context['comments']):]
        # 步骤1：分析最新评论阶段
        new_added_comments_phase = analyzer.analyze_phase(Current_context, new_added_comments)
        for i in range(len(new_added_comments)):
            new_added_comments[i]['message_phase'] = new_added_comments_phase[i]
        # print(new_added_comments)
        Current_context['graph'] = analyzer.add_to_graph(Current_context, new_added_comments)
        # print(Current_context['comments'])
        # print(new_added_comments)
        # Current_context['comments'] = Current_context['comments'] + new_added_comments
        # print(Current_context['comments'])

        # 步骤2：检查当前应该协助的阶段
        analysis_result = analyzer.check_discussion_sufficiency(Current_context, new_added_comments)
        # Current_context['is_sufficient'] = analysis_result['is_sufficient']
        Current_context['discussion_patience'] = analysis_result['patience']
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
            # comment_response_data = comment_response.json()
            # # print(comment_response_data)
            # if comment_response.status_code == 200:
            #     print("Comment posted successfully")
            # else:
            #     print("Failed to post comment")
            # # 更新上下文
            # Current_context['comments'].append(comment_response_data)
            # 更新数据库
        elif Current_context['discussion_patience'] ==4:
            # 到达终点
            pass
        else:
            pass
        update_context_to_database()
    # return response

# 初始化计时器管理器
timer_manager = TimerManager(timeout_seconds=arg.DEFAULT_TIMEOUT_SECONDS, callback_func=on_timeout_callback)

if __name__ == '__main__':
    # init()
    # 启动计时器
    timer_manager.start_timer()
    
    # 使用arg.py中的环境变量配置
    app.run(debug=arg.FLASK_DEBUG, host=arg.FLASK_HOST, port=arg.FLASK_PORT) 