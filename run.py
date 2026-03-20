#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代理记账客户管理系统启动脚本
Accounting Customer Management System Startup Script

使用方法 / Usage:
    python run.py
    python run.py --host 0.0.0.0 --port 5000
    FLASK_ENV=production python run.py
"""
import argparse
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app


def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(
        description='Accounting Customer Management System'
    )
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--config',
        default=None,
        help='Configuration name (development, production, testing)'
    )
    
    args = parser.parse_args()
    
    # 创建应用实例
    config_name = args.config or os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     代理记账客户管理系统 / Accounting Customer Management      ║
╠══════════════════════════════════════════════════════════════╣
║  环境 / Environment: {config_name:<20}                    ║
║  调试 / Debug:       {str(app.debug):<20}                    ║
║  地址 / Host:        {args.host:<20}                    ║
║  端口 / Port:        {args.port:<20}                    ║
╚══════════════════════════════════════════════════════════════╝

访问地址 / Visit: http://{args.host}:{args.port}
    """)
    
    # 启动应用
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug or app.debug
    )


if __name__ == '__main__':
    main()
