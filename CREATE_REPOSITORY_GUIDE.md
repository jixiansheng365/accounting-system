# 🚀 GitHub仓库创建详细指南

## 步骤1：登录GitHub

1. 访问 https://github.com/login
2. 输入您的用户名或邮箱地址
3. 输入密码
4. 点击 **Sign in** 登录

## 步骤2：创建新仓库

登录成功后：

1. 访问 https://github.com/new
2. 填写以下信息：

| 字段 | 值 | 说明 |
|------|-----|------|
| Repository name | `accounting-system` | 仓库名称 |
| Description | `代理记账客户管理系统` | 可选，填写项目描述 |
| Public/Private | **Public** | 必须选择公开，Render才能访问 |
| Add a README file | ☐ 不勾选 | 我们已经有代码了 |
| Add .gitignore | ☐ 不勾选 | 我们已经有了 |
| Choose a license | 不选择 |  |

3. 点击绿色按钮 **Create repository**

## 步骤3：配置本地Git连接

仓库创建成功后，GitHub会显示一个页面，上面有仓库的URL。

复制这个URL（类似：`https://github.com/您的用户名/accounting-system.git`），然后：

### 方法A：使用我准备的脚本（推荐）

```bash
双击运行: fix-github-connection.bat
```

选择 **方式1 (HTTPS)**，然后粘贴您的GitHub用户名。

### 方法B：手动配置

在项目目录打开终端，执行：

```bash
cd c:\Users\Administrator\Documents\trae_projects\projects_gongju\bi-ai-platform\accounting-system

# 添加远程仓库（替换为您的真实URL）
git remote add origin https://github.com/您的用户名/accounting-system.git

# 验证配置
git remote -v
```

## 步骤4：推送代码到GitHub

```bash
# 推送代码
git push -u origin main
```

如果提示输入用户名和密码：
- **用户名**：您的GitHub用户名
- **密码**：如果启用了两步验证，需要使用个人访问令牌(PAT)

### 创建个人访问令牌(PAT)

如果需要PAT：
1. 访问 https://github.com/settings/tokens
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 勾选 `repo` 权限
4. 点击 **Generate token**
5. **重要**：复制生成的token，只显示一次
6. 推送时用这个token代替密码

## 步骤5：在Render.com部署

代码推送成功后：

1. 访问 https://dashboard.render.com/
2. 点击 **New +** → **Web Service**
3. 连接您的GitHub账号
4. 选择 `accounting-system` 仓库
5. Render会自动识别配置
6. 点击 **Create Web Service**

## 完成！

部署成功后，您会获得一个URL：
```
https://accounting-system-xxx.onrender.com
```

默认登录账号：
- 用户名：`admin`
- 密码：`Test@123456`

---

## 快捷命令参考

```bash
# 查看当前状态
git status

# 查看远程仓库
git remote -v

# 移除旧的远程仓库
git remote remove origin

# 添加新的远程仓库
git remote add origin https://github.com/用户名/accounting-system.git

# 推送代码
git push -u origin main
```
