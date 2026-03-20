"""
报表服务层 / Report Service Layer
处理报表相关的业务逻辑
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from flask import current_app
from flask_babel import gettext as _
from werkzeug.utils import secure_filename

from app.models import db
from app.models.report import Report
from app.models.customer import Customer
from app.models.user import User


class ReportService:
    """报表服务类 / Report Service Class"""
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip', 'rar'}
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        检查文件扩展名是否允许 / Check if file extension is allowed
        
        Args:
            filename: 文件名
            
        Returns:
            是否允许
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ReportService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_report_by_id(report_id: int) -> Optional[Report]:
        """
        根据ID获取报表 / Get report by ID
        
        Args:
            report_id: 报表ID
            
        Returns:
            Report对象或None
        """
        return Report.query.get(report_id)
    
    @staticmethod
    def list_reports(
        page: int = 1,
        per_page: int = 20,
        customer_id: Optional[int] = None,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        created_by: Optional[int] = None,
        order_by: str = 'created_at',
        order_desc: bool = True
    ) -> Tuple[List[Report], int]:
        """
        获取报表列表 / Get report list
        
        Args:
            page: 页码
            per_page: 每页数量
            customer_id: 客户ID筛选
            report_type: 报表类型筛选
            status: 状态筛选
            year: 年份筛选
            month: 月份筛选
            created_by: 创建人筛选
            order_by: 排序字段
            order_desc: 是否降序
            
        Returns:
            (报表列表, 总数)
        """
        query = Report.query
        
        # 应用筛选条件
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if report_type:
            query = query.filter_by(report_type=report_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if year:
            query = query.filter_by(year=year)
        
        if month:
            query = query.filter_by(month=month)
        
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        # 应用排序
        order_column = getattr(Report, order_by, Report.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def create_report(data: Dict[str, Any]) -> Tuple[Optional[Report], Optional[str]]:
        """
        创建报表 / Create report
        
        Args:
            data: 报表数据字典
            
        Returns:
            (Report对象, 错误信息)
        """
        # 验证必填字段
        required_fields = ['report_name', 'report_type', 'year', 'customer_id']
        for field in required_fields:
            if not data.get(field):
                return None, _('{} is required').format(field)
        
        # 验证客户是否存在
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return None, _('Customer not found')
        
        try:
            report = Report(
                report_name=data.get('report_name'),
                report_type=data.get('report_type'),
                year=data.get('year'),
                month=data.get('month'),
                report_quarter=data.get('report_quarter'),
                customer_id=data.get('customer_id'),
                file_path=data.get('file_path'),
                file_name=data.get('file_name'),
                file_size=data.get('file_size'),
                file_type=data.get('file_type'),
                status=data.get('status', 'draft'),
                description=data.get('description'),
                remarks=data.get('remarks'),
                created_by=data.get('created_by')
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def upload_report(
        file,
        customer_id: int,
        report_name: str,
        report_type: str,
        year: int,
        month: Optional[int] = None,
        description: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Tuple[Optional[Report], Optional[str]]:
        """
        上传报表文件 / Upload report file
        
        Args:
            file: 文件对象
            customer_id: 客户ID
            report_name: 报表名称
            report_type: 报表类型
            year: 年份
            month: 月份
            description: 描述
            created_by: 创建人ID
            
        Returns:
            (Report对象, 错误信息)
        """
        # 验证客户是否存在
        customer = Customer.query.get(customer_id)
        if not customer:
            return None, _('Customer not found')
        
        # 验证文件
        if not file or not file.filename:
            return None, _('No file provided')
        
        if not ReportService.allowed_file(file.filename):
            return None, _('File type not allowed. Allowed types: {}').format(
                ', '.join(ReportService.ALLOWED_EXTENSIONS)
            )
        
        try:
            # 生成安全的文件名
            original_filename = secure_filename(file.filename)
            file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}" if file_ext else uuid.uuid4().hex
            
            # 创建客户专属目录
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            # 使用绝对路径
            base_upload_dir = os.path.join(current_app.root_path, '..', upload_folder)
            base_upload_dir = os.path.abspath(base_upload_dir)
            
            customer_folder = os.path.join(base_upload_dir, f'customer_{customer_id}')
            os.makedirs(customer_folder, exist_ok=True)
            
            # 按年月组织文件
            year_month_folder = os.path.join(customer_folder, f'{year}', f'{month:02d}' if month else '00')
            os.makedirs(year_month_folder, exist_ok=True)
            
            # 保存文件 - 使用绝对路径
            abs_file_path = os.path.join(year_month_folder, unique_filename)
            file.save(abs_file_path)
            
            # 获取文件大小
            file_size = os.path.getsize(abs_file_path)
            
            # 保存相对路径到数据库（便于迁移）
            relative_path = os.path.join(f'customer_{customer_id}', f'{year}', f'{month:02d}' if month else '00', unique_filename)
            
            # 创建报表记录
            report = Report(
                report_name=report_name,
                report_type=report_type,
                year=year,
                month=month,
                customer_id=customer_id,
                file_path=relative_path,
                file_name=original_filename,
                file_size=file_size,
                file_type=file_ext,
                status='submitted',  # 上传后默认为已提交状态
                description=description,
                created_by=created_by
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report, None
            
        except Exception as e:
            db.session.rollback()
            # 如果文件已保存，尝试删除
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            return None, str(e)
    
    @staticmethod
    def update_report(report_id: int, data: Dict[str, Any]) -> Tuple[Optional[Report], Optional[str]]:
        """
        更新报表信息 / Update report
        
        Args:
            report_id: 报表ID
            data: 更新数据字典
            
        Returns:
            (Report对象, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return None, _('Report not found')
        
        try:
            # 可更新的字段
            fields = [
                'report_name', 'report_type', 'year', 'month',
                'report_quarter', 'description', 'remarks'
            ]
            
            for field in fields:
                if field in data:
                    setattr(report, field, data[field])
            
            db.session.commit()
            
            return report, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_report(report_id: int, delete_file: bool = True) -> Tuple[bool, Optional[str]]:
        """
        删除报表 / Delete report
        
        Args:
            report_id: 报表ID
            delete_file: 是否同时删除文件
            
        Returns:
            (是否成功, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return False, _('Report not found')
        
        file_path = report.file_path
        
        try:
            db.session.delete(report)
            db.session.commit()
            
            # 删除文件
            if delete_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    # 记录错误但不影响删除操作
                    current_app.logger.warning(f'Failed to delete file {file_path}: {e}')
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def submit_report(report_id: int) -> Tuple[Optional[Report], Optional[str]]:
        """
        提交报表 / Submit report
        
        Args:
            report_id: 报表ID
            
        Returns:
            (Report对象, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return None, _('Report not found')
        
        if report.status != 'draft':
            return None, _('Only draft reports can be submitted')
        
        try:
            report.submit()
            db.session.commit()
            return report, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def review_report(report_id: int, reviewer_id: int, approved: bool = True) -> Tuple[Optional[Report], Optional[str]]:
        """
        审核报表 / Review report
        
        Args:
            report_id: 报表ID
            reviewer_id: 审核人ID
            approved: 是否通过审核
            
        Returns:
            (Report对象, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return None, _('Report not found')
        
        if report.status != 'submitted':
            return None, _('Only submitted reports can be reviewed')
        
        # 验证审核人是否存在
        reviewer = User.query.get(reviewer_id)
        if not reviewer:
            return None, _('Reviewer not found')
        
        try:
            if approved:
                report.review(reviewer_id)
            else:
                # 审核不通过，退回草稿状态
                report.status = 'draft'
                report.remarks = (report.remarks or '') + f'\n[审核不通过 - {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}]'
            
            db.session.commit()
            return report, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def approve_report(report_id: int) -> Tuple[Optional[Report], Optional[str]]:
        """
        批准报表 / Approve report
        
        Args:
            report_id: 报表ID
            
        Returns:
            (Report对象, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return None, _('Report not found')
        
        if report.status != 'reviewed':
            return None, _('Only reviewed reports can be approved')
        
        try:
            report.approve()
            db.session.commit()
            return report, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def archive_report(report_id: int) -> Tuple[Optional[Report], Optional[str]]:
        """
        归档报表 / Archive report
        
        Args:
            report_id: 报表ID
            
        Returns:
            (Report对象, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return None, _('Report not found')
        
        try:
            report.archive()
            db.session.commit()
            return report, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_report_file_path(report_id: int) -> Tuple[Optional[str], Optional[str]]:
        """
        获取报表文件路径 / Get report file path
        
        Args:
            report_id: 报表 ID
            
        Returns:
            (文件路径，错误信息)
        """
        from flask import current_app
        
        report = Report.query.get(report_id)
        if not report:
            return None, _('Report not found')
        
        if not report.file_path:
            return None, _('File path not recorded')
        
        # 如果是相对路径，转换为绝对路径
        file_path = report.file_path
        
        # 处理以 / 开头的路径（Unix 风格相对路径）
        if file_path.startswith('/'):
            file_path = file_path[1:]  # 去掉开头的 /
        
        if not os.path.isabs(file_path):
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            # 确保 upload_folder 是字符串
            if isinstance(upload_folder, str):
                upload_dir = upload_folder
            else:
                upload_dir = 'uploads'
            
            # 如果 upload_dir 已经是绝对路径，直接拼接 file_path
            if os.path.isabs(upload_dir):
                file_path = os.path.join(upload_dir, file_path)
            else:
                file_path = os.path.join(current_app.root_path, '..', upload_dir, file_path)
            
            file_path = os.path.abspath(file_path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            current_app.logger.error(f'File not found: {file_path}')
            return None, _('File not found')
        
        return file_path, None
    
    @staticmethod
    def increment_download_count(report_id: int) -> Tuple[bool, Optional[str]]:
        """
        增加下载次数 / Increment download count
        
        Args:
            report_id: 报表ID
            
        Returns:
            (是否成功, 错误信息)
        """
        report = Report.query.get(report_id)
        if not report:
            return False, _('Report not found')
        
        try:
            report.download_count = (report.download_count or 0) + 1
            report.last_downloaded_at = datetime.utcnow()
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_report_statistics() -> Dict[str, Any]:
        """
        获取报表统计信息 / Get report statistics
        
        Returns:
            统计信息字典
        """
        total = Report.query.count()
        
        # 按状态统计
        by_status = {}
        for status, _ in Report.get_status_choices():
            count = Report.query.filter_by(status=status).count()
            by_status[status] = count
        
        # 按类型统计
        by_type = {}
        for report_type, _ in Report.get_type_choices():
            count = Report.query.filter_by(report_type=report_type).count()
            by_type[report_type] = count
        
        # 本月上传
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        uploaded_this_month = Report.query.filter(Report.created_at >= current_month).count()
        
        # 按年份统计
        years = db.session.query(Report.year).distinct().all()
        by_year = {}
        for year_tuple in years:
            year = year_tuple[0]
            if year:
                count = Report.query.filter_by(year=year).count()
                by_year[year] = count
        
        return {
            'total': total,
            'by_status': by_status,
            'by_type': by_type,
            'by_year': by_year,
            'uploaded_this_month': uploaded_this_month
        }
    
    @staticmethod
    def get_customer_report_statistics(customer_id: int) -> Dict[str, Any]:
        """
        获取客户的报表统计 / Get customer's report statistics
        
        Args:
            customer_id: 客户ID
            
        Returns:
            统计信息字典
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return {}
        
        total = Report.query.filter_by(customer_id=customer_id).count()
        
        # 按状态统计
        by_status = {}
        for status, _ in Report.get_status_choices():
            count = Report.query.filter_by(customer_id=customer_id, status=status).count()
            by_status[status] = count
        
        # 按类型统计
        by_type = {}
        for report_type, _ in Report.get_type_choices():
            count = Report.query.filter_by(customer_id=customer_id, report_type=report_type).count()
            by_type[report_type] = count
        
        # 最近上传
        recent_reports = Report.query.filter_by(customer_id=customer_id).order_by(
            Report.created_at.desc()
        ).limit(5).all()
        
        return {
            'customer_id': customer_id,
            'customer_name': customer.company_name,
            'total': total,
            'by_status': by_status,
            'by_type': by_type,
            'recent_reports': [r.to_dict() for r in recent_reports]
        }
    
    @staticmethod
    def batch_upload_reports(
        files: List,
        customer_id: int,
        report_type: str,
        year: int,
        month: Optional[int] = None,
        created_by: Optional[int] = None
    ) -> Tuple[List[Report], List[Dict[str, str]]]:
        """
        批量上传报表 / Batch upload reports
        
        Args:
            files: 文件列表
            customer_id: 客户ID
            report_type: 报表类型
            year: 年份
            month: 月份
            created_by: 创建人ID
            
        Returns:
            (成功列表, 失败列表)
        """
        success_reports = []
        failed_files = []
        
        for file in files:
            if not file or not file.filename:
                continue
            
            # 使用文件名作为报表名称（去除扩展名）
            report_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
            
            report, error = ReportService.upload_report(
                file=file,
                customer_id=customer_id,
                report_name=report_name,
                report_type=report_type,
                year=year,
                month=month,
                created_by=created_by
            )
            
            if report:
                success_reports.append(report)
            else:
                failed_files.append({
                    'filename': file.filename,
                    'error': error
                })
        
        return success_reports, failed_files
