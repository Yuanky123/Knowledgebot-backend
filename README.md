# 智能讨论干预系统 (Intelligent Discussion Intervention System)

一个基于Flask的智能讨论辅导系统，能够实时监听、分析和干预在线讨论，提供个性化的讨论引导和支持。

## 🎯 项目概述

本系统旨在通过智能化的讨论分析和干预机制，提升在线讨论的质量和效率。系统能够：
- 实时分析讨论阶段和参与度
- 基于不同讨论策略提供个性化干预
- 支持多种讨论风格的智能切换
- 提供讨论过程的全面统计和分析

## ✨ 功能特性

### 🔍 智能分析
- **阶段识别**: 自动识别讨论的四个阶段（启动、探索、协商、共建）
- **参与度评估**: 实时评估讨论充分性和参与者活跃度
- **内容分析**: 深度分析讨论内容的质量和方向

### 🎛️ 干预管理
- **策略选择**: 支持四种讨论策略（告知型、推销型、参与型、委托型）
- **智能干预**: 基于讨论状态自动选择合适的干预时机和方式
- **个性化回复**: 根据讨论情境生成个性化的引导回复

### ⏱️ 时间管理
- **计时器机制**: 智能监控讨论活跃度和超时情况
- **耐心值管理**: 动态调整系统对讨论进展的期望
- **活动检测**: 实时检测讨论活动并相应调整策略

### 🔧 配置管理
- **环境变量**: 支持.env文件配置系统参数
- **策略热更新**: 支持在线更新讨论策略库
- **灵活配置**: 可配置超时时间、耐心值等关键参数

## 🏗️ 技术架构

### 后端框架
- **Flask**: 轻量级Web框架
- **Python 3.x**: 主要开发语言
- **JSON**: 数据存储和交换格式

### 核心模块
- **CommentAnalyzer**: 评论分析器
- **InterventionManager**: 干预管理器
- **ResponseGenerator**: 回复生成器
- **TimerManager**: 计时器管理器
- **ResponseHandler**: 响应处理器

### 数据存储
- **策略数据库**: JSON格式存储讨论策略
- **知识建构**: 支持知识建构相关数据

## 📦 安装指南

### 环境要求
- Python 3.7+
- pip包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env
# 编辑.env文件，设置你的配置
vim .env
```

5. **启动服务**
```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动。

## 🔧 配置说明

### 环境变量配置

在`.env`文件中配置以下参数：

```env
# Flask应用配置
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 讨论策略配置
CURRENT_STYLE=0          # 0:Telling, 1:Selling, 2:Participating, 3:Delegating
CURRENT_TOPIC=0          # 当前讨论话题ID
DEFAULT_TIMEOUT_SECONDS=30  # 默认超时时间
MAX_PATIENCE=10          # 最大耐心值 # discussion patience
INTERVENTION_THRESHOLD=5  # 干预阈值

# 数据库配置
DATABASE_URL=sqlite:///database.db

# API配置
API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

### 策略配置

系统支持四种讨论策略，每种策略对应不同的干预风格：

- **Telling (告知型)**: 直接提供信息和指导
- **Selling (推销型)**: 说服性的引导和建议
- **Participating (参与型)**: 协作式的讨论参与
- **Delegating (委托型)**: 授权式的讨论支持

## 📁 项目结构

```
backend/
├── app.py                          # Flask主应用程序
├── arg.py                          # 环境变量配置模块
├── requirements.txt                # Python依赖包
├── test_client.py                  # 测试客户端
├── strategies.json                 # 策略配置文件
├── .env                           # 环境变量配置
├── .env.example                   # 环境变量模板
├── README.md                      # 项目说明文档
├── Database/                      # 数据库目录
│   ├── Strategy/                  # 策略数据库
│   │   ├── telling.json          # 告知型策略
│   │   ├── selling.json          # 推销型策略
│   │   ├── participating.json    # 参与型策略
│   │   └── delegating.json       # 委托型策略
│   └── Knowlege_building/         # 知识建构相关数据
└── function/                      # 核心功能模块
    ├── __init__.py               # 模块初始化
    ├── comment_analyzer.py       # 评论分析器
    ├── intervention_manager.py   # 干预管理器
    ├── response_generator.py     # 回复生成器
    ├── response_handler.py       # 响应处理器
    └── timer_manager.py          # 计时器管理器
```

## 🚀 使用说明

### 基本使用流程

1. **初始化讨论**
```bash
POST /api/init
```
设置讨论环境和参数

2. **发送评论**
```bash
POST /api/comments
{
  "comments": ["用户评论内容..."]
}
```

3. **接收系统干预**
系统会根据讨论情况自动生成干预回复

### 测试客户端

使用内置的测试客户端进行功能验证：

```bash
python test_client.py
```

## 🛠️ 开发指南

### 添加新的讨论策略

1. 在`Database/Strategy/`目录下创建新的策略文件
2. 按照现有格式定义四个讨论阶段的策略
3. 更新`arg.py`中的策略配置

### 扩展分析功能

1. 在`function/comment_analyzer.py`中添加新的分析方法
2. 更新`InterventionManager`以支持新的分析结果
3. 相应更新响应生成逻辑

### 自定义干预策略

1. 修改`function/intervention_manager.py`
2. 添加新的干预判断逻辑
3. 更新策略选择算法

## 📊 API接口

### 讨论初始化
```http
POST /api/init
Content-Type: application/json

