#!/usr/bin/env python3
"""
简体中文版本系统测试脚本
System Test Script for Simplified Chinese Version
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

# 测试用例
TESTS = []

def test_case(name):
    """装饰器：注册测试用例"""
    def decorator(func):
        TESTS.append((name, func))
        return func
    return decorator

# 测试结果
results = []

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("简体中文版本系统测试 / Simplified Chinese Version Test")
    print("=" * 60)
    
    for name, test_func in TESTS:
        try:
            print(f"\n📝 测试: {name}")
            test_func()
            results.append((name, "✅ 通过", None))
            print(f"   ✅ 通过")
        except Exception as e:
            results.append((name, "❌ 失败", str(e)))
            print(f"   ❌ 失败: {e}")
    
    # 打印测试报告
    print("\n" + "=" * 60)
    print("测试报告 / Test Report")
    print("=" * 60)
    
    passed = sum(1 for _, status, _ in results if "通过" in status)
    failed = sum(1 for _, status, _ in results if "失败" in status)
    
    for name, status, error in results:
        print(f"{status} {name}")
        if error:
            print(f"   错误: {error}")
    
    print("\n" + "-" * 60)
    print(f"总计: {len(results)} | 通过: {passed} | 失败: {failed}")
    print("=" * 60)
    
    return failed == 0


@test_case("登录页面加载 (简体中文)")
def test_login_page_zh_cn():
    """测试登录页面是否能正确加载并显示简体中文"""
    session = requests.Session()
    
    # 访问登录页面，指定简体中文
    response = session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    assert response.status_code == 200, f"状态码错误: {response.status_code}"
    
    html = response.text
    
    # 检查关键中文文本是否存在
    assert "用户登录" in html, "页面未显示'用户登录'"
    assert "密码" in html, "页面未显示'密码'"
    assert "登录" in html, "页面未显示'登录'"
    
    print("   ✓ 页面正确显示简体中文")


@test_case("管理员登录功能")
def test_admin_login():
    """测试管理员登录功能"""
    session = requests.Session()
    
    # 访问登录页面获取session
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    
    # 提交登录表单
    login_data = {
        "username": "admin",
        "password": "Test@123456"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    
    # 检查是否重定向到仪表板
    assert response.status_code in [302, 200], f"登录失败，状态码: {response.status_code}"
    
    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        assert 'dashboard' in redirect_url, f"未正确重定向到仪表板: {redirect_url}"
        print(f"   ✓ 登录成功，重定向到: {redirect_url}")
    else:
        # 检查响应内容
        assert "dashboard" in response.text.lower() or "仪表板" in response.text, "登录后未显示仪表板"
        print("   ✓ 登录成功")


@test_case("管理员仪表板访问")
def test_admin_dashboard():
    """测试管理员仪表板页面"""
    session = requests.Session()
    
    # 先登录
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    login_data = {"username": "admin", "password": "Test@123456"}
    session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    # 访问仪表板
    response = session.get(f"{BASE_URL}/admin/dashboard")
    
    # 检查是否返回HTML而不是JSON
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"返回了错误的内容类型: {content_type}"
    
    html = response.text
    assert "<!DOCTYPE html>" in html or "<html" in html, "返回的不是HTML页面"
    
    print("   ✓ 仪表板正确返回HTML页面")


@test_case("报表上传页面访问")
def test_upload_page():
    """测试报表上传页面"""
    session = requests.Session()
    
    # 先登录
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    login_data = {"username": "admin", "password": "Test@123456"}
    session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    # 访问上传页面
    response = session.get(f"{BASE_URL}/admin/upload-page")
    
    # 检查是否返回HTML
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"返回了错误的内容类型: {content_type}"
    
    html = response.text
    assert "<!DOCTYPE html>" in html or "<html" in html, "返回的不是HTML页面"
    
    print("   ✓ 上传页面正确返回HTML")


@test_case("报表管理页面访问")
def test_reports_page():
    """测试报表管理页面"""
    session = requests.Session()
    
    # 先登录
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    login_data = {"username": "admin", "password": "Test@123456"}
    session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    # 访问报表管理页面
    response = session.get(f"{BASE_URL}/admin/reports-page")
    
    # 检查是否返回HTML
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"返回了错误的内容类型: {content_type}"
    
    html = response.text
    assert "<!DOCTYPE html>" in html or "<html" in html, "返回的不是HTML页面"
    
    print("   ✓ 报表管理页面正确返回HTML")


@test_case("客户管理页面访问")
def test_customers_page():
    """测试客户管理页面"""
    session = requests.Session()
    
    # 先登录
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    login_data = {"username": "admin", "password": "Test@123456"}
    session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    # 访问客户管理页面
    response = session.get(f"{BASE_URL}/admin/customers-page")
    
    # 检查是否返回HTML
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"返回了错误的内容类型: {content_type}"
    
    html = response.text
    assert "<!DOCTYPE html>" in html or "<html" in html, "返回的不是HTML页面"
    
    print("   ✓ 客户管理页面正确返回HTML")


@test_case("未登录时访问管理页面重定向")
def test_unauthorized_redirect():
    """测试未登录时访问管理页面是否正确重定向到登录页"""
    session = requests.Session()
    
    # 不登录，直接访问管理页面
    response = session.get(f"{BASE_URL}/admin/dashboard", allow_redirects=False)
    
    # 检查是否重定向到登录页
    assert response.status_code == 302, f"未返回302重定向，状态码: {response.status_code}"
    
    redirect_url = response.headers.get('Location', '')
    assert 'login' in redirect_url, f"未重定向到登录页: {redirect_url}"
    
    print(f"   ✓ 正确重定向到登录页: {redirect_url}")


@test_case("系统设置页面访问")
def test_settings_page():
    """测试系统设置页面"""
    session = requests.Session()
    
    # 先登录
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    login_data = {"username": "admin", "password": "Test@123456"}
    session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    # 访问系统设置页面
    response = session.get(f"{BASE_URL}/admin/settings")
    
    # 检查是否返回HTML
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"返回了错误的内容类型: {content_type}"
    
    html = response.text
    assert "<!DOCTYPE html>" in html or "<html" in html, "返回的不是HTML页面"
    
    print("   ✓ 系统设置页面正确返回HTML")


@test_case("系统日志页面访问")
def test_logs_page():
    """测试系统日志页面"""
    session = requests.Session()
    
    # 先登录
    session.get(f"{BASE_URL}/auth/login?lang=zh_CN")
    login_data = {"username": "admin", "password": "Test@123456"}
    session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    # 访问系统日志页面
    response = session.get(f"{BASE_URL}/admin/logs")
    
    # 检查是否返回HTML
    content_type = response.headers.get('Content-Type', '')
    assert 'text/html' in content_type, f"返回了错误的内容类型: {content_type}"
    
    html = response.text
    assert "<!DOCTYPE html>" in html or "<html" in html, "返回的不是HTML页面"
    
    print("   ✓ 系统日志页面正确返回HTML")


@test_case("翻译文件完整性检查")
def test_translation_completeness():
    """测试简体中文翻译文件的完整性"""
    import os
    
    # 使用新的Babel标准locale路径
    po_file = os.path.join(
        os.path.dirname(__file__), 
        'app', 'translations', 'zh_Hans_CN', 'LC_MESSAGES', 'messages.po'
    )
    
    assert os.path.exists(po_file), f"翻译文件不存在: {po_file}"
    
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键翻译是否存在
    key_translations = [
        ('msgid "User Login"', 'msgstr "用户登录"'),
        ('msgid "Password"', 'msgstr "密码"'),
        ('msgid "Login"', 'msgstr "登录"'),
        ('msgid "Logout"', 'msgstr "退出登录"'),
    ]
    
    for msgid, msgstr in key_translations:
        assert msgid in content, f"缺少翻译键: {msgid}"
        assert msgstr in content, f"缺少翻译值: {msgstr}"
    
    # 统计翻译条目数
    msgid_count = content.count('msgid "')
    msgstr_count = content.count('msgstr "')
    
    print(f"   ✓ 翻译文件存在，包含约 {msgid_count} 个翻译键")


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
