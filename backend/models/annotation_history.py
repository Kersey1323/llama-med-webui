from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.sql import func
import json
from . import db

class AnnotationHistory(db.Model):
    """标注历史表"""
    __tablename__ = 'annotation_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    error_record_id = Column(Integer, ForeignKey('error_records.id'), nullable=False, comment='关联的错误记录ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='标注用户ID')
    annotation_time = Column(DateTime, default=func.now(), comment='标注时间')
    annotation_groups = Column(Text, nullable=False, comment='标注组数据(JSON格式)')
    action = Column(String(20), nullable=False, comment='操作类型：create/update/delete')
    
    def to_dict(self):
        """转换为字典格式用于JSON响应"""
        try:
            groups_data = json.loads(self.annotation_groups) if self.annotation_groups else []
        except (json.JSONDecodeError, TypeError):
            groups_data = []
            
        return {
            'id': self.id,
            'errorRecordId': self.error_record_id,
            'userId': self.user_id,
            'annotationTime': self.annotation_time.strftime('%Y-%m-%d %H:%M:%S') if self.annotation_time else None,
            'annotationGroups': groups_data,
            'action': self.action
        } 