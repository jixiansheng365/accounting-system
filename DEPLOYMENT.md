# 代理记账客户管理系统 - 部署文档

## 系统版本信息

- **版本**: v1.0.0 (初版)
- **语言**: 简体中文 (zh_CN)
- **部署日期**: 2026-03-20
- **测试状态**: ✅ 全部通过

## 系统功能清单

### 已完成功能

1. **用户认证**
   - ✅ 用户登录/登出
   - ✅ 管理员登录
   - ✅ 登录日志记录

2. **客户管理**
   - ✅ 客户列表
   - ✅ 客户详情
   - ✅ 添加/编辑/删除客户
   - ✅ 客户搜索

3. **报表管理**
   - ✅ 报表上传
   - ✅ 报表列表
   - ✅ 报表预览
   - ✅ 报表下载

4. **系统功能**
   - ✅ 系统设置
   - ✅ 系统日志
   - ✅ 多语言支持 (简体中文)

## 部署要求

### 服务器环境

- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 7+)
- **Python**: 3.9+
- **内存**: 2GB+
- **磁盘**: 10GB+

### 依赖软件

- Python 3.9+
- pip
- virtualenv (推荐)
- Nginx (生产环境)
- Gunicorn (WSGI服务器)

## 部署步骤

### 1. 上传代码

```bash
# 将代码上传到服务器
scp -r accounting-system user@server:/opt/
# 或
rsync -avz --exclude='__pycache__' --exclude='*.pyc' accounting-system/ user@server:/opt/accounting-system/
```

### 2. 安装依赖

```bash
cd /opt/accounting-system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置生产环境

```bash
# 设置环境变量
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here-change-in-production
export DATABASE_URL=sqlite:///data/accounting.db
```

### 4. 初始化数据库

```bash
# 创建数据目录
mkdir -p data uploads logs

# 运行数据库初始化
python -c "from app import create_app; from app.models import db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 创建管理员账号
python reset_password.py
```

### 5. 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/accounting-system/app/static;
        expires 30d;
    }

    location /uploads {
        alias /opt/accounting-system/uploads;
        expires 30d;
    }
}
```

### 6. 配置 Systemd 服务

```ini
# /etc/systemd/system/accounting.service
[Unit]
Description=Accounting Customer Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/accounting-system
Environment="PATH=/opt/accounting-system/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/opt/accounting-system/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app('production')"

[Install]
WantedBy=multi-user.target
```

### 7. 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start accounting
sudo systemctl enable accounting

# 检查状态
sudo systemctl status accounting
```

## 测试清单

部署完成后，请进行以下测试：

### 基础功能测试

- [ ] 访问登录页面 http://your-domain.com/auth/login
- [ ] 使用 admin/Test@123456 登录
- [ ] 访问仪表盘
- [ ] 访问客户管理页面
- [ ] 访问报表管理页面
- [ ] 访问系统设置页面
- [ ] 访问系统日志页面

### 安全测试

- [ ] 未登录时访问管理页面应重定向到登录页
- [ ] 错误密码登录应显示错误提示

## 默认账号

- **管理员账号**: admin
- **默认密码**: Test@123456
- **建议**: 首次登录后立即修改密码

## 备份策略

### 数据库备份

```bash
# 每天凌晨3点备份
0 3 * * * cp /opt/accounting-system/data/accounting.db /opt/accounting-system/backups/accounting_$(date +\%Y\%m\%d).db
```

### 上传文件备份

```bash
# 每周日备份上传文件
0 0 * * 0 tar -czf /opt/accounting-system/backups/uploads_$(date +\%Y\%m\%d).tar.gz /opt/accounting-system/uploads/
```

## 故障排除

### 常见问题

1. **无法访问页面**
   - 检查服务状态: `sudo systemctl status accounting`
   - 检查端口占用: `netstat -tlnp | grep 5000`
   - 查看日志: `sudo journalctl -u accounting -f`

2. **翻译不生效**
   - 重新编译翻译: `pybabel compile -d app/translations -f`
   - 重启服务

3. **数据库错误**
   - 检查数据库文件权限
   - 确保数据目录可写

## 技术支持

- **测试脚本**: `python test_zh_cn.py`
- **重置密码**: `python reset_password.py`
- **日志位置**: `/opt/accounting-system/logs/`

## 版本历史

### v1.0.0 (2026-03-20)
- 初始版本
- 简体中文支持
- 基础功能完整

---

**部署完成确认**: 所有功能测试通过，系统可正常使用。
