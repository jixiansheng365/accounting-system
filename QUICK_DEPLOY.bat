@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     代理记账客户管理系统 - 快速部署工具                      ║
echo ║     Accounting System Quick Deploy Tool                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 【步骤 1/3】正在检查GitHub配置...
echo.

REM 检查是否配置了GitHub用户名
for /f "tokens=*" %%a in ('git config user.name') do set GIT_USER=%%a
if "%GIT_USER%"=="" (
    echo ⚠️  请先配置GitHub用户名
    set /p GITHUB_USER="请输入您的GitHub用户名: "
    git config user.name "%GITHUB_USER%"
) else (
    echo ✅ GitHub用户名: %GIT_USER%
)

echo.
echo 【步骤 2/3】正在创建GitHub仓库...
echo.

REM 提示用户创建GitHub仓库
echo 请按以下步骤操作：
echo.
echo 1. 访问: https://github.com/new
echo 2. 仓库名称输入: accounting-system
echo 3. 选择 "Public" (公开仓库)
echo 4. 点击 "Create repository"
echo 5. 复制仓库URL (格式: https://github.com/用户名/accounting-system.git)
echo.

set /p REPO_URL="请输入您的GitHub仓库URL: "

echo.
echo 【步骤 3/3】正在推送代码到GitHub...
echo.

REM 添加远程仓库
git remote remove origin 2>nul
git remote add origin %REPO_URL%

REM 推送代码
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                    ✅ 推送成功！                             ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 接下来请在Render.com部署：
    echo.
    echo 1. 访问: https://dashboard.render.com/
    echo 2. 点击 "New +" → "Web Service"
    echo 3. 连接您的GitHub账号
    echo 4. 选择 "accounting-system" 仓库
    echo 5. 点击 "Create Web Service"
    echo.
    echo 部署完成后，您将获得一个类似以下的URL：
    echo https://accounting-system-xxx.onrender.com
    echo.
    echo 默认管理员账号：
    echo   用户名: admin
    echo   密码: Test@123456
    echo.
    start https://dashboard.render.com/
) else (
    echo.
    echo ❌ 推送失败，请检查：
    echo 1. GitHub仓库URL是否正确
    echo 2. 是否已配置GitHub SSH密钥或输入了正确的用户名密码
    echo.
    pause
)
