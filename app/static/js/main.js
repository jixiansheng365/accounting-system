/**
 * 代理记账客户管理系统 - 主 JavaScript 文件
 * Accounting Customer Management System - Main JavaScript File
 */

// 等待 DOM 加载完成
// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Accounting System initialized');
    
    // 初始化所有组件
    initializeComponents();
});

/**
 * 初始化所有组件
 * Initialize all components
 */
function initializeComponents() {
    // 初始化确认对话框
    initConfirmDialogs();
    
    // 初始化表单验证
    initFormValidation();
    
    // 初始化 AJAX 请求
    initAjaxRequests();
}

/**
 * 初始化确认对话框
 * Initialize confirmation dialogs
 */
function initConfirmDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * 初始化表单验证
 * Initialize form validation
 */
function initFormValidation() {
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // 验证必填字段
            this.querySelectorAll('[required]').forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    showFieldError(field, 'This field is required');
                } else {
                    field.classList.remove('error');
                    hideFieldError(field);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

/**
 * 显示字段错误信息
 * Show field error message
 */
function showFieldError(field, message) {
    let errorDiv = field.parentNode.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
    errorDiv.style.color = '#ff4d4f';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '4px';
}

/**
 * 隐藏字段错误信息
 * Hide field error message
 */
function hideFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * 初始化 AJAX 请求
 * Initialize AJAX requests
 */
function initAjaxRequests() {
    // 为所有带有 data-ajax 属性的链接添加 AJAX 处理
    document.querySelectorAll('a[data-ajax]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            const method = this.getAttribute('data-method') || 'GET';
            
            fetch(url, {
                method: method,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                handleAjaxResponse(data);
            })
            .catch(error => {
                console.error('AJAX Error:', error);
                showNotification('Error occurred', 'error');
            });
        });
    });
}

/**
 * 处理 AJAX 响应
 * Handle AJAX response
 */
function handleAjaxResponse(data) {
    if (data.success) {
        showNotification(data.message || 'Operation successful', 'success');
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    } else {
        showNotification(data.message || 'Operation failed', 'error');
    }
}

/**
 * 显示通知消息
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 4px;
        color: #fff;
        font-size: 14px;
        z-index: 9999;
        transition: opacity 0.3s;
    `;
    
    // 根据类型设置背景色
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#52c41a';
            break;
        case 'error':
            notification.style.backgroundColor = '#ff4d4f';
            break;
        case 'warning':
            notification.style.backgroundColor = '#faad14';
            break;
        default:
            notification.style.backgroundColor = '#1890ff';
    }
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * API 请求辅助函数
 * API request helper function
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    if (options.body && typeof options.body === 'object') {
        mergedOptions.body = JSON.stringify(options.body);
    }
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * 格式化日期
 * Format date
 */
function formatDate(dateString, format = 'YYYY-MM-DD') {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day);
}

/**
 * 格式化货币
 * Format currency
 */
function formatCurrency(amount, currency = 'CNY') {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * 防抖函数
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出全局函数
window.AccountingSystem = {
    apiRequest,
    showNotification,
    formatDate,
    formatCurrency,
    debounce,
    throttle
};
