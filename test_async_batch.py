#!/usr/bin/env python3
"""
测试异步批处理功能
"""

import requests
import time
import json

def test_async_batch():
    """测试异步批处理"""
    base_url = "http://localhost:8000"
    
    # 1. 登录获取token
    login_data = {
        "username": "testuser",
        "password": "testpassword123",
        "captcha": "1234",
        "captcha_uuid": "test-uuid"
    }
    
    try:
        # 登录
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print("❌ 登录失败")
            return False
        
        print("✅ 登录成功")
        
        # 获取session cookie
        cookies = login_response.cookies
        
        # 2. 上传文件
        files = {'file': open('test_data.xlsx', 'rb')}
        upload_response = requests.post(
            f"{base_url}/api/batch/upload",
            files=files,
            cookies=cookies
        )
        
        if upload_response.status_code != 200:
            print("❌ 文件上传失败")
            return False
        
        print("✅ 文件上传成功")
        
        # 3. 启动批处理
        start_response = requests.get(
            f"{base_url}/api/batch/startProcess",
            cookies=cookies
        )
        
        if start_response.status_code != 200:
            print("❌ 启动批处理失败")
            print(f"响应: {start_response.text}")
            return False
        
        print("✅ 批处理启动成功")
        
        # 4. 监控进度
        for i in range(30):  # 最多监控30次
            time.sleep(2)
            progress_response = requests.get(
                f"{base_url}/api/batch/progress",
                cookies=cookies
            )
            
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                progress = progress_data.get('progress', 0)
                print(f"📊 进度: {progress}%")
                
                if progress >= 100:
                    print("✅ 批处理完成")
                    return True
            else:
                print(f"❌ 获取进度失败: {progress_response.status_code}")
        
        print("⏰ 批处理超时")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试异步批处理...")
    success = test_async_batch()
    if success:
        print("✅ 测试通过")
    else:
        print("❌ 测试失败") 