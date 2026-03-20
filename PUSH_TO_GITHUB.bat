@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     推送代码到GitHub                                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 当前状态:
echo - 仓库: https://github.com/jixiansheng365/accounting-system
echo - 本地分支: master
echo.

git status
echo.
echo 正在尝试推送...
echo.
git push -u origin master
echo.
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                    ✅ 推送成功！                             ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 现在去Render.com部署：
    echo.
    echo 1. 访问: https://dashboard.render.com/
    echo 2. 点击 New + ^> Web Service
    echo 3. 连接GitHub账号 jixiansheng365
    echo 4. 选择 accounting-system 仓库
    echo 5. 点击 Create Web Service
    echo.
    start https://dashboard.render.com/
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                    ❌ 推送失败，请检查网络和认证                              ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 可能的解决方案：
    echo.
    echo 1. 检查网络连接
    echo 2. 配置GitHub个人访问令牌(PAT)
    echo 3. 或者使用GitHub Desktop客户端
    echo.
    echo 创建PAT: https://github.com/settings/tokens
    echo.
)
echo.
pause
