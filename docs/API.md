# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5001/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 认证流程

### 1. 登录获取 Token

```bash
POST http://localhost:5001/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### 2. 使用 Token 访问受保护接口

```bash
GET http://localhost:5001/api/v1/customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## API 端点列表

### 🔐 认证接口

#### POST /auth/login
用户登录，返回 JWT Token

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应**:
- `success`: boolean - 是否成功
- `message`: string - 响应消息
- `user`: object - 用户信息
- `token`: string - JWT Token
- `expires_in`: number - Token 过期时间（秒）

---

#### POST /auth/logout
用户登出

**请求头**:
- Authorization: Bearer <token>

**响应**:
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

#### GET /auth/me
获取当前登录用户信息

**请求头**:
- Authorization: Bearer <token>

**响应**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

---

### 👥 客户管理接口

#### GET /api/v1/customers
获取客户列表（分页）

**请求头**:
- Authorization: Bearer <token>

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| per_page | integer | 20 | 每页数量 |

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "pages": 5,
    "current_page": 1,
    "per_page": 20
  }
}
```

---

#### GET /api/v1/customers/:id
获取客户详情

**请求头**:
- Authorization: Bearer <token>

**路径参数**:
- id: 客户 ID

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "company_name": "ABC 公司",
    "company_code": "91310000MA1234567X",
    "contact_name": "张三",
    "contact_phone": "13800138000",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

#### POST /api/v1/customers
创建新客户

**请求头**:
- Authorization: Bearer <token>
- Content-Type: application/json

**请求体**:
```json
{
  "company_name": "XYZ 公司",
  "company_code": "91310000MA7654321Y",
  "contact_name": "李四",
  "contact_phone": "13900139000",
  "status": "active"
}
```

**响应**: 201 Created
```json
{
  "success": true,
  "data": {
    "id": 2,
    "company_name": "XYZ 公司",
    ...
  }
}
```

---

#### PUT /api/v1/customers/:id
更新客户信息

**请求头**:
- Authorization: Bearer <token>
- Content-Type: application/json

**路径参数**:
- id: 客户 ID

**请求体**:
```json
{
  "company_name": "Updated 公司",
  "contact_phone": "13800138000"
}
```

---

#### DELETE /api/v1/customers/:id
删除客户

**请求头**:
- Authorization: Bearer <token>

**路径参数**:
- id: 客户 ID

**响应**:
```json
{
  "success": true,
  "message": "Customer deleted"
}
```

---

### 📊 报表管理接口

#### GET /api/v1/reports
获取报表列表（分页）

**请求头**:
- Authorization: Bearer <token>

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| per_page | integer | 20 | 每页数量 |

---

#### GET /api/v1/reports/:id
获取报表详情

**请求头**:
- Authorization: Bearer <token>

---

#### POST /api/v1/reports
创建新报表

**请求头**:
- Authorization: Bearer <token>
- Content-Type: application/json

**请求体**:
```json
{
  "report_name": "2024 年 3 月利润表",
  "report_type": "income_statement",
  "year": 2024,
  "month": 3,
  "customer_id": 1,
  "description": "月度利润表"
}
```

---

#### PUT /api/v1/reports/:id
更新报表信息

---

#### DELETE /api/v1/reports/:id
删除报表

---

### 📈 仪表盘接口

#### GET /api/v1/dashboard
获取仪表盘统计数据

**请求头**:
- Authorization: Bearer <token>

**响应**:
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_customers": 150,
      "active_customers": 120,
      "total_reports": 500,
      "pending_reports": 25,
      "total_users": 10
    },
    "recent_activity": [...]
  }
}
```

---

### 👤 用户管理接口

#### GET /api/v1/users
获取用户列表（分页）

**请求头**:
- Authorization: Bearer <token>

---

#### GET /api/v1/users/:id
获取用户详情

**请求头**:
- Authorization: Bearer <token>

---

### 📝 日志接口

#### GET /api/v1/logs
获取登录日志列表（分页）

**请求头**:
- Authorization: Bearer <token>

---

## 错误响应

### 401 Unauthorized - 未认证
```json
{
  "success": false,
  "message": "Token is missing"
}
```

### 401 Unauthorized - Token 无效
```json
{
  "success": false,
  "message": "Token is invalid or expired"
}
```

### 403 Forbidden - 权限不足
```json
{
  "success": false,
  "message": "Admin access required"
}
```

### 404 Not Found - 资源不存在
```json
{
  "success": false,
  "message": "Customer not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error"
}
```

---

## 使用示例

### JavaScript/Fetch
```javascript
// 登录
const loginResponse = await fetch('http://localhost:5001/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'password123'
  })
});

const { token } = await loginResponse.json();

// 获取客户列表
const customersResponse = await fetch('http://localhost:5001/api/v1/customers', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { data } = await customersResponse.json();
console.log(data.items);
```

### cURL
```bash
# 登录
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'

# 获取客户列表
curl -X GET http://localhost:5001/api/v1/customers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| accountant1 | password123 | 会计 |

---

## 注意事项

1. **Token 有效期**: 24 小时
2. **Token 刷新**: 当前版本不支持刷新 token，过期后需重新登录
3. **跨域访问**: 已启用 CORS，允许 React 前端调用
4. **数据格式**: 所有日期时间使用 ISO 8601 格式
5. **分页**: 所有列表接口都支持分页
