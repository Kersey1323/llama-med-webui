from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from . import db

class ErrorRecord(db.Model):
    """错误数据记录表"""
    __tablename__ = 'error_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_job_id = Column(Integer, ForeignKey('batch_jobs.id'), nullable=False, comment='关联的批处理任务ID')
    row_number = Column(Integer, nullable=False, comment='在Excel中的行号')
    error_type = Column(String(50), nullable=False, comment='错误类型')
    error_content = Column(Text, nullable=False, comment='错误内容')
    suggested_correction = Column(Text, nullable=False, comment='建议修改')
    original_text = Column(Text, nullable=False, comment='原始文本')
    original_diagnosis =  Column(Text, nullable=False, comment='原始诊断')
    gen_diagnosis = Column(Text, nullable=False, comment='生成诊断')
    status = Column(Enum('pending', 'corrected', 'ignored', name='error_status'), 
                 default='pending', comment='处理状态')
    corrected_by = Column(Integer, ForeignKey('users.id'), nullable=True, comment='修改人')
    corrected_at = Column(DateTime, nullable=True, comment='修改时间')
    annotated = Column(Boolean, default=False, comment='是否已标注')
    annotated_by = Column(Integer, ForeignKey('users.id'), nullable=True, comment='标注人')
    annotated_at = Column(DateTime, nullable=True, comment='标注时间')
    
    def to_dict(self):
        """转换为字典格式用于JSON响应"""
        annotated_value = bool(self.annotated) if self.annotated is not None else False
        
        return {
            'id': self.id,
            'row': self.row_number,
            'type': self.error_type,
            'content': self.error_content,
            'suggestion': self.suggested_correction,
            'status': self.status,
            'originalText': self.original_text,
            'original_diagnosis': self.original_diagnosis,
            'genDiagnosis': self.gen_diagnosis,
            'correctedBy': self.corrected_by,
            'correctedAt': self.corrected_at.strftime('%Y-%m-%d %H:%M:%S') if self.corrected_at else None,
            'annotated': annotated_value,
            'annotatedBy': self.annotated_by,
            'annotatedAt': self.annotated_at.strftime('%Y-%m-%d %H:%M:%S') if self.annotated_at else None
        } 