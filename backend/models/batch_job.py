from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from . import db
class BatchJob(db.Model):
    """批处理任务表"""
    __tablename__ = 'batch_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False, comment='上传的文件名称')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    completed_at = Column(DateTime, nullable=True, comment='完成时间')
    status = Column(Enum('pending', 'processing', 'completed', 'failed', name='job_status'), 
                 default='pending', comment='处理状态')
    total_rows = Column(Integer, default=0, comment='总行数')
    error_rows = Column(Integer, default=0, comment='错误行数')
    correction_rate = Column(Float, default=0.0, comment='修正率(百分比)')
    original_file_path = Column(String(255), nullable=False, comment='原始文件路径')
    processed_file_path = Column(String(255), nullable=True, comment='处理后文件路径')
    processing_time = Column(Integer, default=0, comment='处理耗时(秒)')
    is_deleted = Column(Boolean, default=False, comment='删除标记')

    def to_dict(self):
        """转换为字典格式用于JSON响应"""
        return {
            'id': self.id,
            'name': self.file_name,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'total': self.total_rows,
            'errors': self.error_rows,
            'correctionRate': round(self.correction_rate, 2),
            'status': self.status,
            'completedAt': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'processingTime': self.processing_time,
            'is_deleted': self.is_deleted,
        } 