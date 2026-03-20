# 🎯 Render配置指南 - 512MB免费方案

## ⚠️ 当前页面需要修改的配置

您现在在Render配置页面，请按以下步骤修改：

---

## 🔧 需要修改的配置项

### 1. Language（重要！）

**当前显示：Node**  
**请修改为：Python 3**

点击Language下拉框，选择 **Python 3**（或 Python 3.9）

---

### 2. Name（可选）

当前：`accounting-system`
可以保持不变，或修改为您喜欢的名字

---

### 3. Branch

**保持为：`main`（已经是了）

---

### 4. Region（日本访问建议）

| 选项 | 日本访问延迟 |
|------|-------------|
| Oregon (US West) | ⚠️ 约150ms |
| Frankfurt (EU) | ⚠️ 约200ms |
| Singapore (如果有的话 | ✅ 约80ms（推荐） |

---

### 5. Build Command

**输入：**
```
pip install -r requirements.txt
```

---

### 6. Start Command

**输入：**
```
gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app('production')"
```

---

### 7. Instance Type（免费方案）

点击 **Advanced** 展开，选择：

**Free**（512 MB RAM / 0.1 CPU）

✅ 512MB 足够您的系统使用！

---

### 8. Environment Variables（可选，但推荐）

点击 **Add Environment Variable** 添加：

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | （点击Generate生成） |
| `DATABASE_URL` | `sqlite:///data/accounting.db` |

---

## 🚀 完成配置后

1. 检查所有配置都修改正确后：
2. 点击 **Deploy Web Service**（黑色按钮）
3. 等待2-5分钟部署完成
4. 查看日志等待状态变为 **Live**

---

## 🌐 部署完成后

您会获得一个URL：
```
https://accounting-system-xxx.onrender.com
```

**默认登录账号：
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | Test@123456 |

---

## ⚠️ Render免费版说明

| 限制 | 说明 |
|------|------|
| RAM | 512MB（足够） |
| CPU | 0.1（足够演示） |
| 休眠 | 15分钟无访问后休眠 |
| 唤醒 | 首次访问需30秒唤醒 |
| 每月 | 750小时免费运行时间 |

---

## 📋 配置检查清单

在点击Deploy前，请确认：

- [ ] Language已改为 **Python 3**
- [ ] Build Command已填写
- [ ] Start Command已填写
- [ ] Instance Type选择了 **Free**
- [ ] （可选）添加了Environment Variables

---

**现在按照上面的指南修改配置吧！**
