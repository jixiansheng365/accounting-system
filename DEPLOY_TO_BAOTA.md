# 宝塔面板部署指南

## 服务器信息

- **公网IP**: 111.231.74.27
- **配置**: 2核2G 3M带宽 40G SSD
- **地域**: 上海
- **面板**: 宝塔Linux面板

---

## 第一步：登录宝塔面板

### 1.1 获取宝塔面板登录信息

1. 登录腾讯云控制台
2. 进入轻量应用服务器管理页面
3. 找到你的服务器实例，点击"登录"或"更多操作" → "重置密码"
4. 查看宝塔面板登录地址、用户名和密码

### 1.2 访问宝塔面板

在浏览器中访问：
```
http://111.231.74.27:8888
```

> **注意**：首次访问可能需要放行8888端口。如果无法访问，请在腾讯云控制台的"防火墙"中添加规则：
> - 协议：TCP
> - 端口：8888
> - 来源：0.0.0.0/0

---

## 第二步：安装必要软件

### 2.1 安装Python 3.9

1. 登录宝塔面板后，点击左侧"软件商店"
2. 搜索"Python"
3. 找到"Python 3.9"或"Python 3.10"，点击"安装"
4. 选择"极速安装"或"编译安装"（推荐极速安装）

### 2.2 安装Nginx

1. 在软件商店搜索"Nginx"
2. 点击"安装"，选择最新稳定版本

---

## 第三步：上传项目代码

### 3.1 创建网站目录

1. 点击左侧"文件"
2. 进入 `/www/wwwroot/` 目录
3. 点击"新建目录"，命名为 `accounting-system`

### 3.2 上传代码

**方式一：使用Git（推荐）**

1. 点击左侧"终端"或使用SSH连接服务器
2. 执行以下命令：

```bash
cd /www/wwwroot
git clone https://github.com/jixiansheng365/accounting-system.git
cd accounting-system
```

**方式二：直接上传压缩包**

1. 在本地将 `accounting-system` 文件夹压缩为 zip
2. 在宝塔文件管理中进入 `/www/wwwroot/`
3. 点击"上传"，选择压缩包
4. 上传后右键点击压缩包，选择"解压"

---

## 第四步：配置Python项目

### 4.1 安装Python项目管理器

1. 点击左侧"软件商店"
2. 搜索"Python项目管理器"或"PM2"
3. 安装"Python项目管理器"（如果有）

### 4.2 创建虚拟环境并安装依赖

1. 点击左侧"终端"
2. 执行以下命令：

```bash
cd /www/wwwroot/accounting-system

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 4.3 初始化数据库

```bash
# 创建必要目录
mkdir -p data uploads logs

# 初始化数据库
python -c "from app import create_app; from app.models import db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 创建管理员账号
python reset_password.py
```

---

## 第五步：配置Nginx反向代理

### 5.1 创建网站

1. 点击左侧"网站"
2. 点击"添加站点"
3. 填写信息：
   - **域名**: 填写你的IP地址 `111.231.74.27` 或你的域名
   - **根目录**: `/www/wwwroot/accounting-system`
   - **PHP版本**: 纯静态
4. 点击"提交"

### 5.2 配置反向代理

1. 在网站列表中找到刚创建的站点，点击"设置"
2. 点击左侧"反向代理"
3. 点击"添加反向代理"
4. 填写信息：
   - **代理名称**: `accounting`
   - **目标URL**: `http://127.0.0.1:5000`
   - **发送域名**: `$host`
5. 点击"提交"

### 5.3 配置静态文件

1. 在站点设置中点击"配置文件"
2. 在 `server` 块中添加以下配置：

```nginx
location /static {
    alias /www/wwwroot/accounting-system/app/static;
    expires 30d;
}

location /uploads {
    alias /www/wwwroot/accounting-system/uploads;
    expires 30d;
}
```

3. 点击"保存"

---

## 第六步：使用PM2启动应用

### 6.1 安装PM2

```bash
npm install -g pm2
```

### 6.2 创建PM2配置文件

在 `/www/wwwroot/accounting-system/` 目录下创建 `ecosystem.config.js`：

```javascript
module.exports = {
  apps: [{
    name: 'accounting-system',
    script: 'venv/bin/gunicorn',
    args: '-w 2 -b 127.0.0.1:5000 "app:create_app(\'production\')"',
    cwd: '/www/wwwroot/accounting-system',
    interpreter: 'none',
    env: {
      'FLASK_ENV': 'production',
      'SECRET_KEY': 'your-secret-key-change-this-in-production',
      'DATABASE_URL': 'sqlite:///data/accounting.db'
    },
    error_file: 'logs/pm2-error.log',
    out_file: 'logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
```

### 6.3 启动应用

```bash
cd /www/wwwroot/accounting-system
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 第七步：配置防火墙

### 7.1 放行端口

在腾讯云控制台 → 轻量应用服务器 → 防火墙 → 添加规则：

| 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|
| TCP | 80 | 0.0.0.0/0 | HTTP访问 |
| TCP | 443 | 0.0.0.0/0 | HTTPS访问 |
| TCP | 8888 | 你的IP | 宝塔面板（限制只允许你的IP访问） |

### 7.2 宝塔面板安全设置

在宝塔面板 → 安全 → 放行端口：

- 80
- 443
- 8888

---

## 第八步：访问系统

### 8.1 访问地址

在浏览器中访问：
```
http://111.231.74.27
```

### 8.2 登录账号

- **管理员账号**: admin
- **默认密码**: Test@123456

> **重要**：首次登录后请立即修改密码！

---

## 常用命令

### PM2命令

```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs accounting-system

# 重启应用
pm2 restart accounting-system

# 停止应用
pm2 stop accounting-system
```

### 文件权限

```bash
# 设置正确的文件权限
cd /www/wwwroot/accounting-system
chown -R www:www .
chmod -R 755 .
chmod -R 777 data uploads logs
```

---

## 故障排除

### 问题1：502 Bad Gateway

**检查步骤**：
1. 确认PM2应用正在运行：`pm2 status`
2. 查看应用日志：`pm2 logs accounting-system`
3. 检查端口5000是否被占用：`netstat -tlnp | grep 5000`

### 问题2：数据库错误

**检查步骤**：
1. 确认data目录存在且有写权限
2. 检查数据库文件权限：`ls -la data/`
3. 重新初始化数据库

### 问题3：静态文件404

**检查步骤**：
1. 确认Nginx配置中static和uploads的alias路径正确
2. 检查文件权限
3. 重启Nginx：`nginx -s reload`

---

## 备份建议

### 数据库备份

```bash
# 每天凌晨3点备份数据库
0 3 * * * cp /www/wwwroot/accounting-system/data/accounting.db /www/wwwroot/accounting-system/backups/accounting_$(date +\%Y\%m\%d).db
```

### 上传文件备份

```bash
# 每周日备份上传文件
0 0 * * 0 tar -czf /www/wwwroot/accounting-system/backups/uploads_$(date +\%Y\%m\%d).tar.gz /www/wwwroot/accounting-system/uploads/
```

---

## 技术支持

如遇到问题，请检查：
1. PM2日志：`pm2 logs accounting-system`
2. Nginx日志：`/www/wwwlogs/`
3. 应用日志：`/www/wwwroot/accounting-system/logs/`
