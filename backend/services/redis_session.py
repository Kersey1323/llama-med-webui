import json
import redis
from datetime import datetime, timedelta
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

class RedisSessionManager:
    """Redis会话管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
    
    def _get_user_session_key(self, user_id):
        """获取用户会话的Redis键"""
        return f"user_session:{user_id}"
    
    def _get_job_progress_key(self, job_id):
        """获取任务进度的Redis键"""
        return f"job_progress:{job_id}"
    
    def set_user_session(self, user_id, session_data, expire_time=43200):  # 12小时过期
        """设置用户会话数据"""
        key = self._get_user_session_key(user_id)
        session_data['updated_at'] = datetime.now().isoformat()
        self.redis_client.setex(
            key, 
            expire_time, 
            json.dumps(session_data, ensure_ascii=False)
        )
    
    def get_user_session(self, user_id):
        """获取用户会话数据"""
        key = self._get_user_session_key(user_id)
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def update_user_session(self, user_id, **kwargs):
        """更新用户会话数据"""
        session_data = self.get_user_session(user_id) or {}
        session_data['user_id'] = user_id
        session_data.update(kwargs)
        self.set_user_session(user_id, session_data)
        return session_data

    def set_job_progress(self, job_id, progress, expire_time=43200):  # 12小时过期
        """设置任务进度 - 确保存储的是整数进度值"""
        key = self._get_job_progress_key(job_id)
        progress_data = {
            'progress': progress,  # 确保存储的是整数进度值
            'updated_at': datetime.now().isoformat()
        }
        self.redis_client.setex(
            key,
            expire_time,
            json.dumps(progress_data, ensure_ascii=False)
        )

    def get_job_progress(self, job_id):
        """获取任务进度 - 返回整数进度值"""
        key = self._get_job_progress_key(job_id)
        data = self.redis_client.get(key)
        if data:
            progress_data = json.loads(data)
            return progress_data.get('progress', 0)  # 返回整数进度值
        return 0  # 没有记录时返回0
    
    def delete_user_session(self, user_id):
        """删除用户会话"""
        key = self._get_user_session_key(user_id)
        self.redis_client.delete(key)
    
    def delete_job_progress(self, job_id):
        """删除任务进度"""
        key = self._get_job_progress_key(job_id)
        self.redis_client.delete(key)
    
    def get_all_user_sessions(self):
        """获取所有用户会话（用于调试）"""
        pattern = "user_session:*"
        keys = self.redis_client.keys(pattern)
        sessions = {}
        for key in keys:
            user_id = key.split(':')[1]
            sessions[user_id] = self.get_user_session(user_id)
        return sessions
    
    def get_all_job_progress(self):
        """获取所有任务进度（用于调试）"""
        pattern = "job_progress:*"
        keys = self.redis_client.keys(pattern)
        progress_data = {}
        for key in keys:
            job_id = key.split(':')[1]
            progress_data[job_id] = self.get_job_progress(job_id)
        return progress_data 