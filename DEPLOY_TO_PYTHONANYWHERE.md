# 🚀 PythonAnywhere 完全免费部署指南

## ✅ 为什么选择PythonAnywhere？

| 特性 | 说明 |
|------|------|
| 价格 | 完全免费，无需信用卡 |
| 存储空间 | 512MB（足够） |
| 支持 | Flask + SQLite完美支持 |
| 有效期 | 永久免费（不是试用） |
| 适合 | 演示和小型项目 |

---

## 📋 部署步骤（10分钟完成）

### 第1步：注册PythonAnywhere账号

1. 访问：https://www.pythonanywhere.com/
2. 点击 **Pricing** → 选择 **Create a Beginner account**（免费）
3. 填写注册信息：
   - 用户名：`accountingsystem`（或您喜欢的名字）
   - 邮箱和密码
4. 点击 **Register** 完成注册
5. 验证邮箱

---

### 第2步：上传代码

登录后，在Dashboard页面：

#### 方法A：使用Git上传（推荐）

1. 点击顶部菜单 **Consoles** → **Bash**
2. 在Bash终端执行：

```bash
# 克隆您的GitHub仓库
git clone https://github.com/jixiansheng365/accounting-system.git

# 进入项目目录
cd accounting-system

# 查看文件
ls -la
```

#### 方法B：手动上传文件

如果Git不行，可以手动上传：
1. 点击 **Files** 标签
2. 点击 **Upload a file** 逐个上传
3. 或创建文件夹后批量上传

---

### 第3步：创建虚拟环境并安装依赖

在Bash终端继续执行：

```bash
cd accounting-system

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 验证安装
pip list
```

---

### 第4步：配置WSGI文件

1. 点击顶部菜单 **Web**
2. 点击 **Add a new web app**
3. 选择 **Manual configuration**
4. 选择 **Python 3.9**（或最新版本）
5. 点击 **Next** 完成

配置WSGI文件：
1. 在Web页面，找到 **Code** 部分
2. 点击 **WSGI configuration file** 链接
3. 替换内容为：

```python
import sys
import os

# 添加项目路径
path = '/home/您的用户名/accounting-system'
if path not in sys.path:
    sys.path.append(path)

# 激活虚拟环境
activate_this = '/home/您的用户名/accounting-system/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# 导入Flask应用
from app import create_app

# 设置生产环境
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
os.environ['DATABASE_URL'] = 'sqlite:////home/您的用户名/accounting-system/data/accounting.db'

# 创建应用
application = create_app('production')
```

**注意**：把 `您的用户名` 替换为您的PythonAnywhere用户名！

---

### 第5步：配置静态文件

在Web页面的 **Static files** 部分：

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/您的用户名/accounting-system/app/static` |
| `/uploads/` | `/home/您的用户名/accounting-system/uploads` |

点击 **Add a new static file mapping** 添加上面两个路径。

---

### 第6步：初始化数据库

回到Bash终端：

```bash
cd accounting-system
source venv/bin/activate

# 创建必要的目录
mkdir -p data uploads logs

# 初始化数据库
python -c "from app import create_app; from app.models import db; app = create_app('production'); app.app_context().push(); db.create_all()"

# 创建管理员账号
python reset_password.py
```

---

### 第7步：启动应用

1. 回到 **Web** 页面
2. 点击绿色的 **Reload** 按钮
3. 等待几秒钟
4. 访问您的URL：`https://您的用户名.pythonanywhere.com`

---

## 🌐 访问您的系统

部署成功后，访问地址：
```
https://您的用户名.pythonanywhere.com
```

**默认登录账号：**
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | Test@123456 |

---

## ⚠️ PythonAnywhere免费版限制

| 限制 | 说明 |
|------|------|
| 存储空间 | 512MB（足够） |
| CPU时间 | 100秒/天（足够演示） |
| 网络流量 | 不限 |
| 休眠 | 24小时无访问后休眠（访问一下即可唤醒） |
| 数据库 | SQLite完全支持 |

---

## 🔧 常见问题

### Q: 如何更新代码？
A: 在Bash终端执行：
```bash
cd accounting-system
git pull
source venv/bin/activate
pip install -r requirements.txt
```
然后在Web页面点击 **Reload**。

### Q: 如何查看日志？
A: 在Web页面的 **Log files** 部分查看。

### Q: 数据库在哪里？
A: `/home/您的用户名/accounting-system/data/accounting.db`

---

## 📞 需要帮助？

查看详细文档：
- GitHub仓库：https://github.com/jixiansheng365/accounting-system
- PythonAnywhere文档：https://help.pythonanywhere.com/

---

## 🎉 开始部署！

**立即访问：https://www.pythonanywhere.com/ 注册并开始部署！**
