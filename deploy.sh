#!/bin/bash

# 会计系统宝塔面板部署脚本
# 使用方法：bash deploy.sh

echo "=========================================="
echo "  会计系统 - 宝塔面板部署脚本"
echo "=========================================="

# 检查是否在正确目录
if [ ! -f "requirements.txt" ]; then
    echo "错误：请在项目根目录运行此脚本"
    exit 1
fi

echo ""
echo "[1/6] 创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "错误：创建虚拟环境失败"
    exit 1
fi

echo ""
echo "[2/6] 激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误：安装依赖失败"
    exit 1
fi

echo ""
echo "[3/6] 创建必要目录..."
mkdir -p data uploads logs backups

echo ""
echo "[4/6] 初始化数据库..."
python -c "from app import create_app; from app.models import db; app = create_app('production'); app.app_context().push(); db.create_all()"
if [ $? -ne 0 ]; then
    echo "错误：数据库初始化失败"
    exit 1
fi

echo ""
echo "[5/6] 创建管理员账号..."
python reset_password.py

echo ""
echo "[6/6] 设置文件权限..."
chmod -R 755 .
chmod -R 777 data uploads logs backups

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 安装PM2: npm install -g pm2"
echo "2. 启动应用: pm2 start ecosystem.config.js"
echo "3. 保存PM2配置: pm2 save"
echo "4. 设置开机自启: pm2 startup"
echo ""
echo "默认登录账号："
echo "  用户名: admin"
echo "  密码: Test@123456"
echo ""
