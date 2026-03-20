# 🚀 快速部署指南 - 5分钟上线

## ✅ 当前状态

- ✅ GitHub仓库已创建：https://github.com/jixiansheng365/accounting-system
- ✅ 本地代码已准备完毕
- ✅ 部署配置文件已就绪

---

## 📋 现在请按顺序完成以下4步：

---

### 第1步：登录GitHub（现在页面）

在当前浏览器页面：
1. 输入您的GitHub用户名：`jixiansheng365`
2. 输入您的GitHub密码
3. 点击 **Sign in** 登录

---

### 第2步：创建/获取个人访问令牌(PAT)

登录后，您已经在个人访问令牌页面了。

**如果要创建新令牌：**
1. 点击 **Generate new token** → **Generate new token (classic)**
2. Note（说明）填写：`Accounting System Deploy`
3. Expiration（过期时间）选择：`90 days`
4. 勾选权限：✅ `repo`（第一项，全部勾选）
5. 点击 **Generate token**
6. **重要**：立即复制生成的token（类似 `ghp_xxxxxxxxxxxx`）

**或者使用现有令牌：**
您已经有两个令牌，可以直接复制其中一个使用。

---

### 第3步：推送代码到GitHub

打开一个新的终端（或使用现有的），执行：

```bash
cd c:\Users\Administrator\Documents\trae_projects\projects_gongju\bi-ai-platform\accounting-system
git push -u origin master
```

**提示输入时：**
- 用户名：`jixiansheng365`
- 密码：**粘贴刚才复制的token**（不是GitHub密码！）

---

### 第4步：在Render.com部署

代码推送成功后：

1. 访问：https://dashboard.render.com/
2. 点击 **New +** → **Web Service**
3. 连接您的GitHub账号（jixiansheng365）
4. 选择 `accounting-system` 仓库
5. Render会自动识别配置
6. 点击 **Create Web Service**
7. 等待2-5分钟部署完成

---

## 🎉 完成！

部署成功后，您会获得一个URL：
```
https://accounting-system-xxx.onrender.com
```

**默认登录账号：**
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | Test@123456 |

---

## 💡 快捷脚本

我也为您准备了一键脚本：

| 脚本 | 用途 |
|------|------|
| `PUSH_TO_GITHUB.bat` | 推送代码到GitHub（双击运行） |
| `fix-github-connection.bat` | 修复Git连接问题 |

---

## ⚠️ 注意事项

1. **个人访问令牌只显示一次**，请立即复制保存
2. Render免费版15分钟无访问后会休眠，首次访问需30秒唤醒
3. 数据库会自动持久化保存（1GB空间）
4. 每月750小时免费运行时间，足够演示使用

---

## 📞 遇到问题？

查看详细文档：
- `FINAL_DEPLOY_GUIDE.md` - 完整部署指南
- `deploy-to-render.md` - Render详细文档
