import os
from dotenv import load_dotenv

# 载入环境变量
load_dotenv()

# Flask应用配置
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))

# 数据库配置
DATABASE_PATH = os.getenv('DATABASE_PATH', 'Database/')

# API密钥和认证
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
API_KEY = os.getenv('API_KEY', 'your-api-key-here')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')

# 第三方服务配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# 应用特定配置
DEFAULT_TIMEOUT_SECONDS = int(os.getenv('DEFAULT_TIMEOUT_SECONDS', '60'))
MAX_PATIENCE = int(os.getenv('MAX_PATIENCE', '20')) # 讨论阶段最大耐心值，单位条数
MAX_TIME_PATIENCE = int(os.getenv('MAX_TIME_PATIENCE', '5')) # 时间阶段最大耐心值，单位轮次
INTERVENTION_THRESHOLD = int(os.getenv('INTERVENTION_THRESHOLD', '5'))
CURRENT_STYLE = int(os.getenv('CURRENT_STYLE', '0')) # 0: Telling, 1: Selling 2: Participating 3: Delegating
CURRENT_TOPIC = int(os.getenv('CURRENT_TOPIC', '0')) # 0: 新讨论话题 1: 新讨论话题 2: 新讨论话题 3: 新讨论话题

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')

# 跨域配置
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')

# 文件上传配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))

# 邮件配置
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')

# 环境标识
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# 打印配置信息（仅在开发环境）
if FLASK_ENV == 'development':
    print(f"环境变量载入完成:")
    print(f"  - Flask环境: {FLASK_ENV}")
    print(f"  - Flask调试模式: {FLASK_DEBUG}")
    print(f"  - Flask主机: {FLASK_HOST}")
    print(f"  - Flask端口: {FLASK_PORT}")
    print(f"  - 数据库URL: {DATABASE_URL}")
    print(f"  - 默认超时时间: {DEFAULT_TIMEOUT_SECONDS}秒")
    print(f"  - 最大耐心值: {MAX_PATIENCE}")
