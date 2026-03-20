@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     修复GitHub连接问题                                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 【步骤1】配置Git用户信息...
echo.

REM 设置Git用户名和邮箱（使用通用配置）
git config user.email "deploy@accounting-system.local"
git config user.name "Accounting System Deploy"

echo ✅ Git用户信息已配置
echo    邮箱: deploy@accounting-system.local
echo    用户名: Accounting System Deploy
echo.

echo 【步骤2】检查网络代理设置...
echo.

REM 检查是否有代理设置
git config --global http.proxy >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  发现HTTP代理设置，正在清除...
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    echo ✅ 代理设置已清除
) else (
    echo ✅ 没有代理设置
)
echo.

echo 【步骤3】配置GitHub访问...
echo.

REM 使用HTTPS方式，避免SSH密钥问题
echo 请选择GitHub连接方式：
echo.
echo 方式1: HTTPS (推荐，最简单)
echo    - 使用用户名和密码/个人访问令牌
echo    - 不需要配置SSH密钥
echo.
echo 方式2: SSH
echo    - 需要配置SSH密钥
echo    - 更适合长期使用
echo.

set /p CONNECTION_TYPE="请输入选项 (1 或 2): "

if "%CONNECTION_TYPE%"=="1" (
    echo.
    echo 您选择了HTTPS方式
echo.
    set /p GITHUB_USER="请输入您的GitHub用户名: "
    
    REM 设置远程仓库为HTTPS
    git remote remove origin 2>nul
    git remote add origin https://github.com/%GITHUB_USER%/accounting-system.git
    
    echo.
    echo ✅ 远程仓库已配置为HTTPS方式
    echo    地址: https://github.com/%GITHUB_USER%/accounting-system.git
    echo.
    echo ⚠️  重要提示：
    echo    推送时会要求输入GitHub密码或个人访问令牌(PAT)
echo.
    echo    如果您启用了两步验证，需要使用PAT代替密码
echo    创建PAT: https://github.com/settings/tokens
echo.
    
) else if "%CONNECTION_TYPE%"=="2" (
    echo.
    echo 您选择了SSH方式
echo.
    
    REM 检查SSH密钥
    if not exist "%USERPROFILE%\.ssh\id_rsa.pub" (
        echo ⚠️  未找到SSH密钥，正在生成...
        echo.
        set /p SSH_EMAIL="请输入您的邮箱地址: "
        ssh-keygen -t rsa -b 4096 -C "%SSH_EMAIL%" -f "%USERPROFILE%\.ssh\id_rsa" -N ""
        echo.
        echo ✅ SSH密钥已生成
        echo.
        echo 请将以下公钥添加到GitHub：
echo.
        type "%USERPROFILE%\.ssh\id_rsa.pub"
        echo.
        echo 添加地址: https://github.com/settings/keys
echo.
        pause
    ) else (
        echo ✅ SSH密钥已存在
    )
    
    set /p GITHUB_USER="请输入您的GitHub用户名: "
    
    REM 设置远程仓库为SSH
    git remote remove origin 2>nul
    git remote add origin git@github.com:%GITHUB_USER%/accounting-system.git
    
    echo.
    echo ✅ 远程仓库已配置为SSH方式
    echo    地址: git@github.com:%GITHUB_USER%/accounting-system.git
)

echo.
echo 【步骤4】测试连接...
echo.

git remote -v
echo.

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ✅ 配置完成！                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 现在您可以推送代码了：
echo    git push -u origin main
echo.
echo 或者运行一键部署脚本：
echo    QUICK_DEPLOY.bat
echo.

pause
