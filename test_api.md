# API 测试脚本

## 使用 PowerShell 测试 API

### 1. 测试登录接口
```powershell
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5001/auth/login" -Method POST -Body $body -ContentType "application/json"
$response.token
```

### 2. 使用 Token 访问客户列表
```powershell
$token = "YOUR_TOKEN_HERE"
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5001/api/v1/customers" -Method GET -Headers $headers
```

### 3. 获取仪表盘数据
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/api/v1/dashboard" -Method GET -Headers $headers
```

---

## 使用 cURL 测试

### 登录
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### 获取客户列表
```bash
curl -X GET http://localhost:5001/api/v1/customers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 获取仪表盘数据
```bash
curl -X GET http://localhost:5001/api/v1/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 使用 Postman 测试

### 1. 创建请求
- Method: POST
- URL: http://localhost:5001/auth/login
- Headers: Content-Type: application/json
- Body (raw JSON):
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### 2. 保存 Token
从响应中复制 token，然后在后续请求的 Headers 中添加：
```
Authorization: Bearer YOUR_TOKEN_HERE
```

### 3. 测试其他接口
- GET http://localhost:5001/api/v1/customers
- GET http://localhost:5001/api/v1/reports
- GET http://localhost:5001/api/v1/dashboard

---

## 预期响应示例

### 登录成功
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

### 获取客户列表
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "company_name": "ABC 公司",
        "company_code": "91310000MA1234567X",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 12,
    "pages": 1,
    "current_page": 1,
    "per_page": 20
  }
}
```

### 仪表盘数据
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_customers": 12,
      "active_customers": 10,
      "total_reports": 144,
      "pending_reports": 5,
      "total_users": 3
    },
    "recent_activity": [...]
  }
}
```

---

## 常见错误

### 401 Unauthorized - Token 缺失
```json
{
  "success": false,
  "message": "Token is missing"
}
```
**解决**: 确保在请求头中添加了 `Authorization: Bearer <token>`

### 401 Unauthorized - Token 无效
```json
{
  "success": false,
  "message": "Token is invalid or expired"
}
```
**解决**: Token 已过期，需要重新登录获取新 token

### 403 Forbidden - 权限不足
```json
{
  "success": false,
  "message": "Admin access required"
}
```
**解决**: 当前用户没有管理员权限

### 404 Not Found - 资源不存在
```json
{
  "success": false,
  "message": "Customer not found"
}
```
**解决**: 检查资源 ID 是否正确

---

## 测试清单

- [ ] 登录接口返回 token
- [ ] Token 可以访问客户列表
- [ ] Token 可以访问报表列表
- [ ] Token 可以访问仪表盘数据
- [ ] Token 过期后自动跳转到登录页
- [ ] 创建新客户成功
- [ ] 更新客户信息成功
- [ ] 删除客户成功
- [ ] 分页功能正常
- [ ] 错误处理正常

---

## 下一步

测试通过后，继续开发：
1. 客户列表页面
2. 客户详情页面
3. 报表管理页面
4. 数据可视化