{
  "topic": "讨论话题",
  "participants": ["参与者列表"]
}
```

### 评论处理
```http
POST /api/comments
Content-Type: application/json

{
  "comments": ["评论内容数组"]
}
```

### 计时器配置
```http
POST /api/timer/config
Content-Type: application/json

{
  "timeout_seconds": 30
}
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📝 许可证

本项目基于MIT许可证开源。详情请参阅LICENSE文件。

## 📧 联系信息

如有问题或建议，请联系项目维护者。

---

*本项目致力于提升在线讨论的质量和效率，通过智能化的干预机制促进更好的知识建构和协作学习。*


# TODO:
- [x] fetch的评论的顺序可能不对
  是乱序，需要按照id或created_at排序

- [x] 中间发新评论，fetch到的是None
  原因：return的comment不是按照任何一个时间顺序来排列的
  [ ] 要不要关掉modify comments的功能？

- [x] 阶段1 要忽略所有阶段>1的comment
以此类推
(后面的阶段不需要再fetch原始comment了)

活动时间已更新: 2025-08-01 16:32:41
    🐞: New comments detected; len(new_comments) = 69, len(Current_context['comments']) = 66
    **** Analyzing comment 0: I think it is important to have good public transportations so that people won't spend a lot of time commuting.
    Comment Classifier Response: 1
- [x] 是Append和sort by time 有冲突

- [x] bot生成的评论Phase的赋值
  - [x] bot style 为participating时，当前处在哪个阶段，bot message 就赋值为哪个阶段； 其他风格的bot message phase全部为0
    - [ ] 另一个观察： bot自己的评论即使算作Phase，但并不直接导致大家继续。只有有人发了新评论，才能够真的推进到下一阶段。(但对整个系统影响不大，甚至可能是我们想要的效果？)

- [ ] 重复评论会当做两个不同的argument

- [x] 所有有random的地方都输出一个log

- [ ] 并发测试：60人同时post comments

- [ ] 读写context，（加锁？）modify需要一个文件副本？interface?

- [ ] comment phase analyzer: 如果之前已经有了Phase，则不重新分析
  但感觉没有那么必要

- [x] phase 3 consensus 分类
  + 三种consensus的定义

- [x] phase 3 第二阶段的response generator

- [x] phase 4 - 1 consensus type 加进Template

- [x] phase 4 - 2 for above mentioned consensus, please反思应用

- [x] phase 4 - 2 饱和判断条件（threshold条comment属于反思或应用）

- [ ] 运行bot 几个人测试一下

- [ ] id_to_comment 变量 容易没考虑到new_added_comments


- [x] 提取counterargument有false positive: 
    "2": {
                "argument": {
                    "text": "I think we should enforce strict labor laws so that people don't overwork.",
                    "explanation": "This statement is the central claim of the discussion, advocating for the enforcement of labor laws to prevent overworking, which is a concern that resonates with many individuals."
                },
                "counterargument": {
                    "text": "We should also make connections among neighborhood to build a strong community.",
                    "explanation": "While this statement does not directly refute the main argument, it introduces an alternative perspective that emphasizes community building rather than focusing solely on labor laws. It suggests that addressing overwork might also involve fostering community connections, which could be seen as a different approach to the issue."
                }
            },
    Note: 部分是因为一开始assign tree的时候搞错了
    (在prompt中加了，但是还没找到case测试，不确定是否有效) - comment analyzer line 308
    - [ ] analyze_connection_batch中也可以加：(respond A: we can also consider B2 => group with B1?)


- [ ] bot干预策略，random选择target的时候，尽量不要反复持续干预同一个点

- [ ] argument score evaluation: 先输出原因再输出分数；给出三个dimension的定义？因为现在很明显的评论都分不出来 eg. The phrase 'I think' indicates a personal opinion, which serves as a qualifier for the strength of the main argument.', - 但还行

- [x] 总是输出time patience + discussion patience


- [x] discussion patience < 0 时每回合都会intervene？这是符合我们预期的吗
  并非如此


- [x] In reply to:加换行 (build_chain)

- [ ] 确定phase 2 sufficient criteria (现在用的比较宽松)

- [ ] 所有输入comment list的地方按照id排序



- [x] 三者随机: qualifier evidence reasoning


- [x] LLM 重写generated message







- [o] delegating 不需要LLM重写
- [ ] delegating 只在每个阶段开始时发一条消息


- [ ] participating 不能是问句

- [o] Initiation措辞：new angle -> new claim distinct from existing claims

- [o] Participating style prompt: 
  - [o] {"role": "system", "content": "You are a user in an online knowledge community."},
  - [o] no "user-like"
  - [o] participating的结尾鼓励user参与/补充 Who can ....?

- [o] 删掉“you”之类的用词,不用给人员的代指；anyone可以
    solution: 在最后的改写prompt中

- [ ] 确保bot的评论在任何情况下都不计入graph； 

- [o] phase 2 counter argument supporting factor也要3选2


- [x] fine-tune llm : reply 1: >= 2

- [ ] coverage_of_consensus: 不考虑intra-tree with no counterargument

- [x] increase temperature for LLM

concurrency
- [x] LLM concurrent api cal
    solution: use python 3.10+; 3.9 will raise error
- [ ] -> backend
- [ ] -> frontend

- [ ] 莫名其妙出现的4个tree（yuanhao test的四个case之一）


- [ ] 所有log 加timestamp




 get phase x comments 的时候会不会把bot也考虑进去？