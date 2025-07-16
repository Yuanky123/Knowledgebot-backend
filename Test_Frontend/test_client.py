#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime

class TestClient:
    """测试客户端，模拟前端发送消息"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_status(self):
        """测试服务器状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/timer/status")
            print(f"服务器状态: {response.status_code}")
            print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
    
    def init_discussion(self, topic="测试话题"):
        """初始化讨论"""
        try:
            payload = {"topic": topic}
            response = self.session.post(
                f"{self.base_url}/api/init",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n{'='*50}")
            print(f"初始化讨论")
            print(f"话题: {topic}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"消息: {result.get('message', '')}")
                print(f"阶段: {result.get('phase_name', '')}")
                return result
            else:
                print(f"初始化失败: {response.text}")
                return None
        except Exception as e:
            print(f"初始化失败: {e}")
            return None
    
    def send_comment(self, context, topic="测试话题"):
        """发送评论进行测试"""
        payload = {
            "context": context,
            "topic": topic
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/process_comment",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n{'='*50}")
            print(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"评论数量: {len(context)}")
            print(f"话题: {topic}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"当前阶段: {result.get('phase_name', '未知')}")
                print(f"讨论充分性: {'充分' if result.get('is_sufficient') else '不充分'}")
                print(f"执行动作: {result.get('action', '无')}")
                
                # 显示计时器状态
                timer_status = result.get('timer_status', {})
                if timer_status and timer_status.get('is_active'):
                    print(f"计时器剩余时间: {timer_status.get('remaining_time', 0)} 秒")
                
                # 显示干预信息
                intervention = result.get('intervention')
                if intervention:
                    print(f"干预类型: {intervention.get('intervention_type', '未知')}")
                    print(f"系统回复: {intervention.get('response', '无')}")
                    if intervention.get('strategy'):
                        strategy = intervention['strategy']
                        print(f"使用策略: {strategy.get('name', '未知策略')}")
                        print(f"策略描述: {strategy.get('description', '无描述')}")
                else:
                    print("系统回复: 无需干预")
                
                return result
            else:
                print(f"请求失败: {response.text}")
                return None
                
        except Exception as e:
            print(f"发送请求失败: {e}")
            return None
    
    def get_current_state(self):
        """获取当前讨论状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/state")
            if response.status_code == 200:
                state = response.json()
                print(f"\n当前讨论状态:")
                print(f"  话题: {state.get('topic', '未知')}")
                print(f"  阶段: {state.get('phase_name', '未知')} (阶段{state.get('phase', 0)})")
                print(f"  讨论充分性: {'充分' if state.get('is_sufficient') else '不充分'}")
                print(f"  评论数量: {state.get('context_length', 0)}")
                print(f"  可用策略风格: {state.get('available_styles', [])}")
                return state
            else:
                print(f"获取状态失败: {response.text}")
                return None
        except Exception as e:
            print(f"获取状态失败: {e}")
            return None
    
    def manual_intervention(self, style=None):
        """手动触发干预"""
        try:
            payload = {"style": style} if style is not None else {}
            response = self.session.post(
                f"{self.base_url}/api/manual_intervention",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"\n{result.get('message', '手动干预已执行')}")
                intervention = result.get('intervention', {})
                if intervention:
                    print(f"干预响应: {intervention.get('response', '无')}")
                    if intervention.get('strategy'):
                        strategy = intervention['strategy']
                        print(f"使用策略: {strategy.get('name', '未知')}")
                return result
            else:
                print(f"手动干预失败: {response.text}")
                return None
        except Exception as e:
            print(f"手动干预失败: {e}")
            return None
    
    def get_strategy_suggestions(self):
        """获取策略建议"""
        try:
            response = self.session.get(f"{self.base_url}/api/strategy_suggestions")
            if response.status_code == 200:
                suggestions = response.json()
                print(f"\n策略建议:")
                print(f"  当前阶段: {suggestions.get('current_phase', 0)}")
                
                available_strategies = suggestions.get('available_strategies', {})
                for style, strategies in available_strategies.items():
                    print(f"  {style} 风格策略 ({len(strategies)} 个):")
                    for strategy in strategies[:2]:  # 只显示前2个
                        print(f"    - {strategy.get('name', '未知')}: {strategy.get('description', '无描述')}")
                
                progression = suggestions.get('progression_suggestion', {})
                print(f"  阶段推进建议: {progression.get('suggestion', '无建议')}")
                
                return suggestions
            else:
                print(f"获取策略建议失败: {response.text}")
                return None
        except Exception as e:
            print(f"获取策略建议失败: {e}")
            return None
    
    def get_strategies(self):
        """获取所有策略"""
        try:
            response = self.session.get(f"{self.base_url}/api/strategies")
            if response.status_code == 200:
                strategies = response.json()
                print(f"\n策略数据库:")
                for phase_name, phase_strategies in strategies.items():
                    if phase_name == 'timeout':
                        print(f"  {phase_name}: {len(phase_strategies)} 个策略")
                        continue
                    print(f"  {phase_name} 阶段:")
                    for style_name, style_strategies in phase_strategies.items():
                        print(f"    {style_name}: {len(style_strategies)} 个策略")
                        for strategy in style_strategies[:1]:  # 只显示第一个
                            print(f"      - {strategy['name']}: {strategy['description']}")
                return strategies
            else:
                print(f"获取策略失败: {response.text}")
                return None
        except Exception as e:
            print(f"获取策略失败: {e}")
            return None
    
    def get_timer_status(self):
        """获取计时器状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/timer/status")
            if response.status_code == 200:
                status = response.json()
                print(f"\n计时器状态:")
                print(f"  是否激活: {'是' if status.get('is_active') else '否'}")
                print(f"  超时时间: {status.get('timeout_seconds', 0)} 秒")
                print(f"  剩余时间: {status.get('remaining_time', 0)} 秒")
                print(f"  超时次数: {status.get('timeout_count', 0)}")
                print(f"  总超时次数: {status.get('total_timeouts', 0)}")
                if status.get('last_activity_time'):
                    print(f"  最后活动时间: {status['last_activity_time']}")
                return status
            else:
                print(f"获取计时器状态失败: {response.text}")
                return None
        except Exception as e:
            print(f"获取计时器状态失败: {e}")
            return None
    
    def config_timer(self, timeout_seconds):
        """配置计时器"""
        try:
            payload = {"timeout_seconds": timeout_seconds}
            response = self.session.post(
                f"{self.base_url}/api/timer/config",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"\n{result.get('message', '计时器配置已更新')}")
                return True
            else:
                print(f"配置计时器失败: {response.text}")
                return False
        except Exception as e:
            print(f"配置计时器失败: {e}")
            return False
    
    def test_timeout_intervention(self, wait_seconds=5):
        """测试超时干预功能"""
        print(f"\n开始测试超时干预功能...")
        print(f"将等待 {wait_seconds} 秒来触发超时...")
        
        # 先配置一个短的超时时间
        self.config_timer(wait_seconds)
        
        # 发送一条评论来启动计时器
        self.send_comment([["测试用户", "开始测试超时功能"]], "超时测试")
        
        # 等待超时
        print(f"等待 {wait_seconds + 2} 秒...")
        for i in range(wait_seconds + 2):
            time.sleep(1)
            print(f"剩余等待时间: {wait_seconds + 2 - i - 1} 秒")
        
        # 查看结果
        print("\n超时后的状态:")
        self.get_timer_status()
        self.get_current_state()
    
    def run_four_phase_test(self):
        """运行四阶段讨论测试"""
        print("开始四阶段讨论测试...")
        
        # 初始化讨论
        print("\n=== 初始化讨论 ===")
        self.init_discussion("人工智能的发展前景")
        
        # 阶段1：初始阶段（Initiation）
        print("\n=== 阶段1：初始阶段 ===")
        context1 = [
            ["Alice", "我觉得AI技术发展很快，但还有很多挑战需要解决"]
        ]
        self.send_comment(context1, "人工智能的发展前景")
        self.get_current_state()
        
        # 添加更多评论使初始阶段充分
        context2 = [
            ["Alice", "我觉得AI技术发展很快，但还有很多挑战需要解决"],
            ["Bob", "是的，特别是在伦理和安全方面需要更多关注和规范"]
        ]
        self.send_comment(context2, "人工智能的发展前景")
        
        # 阶段2：探索阶段（Exploration）
        print("\n=== 阶段2：探索阶段 ===")
        context3 = context2 + [
            ["Charlie", "我们还需要考虑AI对就业市场的影响，这可能会带来社会问题"],
            ["Alice", "但AI也会创造新的工作机会，关键是如何进行转型和培训"],
            ["David", "教育系统也需要适应，培养适应AI时代的人才和技能"]
        ]
        self.send_comment(context3, "人工智能的发展前景")
        
        # 阶段3：协商阶段（Negotiation）
        print("\n=== 阶段3：协商阶段 ===")
        context4 = context3 + [
            ["Bob", "虽然AI带来机会，但我们不能忽视风险，需要平衡发展和安全"],
            ["Charlie", "我同意Bob的观点，我们需要制定合理的监管政策"],
            ["Eve", "监管很重要，但也不能过度限制创新，需要找到平衡点"],
            ["Alice", "也许我们可以采用分阶段、分领域的监管approach？"]
        ]
        self.send_comment(context4, "人工智能的发展前景")
        
        # 阶段4：共同构建阶段（Co-Construction）
        print("\n=== 阶段4：共同构建阶段 ===")
        context5 = context4 + [
            ["David", "基于大家的讨论，我觉得我们可以形成一个comprehensive的框架"],
            ["Bob", "确实，我们需要技术发展、伦理考量、教育改革三管齐下"],
            ["Charlie", "还要加上适度监管和国际合作，这样才能实现AI的健康发展"],
            ["Eve", "总结起来就是：负责任的创新、包容性的发展、前瞻性的治理"]
        ]
        self.send_comment(context5, "人工智能的发展前景")
        
        print("\n=== 测试总结 ===")
        self.get_current_state()
        self.get_strategy_suggestions()
    
    def run_intervention_style_test(self):
        """测试不同干预风格"""
        print("开始测试不同干预风格...")
        
        styles = {
            0: "Telling (告知)",
            1: "Selling (说服)", 
            2: "Participating (参与)",
            3: "Delegating (委托)"
        }
        
        for style_id, style_name in styles.items():
            print(f"\n=== 测试 {style_name} 风格 ===")
            result = self.manual_intervention(style_id)
            if result:
                time.sleep(1)  # 稍作停顿

def main():
    """主函数"""
    client = TestClient()
    
    # 检查服务器状态
    print("检查服务器状态...")
    if not client.test_status():
        print("服务器未运行，请先启动服务器: python app.py")
        return
    
    while True:
        print("\n" + "="*60)
        print("智能评论干预系统测试菜单:")
        print("1. 初始化讨论")
        print("2. 发送评论")
        print("3. 获取当前状态")
        print("4. 手动触发干预")
        print("5. 获取策略建议")
        print("6. 查看所有策略")
        print("7. 四阶段讨论测试")
        print("8. 干预风格测试")
        print("9. 计时器状态")
        print("10. 配置计时器")
        print("11. 测试超时干预")
        print("12. 退出")
        
        choice = input("请选择 (1-12): ").strip()
        
        if choice == "1":
            topic = input("请输入讨论话题: ").strip() or "默认话题"
            client.init_discussion(topic)
        elif choice == "2":
            topic = input("请输入话题: ").strip() or "默认话题"
            
            context = []
            print("请输入评论（格式：用户名 评论内容，输入空行结束）:")
            while True:
                comment_input = input(f"评论 {len(context)+1}: ").strip()
                if not comment_input:
                    break
                parts = comment_input.split(' ', 1)
                if len(parts) == 2:
                    user_name, content = parts
                    context.append([user_name, content])
                else:
                    context.append(["用户", comment_input])
            
            client.send_comment(context, topic)
        elif choice == "3":
            client.get_current_state()
        elif choice == "4":
            style_input = input("请输入干预风格 (0:告知, 1:说服, 2:参与, 3:委托, 回车:自动): ").strip()
            style = int(style_input) if style_input.isdigit() else None
            client.manual_intervention(style)
        elif choice == "5":
            client.get_strategy_suggestions()
        elif choice == "6":
            client.get_strategies()
        elif choice == "7":
            client.run_four_phase_test()
        elif choice == "8":
            client.run_intervention_style_test()
        elif choice == "9":
            client.get_timer_status()
        elif choice == "10":
            timeout = input("请输入超时时间（秒）: ").strip()
            try:
                timeout_seconds = int(timeout)
                client.config_timer(timeout_seconds)
            except ValueError:
                print("请输入有效的数字")
        elif choice == "11":
            wait_time = input("请输入等待时间（秒，默认5秒）: ").strip()
            try:
                wait_seconds = int(wait_time) if wait_time else 5
                client.test_timeout_intervention(wait_seconds)
            except ValueError:
                print("请输入有效的数字")
        elif choice == "12":
            print("退出测试")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main() 