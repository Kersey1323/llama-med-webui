import json
import os
import time
import pandas as pd
from datetime import datetime

from flask import jsonify
from models.batch_job import BatchJob
from models.error_record import ErrorRecord
from models.error_type import ErrorType
from models import db
from openpyxl import Workbook
from utils.clients import Client, LocalClient
from utils.moe_client import MOE_CLIENT
from utils.Demo_3_desc import main_desc
from config import (
    API_KEY,
    BASE_URL,
    MODEL_NAME,
    LOCAL_API_KEY,
    LOCAL_BASE_URL,
    LOCAL_MODEL_NAME,
)
import unicodedata
import re
from services.redis_session import RedisSessionManager


def custom_secure_filename(filename):
    """
    自定义文件名处理函数，保留中文字符，同时确保安全性。
    """
    # 使用 unicodedata 规范化文件名
    filename = unicodedata.normalize("NFKC", filename)
    # 移除非法字符（如路径分隔符、空格等）
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return filename


class BatchProcessService:
    """批处理服务"""

    def __init__(self, upload_folder, output_folder):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        self._ensure_upload_folder()
        self.redis_session = RedisSessionManager()  # 使用Redis会话管理

    # def _get_user_session(self, user_id):
    #     """获取用户会话"""
    #     if user_id not in self.user_sessions:
    #         self.user_sessions[user_id] = {
    #             'current_job_id': None,
    #             'progress': 0
    #         }
    #     return self.user_sessions[user_id]

    def _ensure_upload_folder(self):
        """确保上传文件夹存在"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def _ensure_output_folder(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def process_file(self, file, user_id):
        """处理上传的文件"""
        # 保存文件
        try:
            print(user_id)
            filename = custom_secure_filename(file.filename)
            timestamp = int(time.time())
            file_path = os.path.join(self.upload_folder, f"{timestamp}_{filename}")
            print(file_path)
            file.save(file_path)

            # 创建批处理任务记录
            job = BatchJob(
                file_name=filename,
                user_id=user_id,
                original_file_path=file_path,
                status="pending",
            )
            db.session.add(job)
            db.session.commit()

            # 更新Redis中的用户会话
            self.redis_session.update_user_session(
                user_id=user_id,
                current_job_id=job.id,
                progress=0,
                last_activity=datetime.now().isoformat(),
            )

            return job.id
        except Exception as e:
            traceback.print_exc()
            print(f"保存文件时出错：{e}")
            raise ValueError("保存文件时出错")

    def start_batch_process_async(self, job_id, user_id=None):
        """异步启动批处理过程"""
        import threading

        # 验证任务是否存在
        job = BatchJob.query.get(job_id)
        if not job:
            raise ValueError(f"找不到ID为{job_id}的批处理任务")

        # 检查任务状态
        if job.status in ["processing", "completed"]:
            raise ValueError(f"任务 {job_id} 已经在处理中或已完成，不能重复处理")

        # 更新任务状态为处理中
        job.status = "processing"
        db.session.commit()

        # 启动后台线程处理
        thread = threading.Thread(
            target=self._process_batch_in_background, args=(job_id, user_id)
        )
        thread.daemon = True
        thread.start()

        return {"message": "批处理已启动", "job_id": job_id}

    def _process_batch_in_background(self, job_id, user_id=None):
        """在后台处理批处理任务"""
        from app import create_app
        import traceback

        # 创建应用上下文
        app = create_app()
        with app.app_context():
            try:
                print(f"开始后台处理任务: {job_id}")
                self.start_batch_process(job_id, user_id)
                print(f"任务 {job_id} 处理完成")
            except Exception as e:
                print(f"后台批处理出错: {e}")
                traceback.print_exc()
                # 更新任务状态为失败
                try:
                    job = BatchJob.query.get(job_id)
                    if job:
                        job.status = "failed"
                        db.session.commit()
                        print(f"任务 {job_id} 状态已更新为失败")
                except Exception as db_error:
                    print(f"更新任务状态失败: {db_error}")

    def start_batch_process(self, job_id, user_id=None):
        """开始批处理过程"""
        print(f"开始处理任务: {job_id}")
        job = BatchJob.query.get(job_id)
        if not job:
            raise ValueError(f"找不到ID为{job_id}的批处理任务")

        # 注意：状态检查已在异步启动方法中完成
        # 这里只处理实际的批处理逻辑

        # 如果未传入user_id，尝试从任务获取
        if not user_id and job.user_id:
            user_id = job.user_id
        # 更新Redis中的用户会话和任务进度
        if user_id:
            self.redis_session.update_user_session(
                user_id,
                current_job_id=job_id,
                progress=0,
                last_activity=datetime.now().isoformat(),
            )

        # 初始化任务进度
        self.redis_session.set_job_progress(job_id, 0)

        # 清理该任务之前的错误记录，防止重复
        ErrorRecord.query.filter_by(batch_job_id=job_id).delete()
        db.session.commit()

        try:

            # 读取Excel文件
            df = pd.read_excel(job.original_file_path)
            print(os.getcwd())
            total_rows = len(df)
            job.total_rows = total_rows

            # 假设 Excel 文件的列名为 '影像描述' 和 '影像诊断'
            data = []

            # 遍历每一行，处理数据
            for index, row in df.iterrows():
                # 清理影像描述和影像诊断中的多余空格
                image_desc = str(row["影像描述"]).strip()  # 去掉两端空格
                image_desc = " ".join(
                    image_desc.split()
                )  # 替换中间的多余空格为单个空格
                image_diagnosis = str(row["影像诊断"]).strip()  # 去掉两端空格
                image_diagnosis = " ".join(
                    image_diagnosis.split()
                )  # 替换中间的多余空格为单个空格
                # image_body = str(row['检查部位']).strip()  # 去掉两端空格
                # image_body = ' '.join(image_body.split())  # 替换中间的多余空格为单个空格

                # 过滤掉影像描述长度小于 10 的项
                if len(image_desc) >= 10:
                    # data.append({"影像描述": image_desc, "影像诊断": image_diagnosis,"检查部位": image_body})
                    data.append({"影像描述": image_desc, "影像诊断": image_diagnosis})

            # 开始批处理
            # 创建一个新的Excel工作簿和工作表
            wb = Workbook()
            ws = wb.active
            ws.title = "影像描述与报告"
            # 添加表头
            ws.append(
                [
                    "影像描述",
                    "影像诊断",
                    "生成诊断",
                    "是否修改",
                    "错误类型",
                    "修改建议",
                    "分析过程",
                ]
            )
            errors = []
            try:
                start_time = time.time()
                count = 0
                process_num = len(data)
                for i, record in enumerate(data):
                    description = record["影像描述"]
                    true_report = record["影像诊断"]
                    # body_part = record['检查部位']
                    print(description, true_report)
                    # local_client = LocalClient(
                    #     API_KEY=LOCAL_API_KEY,
                    #     base_url=LOCAL_BASE_URL,
                    #     model_name=LOCAL_MODEL_NAME,
                    # )
                    # client = Client(
                    #     API_KEY=API_KEY, base_url=BASE_URL, model_name=MODEL_NAME
                    # )
                    # gen_report = local_client.generate(description)
                    # # start_time = time.time()
                    # # gen_desc = main_desc(body_part, description)
                    # # end_time = time.time()
                    # # print("修改描述：",gen_desc)
                    # # print("真实描述：",description)
                    # # print("Time of Desc modify:", end_time - start_time)
                    # input_data = {
                    #     "desc": description,
                    #     "answer": true_report,
                    #     "pred": gen_report,
                    #     # "gen_desc": gen_desc,
                    # }
                    # check_data = client.check_modify(input_data)

                    # # 如果client返回的处理值有错误直接跳过
                    # if not check_data:
                    #     error = ErrorRecord(
                    #         batch_job_id=job.id,
                    #         row_number=i + 1,
                    #         error_type="服务器错误！",
                    #         original_text=description,
                    #         status="pending",
                    #     )
                    #     db.session.add(error)  # 确保添加到数据库
                    #     ws.append(
                    #         [description, true_report, None, "服务器错误", None, None, None]
                    #     )

                    #     errors.append(error)
                    #     # self.progress = int((i + 1) / len(description[:process_num]) * 100)
                    #     self.progress = int((i + 1) / len(data) * 100)
                    #     batch_progress = self.progress
                    #     continue
                    moe_client = MOE_CLIENT()
                    try:
                        response = moe_client(description, true_report)
                    except Exception as e:
                        import traceback
                        
                        print("发生异常：", str(e))
                        print("详细堆栈信息：")
                        print(traceback.format_exc())
                        continue
                    verify_result = response["verify_result"]
                    gen_report = response["gen_report"]
                    if verify_result["是否修改"] == "是":
                        count = count + 1
                        error = ErrorRecord(
                            batch_job_id=job.id,
                            row_number=i + 1,
                            error_type=verify_result["错误类型"],
                            error_content=verify_result["分析过程"],
                            suggested_correction=f"修改建议: {verify_result["修改建议"]}",
                            original_text=description,
                            original_diagnosis=verify_result["标注后的真实诊断"],
                            gen_diagnosis=gen_report,
                            status="pending",
                        )
                        db.session.add(error)

                        errors.append(error)
                    if verify_result["是否修改"] == "False":
                        # ws.append(
                        #     [
                        #         description,
                        #         verify_result["标注后的真实诊断"],
                        #         verify_result["是否修改"],
                        #         "",
                        #         verify_result["纠错合理性"],
                        #         verify_result["纠错解释"],
                        #     ]
                        # )
                        continue
                    else:
                        ws.append(
                            [
                                description,
                                verify_result["标注后的真实诊断"],
                                gen_report,
                                verify_result["是否修改"],
                                verify_result["错误类型"],
                                verify_result["修改建议"],
                                verify_result["分析过程"],
                            ]
                        )
                    # 更新进度条
                    # self.progress = int((i + 1) / len(description[:process_num]) * 100)
                    progress = int((i + 1) / len(data) * 100)
                    print(progress)
                    # 更新Redis中的任务进度
                    self.redis_session.set_job_progress(job_id, progress)
                    # 更新用户会话进度
                    if user_id:
                        self.redis_session.update_user_session(
                            job.user_id,
                            progress=progress,
                            last_activity=datetime.now().isoformat(),
                        )
                    # 每处理50条记录提交一次数据库，减少数据库压力
                    if (i + 1) % 50 == 0:
                        db.session.commit()

                # 保存到xlsx文件
                processed_filename = (
                    f"processed_{os.path.basename(job.original_file_path)}"
                )
                processed_file_path = os.path.join(
                    self.output_folder, processed_filename
                )

                print(processed_file_path)
                wb.save(processed_file_path)
                # 保存处理后的文件路径
                job.processed_file_path = processed_file_path
                # 更新任务状态
                job.error_rows = len(errors)
                job.correction_rate = (
                    (total_rows - len(errors)) / total_rows * 100
                    if total_rows > 0
                    else 0
                )
                job.processing_time = int(time.time() - start_time)
                job.completed_at = datetime.now()
                job.status = "completed"

                db.session.commit()
                # 更新Redis中的任务进度和用户会话
                self.redis_session.set_job_progress(job_id, 100)
                if user_id:
                    self.redis_session.update_user_session(
                        job.user_id,
                        progress=100,
                        last_activity=datetime.now().isoformat(),
                    )
                result = {
                    "id": job.id,
                    "errors": len(errors),
                    "processing_time": int(time.time() - start_time),
                    "status": job.status,
                }

                return result, 200
            except Exception as e:
                import traceback

                print("Error during batch-process:")
                traceback.print_exc()  # 打印详细堆栈
                return jsonify({"error": f"批处理内部错误: {str(e)}"}), 500

        except Exception as e:
            job.status = "failed"
            db.session.commit()
            raise e

    def get_progress(self, user_id=None):
        """获取当前批处理进度 - 修复进度获取逻辑"""
        if user_id:
            # 从Redis获取用户会话信息
            user_session = self.redis_session.get_user_session(user_id)
            if user_session and "current_job_id" in user_session:
                job_id = user_session["current_job_id"]
                # 直接获取整数进度值
                progress = self.redis_session.get_job_progress(job_id)
                return {"job_id": job_id, "progress": progress}

            # 如果Redis中没有用户会话，尝试从数据库获取
            job = (
                BatchJob.query.filter(
                    BatchJob.user_id == user_id, BatchJob.status == "processing"
                )
                .order_by(BatchJob.created_at.desc())
                .first()
            )

            if job:
                # 计算数据库中的进度
                processed_rows = ErrorRecord.query.filter_by(
                    batch_job_id=job.id
                ).count()
                progress = min(
                    int((processed_rows / max(job.total_rows, 1)) * 100), 100
                )
                return {"job_id": job.id, "progress": progress}

        return {"job_id": None, "progress": 0}

    def get_batch_jobs(self, user_id=None, page=1, page_size=10):
        """获取批处理任务列表"""
        query = BatchJob.query.filter_by(is_deleted=False)
        if user_id:
            query = query.filter_by(user_id=user_id)

        total = query.count()
        # 分页查询
        jobs = (
            query.order_by(BatchJob.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # 计算每个任务的标注状态和已标注数
        job_data = []
        for job in jobs:
            job_dict = job.to_dict()
            job_dict["annotationStatus"] = self._calculate_annotation_status(job.id)
            # 新增：统计已标注错误数
            annotated_count = ErrorRecord.query.filter_by(
                batch_job_id=job.id, annotated=True
            ).count()
            job_dict["annotatedCount"] = annotated_count
            job_data.append(job_dict)

        return {"total": total, "page": page, "page_size": page_size, "data": job_data}

    def _calculate_annotation_status(self, job_id):
        """计算批处理任务的标注状态"""
        try:
            # 获取该任务的所有错误记录
            total_errors = ErrorRecord.query.filter_by(batch_job_id=job_id).count()
            if total_errors == 0:
                return "未标注"  # 没有错误记录，标记为未标注

            # 获取已标注的错误记录数量
            annotated_errors = ErrorRecord.query.filter_by(
                batch_job_id=job_id, annotated=True
            ).count()

            if annotated_errors == 0:
                return "未标注"  # 没有已标注的记录
            elif annotated_errors == total_errors:
                return "标注完成"  # 所有错误都已标注
            else:
                return "标注中"  # 部分已标注

        except Exception as e:
            print(f"计算标注状态失败: {e}")
            return "未知"

    def get_errors_by_job(self, job_id, page=1, page_size=10):
        """获取指定批处理任务的错误列表"""
        query = ErrorRecord.query.filter_by(batch_job_id=job_id)

        # 计算总记录数
        total = query.count()

        # 分页查询
        errors = (
            query.order_by(ErrorRecord.row_number.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [error.to_dict() for error in errors],
        }

    def output_file_by_job(self, job_id):
        # 查询指定 job_id 的记录，并获取 processed_file_path 字段
        job = BatchJob.query.filter_by(id=job_id).first()  # 使用 filter_by 过滤条件
        if job:
            return job.processed_file_path  # 返回 processed_file_path 字段的值
        else:
            raise ValueError(f"找不到ID为 {job_id} 的批处理任务")

    def update_error(self, error_id, user_id, action_type, corrected_text=None):
        """更新错误记录（增强版）"""
        error = ErrorRecord.query.get(error_id)
        if not error:
            raise ValueError(f"找不到ID为{error_id}的错误记录")
        # 创建修正历史
        from models.correction_history import CorrectionHistory

        correction_data = {
            "error_record_id": error_id,
            "user_id": user_id,
            "original_text": error.original_text,
        }
        # 根据操作类型处理
        if action_type == "accept":
            error.status = "corrected"
            correction_data["corrected_text"] = error.suggested_correction
        elif action_type == "custom":
            if not corrected_text:
                raise ValueError("自定义修改需要提供修正内容")
            error.status = "corrected"
            correction_data["corrected_text"] = corrected_text
        elif action_type == "ignore":
            error.status = "ignored"
            correction_data["corrected_text"] = "标记为非错误"
        else:
            raise ValueError("无效的操作类型")
        # 更新错误记录
        error.corrected_by = user_id
        error.corrected_at = datetime.now()
        # 保存修正历史
        correction = CorrectionHistory(**correction_data)
        db.session.add(correction)
        db.session.commit()
        return error.to_dict()

    def delete_batch_job(self, job_id):
        """逻辑删除批处理任务"""
        job = BatchJob.query.get(job_id)
        if not job:
            raise ValueError("任务不存在")

        # 执行逻辑删除
        job.is_deleted = True
        db.session.commit()
        return True

    def _initialize_error_types(self):
        """初始化错误类型"""
        default_types = [
            ("器官词不对应", "器官名称与描述不匹配或错误", 1),
            ("方位词错误", "方位描述错误，如左右、上下位置描述有误", 2),
            ("描述不一致", "各部分描述之间存在不一致或冲突", 3),
        ]

        for name, desc, priority in default_types:
            error_type = ErrorType(name=name, description=desc, priority=priority)
            db.session.add(error_type)

        db.session.commit()
