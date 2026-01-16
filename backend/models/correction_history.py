from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from . import db

class CorrectionHistory(db.Model):
    """修正历史表"""
    __tablename__ = 'correction_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    error_record_id = Column(Integer, ForeignKey('error_records.id'), nullable=False, comment='关联的错误记录ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='修改用户ID')
    correction_time = Column(DateTime, default=func.now(), comment='修改时间')
    original_text = Column(Text, nullable=False, comment='修改前文本')
    corrected_text = Column(Text, nullable=False, comment='修改后文本')
    
    def to_dict(self):
        """转换为字典格式用于JSON响应"""
        return {
            'id': self.id,
            'errorRecordId': self.error_record_id,
            'userId': self.user_id,
            'time': self.correction_time.strftime('%Y-%m-%d %H:%M:%S') if self.correction_time else None,
            'original': self.original_text,
            'corrected': self.corrected_text
        } 