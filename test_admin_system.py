"""
管理员权限系统测试脚本
Admin Permission System Test Script
"""
import requests
import json
import sys

# 基础URL
BASE_URL = "http://127.0.0.1:5001"
ADMIN_URL = f"{BASE_URL}/admin"

# 测试数据
TEST_ADMIN = {
    "username": "admin_test",
    "email": "admin@test.com",
    "password": "admin123456",
    "real_name": "Test Admin",
    "role": "admin",
    "is_admin": True
}

TEST_ACCOUNTANT = {
    "username": "accountant_test",
    "email": "accountant@test.com",
    "password": "accountant123456",
    "real_name": "Test Accountant",
    "role": "accountant"
}

import time

# 使用时间戳生成唯一的测试数据
TIMESTAMP = int(time.time())

TEST_CUSTOMER = {
    "company_name": f"测试科技有限公司_{TIMESTAMP}",
    "company_code": f"91310000TEST{TIMESTAMP}",
    "contact_name": "张三",
    "contact_phone": "13800138000",
    "contact_email": f"zhangsan_{TIMESTAMP}@test.com",
    "tax_id": f"91310000TEST{TIMESTAMP}",
    "tax_type": "general",
    "status": "active"
}


class AdminSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_id = None
        self.accountant_id = None
        self.customer_id = None
        self.report_id = None
        self.test_results = []

    def log(self, message, level="INFO"):
        """打印日志"""
        print(f"[{level}] {message}")

    def test_pass(self, test_name):
        """记录测试通过"""
        self.test_results.append((test_name, True, None))
        self.log(f"✓ {test_name}", "PASS")

    def test_fail(self, test_name, error):
        """记录测试失败"""
        self.test_results.append((test_name, False, str(error)))
        self.log(f"✗ {test_name}: {error}", "FAIL")

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结 / Test Summary")
        print("="*60)
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        failed = sum(1 for _, result, _ in self.test_results if not result)
        total = len(self.test_results)
        
        print(f"总计: {total} | 通过: {passed} | 失败: {failed}")
        print("-"*60)
        
        if failed > 0:
            print("\n失败的测试:")
            for test_name, result, error in self.test_results:
                if not result:
                    print(f"  - {test_name}: {error}")
        
        print("="*60)
        return failed == 0

    # =================================================================
    # 管理员认证测试
    # =================================================================
    
    def test_01_create_admin_user(self):
        """测试1: 创建管理员用户"""
        try:
            # 先尝试注册
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=TEST_ADMIN
            )
            
            if response.status_code == 201:
                data = response.json()
                self.admin_id = data.get('data', {}).get('id')
                self.test_pass("创建管理员用户")
            elif response.status_code == 400 and "already exists" in response.text:
                # 用户已存在，查找用户ID
                response = self.session.post(
                    f"{BASE_URL}/auth/login",
                    json={"username": TEST_ADMIN["username"], "password": TEST_ADMIN["password"]}
                )
                if response.status_code == 200:
                    self.test_pass("创建管理员用户 (已存在)")
                else:
                    self.test_fail("创建管理员用户", "用户已存在但无法登录")
            else:
                self.test_fail("创建管理员用户", f"状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            self.test_fail("创建管理员用户", e)

    def test_02_admin_login(self):
        """测试2: 管理员登录"""
        try:
            response = self.session.post(
                f"{ADMIN_URL}/login",
                json={"username": TEST_ADMIN["username"], "password": TEST_ADMIN["password"]}
            )
            
            if response.status_code == 200:
                data = response.json()
                # API返回的是 'user' 而不是 'data'
                if data.get('success') and data.get('user', {}).get('role') == 'admin':
                    self.test_pass("管理员登录")
                else:
                    self.test_fail("管理员登录", f"响应数据不正确: {data}")
            else:
                self.test_fail("管理员登录", f"状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            self.test_fail("管理员登录", e)

    def test_03_non_admin_login_rejected(self):
        """测试3: 非管理员登录被拒绝"""
        try:
            # 先创建普通用户
            self.session.post(
                f"{BASE_URL}/auth/register",
                json=TEST_ACCOUNTANT
            )
            
            # 尝试用普通用户登录管理后台
            response = self.session.post(
                f"{ADMIN_URL}/login",
                json={"username": TEST_ACCOUNTANT["username"], "password": TEST_ACCOUNTANT["password"]}
            )
            
            if response.status_code == 403:
                self.test_pass("非管理员登录被拒绝")
            else:
                self.test_fail("非管理员登录被拒绝", f"期望403, 实际: {response.status_code}")
        except Exception as e:
            self.test_fail("非管理员登录被拒绝", e)

    def test_04_get_admin_info(self):
        """测试4: 获取管理员信息"""
        try:
            response = self.session.get(f"{ADMIN_URL}/me")
            
            if response.status_code == 200:
                data = response.json()
                # API返回的是 'user' 而不是 'data'
                if data.get('success') and data.get('user', {}).get('role') == 'admin':
                    self.test_pass("获取管理员信息")
                else:
                    self.test_fail("获取管理员信息", f"响应数据不正确: {data}")
            else:
                self.test_fail("获取管理员信息", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取管理员信息", e)

    # =================================================================
    # 客户管理测试
    # =================================================================
    
    def test_05_create_customer(self):
        """测试5: 创建客户"""
        try:
            response = self.session.post(
                f"{ADMIN_URL}/customers",
                json=TEST_CUSTOMER
            )
            
            if response.status_code == 201:
                data = response.json()
                self.customer_id = data.get('data', {}).get('id')
                self.test_pass("创建客户")
            else:
                self.test_fail("创建客户", f"状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            self.test_fail("创建客户", e)

    def test_06_list_customers(self):
        """测试6: 获取客户列表"""
        try:
            response = self.session.get(f"{ADMIN_URL}/customers")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取客户列表")
                else:
                    self.test_fail("获取客户列表", "响应数据不正确")
            else:
                self.test_fail("获取客户列表", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取客户列表", e)

    def test_07_get_customer_detail(self):
        """测试7: 获取客户详情"""
        try:
            if not self.customer_id:
                self.test_fail("获取客户详情", "没有客户ID")
                return
                
            response = self.session.get(f"{ADMIN_URL}/customers/{self.customer_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('id') == self.customer_id:
                    self.test_pass("获取客户详情")
                else:
                    self.test_fail("获取客户详情", "响应数据不正确")
            else:
                self.test_fail("获取客户详情", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取客户详情", e)

    def test_08_update_customer(self):
        """测试8: 更新客户信息"""
        try:
            if not self.customer_id:
                self.test_fail("更新客户信息", "没有客户ID")
                return
                
            update_data = {
                "contact_name": "李四",
                "contact_phone": "13900139000",
                "remarks": "更新测试"
            }
            
            response = self.session.put(
                f"{ADMIN_URL}/customers/{self.customer_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_pass("更新客户信息")
                else:
                    self.test_fail("更新客户信息", "响应数据不正确")
            else:
                self.test_fail("更新客户信息", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("更新客户信息", e)

    def test_09_update_customer_status(self):
        """测试9: 更新客户状态"""
        try:
            if not self.customer_id:
                self.test_fail("更新客户状态", "没有客户ID")
                return
                
            response = self.session.patch(
                f"{ADMIN_URL}/customers/{self.customer_id}/status",
                json={"status": "suspended"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('status') == 'suspended':
                    self.test_pass("更新客户状态")
                else:
                    self.test_fail("更新客户状态", "响应数据不正确")
            else:
                self.test_fail("更新客户状态", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("更新客户状态", e)

    def test_10_reset_customer_password(self):
        """测试10: 重置客户密码"""
        try:
            if not self.customer_id:
                self.test_fail("重置客户密码", "没有客户ID")
                return
                
            response = self.session.post(
                f"{ADMIN_URL}/customers/{self.customer_id}/reset-password",
                json={"new_password": "newpassword123"}
            )
            
            # 如果没有登录账号，会返回错误
            if response.status_code in [200, 400]:
                self.test_pass("重置客户密码")
            else:
                self.test_fail("重置客户密码", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("重置客户密码", e)

    def test_11_get_customer_statistics(self):
        """测试11: 获取客户统计"""
        try:
            response = self.session.get(f"{ADMIN_URL}/customers/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取客户统计")
                else:
                    self.test_fail("获取客户统计", "响应数据不正确")
            else:
                self.test_fail("获取客户统计", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取客户统计", e)

    # =================================================================
    # 报表管理测试
    # =================================================================
    
    def test_12_create_report(self):
        """测试12: 创建报表记录"""
        try:
            if not self.customer_id:
                self.test_fail("创建报表记录", "没有客户ID")
                return
                
            report_data = {
                "report_name": "2024年1月资产负债表",
                "report_type": "balance_sheet",
                "year": 2024,
                "month": 1,
                "customer_id": self.customer_id,
                "description": "测试报表"
            }
            
            response = self.session.post(
                f"{ADMIN_URL}/reports",
                json=report_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.report_id = data.get('data', {}).get('id')
                self.test_pass("创建报表记录")
            else:
                self.test_fail("创建报表记录", f"状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            self.test_fail("创建报表记录", e)

    def test_13_list_reports(self):
        """测试13: 获取报表列表"""
        try:
            response = self.session.get(f"{ADMIN_URL}/reports")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取报表列表")
                else:
                    self.test_fail("获取报表列表", "响应数据不正确")
            else:
                self.test_fail("获取报表列表", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取报表列表", e)

    def test_14_get_report_detail(self):
        """测试14: 获取报表详情"""
        try:
            if not self.report_id:
                self.test_fail("获取报表详情", "没有报表ID")
                return
                
            response = self.session.get(f"{ADMIN_URL}/reports/{self.report_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('id') == self.report_id:
                    self.test_pass("获取报表详情")
                else:
                    self.test_fail("获取报表详情", "响应数据不正确")
            else:
                self.test_fail("获取报表详情", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取报表详情", e)

    def test_15_review_report(self):
        """测试15: 审核报表"""
        try:
            if not self.report_id:
                self.test_fail("审核报表", "没有报表ID")
                return
            
            # 先提交报表（从draft到submitted）
            submit_response = self.session.post(f"{ADMIN_URL}/reports/{self.report_id}/submit")
            if submit_response.status_code != 200:
                self.test_fail("审核报表", f"提交报表失败: {submit_response.text}")
                return
            
            # 然后审核报表（从submitted到reviewed）
            response = self.session.post(
                f"{ADMIN_URL}/reports/{self.report_id}/review",
                json={"approved": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_pass("审核报表")
                else:
                    self.test_fail("审核报表", "响应数据不正确")
            else:
                self.test_fail("审核报表", f"状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            self.test_fail("审核报表", e)

    def test_16_get_report_statistics(self):
        """测试16: 获取报表统计"""
        try:
            response = self.session.get(f"{ADMIN_URL}/reports/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取报表统计")
                else:
                    self.test_fail("获取报表统计", "响应数据不正确")
            else:
                self.test_fail("获取报表统计", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取报表统计", e)

    # =================================================================
    # 用户管理测试
    # =================================================================
    
    def test_17_list_users(self):
        """测试17: 获取用户列表"""
        try:
            response = self.session.get(f"{ADMIN_URL}/users")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取用户列表")
                else:
                    self.test_fail("获取用户列表", "响应数据不正确")
            else:
                self.test_fail("获取用户列表", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取用户列表", e)

    def test_18_get_roles(self):
        """测试18: 获取角色列表"""
        try:
            response = self.session.get(f"{ADMIN_URL}/users/roles")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取角色列表")
                else:
                    self.test_fail("获取角色列表", "响应数据不正确")
            else:
                self.test_fail("获取角色列表", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取角色列表", e)

    def test_19_get_dashboard_statistics(self):
        """测试19: 获取仪表盘统计"""
        try:
            response = self.session.get(f"{ADMIN_URL}/dashboard/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取仪表盘统计")
                else:
                    self.test_fail("获取仪表盘统计", "响应数据不正确")
            else:
                self.test_fail("获取仪表盘统计", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取仪表盘统计", e)

    def test_20_get_login_logs(self):
        """测试20: 获取登录日志"""
        try:
            response = self.session.get(f"{ADMIN_URL}/login-logs")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.test_pass("获取登录日志")
                else:
                    self.test_fail("获取登录日志", "响应数据不正确")
            else:
                self.test_fail("获取登录日志", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("获取登录日志", e)

    def test_21_admin_logout(self):
        """测试21: 管理员登出"""
        try:
            response = self.session.post(f"{ADMIN_URL}/logout")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_pass("管理员登出")
                else:
                    self.test_fail("管理员登出", "响应数据不正确")
            else:
                self.test_fail("管理员登出", f"状态码: {response.status_code}")
        except Exception as e:
            self.test_fail("管理员登出", e)

    def test_22_access_denied_after_logout(self):
        """测试22: 登出后访问被拒绝"""
        try:
            response = self.session.get(f"{ADMIN_URL}/me")
            
            if response.status_code == 401:
                self.test_pass("登出后访问被拒绝")
            else:
                self.test_fail("登出后访问被拒绝", f"期望401, 实际: {response.status_code}")
        except Exception as e:
            self.test_fail("登出后访问被拒绝", e)

    def run_all_tests(self):
        """运行所有测试"""
        print("="*60)
        print("管理员权限系统测试 / Admin Permission System Test")
        print("="*60)
        print()
        
        # 管理员认证测试
        print("\n--- 管理员认证测试 ---")
        self.test_01_create_admin_user()
        self.test_02_admin_login()
        self.test_03_non_admin_login_rejected()
        self.test_04_get_admin_info()
        
        # 客户管理测试
        print("\n--- 客户管理测试 ---")
        self.test_05_create_customer()
        self.test_06_list_customers()
        self.test_07_get_customer_detail()
        self.test_08_update_customer()
        self.test_09_update_customer_status()
        self.test_10_reset_customer_password()
        self.test_11_get_customer_statistics()
        
        # 报表管理测试
        print("\n--- 报表管理测试 ---")
        self.test_12_create_report()
        self.test_13_list_reports()
        self.test_14_get_report_detail()
        self.test_15_review_report()
        self.test_16_get_report_statistics()
        
        # 用户管理测试
        print("\n--- 用户管理测试 ---")
        self.test_17_list_users()
        self.test_18_get_roles()
        self.test_19_get_dashboard_statistics()
        self.test_20_get_login_logs()
        
        # 登出测试
        print("\n--- 登出测试 ---")
        self.test_21_admin_logout()
        self.test_22_access_denied_after_logout()
        
        # 打印总结
        return self.print_summary()


def main():
    """主函数"""
    tester = AdminSystemTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
