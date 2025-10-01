/**
 * 蜂格标注工具 - 通用JavaScript功能
 */

// 通用工具函数
const Utils = {
    /**
     * 显示提示消息
     */
    showMessage: function(message, type = 'info', duration = 3000) {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' : 
                          type === 'success' ? 'alert-success' : 'alert-info';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 
                                  type === 'warning' ? 'exclamation-circle' : 
                                  type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('afterbegin', alertHtml);
        
        // 自动消失
        if (duration > 0) {
            setTimeout(() => {
                const alert = document.querySelector('.alert.position-fixed');
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, duration);
        }
    },

    /**
     * 格式化数字
     */
    formatNumber: function(num) {
        return num.toLocaleString();
    },

    /**
     * 获取文件扩展名
     */
    getFileExtension: function(filename) {
        return filename.split('.').pop().toLowerCase();
    },

    /**
     * 检查是否为有效的图像文件
     */
    isValidImageFile: function(filename) {
        const validExtensions = ['jpg', 'jpeg', 'png', 'bmp', 'tif', 'tiff'];
        return validExtensions.includes(this.getFileExtension(filename));
    },

    /**
     * 防抖函数
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 节流函数
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// API请求封装
const API = {
    /**
     * 发送POST请求
     */
    post: async function(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    },

    /**
     * 发送GET请求
     */
    get: async function(url) {
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }
};

// 统计信息更新
const StatsUpdater = {
    /**
     * 更新统计信息
     */
    updateStats: async function() {
        try {
            const response = await API.get('/api/stats');
            
            if (response.success) {
                this.displayStats(response.stats);
            }
        } catch (error) {
            console.error('获取统计信息失败:', error);
        }
    },

    /**
     * 显示统计信息
     */
    displayStats: function(stats) {
        // 更新总数显示
        const elements = {
            totalImages: document.querySelector('.badge.bg-primary'),
            annotatedImages: document.querySelector('.badge.bg-success'),
            totalAnnotations: document.querySelector('.badge.bg-info')
        };

        if (elements.totalImages) {
            elements.totalImages.textContent = stats.total_images;
        }
        if (elements.annotatedImages) {
            elements.annotatedImages.textContent = stats.annotated_images;
        }
        if (elements.totalAnnotations) {
            elements.totalAnnotations.textContent = stats.total_annotations;
        }

        // 更新进度条
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar && stats.total_images > 0) {
            const percentage = (stats.annotated_images / stats.total_images * 100).toFixed(1);
            progressBar.style.width = `${percentage}%`;
            progressBar.textContent = `${percentage}%`;
        }
    }
};

// 文件上传处理
const FileUploader = {
    /**
     * 初始化文件上传
     */
    init: function() {
        const fileInput = document.getElementById('file');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
    },

    /**
     * 处理文件选择
     */
    handleFileSelect: function(event) {
        const file = event.target.files[0];
        if (file) {
            if (!Utils.isValidImageFile(file.name)) {
                Utils.showMessage('请选择有效的图像文件（JPG, PNG, BMP, TIF）', 'error');
                event.target.value = '';
                return;
            }

            if (file.size > 16 * 1024 * 1024) { // 16MB
                Utils.showMessage('文件大小不能超过16MB', 'error');
                event.target.value = '';
                return;
            }

            Utils.showMessage('文件选择成功，点击上传按钮开始上传', 'success');
        }
    }
};

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化文件上传
    FileUploader.init();
    
    // 定期更新统计信息（如果在首页）
    if (window.location.pathname === '/') {
        StatsUpdater.updateStats();
        setInterval(StatsUpdater.updateStats.bind(StatsUpdater), 30000); // 30秒更新一次
    }
    
    // 初始化提示工具
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 自动关闭Flash消息
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert:not(.position-fixed)');
        alerts.forEach(alert => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        });
    }, 5000);
});

// 错误处理
window.addEventListener('error', function(event) {
    console.error('JavaScript错误:', event.error);
    Utils.showMessage('发生了一个错误，请刷新页面重试', 'error');
});

// 导出到全局
window.Utils = Utils;
window.API = API;
window.StatsUpdater = StatsUpdater; 