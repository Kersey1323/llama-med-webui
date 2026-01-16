# 长时间运行任务配置指南

## 概述
本系统支持长时间运行的批处理任务（最长12小时）。以下是相关的超时配置说明。

## 超时配置汇总

### 1. Gunicorn 配置
- **超时时间**: 43200秒（12小时）
- **配置位置**: `docker-compose.yml`
- **说明**: 后端服务器处理请求的最大时间

### 2. Nginx 配置
- **连接超时**: 43200秒（12小时）
- **发送超时**: 43200秒（12小时）
- **读取超时**: 43200秒（12小时）
- **配置位置**: `frontend/nginx/default.conf`
- **说明**: 代理服务器等待后端响应的最大时间

### 3. Redis 会话配置
- **用户会话过期**: 43200秒（12小时）
- **任务进度过期**: 43200秒（12小时）
- **配置位置**: `backend/services/redis_session.py`
- **说明**: 会话和进度数据的存储时间

### 4. 前端配置
- **启动请求超时**: 60秒
- **进度检查间隔**: 10秒
- **最大检查次数**: 3600次（10小时）
- **配置位置**: `frontend/src/pages/BatchProcess.vue`
- **说明**: 前端监控批处理进度的设置

### 5. 数据库配置
- **提交频率**: 每50条记录提交一次
- **配置位置**: `backend/services/batch_process_service.py`
- **说明**: 减少数据库压力，提高性能

## 监控和日志

### 进度监控
- 每10秒检查一次进度
- 如果10分钟没有进度变化，会显示警告信息
- 最长监控10小时

### 日志记录
- 批处理开始和完成时间
- 错误记录和堆栈跟踪
- 进度更新记录

## 性能优化建议

### 1. 系统资源
- 确保服务器有足够的内存和CPU
- 监控磁盘空间使用情况
- 定期清理临时文件

### 2. 数据库优化
- 定期清理旧的任务记录
- 监控数据库连接池使用情况
- 考虑使用数据库索引优化查询

### 3. Redis 优化
- 监控 Redis 内存使用情况
- 定期清理过期的会话数据
- 考虑设置 Redis 持久化

## 故障排除

### 常见问题
1. **502 Bad Gateway**: 检查超时设置是否正确
2. **进度停滞**: 检查后端日志，确认任务仍在运行
3. **内存不足**: 增加服务器内存或优化批处理逻辑
4. **数据库连接超时**: 检查数据库连接池配置

### 调试命令
```bash
# 查看容器状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 检查 Redis 连接
docker-compose exec backend python -c "import redis; r=redis.Redis(host='redis', port=6379); print(r.ping())"

# 检查数据库连接
docker-compose exec backend python -c "from models import db; from app import create_app; app=create_app(); app.app_context().push(); print(db.engine.execute('SELECT 1').fetchone())"
```

## 部署注意事项

1. **重启服务**: 修改配置后需要重新构建和部署
2. **数据备份**: 长时间任务前建议备份重要数据
3. **监控告警**: 建议设置系统监控和告警
4. **日志轮转**: 配置日志轮转避免磁盘空间不足

## 版本历史
- v1.0: 初始配置，支持最长2小时任务
- v2.0: 升级到12小时，优化监控和错误处理 