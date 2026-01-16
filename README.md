# LlamaMed WebUI - 医学影像诊断报告纠错系统

![Vue](https://img.shields.io/badge/Vue-3.2.0-4FC08D?logo=vuedotjs)
![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)
![Redis](https://img.shields.io/badge/Redis-7-FF4438?logo=redis)
![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)

一个基于AI的医学影像诊断报告自动纠错系统，专注于检测和修正医学影像诊断报告中的方位词（左右、上下）和器官词（肺/肾等）错误。

## ✨ 主要功能

### 🔍 智能纠错
- **方位词纠错**：自动检测和修正"左/右"、"上/下"等方位词错误
- **器官词纠错**：检查器官名称与解剖位置的一致性
- **术语验证**：确保医学术语使用准确性和一致性
- **错误分类**：智能识别错误类型（方位词错误、器官词错误、术语错误）

### 📊 批量处理
- **文件上传**：支持Excel/CSV格式的批量报告上传
- **进度监控**：实时显示处理进度和状态
- **结果导出**：支持纠错结果的批量导出
- **历史记录**：完整的批处理任务历史管理

### 💬 交互式对话
- **实时纠错**：单条报告的交互式纠错
- **AI对话**：基于大语言模型的医学报告分析
- **解释说明**：提供错误原因和修正建议

### 🏷️ 数据标注
- **错误标注**：人工标注和验证AI纠错结果
- **数据管理**：标注数据的导入、导出和管理
- **质量评估**：基于标注数据的模型性能评估

### 👤 用户管理
- **完整认证**：用户注册、登录、密码重置
- **权限控制**：基于角色的访问控制
- **会话管理**：安全的会话和令牌管理
- **个人信息**：用户信息管理和偏好设置

## 🏗️ 技术架构

### 前端技术栈
- **框架**：Vue 3.2.0 + Composition API
- **构建工具**：Vite 5.4.11
- **UI组件库**：Element Plus 2.9.0
- **路由**：Vue Router 4.5.0
- **HTTP客户端**：Axios 1.7.8
- **图标库**：@heroicons/vue, @element-plus/icons-vue

### 后端技术栈
- **框架**：Flask 3.0.0 + Gunicorn
- **数据库**：MySQL 8.0 + SQLAlchemy 2.0.23
- **缓存**：Redis 7 + Flask-Session
- **认证**：JWT + Flask-JWT-Extended 4.6.0
- **安全**：bcrypt 4.1.2 + 速率限制 + CORS
- **文件处理**：Pandas + OpenPyXL

### AI/ML集成
- **大语言模型**：Ollama (qwen2.5:7b) + OpenAI兼容API
- **混合专家系统**：MOE_CLIENT多专家模型
- **提示工程**：精心设计的医学报告纠错提示词
- **NLP处理**：jieba分词 + pypinyin + python-Levenshtein

### 基础设施
- **容器化**：Docker + Docker Compose
- **Web服务器**：Nginx反向代理
- **数据库**：MySQL + Redis
- **监控**：健康检查 + 日志系统

## 🚀 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM（用于AI模型推理）
- 20GB+ 磁盘空间

### 一键部署
```bash
# 克隆项目
git clone <repository-url>
cd llama_med_webui

# 复制环境变量配置
cp .env.example .env
# 编辑.env文件，根据需要修改配置

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 访问应用
- **前端界面**：http://localhost:80
- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/api/docs
- **健康检查**：http://localhost:8000/health

### 默认账户
- **管理员**：admin@example.com / admin123
- **普通用户**：user@example.com / user123

## 📁 项目结构

```
llama_med_webui/
├── backend/                    # 后端Flask应用
│   ├── APP/                   # 应用模块
│   ├── auth/                  # 认证模块
│   ├── data/                  # 数据文件
│   ├── GPT/                   # AI处理模块
│   ├── models/                # 数据库模型
│   ├── routes/                # API路由
│   ├── services/              # 业务服务
│   ├── uploads/               # 上传文件存储
│   ├── outputs/               # 处理结果输出
│   ├── utils/                 # 工具函数
│   ├── app.py                 # 应用入口
│   ├── config.py              # 配置文件
│   └── requirements.txt       # Python依赖
├── frontend/                  # 前端Vue应用
│   ├── src/
│   │   ├── components/        # 可复用组件
│   │   ├── pages/            # 页面组件
│   │   ├── router/           # 路由配置
│   │   ├── utils/            # 工具函数
│   │   ├── views/            # 视图组件
│   │   ├── assets/           # 静态资源
│   │   └── main.js           # 应用入口
│   ├── package.json          # 前端依赖
│   └── vite.config.js        # 构建配置
├── uploads/                   # 全局上传目录
├── docker-compose.yml         # 容器编排配置
├── .env                       # 环境变量
├── .gitignore                # Git忽略配置
└── README.md                 # 项目说明
```

## 🔧 配置说明

### 环境变量配置 (.env)
```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=llama_med
MYSQL_USER=llama_user
MYSQL_PASSWORD=your_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# Flask配置
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key

# AI模型配置
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b
OPENAI_API_KEY=your_openai_api_key

# 应用配置
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
SESSION_TIMEOUT=86400  # 24小时
```

### AI模型配置
系统支持多种AI模型后端：
1. **本地Ollama**：推荐使用qwen2.5:7b模型
2. **OpenAI API**：支持GPT-4/GPT-3.5等模型
3. **混合专家系统**：多模型协同工作

## 📖 使用指南

### 1. 用户注册与登录
1. 访问 http://localhost:80
2. 点击"注册"创建新账户
3. 完成邮箱验证（如配置）
4. 登录系统开始使用

### 2. 单条报告纠错
1. 进入"对话模式"页面
2. 输入或粘贴医学影像诊断报告
3. 点击"分析"按钮
4. 查看AI纠错结果和建议

### 3. 批量报告处理
1. 进入"批量处理"页面
2. 上传Excel/CSV文件（需包含报告文本列）
3. 设置处理参数
4. 监控处理进度
5. 下载处理结果

### 4. 数据标注
1. 进入"标注"页面
2. 查看AI纠错结果
3. 标注正确/错误结果
4. 导出标注数据用于模型优化

### 5. 用户管理
1. 点击右上角用户头像
2. 访问"个人信息"页面
3. 修改密码、邮箱等设置
4. 查看操作历史

## 🔌 API接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/verify` - 令牌验证

### 批处理接口
- `POST /api/batch/upload` - 文件上传
- `GET /api/batch/jobs` - 任务列表
- `GET /api/batch/job/<job_id>` - 任务详情
- `GET /api/batch/progress/<job_id>` - 处理进度
- `GET /api/batch/download/<job_id>` - 结果下载

### AI处理接口
- `POST /api/medllm/analyze` - 单条报告分析
- `POST /api/medllm/batch_analyze` - 批量报告分析

### 标注接口
- `GET /api/annotation/records` - 标注记录列表
- `POST /api/annotation/annotate` - 提交标注
- `GET /api/annotation/export` - 导出标注数据

## 🐳 Docker部署

### 服务说明
```yaml
# docker-compose.yml 包含的服务：
- frontend: Vue应用 + Nginx (端口80)
- backend: Flask应用 + Gunicorn (端口8000)
- mysql: MySQL 8.0数据库 (端口33306)
- redis: Redis 7缓存 (端口6389)
- ollama: AI模型服务 (端口11434) - 可选
```

### 自定义部署
```bash
# 仅启动基础服务（使用外部AI服务）
docker-compose up -d frontend backend mysql redis

# 包含本地AI模型服务
docker-compose -f docker-compose.yml -f docker-compose.ai.yml up -d

# 生产环境部署
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 数据持久化
- MySQL数据：`./data/mysql`
- Redis数据：`./data/redis`
- 上传文件：`./uploads`
- 日志文件：`./logs`

## 🔒 安全特性

### 认证安全
- JWT令牌认证
- 密码哈希存储（bcrypt）
- 会话超时管理
- 账户锁定机制

### 数据安全
- SQL注入防护
- XSS攻击防护
- CSRF保护
- 文件上传验证

### 访问控制
- 基于角色的权限控制
- API速率限制
- CORS安全配置
- 敏感操作日志

### 网络安全
- HTTPS支持（生产环境）
- 安全头部配置
- 输入验证和清理
- 错误信息屏蔽

## 📈 性能优化

### 批处理优化
- 异步任务处理
- Redis进度跟踪
- 分块处理大文件
- 内存使用优化

### AI推理优化
- 模型缓存
- 批量推理
- 超时控制
- 错误重试

### 数据库优化
- 连接池管理
- 查询优化
- 索引优化
- 缓存策略

## 🐛 故障排除

### 常见问题

**Q: 服务启动失败**
```bash
# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# 查看日志
docker-compose logs
tail -f logs/backend.log
```

**Q: 数据库连接失败**
```bash
# 检查MySQL服务
docker-compose ps mysql
docker-compose logs mysql

# 重置数据库
docker-compose down -v
docker-compose up -d
```

**Q: AI模型服务不可用**
```bash
# 检查Ollama服务
curl http://localhost:11434/api/tags

# 拉取模型
docker exec -it ollama ollama pull qwen2.5:7b
```

**Q: 文件上传失败**
- 检查文件大小限制（默认16MB）
- 检查文件格式（支持.xlsx, .csv）
- 检查磁盘空间
- 检查目录权限

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看应用日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🤝 贡献指南

### 开发环境设置
```bash
# 1. 克隆项目
git clone <repository-url>
cd llama_med_webui

# 2. 设置Python虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 3. 设置Node.js环境
cd ../frontend
npm install

# 4. 启动开发服务器
# 后端开发服务器
cd ../backend
flask run --host=0.0.0.0 --port=8000

# 前端开发服务器
cd ../frontend
npm run dev
```

### 代码规范
- 前端：遵循Vue 3 Composition API最佳实践
- 后端：遵循Flask应用结构规范
- 提交信息：使用约定式提交规范
- 代码格式：使用Prettier + ESLint（前端）、Black + isort（后端）

### 测试
```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm test

# E2E测试
npm run test:e2e
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Flask](https://flask.palletsprojects.com/) - Python微框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库
- [Ollama](https://ollama.ai/) - 本地大语言模型运行
- [Docker](https://www.docker.com/) - 容器化平台

## 📞 支持与反馈

- **问题报告**：[GitHub Issues](<issues-url>)
- **功能建议**：[GitHub Discussions](<discussions-url>)
- **文档改进**：[GitHub Wiki](<wiki-url>)
- **紧急支持**：<support-email>

---

**医学影像诊断报告纠错系统** - 让AI成为医生的得力助手，提升医疗报告质量，保障患者安全。

> **免责声明**：本系统为辅助工具，不能替代专业医生的诊断。所有医疗决策应由专业医生基于完整临床信息做出。