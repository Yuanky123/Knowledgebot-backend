<<<<<<< HEAD
# backend
=======
# 智能评论干预系统

这是一个简单的后端框架，用于智能监听和干预评论讨论。

## 功能特性

- **动态监听**: 实时分析评论阶段和讨论充分性
- **策略选择**: 基于讨论状态自动选择合适的干预策略
- **智能回复**: 根据策略生成个性化的回复内容
- **热更新**: 支持在线重新加载策略数据库
- **统计分析**: 提供详细的讨论和干预统计信息
- **自定义回复**: 支持自定义模板生成回复
- **测试工具**: 内置模拟前端的测试客户端

## 项目结构

```
backend/
├── app.py                      # 主应用程序
├── strategies.json             # 策略数据库
├── test_client.py              # 测试客户端
├── requirements.txt            # 依赖包
├── README.md                   # 说明文档
└── function/                   # 功能模块
    ├── __init__.py            # 模块初始化
    ├── comment_analyzer.py     # 评论分析器
    ├── intervention_manager.py # 干预管理器
    └── response_generator.py   # 回复生成器
```

## 模块说明

### 1. CommentAnalyzer (评论分析器)
- 分析评论阶段（初始、发展、深化、结论）
- 评估讨论充分性
- 提供讨论统计信息

### 2. InterventionManager (干预管理器)
- 判断是否需要干预
- 选择合适的干预策略
- 记录干预历史和统计

### 3. ResponseGenerator (回复生成器)
- 根据策略生成回复
- 支持自定义模板
- 记录回复历史和统计

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动，支持热更新。

### 3. 运行测试

在另一个终端窗口中运行测试客户端：

```bash
python test_client.py
```
>>>>>>> c737f62 (create)
