# 🚀 一键部署到 Render.com 指南

## 📋 部署前准备

配置文件已全部准备就绪：
- ✅ `render.yaml` - Render平台配置文件
- ✅ `Procfile` - 进程配置文件
- ✅ `runtime.txt` - Python版本指定
- ✅ `requirements.txt` - 已添加gunicorn

---

## 🎯 快速部署步骤（3分钟完成）

### 步骤1：创建GitHub仓库（1分钟）

1. 访问 https://github.com/new
2. 仓库名称：`accounting-system`
3. 选择 **Public**（公开）
4. 点击 **Create repository**

### 步骤2：推送代码到GitHub（1分钟）

在本地项目目录打开终端，执行：

```bash
cd c:\Users\Administrator\Documents\trae_projects\projects_gongju\bi-ai-platform\accounting-system

# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit for Render deployment"

# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/accounting-system.git

# 推送代码
git push -u origin main
```

### 步骤3：在Render.com部署（1分钟）

1. 访问 https://dashboard.render.com/
2. 点击 **New +** → **Web Service**
3. 连接你的GitHub账号
4. 选择 `accounting-system` 仓库
5. Render会自动识别 `render.yaml` 配置
6. 点击 **Create Web Service**

---

## ⚙️ 自动配置说明

Render会自动配置以下环境：
- **Python版本**: 3.9
- **运行命令**: `gunicorn -w 2 -b 0.0.0.0:10000 "app:create_app('production')"`
- **数据库**: SQLite（自动挂载持久化磁盘）
- **密钥**: 自动生成SECRET_KEY

---

## 🔑 默认登录账号

部署完成后，使用以下账号登录：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | Test@123456 |

**⚠️ 重要**：首次登录后请立即修改密码！

---

## 🌐 访问地址

部署完成后，Render会提供一个类似以下的URL：
```
https://accounting-system-xxx.onrender.com
```

访问路径：
- 管理后台：`https://your-domain.onrender.com/auth/login`
- 客户登录：`https://your-domain.onrender.com/customer/login`

---

## 📁 项目结构

```
accounting-system/
├── app/                    # Flask应用主目录
│   ├── models/            # 数据模型
│   ├── routes/            # 路由处理
│   ├── services/          # 业务逻辑
│   ├── static/            # 静态文件(CSS/JS)
│   ├── templates/         # HTML模板
│   └── translations/      # 多语言文件
├── data/                  # SQLite数据库目录
├── uploads/               # 上传文件目录
├── requirements.txt       # Python依赖
├── render.yaml           # Render配置文件 ⭐
├── Procfile              # 进程配置 ⭐
├── runtime.txt           # Python版本 ⭐
└── run.py                # 启动脚本
```

---

## 🔧 手动部署（备选方案）

如果自动部署失败，可以手动配置：

1. 在Render创建Web Service时选择 **Python 3**
2. 构建命令：`pip install -r requirements.txt`
3. 启动命令：`gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app('production')"`
4. 添加环境变量：
   - `FLASK_ENV=production`
   - `DATABASE_URL=sqlite:///data/accounting.db`
   - `SECRET_KEY`（随机字符串）
5. 添加磁盘：
   - 名称：`data`
   - 挂载路径：`/opt/render/project/src/data`
   - 大小：1GB

---

## ❓ 常见问题

### Q: 部署后数据库在哪里？
A: 数据库存放在挂载的磁盘中，路径为 `/opt/render/project/src/data/accounting.db`，数据会持久化保存。

### Q: 免费版有什么限制？
A: Render免费版限制：
- 服务在15分钟无访问后会休眠
- 首次访问可能需要30秒唤醒
- 每月750小时运行时间
- 足够演示使用

### Q: 如何更新代码？
A: 只需推送新代码到GitHub，Render会自动重新部署：
```bash
git add .
git commit -m "更新说明"
git push
```

### Q: 如何查看日志？
A: 在Render Dashboard中点击你的服务，选择 **Logs** 标签页。

---

## 📞 技术支持

部署遇到问题？检查以下文件：
- [DEPLOYMENT.md](DEPLOYMENT.md) - 详细部署文档
- [test_accounts.md](test_accounts.md) - 测试账号信息

---

**🎉 部署完成后，请将生成的URL分享给客户即可！**
