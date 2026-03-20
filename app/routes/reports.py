"""
报表管理路由 / Report Management Routes
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from flask_babel import gettext as _
from datetime import datetime, timedelta
import os

from app.models import db
from app.models.report import Report
from app.models.customer import Customer
from app.models.user import User
from app.models.login_log import LoginLog
from config import config

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/query')
def query_reports():
    """报表查询页面 / Report query page"""
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    user_id = session.get('user_id')
    customer = Customer.query.filter_by(user_id=user_id).first()
    
    if not customer:
        return render_template('customer/reports.html', 
                               reports=[],
                               available_years=[],
                               report_types=[])
    
    # 获取可用年份
    years = db.session.query(Report.year).filter_by(customer_id=customer.id).distinct().order_by(Report.year.desc()).all()
    available_years = [y[0] for y in years] if years else [datetime.now().year]
    
    # 报表类型
    report_type_map = {
        'monthly': _('Monthly Report'),
        'balance_sheet': _('Balance Sheet'),
        'income_statement': _('Income Statement'),
        'profit_statement': _('Profit Statement'),
        'detail_ledger': _('Detail Ledger'),
        'general_ledger': _('General Ledger')
    }
    
    report_types = [{'id': k, 'name': v} for k, v in report_type_map.items()]
    
    # 获取筛选条件
    selected_year = request.args.get('year', type=int, default=datetime.now().year)
    selected_month = request.args.get('month', type=int)
    selected_report_type = request.args.get('report_type')
    period = request.args.get('period')
    
    # 构建查询
    query = Report.query.filter_by(customer_id=customer.id)
    
    if selected_year:
        query = query.filter_by(year=selected_year)
    if selected_month:
        query = query.filter_by(month=selected_month)
    if selected_report_type:
        query = query.filter_by(report_type=selected_report_type)
    
    # 期间快速筛选
    if period == '3months':
        cutoff = datetime.now() - timedelta(days=90)
        query = query.filter(Report.upload_date >= cutoff)
    elif period == '6months':
        cutoff = datetime.now() - timedelta(days=180)
        query = query.filter(Report.upload_date >= cutoff)
    elif period == '1year':
        cutoff = datetime.now() - timedelta(days=365)
        query = query.filter(Report.upload_date >= cutoff)
    
    reports = query.order_by(Report.upload_date.desc()).all()
    
    # 格式化报表数据
    report_list = []
    for report in reports:
        report_list.append({
            'id': report.id,
            'file_name': report.file_name,
            'report_type_name': report_type_map.get(report.report_type, report.report_type),
            'report_period': f"{report.year}年{report.month}月",
            'upload_date': report.upload_date.strftime('%Y-%m-%d %H:%M'),
            'file_size': format_file_size(report.file_size) if report.file_size else '-'
        })
    
    return render_template('customer/reports.html',
                           reports=report_list,
                           available_years=available_years,
                           report_types=report_types,
                           selected_year=selected_year,
                           selected_month=selected_month,
                           selected_report_type=selected_report_type,
                           period=period)


@reports_bp.route('/download/<int:report_id>')
def download_report(report_id):
    """下载报表 / Download report"""
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    from app.services.report_service import ReportService
    
    report = Report.query.get_or_404(report_id)
    
    # 验证权限 - 只能下载自己的报表
    user_id = session.get('user_id')
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer or report.customer_id != customer.id:
        return jsonify({'success': False, 'message': '无权访问此报表'}), 403
    
    # 获取文件路径
    file_path, error = ReportService.get_report_file_path(report_id)
    if error:
        return jsonify({'success': False, 'message': error}), 404
    
    # 增加下载次数
    ReportService.increment_download_count(report_id)
    
    # 发送文件
    return send_from_directory(
        os.path.dirname(file_path),
        os.path.basename(file_path),
        as_attachment=True,
        download_name=report.file_name
    )


@reports_bp.route('/preview/<int:report_id>')
def preview_report(report_id):
    """预览报表 / Preview report"""
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    from app.services.report_service import ReportService
    
    report = Report.query.get_or_404(report_id)
    
    # 验证权限 - 只能预览自己的报表
    user_id = session.get('user_id')
    customer = Customer.query.filter_by(user_id=user_id).first()
    if not customer or report.customer_id != customer.id:
        return jsonify({'success': False, 'message': '无权访问此报表'}), 403
    
    # 获取文件路径
    file_path, error = ReportService.get_report_file_path(report_id)
    if error:
        return jsonify({'success': False, 'message': error}), 404
    
    # 检查文件类型是否支持预览
    file_ext = report.file_type.lower() if report.file_type else ''
    
    if file_ext == 'pdf':
        # PDF文件直接在线预览
        return send_from_directory(
            os.path.dirname(file_path),
            os.path.basename(file_path),
            mimetype='application/pdf'
        )
    elif file_ext in ['jpg', 'jpeg', 'png']:
        # 图片文件直接显示
        mimetype = 'image/jpeg' if file_ext in ['jpg', 'jpeg'] else 'image/png'
        return send_from_directory(
            os.path.dirname(file_path),
            os.path.basename(file_path),
            mimetype=mimetype
        )
    else:
        # 其他类型文件提示下载
        return jsonify({
            'success': False,
            'message': '该文件类型不支持在线预览，请下载后查看',
            'file_type': file_ext
        }), 400


@reports_bp.route('/login-history')
def login_history():
    """登录历史页面 / Login history page"""
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    user_id = session.get('user_id')
    login_logs = LoginLog.query.filter_by(user_id=user_id).order_by(LoginLog.login_time.desc()).limit(20).all()
    
    return render_template('customer/login_history.html', login_logs=login_logs)


def format_file_size(size):
    """格式化文件大小 / Format file size"""
    if not size:
        return '-'
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


@reports_bp.route('/', methods=['GET'])
def list_reports():
    """报表列表页面 / Report list page"""
    if not session.get('user_id'):
        return redirect(url_for('auth.login_page'))
    
    user_id = session.get('user_id')
    customer = Customer.query.filter_by(user_id=user_id).first()
    
    if not customer:
        return render_template('customer/reports_list.html',
                               reports=[],
                               pagination=None)
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取该客户的报表
    query = Report.query.filter_by(customer_id=customer.id)
    
    pagination = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 处理报表数据
    reports = []
    for report in pagination.items:
        report_data = report.to_dict()
        reports.append(report_data)
    
    return render_template('customer/reports_list.html',
                           reports=reports,
                           pagination=pagination)


@reports_bp.route('/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """获取报表详情 / Get report details"""
    report = Report.query.get_or_404(report_id)
    return jsonify({
        'success': True,
        'data': report.to_dict()
    })


@reports_bp.route('/', methods=['POST'])
def create_report():
    """创建报表 / Create report"""
    data = request.get_json() or {}
    
    # 必填字段验证
    required_fields = ['report_name', 'report_type', 'report_year', 'customer_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': _('{} is required').format(field)
            }), 400
    
    # 验证客户是否存在
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({
            'success': False,
            'message': _('Customer not found')
        }), 404
    
    report = Report(
        report_name=data.get('report_name'),
        report_type=data.get('report_type'),
        report_year=data.get('report_year'),
        report_month=data.get('report_month'),
        report_quarter=data.get('report_quarter'),
        customer_id=data.get('customer_id'),
        file_path=data.get('file_path'),
        file_name=data.get('file_name'),
        file_size=data.get('file_size'),
        file_type=data.get('file_type'),
        description=data.get('description'),
        remarks=data.get('remarks'),
        created_by=data.get('created_by')
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report created successfully'),
        'data': report.to_dict()
    }), 201


@reports_bp.route('/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """更新报表 / Update report"""
    report = Report.query.get_or_404(report_id)
    data = request.get_json() or {}
    
    # 更新字段
    fields = [
        'report_name', 'report_type', 'report_year', 'report_month',
        'report_quarter', 'file_path', 'file_name', 'file_size',
        'file_type', 'description', 'remarks'
    ]
    
    for field in fields:
        if field in data:
            setattr(report, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report updated successfully'),
        'data': report.to_dict()
    })


@reports_bp.route('/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """删除报表 / Delete report"""
    report = Report.query.get_or_404(report_id)
    
    db.session.delete(report)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report deleted successfully')
    })


@reports_bp.route('/<int:report_id>/submit', methods=['POST'])
def submit_report(report_id):
    """提交报表 / Submit report"""
    report = Report.query.get_or_404(report_id)
    
    if report.status != 'draft':
        return jsonify({
            'success': False,
            'message': _('Only draft reports can be submitted')
        }), 400
    
    report.submit()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report submitted successfully'),
        'data': report.to_dict()
    })


@reports_bp.route('/<int:report_id>/review', methods=['POST'])
def review_report(report_id):
    """审核报表 / Review report"""
    report = Report.query.get_or_404(report_id)
    data = request.get_json() or {}
    
    if report.status != 'submitted':
        return jsonify({
            'success': False,
            'message': _('Only submitted reports can be reviewed')
        }), 400
    
    reviewer_id = data.get('reviewer_id')
    if not reviewer_id:
        return jsonify({
            'success': False,
            'message': _('Reviewer ID is required')
        }), 400
    
    report.review(reviewer_id)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report reviewed successfully'),
        'data': report.to_dict()
    })


@reports_bp.route('/<int:report_id>/approve', methods=['POST'])
def approve_report(report_id):
    """批准报表 / Approve report"""
    report = Report.query.get_or_404(report_id)
    
    if report.status != 'reviewed':
        return jsonify({
            'success': False,
            'message': _('Only reviewed reports can be approved')
        }), 400
    
    report.approve()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report approved successfully'),
        'data': report.to_dict()
    })


@reports_bp.route('/<int:report_id>/archive', methods=['POST'])
def archive_report(report_id):
    """归档报表 / Archive report"""
    report = Report.query.get_or_404(report_id)
    
    report.archive()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Report archived successfully'),
        'data': report.to_dict()
    })


@reports_bp.route('/statistics', methods=['GET'])
def get_report_statistics():
    """获取报表统计信息 / Get report statistics"""
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
    
    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'by_status': by_status,
            'by_type': by_type
        }
    })
