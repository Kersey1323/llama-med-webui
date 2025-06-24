import json
from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
# from backend.models import db, ErrorRecord, AnnotationGroup, AnnotationHistory, User
from backend.models.error_record import ErrorRecord
from backend.models.user import User
from backend.models.annotation_group import AnnotationGroup
from backend.models.annotation_history import AnnotationHistory
from backend.models import db
from backend.utils.auth import login_required

annotation_bp = Blueprint('annotation', __name__)

@annotation_bp.route('/api/annotation/error/<int:error_id>/groups', methods=['GET'])
@login_required
def get_annotation_groups(error_id):
    """获取错误记录的标注组"""
    try:
        groups = AnnotationGroup.query.filter_by(error_record_id=error_id).all()
        return jsonify({
            'success': True,
            'data': [group.to_dict() for group in groups]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@annotation_bp.route('/api/annotation/error/<int:error_id>/groups', methods=['POST'])
@login_required
def save_annotation_groups(error_id):
    """保存错误记录的标注组"""
    try:
        current_user_id = session.get('user_id')
        data = request.get_json()
        annotation_groups = data.get('annotationGroups', [])

        # 删除现有的标注组
        AnnotationGroup.query.filter_by(error_record_id=error_id).delete()

        # 保存新的标注组
        for group_data in annotation_groups:
            group = AnnotationGroup(
                error_record_id=error_id,
                description_indices=group_data['descriptionIndices'],
                diagnosis_indices=group_data['diagnosisIndices'],
                description_text=group_data['descriptionText'],
                diagnosis_text=group_data['diagnosisText'],
                color=group_data['color']
            )
            db.session.add(group)

        # 更新错误记录状态
        error_record = ErrorRecord.query.get(error_id)
        if error_record:
            error_record.annotated = True
            error_record.annotated_by = current_user_id
            error_record.annotated_at = datetime.now()

        # 记录标注历史
        history = AnnotationHistory(
            error_record_id=error_id,
            user_id=current_user_id,
            annotation_groups=json.dumps(annotation_groups, ensure_ascii=False),
            action='create'
        )
        db.session.add(history)

        db.session.commit()

        return jsonify({'success': True, 'message': '标注保存成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@annotation_bp.route('/api/annotation/error/<int:error_id>/reset', methods=['POST'])
@login_required
def reset_annotation(error_id):
    """重置错误记录的标注"""
    try:
        current_user_id = session.get('user_id')
        print(f"开始重置标注，错误ID: {error_id}, 用户ID: {current_user_id}")

        # 检查错误记录是否存在
        error_record = ErrorRecord.query.get(error_id)
        if not error_record:
            print(f"错误记录不存在: {error_id}")
            return jsonify({'success': False, 'error': '错误记录不存在'}), 404

        print(f"找到错误记录: {error_record.id}, 当前标注状态: {error_record.annotated}")

        # 删除标注组
        deleted_groups = AnnotationGroup.query.filter_by(error_record_id=error_id).delete()
        print(f"删除了 {deleted_groups} 个标注组")

        # 更新错误记录状态
        error_record.annotated = False
        error_record.annotated_by = None
        error_record.annotated_at = None
        print(f"已重置错误记录的标注状态")

        # 记录标注历史
        history = AnnotationHistory(
            error_record_id=error_id,
            user_id=current_user_id,
            annotation_groups=json.dumps([], ensure_ascii=False),
            action='delete'
        )
        db.session.add(history)
        print(f"已添加标注历史记录")

        db.session.commit()
        print("数据库提交成功")

        return jsonify({'success': True, 'message': '标注重置成功'})
    except Exception as e:
        db.session.rollback()
        print(f"标注重置失败，错误详情: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'标注重置失败: {str(e)}'}), 500

@annotation_bp.route('/api/annotation/error/<int:error_id>/history', methods=['GET'])
@login_required
def get_annotation_history(error_id):
    """获取错误记录的标注历史"""
    try:
        history_records = AnnotationHistory.query.filter_by(error_record_id=error_id).order_by(AnnotationHistory.annotation_time.desc()).all()

        # 获取用户信息
        user_ids = list(set([h.user_id for h in history_records]))
        users = {u.id: u.username for u in User.query.filter(User.id.in_(user_ids)).all()}

        history_data = []
        for record in history_records:
            data = record.to_dict()
            data['username'] = users.get(record.user_id, '未知用户')
            history_data.append(data)

        return jsonify({
            'success': True,
            'data': history_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500