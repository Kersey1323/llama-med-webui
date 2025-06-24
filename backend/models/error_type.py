from sqlalchemy import Column, Integer, String, Text
from . import db

class ErrorType(db.Model):
    """错误类型表"""
    __tablename__ = 'error_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment='错误类型名称')
    description = Column(Text, nullable=True, comment='描述')
    priority = Column(Integer, default=0, comment='优先级，用于排序')
    
    def to_dict(self):
        """转换为字典格式用于JSON响应"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'priority': self.priority
        } 