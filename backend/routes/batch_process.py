import os
from flask import Blueprint, request, jsonify, current_app, g, session
from backend.services.batch_process_service import BatchProcessService
from backend.utils.auth import login_required
from flask import send_from_directory
from io import BytesIO
import pandas as pd

batch_bp = Blueprint('batch', __name__, url_prefix='/api/batch')

# 初始化服务
upload_folder = os.path.join(current_app.root_path, 'uploads') if current_app else 'uploads'
output_folder = os.path.join(current_app.root_path, 'outputs') if current_app else 'outputs'
batch_service = BatchProcessService(upload_folder, output_folder)


@batch_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """上传文件接口"""
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 检查文件类型
    allowed_extensions = {'xlsx', 'xls', 'csv'}
    if not file.filename.split('.')[-1].lower() in allowed_extensions:
        return jsonify({'error': '不支持的文件类型，请上传Excel或CSV文件'}), 400

    try:
        # 获取当前用户ID
        user_id = session.get('user_id')
        # 处理文件
        job_id = batch_service.process_file(file, user_id)


        return jsonify({
            'message': '文件上传成功',
            'job_id': job_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batch_bp.route('/startProcess', methods=['GET'])
@login_required
def start_process():

    result = batch_service.start_batch_process(job_id=batch_service.current_job_id)
    print(result)
    print(type(result))
    if isinstance(result, tuple):
        data, status_code = result
        print(data,status_code)
        if status_code == 500:
            return jsonify({'error': "服务器繁忙！"}), 500
        return jsonify(data), status_code
    else:
        # 处理未知返回值类型
        return jsonify({"error": "Invalid response format"}), 500




@batch_bp.route('/progress', methods=['GET'])
@login_required
def get_progress():
    """获取处理进度"""
    results = batch_service.get_progress()
    return jsonify(results), 200


@batch_bp.route('/jobs', methods=['GET'])
@login_required
def get_jobs():
    """获取批处理任务列表（支持分页）"""
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    try:
        result = batch_service.get_batch_jobs(user_id, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batch_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    try:
        batch_service.delete_batch_job(job_id)
        return jsonify({'message': '删除成功'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/jobs/<int:job_id>/errors', methods=['GET'])
@login_required
def get_errors(job_id):
    """获取批处理任务的错误列表（支持分页）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    try:
        result = batch_service.get_errors_by_job(job_id, page, page_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batch_bp.route('/jobs/<int:job_id>/export', methods=['GET'])
@login_required
def export_file(job_id):
    try:
        file_path = batch_service.output_file_by_job(job_id)
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return send_from_directory(
            directory=directory,
            path=filename,
            as_attachment=True,
            download_name=filename  # 确保中文文件名兼容
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batch_bp.route('/errors/<int:error_id>', methods=['PUT'])
@login_required
def update_error(error_id):
    data = request.json
    if not data or 'action_type' not in data:
        return jsonify({'error': '缺少必要参数'}), 400

    try:
        user_id = session.get('user_id')
        corrected_text = data.get('corrected_text')
        updated_error = batch_service.update_error(
            error_id,
            user_id,
            data['action_type'],
            corrected_text
        )
        return jsonify(updated_error), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batch_bp.route('/jobs/<int:job_id>/export-annotation', methods=['GET'])
@login_required
def export_annotation(job_id):
    """导出该批次下所有标注内容（annotation_groups）为Excel"""
    try:
        # 1. 获取该批次下所有error_record的id
        from backend.models.error_record import ErrorRecord
        from backend.models.annotation_group import AnnotationGroup
        error_ids = [e.id for e in ErrorRecord.query.filter_by(batch_job_id=job_id).all()]
        if not error_ids:
            return jsonify({'error': '该批次下无错误数据'}), 404
        # 2. 获取所有annotation_groups
        groups = AnnotationGroup.query.filter(AnnotationGroup.error_record_id.in_(error_ids)).all()
        if not groups:
            return jsonify({'error': '该批次下无标注内容'}), 404
        # 3. 组装数据
        data = [
            {'影像描述': g.description_text, '影像诊断': g.diagnosis_text}
            for g in groups
        ]
        df = pd.DataFrame(data)
        # 4. 写入Excel到内存
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='标注内容')
        output.seek(0)
        # 5. 返回文件流
        from flask import send_file
        filename = f'annotation_job_{job_id}.xlsx'
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

