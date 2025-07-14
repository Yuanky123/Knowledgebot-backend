from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

# 从function模块导入各个组件
from function import CommentAnalyzer, InterventionManager, ResponseGenerator, TimerManager

app = Flask(__name__)

# 加载策略数据库
def load_strategies():
    try:
        with open('strategies.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 策略数据库
strategies_db = load_strategies()

# 初始化组件
analyzer = CommentAnalyzer()
intervention_manager = InterventionManager(strategies_db)
response_generator = ResponseGenerator()

# 定义全局变量
Current_context = []  # 当前上下文
Current_phase = 0  # 0:start 1: initiation, 2: Exploration, 3: Negotiation, 4: Co-Construction
Current_is_sufficient = False  # 当前阶段讨论是否充分
Current_style = [0, 1, 2, 3]  # 0: Telling, 1: Selling 2: Participating 3: Delegating
Current_topic = [0, 1, 2, 3]  # 当前讨论话题
Current_patience = 10  # 当前耐心值

# 计时器超时回调函数
def on_timeout_callback():
    """当计时器超时时触发干预"""
    global Current_context, Current_phase
    
    # 使用干预管理器进行超时干预
    intervention_strategy = intervention_manager.intervene(Current_phase)
    
    # 生成干预响应
    response = response_generator.generate_custom_response(intervention_strategy, Current_context)

    # 更新上下文
    Current_context.append(response)

    return response

# 初始化计时器管理器（默认30秒超时）
timer_manager = TimerManager(timeout_seconds=30, callback_func=on_timeout_callback)

@app.route('/api/init', methods=['POST'])
def init():
    """初始化讨论"""
    global Current_context, Current_phase, Current_is_sufficient, Current_topic
    
    try:
        data = request.json or {}
        
        # 初始化全局变量
        Current_context = []
        Current_phase = 0
        Current_is_sufficient = False
        Current_topic = data.get('topic', '新讨论话题')
        
        # 重启计时器
        timer_manager.start_timer()
        
        return jsonify({
            'message': '讨论已初始化',
            'topic': Current_topic,
            'phase': Current_phase,
            'phase_name': analyzer.discussion_phases.get('initiation', '初始阶段'),
            'timer_status': timer_manager.get_status()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_comment', methods=['POST'])
def process_comment():
    """处理评论的主要端点"""
    global Current_context, Current_phase, Current_is_sufficient, Current_topic
    
    
    data = request.json
    
    # 提取数据 
    new_context = data.get('context', [])
    topic = data.get('topic', Current_topic[0])
    
    # 更新全局状态
    Current_context = new_context
    Current_topic = topic
    
    # 收到新评论时重置计时器
    timer_manager.update_activity()
    
    # 步骤1：分析最新评论阶段
    Current_context[0]['message_phase'] = analyzer.analyze_phase(Current_context[0]['message'])
    
    # 步骤2：检查当前阶段讨论充分性
    if Current_is_sufficient == False:
        is_sufficient = analyzer.check_discussion_sufficiency(Current_context, Current_phase)
        if is_sufficient:
            Current_is_sufficient = True
            Current_phase = Current_phase + 1
            Current_patience = 10
        else:
            Current_is_sufficient = False

    # 步骤3：决定是否需要干预和如何干预
    if is_sufficient:
        # 讨论充分，推进到下一阶段
        # 使用推荐的策略风格进行阶段过渡干预
        # 消耗耐心值
        Current_patience = Current_patience - 1
        if Current_patience <= 0:
            # 耐心值耗尽，触发超时干预
            Current_phase = Current_phase + 1
            Current_is_sufficient = False
            # 干预
    else:
        # 讨论不充分，进行促进干预
        Current_patience = Current_patience - 1
        if Current_patience <= 0:
            # 干预
    

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """获取所有策略"""
    return jsonify(strategies_db)


# 计时器相关的API端点
@app.route('/api/timer/status', methods=['GET'])
def get_timer_status():
    """获取计时器状态"""
    try:
        status = timer_manager.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timer/start', methods=['POST'])
def start_timer():
    """启动计时器"""
    try:
        timer_manager.start_timer()
        return jsonify({'message': '计时器已启动', 'status': timer_manager.get_status()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timer/stop', methods=['POST'])
def stop_timer():
    """停止计时器"""
    try:
        timer_manager.stop_timer()
        return jsonify({'message': '计时器已停止', 'status': timer_manager.get_status()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timer/reset', methods=['POST'])
def reset_timer():
    """重置计时器"""
    try:
        timer_manager.reset_timer()
        return jsonify({'message': '计时器已重置', 'status': timer_manager.get_status()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timer/config', methods=['POST'])
def config_timer():
    """配置计时器"""
    try:
        data = request.json
        timeout_seconds = data.get('timeout_seconds', 30)
        
        timer_manager.set_timeout(timeout_seconds)
        
        return jsonify({
            'message': f'计时器配置已更新，超时时间: {timeout_seconds}秒',
            'status': timer_manager.get_status()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 启动计时器
    print("启动计时器...")
    timer_manager.start_timer()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 