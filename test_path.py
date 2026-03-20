import os
from app import create_app
from app.services.report_service import ReportService

app = create_app()
app.app_context().push()

# 测试 ID 24 的报表
report_id = 24
file_path, error = ReportService.get_report_file_path(report_id)

print(f"Report ID: {report_id}")
print(f"Computed file path: {file_path}")
print(f"Error: {error}")
print(f"File exists: {os.path.exists(file_path) if file_path else False}")

# 检查 UPLOAD_FOLDER
upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
print(f"\nUPLOAD_FOLDER config: {upload_folder}")
print(f"UPLOAD_FOLDER type: {type(upload_folder)}")

# 检查 app.root_path
print(f"\nApp root_path: {app.root_path}")
