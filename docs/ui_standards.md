# 商业门户网站 UI 统一规范（权威标准）

> **执行标准**：所有智能体必须严格遵守，直接照搬，禁止自定义修改

---

## 📚 1. 全局视觉规范（所有页面必须遵守）

### （1）色彩规范（全系统仅 3 种颜色，杜绝杂乱）

| 用途 | 色值 | 说明 |
|------|------|------|
| **主色** | `#0d6efd` | 商业蓝，正式大气 |
| **辅助色-灰** | `#6c757d` | 灰色，辅助信息 |
| **辅助色-绿** | `#28a745` | 绿色，成功状态 |
| **背景色-浅灰** | `#f8f9fa` | 页面背景 |
| **背景色-白** | `#ffffff` | 卡片背景 |

**禁止**：高饱和艳色、多色彩混用

### （2）字体规范（全系统仅 3 种字号，统一阅读）

| 用途 | 字号 | 字重 | 字体 |
|------|------|------|------|
| **标题** | 20px | 加粗 (600) | Microsoft YaHei / PingFang SC |
| **正文** | 16px | 常规 (400) | Microsoft YaHei / PingFang SC |
| **辅助文字** | 14px | 常规 (400) | 浅灰色 (#6c757d) |

**字体家族**：`font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;`

### （3）间距规范（全系统统一留白，告别拥挤）

| 用途 | 数值 |
|------|------|
| **模块间距** | 24px |
| **卡片内边距** | 24px |
| **元素间距-小** | 12px |
| **元素间距-中** | 16px |
| **全局圆角** | 12px（按钮/卡片/输入框统一） |

---

## 📚 2. 布局层级规范（解决 UI 层级不统一！核心）

### （1）全局布局（所有页面必须用这套结构）

```html
<!-- 页面最外层 → container（居中容器） -->
<div class="container-fluid px-3 px-md-4">
    
    <!-- 功能模块 → modern-box（统一卡片） -->
    <div class="modern-box">
        
        <!-- 标题 → modern-title（统一左侧边框标题） -->
        <h4 class="modern-title">
            <i class="fa-solid fa-icon"></i>
            标题文字
        </h4>
        
        <!-- 内容区域 → 统一间距、对齐、排版 -->
        <div class="content-area">
            <!-- 业务内容 -->
        </div>
    </div>
</div>
```

### （2）层级规则（从上到下固定层级，禁止混乱）

```
页面顶部：导航栏（统一高度、样式）
    ↓
页面标题：大标题（统一字体、间距）
    ↓
功能模块：卡片分组（统一卡片样式）
    ↓
底部：页脚（统一样式）
```

---

## 📚 3. 组件统一规范（所有控件必须一致）

### 按钮规范

```css
.btn-primary {
    background-color: #0d6efd;
    border-color: #0d6efd;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
}
```

### 表格规范

```html
<table class="table table-hover table-striped align-middle">
    <!-- 表格内容 -->
</table>
```

### 表单规范

```css
.form-control {
    border-radius: 12px;
    border: 1px solid #dee2e6;
    padding: 10px 16px;
    font-size: 16px;
}
```

### 图标规范

- **统一使用**：Font Awesome 6
- **风格**：solid 风格（`fa-solid`）
- **大小**：默认 16px，标题 20px

### 卡片规范

```css
.modern-box {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    padding: 24px;
    margin-bottom: 24px;
}
```

---

## 📚 4. 交互体验规范

### 卡片悬停效果

```css
.modern-box {
    transition: all 0.3s ease;
}

.modern-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
```

### 按钮点击反馈

```css
.btn:active {
    transform: scale(0.98);
}
```

### 平滑滚动

```css
html {
    scroll-behavior: smooth;
}
```

### 响应式断点

| 断点 | 宽度 | 容器内边距 |
|------|------|-----------|
| 手机 | < 768px | px-3 (16px) |
| 平板 | 768px - 1024px | px-3 (16px) |
| 电脑 | > 1024px | px-4 (24px) |

---

## 📚 5. 代码开发规范

### 前端技术栈

- **框架**：Bootstrap 5.3.2
- **图标**：Font Awesome 6.4.0
- **表格**：DataTables 1.13.7
- **脚本**：jQuery 3.7.1

### 样式优先级

1. **优先使用**：Bootstrap5 原生类
2. **其次使用**：`modern-box` / `modern-title` 统一类名
3. **最后使用**：自定义 CSS（需审批）

### HTML 结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题 - 系统名称</title>
    <!-- Bootstrap5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- 自定义样式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/pages/dashboard.css') }}">
</head>
<body>
    <!-- 全局响应式容器 -->
    <div class="container-fluid px-3 px-md-4">
        
        <!-- 返回按钮 -->
        <button class="back-button" onclick="history.back()">
            <i class="fa-solid fa-arrow-left"></i>
            返回上一级
        </button>
        
        <!-- 功能模块卡片 -->
        <div class="modern-box">
            <h4 class="modern-title">
                <i class="fa-solid fa-icon"></i>
                模块标题
            </h4>
            <!-- 业务内容 -->
        </div>
        
    </div>
    
    <!-- Bootstrap5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### 禁止事项

- ❌ 自定义杂乱样式
- ❌ 随意修改布局
- ❌ 使用非标准颜色
- ❌ 混用多种字体
- ❌ 不统一的间距
- ❌ 不兼容的框架

---

## 📋 智能体执行检查清单

修改页面时必须检查：

- [ ] 是否使用 `container-fluid px-3 px-md-4` 包裹？
- [ ] 是否使用 `modern-box` 卡片？
- [ ] 标题是否使用 `modern-title` + Font Awesome 图标？
- [ ] 颜色是否使用标准色值（#0d6efd / #6c757d / #28a745）？
- [ ] 字号是否符合规范（20px / 16px / 14px）？
- [ ] 间距是否统一（24px / 12px / 16px）？
- [ ] 圆角是否统一（12px）？
- [ ] 是否有返回按钮？
- [ ] 底部用户区域是否有默认头像和阴影按钮？
- [ ] 是否响应式（手机/平板/电脑适配）？
- [ ] 是否平滑滚动？
- [ ] 业务逻辑是否完好？

---

**生效日期**：2026-03-19  
**版本**：v1.0  
**执行力度**：强制标准，不达标退回整改
