from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from . import db

class AnnotationGroup(db.Model):
    """标注组表"""
    __tablename__ = 'annotation_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    error_record_id = Column(Integer, ForeignKey('error_records.id'), nullable=False, comment='关联的错误记录ID')
    description_indices = Column(JSON, nullable=False, comment='描述段落索引数组')
    diagnosis_indices = Column(JSON, nullable=False, comment='诊断段落索引数组')
    description_text = Column(Text, nullable=False, comment='合并后的描述文本')
    diagnosis_text = Column(Text, nullable=False, comment='合并后的诊断文本')
    color = Column(String(50), nullable=False, comment='标注颜色')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    
    def to_dict(self):
        """转换为字典格式用于JSON响应"""
        return {
            'id': self.id,
            'errorRecordId': self.error_record_id,
            'descriptionIndices': self.description_indices,
            'diagnosisIndices': self.diagnosis_indices,
            'descriptionText': self.description_text,
            'diagnosisText': self.diagnosis_text,
            'color': self.color,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        } 