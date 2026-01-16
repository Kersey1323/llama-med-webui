#!/usr/bin/env python3
"""
健康检查脚本 - 用于诊断 Docker 容器间的连接问题
"""

import os
import sys
import requests
import redis
import pymysql
from datetime import datetime

def check_redis_connection():
    """检查 Redis 连接"""
    try:
        redis_host = os.environ.get('REDIS_HOST', 'redis')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        
        r = redis.Redis(host=redis_host, port=redis_port, db=0, socket_connect_timeout=5)
        r.ping()
        print(f"✅ Redis 连接成功: {redis_host}:{redis_port}")
        return True
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        return False

def check_mysql_connection():
    """检查 MySQL 连接"""
    try:
        mysql_host = os.environ.get('MYSQL_HOST', 'mysql')
        mysql_port = int(os.environ.get('MYSQL_PORT', 3306))
        mysql_user = os.environ.get('MYSQL_USER', 'user')
        mysql_password = os.environ.get('MYSQL_PASSWORD', 'password')
        mysql_database = os.environ.get('MYSQL_DATABASE', 'llama_med_db')
        
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            connect_timeout=5
        )
        conn.close()
        print(f"✅ MySQL 连接成功: {mysql_host}:{mysql_port}")
        return True
    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")
        return False

def check_backend_api():
    """检查后端 API 是否可访问"""
    try:
        # 检查本地 API
        response = requests.get('http://localhost:8000/api/auth/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端 API 本地访问成功")
            return True
    except Exception as e:
        print(f"❌ 后端 API 本地访问失败: {e}")
    
    try:
        # 检查容器内 API
        response = requests.get('http://backend:8000/api/auth/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端 API 容器内访问成功")
            return True
    except Exception as e:
        print(f"❌ 后端 API 容器内访问失败: {e}")
    
    return False

def check_environment():
    """检查环境变量"""
    print("\n📋 环境变量检查:")
    important_vars = [
        'FLASK_ENV',
        'REDIS_HOST',
        'REDIS_PORT',
        'MYSQL_HOST',
        'MYSQL_PORT',
        'MYSQL_USER',
        'MYSQL_DATABASE'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, '未设置')
        print(f"  {var}: {value}")

def main():
    """主函数"""
    print("🔍 开始健康检查...")
    print(f"⏰ 检查时间: {datetime.now()}")
    
    # 检查环境变量
    check_environment()
    
    print("\n🔗 连接检查:")
    
    # 检查各种连接
    redis_ok = check_redis_connection()
    mysql_ok = check_mysql_connection()
    api_ok = check_backend_api()
    
    print("\n📊 检查结果:")
    if redis_ok and mysql_ok and api_ok:
        print("✅ 所有服务连接正常")
        return 0
    else:
        print("❌ 存在连接问题，请检查配置")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 