# 系统测试清单 / System Test Checklist

## 简体中文版本测试 / Simplified Chinese Version Tests

### 1. 登录功能测试 / Login Functionality Tests

| 测试项 | 测试步骤 | 预期结果 | 状态 |
|--------|----------|----------|------|
| 登录页面加载 | 访问 `/auth/login?lang=zh_CN` | 页面显示"用户登录"标题 | ✅ |
| 简体中文翻译 | 检查页面文本 | 显示"密码"、"登录"等中文 | ✅ |
| 管理员登录 | 使用 admin/Test@123456 登录 | 成功重定向到仪表板 | ✅ |
| 错误密码提示 | 输入错误密码 | 显示中文错误提示 | ⬜ |

### 2. 页面访问测试 / Page Access Tests

| 测试项 | 测试步骤 | 预期结果 | 状态 |
|--------|----------|----------|------|
| 管理员仪表板 | 登录后访问 `/admin/dashboard` | 返回HTML页面，非JSON | ✅ |
| 报表上传页面 | 访问 `/admin/upload-page` | 返回HTML页面 | ✅ |
| 报表管理页面 | 访问 `/admin/reports-page` | 返回HTML页面 | ✅ |
| 客户管理页面 | 访问 `/admin/customers-page` | 返回HTML页面 | ✅ |
| 未登录重定向 | 未登录访问管理页面 | 302重定向到登录页 | ✅ |

### 3. 翻译完整性测试 / Translation Tests

| 测试项 | 测试步骤 | 预期结果 | 状态 |
|--------|----------|----------|------|
| 翻译文件存在 | 检查 `zh_Hans_CN/LC_MESSAGES/messages.po` | 文件存在 | ✅ |
| 关键翻译键 | 检查 User Login, Password, Login | 都有中文翻译 | ✅ |
| 翻译条目数 | 统计 msgid 数量 | > 200 个翻译键 | ✅ |
| 编译文件 | 检查 .mo 文件 | 已编译且最新 | ✅ |

---

## 防止回归的开发规范 / Development Guidelines to Prevent Regressions

### 1. 路由修改规范 / Route Modification Rules

**问题**: 经常出现路由错误（405 Method Not Allowed, url_for 错误）

**解决方案**:
```python
# ✅ 页面路由（返回HTML）使用 @admin_page_required
@admin_bp.route('/dashboard')
@admin_page_required
def dashboard():
    return render_template('admin/dashboard.html')

# ✅ API路由（返回JSON）使用 @admin_required
@admin_bp.route('/customers', methods=['GET'])
@admin_required
def list_customers():
    return jsonify({'success': True, 'data': ...})
```

**检查清单**:
- [ ] 页面路由使用 `@admin_page_required` 或 `@login_page_required`
- [ ] API路由使用 `@admin_required` 或 `@login_required`
- [ ] 路由方法明确指定（GET/POST/PUT/DELETE）
- [ ] 模板中使用 `url_for('蓝图名.函数名')` 时，函数名正确

### 2. 多语言支持规范 / i18n Guidelines

**问题**: 翻译不生效，显示英文原文

**根本原因**: Babel使用标准locale标识符（如`zh_Hans_CN`），而我们使用简化标识符（如`zh_CN`）

**解决方案**:
```python
# ✅ 在 app/__init__.py 中正确映射
lang_mapping = {
    'zh_CN': 'zh_Hans_CN',    # 简体中文
    'zh_TW': 'zh_Hant_TW',    # 繁体中文
    'ja': 'ja',               # 日语
    'en': 'en',               # 英语
    'ko': 'ko'                # 韩语
}

# ✅ 翻译目录结构
app/translations/
├── zh_Hans_CN/          # 简体中文（Babel标准）
├── zh_Hant_TW/          # 繁体中文（Babel标准）
├── ja/                  # 日语
├── en/                  # 英语
└── ko/                  # 韩语
```

**修改翻译后的必做步骤**:
1. 修改 `.po` 文件添加翻译
2. 运行 `pybabel compile -d app/translations` 编译
3. 重启服务器（非debug模式）
4. 运行 `python test_zh_cn.py` 验证

### 3. 密码管理规范 / Password Management

**问题**: 密码验证失败

**解决方案**:
```python
# ✅ 使用 Werkzeug 的 generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

**重置密码脚本**: `reset_password.py`
```python
# 运行此脚本重置admin密码
python reset_password.py
```

### 4. 测试驱动开发 / Test-Driven Development

**每次修改后必须运行**:
```bash
# 1. 运行自动化测试
python test_zh_cn.py

# 2. 手动检查关键页面
# - 登录页: http://localhost:5000/auth/login?lang=zh_CN
# - 仪表板: http://localhost:5000/admin/dashboard
# - 上传页: http://localhost:5000/admin/upload-page
```

### 5. 修改前检查清单 / Pre-Modification Checklist

在进行任何修改前，先确认：

- [ ] 当前代码版本已备份或已提交git
- [ ] 已运行测试确认当前状态正常
- [ ] 理解修改可能影响的其他部分
- [ ] 修改后计划运行的测试用例

### 6. 常见错误预防 / Common Error Prevention

| 错误类型 | 预防措施 |
|----------|----------|
| 405 Method Not Allowed | 明确指定methods参数，页面用GET，API用POST/PUT/DELETE |
| url_for 路由错误 | 使用 `蓝图名.函数名` 格式，修改路由后全局搜索旧名称 |
| JSON而非HTML | 页面路由使用 `@admin_page_required` 装饰器 |
| 翻译不生效 | 修改.po后必须编译，检查locale标识符匹配 |
| 密码错误 | 使用reset_password.py重置，不要手动修改数据库 |

---

## 测试脚本使用说明 / Test Script Usage

```bash
# 运行所有测试
python test_zh_cn.py

# 预期输出: 8个测试全部通过
# ============================================================
# 测试报告 / Test Report
# ============================================================
# ✅ 通过 登录页面加载 (简体中文)
# ✅ 通过 管理员登录功能
# ✅ 通过 管理员仪表板访问
# ✅ 通过 报表上传页面访问
# ✅ 通过 报表管理页面访问
# ✅ 通过 客户管理页面访问
# ✅ 通过 未登录时访问管理页面重定向
# ✅ 通过 翻译文件完整性检查
# ------------------------------------------------------------
# 总计: 8 | 通过: 8 | 失败: 0
# ============================================================
```

---

## 当前状态 / Current Status

**最后更新**: 2026-03-20

**简体中文版本状态**: ✅ 完整可用

- 登录功能: ✅ 正常
- 翻译显示: ✅ 正常
- 页面访问: ✅ 正常
- 权限控制: ✅ 正常

**已知问题**: 无

**下一步计划**: 
1. 保持简体中文版本稳定
2. 逐个验证其他语言（日语、英语、韩语、繁体中文）
3. 添加更多自动化测试覆盖
