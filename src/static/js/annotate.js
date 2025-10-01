/**
 * 蜂格标注工具 - 增强版标注功能
 * 支持：缩放、平移、可调整圆形标注、多边形标注（蜂蜜区域）
 */

// 全局变量
let bgCanvas, annotationCanvas, bgCtx, annotCtx;
let imageObj = new Image();
let annotations = [];
let currentClass = 'other';
let isDirty = false;

// 国际化支持
let i18nData = {};

// 获取翻译文本的函数
function getI18nText(key) {
    return i18nData[key] || key;
}

// 视图控制
let scale = 1;
let offsetX = 0, offsetY = 0;
let isDraggingView = false;
let lastMouseX = 0, lastMouseY = 0;
let hasDragged = false;

// 标注控制
let currentTool = 'circle'; // 'circle', 'polygon', 'move'
let currentRadius = 20;
let isDraggingAnnotation = false;
let draggingIndex = -1;
let selectedIndex = -1;

// 多边形绘制
let isDrawingPolygon = false;
let currentPolygon = [];
let currentMousePos = null;



/**
 * 操作历史管理器
 * 支持撤销/重做功能
 */
const HistoryManager = {
    stack: [],
    currentIndex: -1,
    maxSize: 20,
    
    /**
     * 保存当前状态到历史栈
     */
    saveState: function() {
        // 深拷贝当前标注状态
        const state = JSON.parse(JSON.stringify(annotations));
        
        // 如果当前不在栈顶，删除后面的状态
        this.stack = this.stack.slice(0, this.currentIndex + 1);
        
        // 添加新状态
        this.stack.push(state);
        
        // 限制栈大小
        if (this.stack.length > this.maxSize) {
            this.stack.shift();
        } else {
            this.currentIndex++;
        }
        
        // 更新按钮状态
        this.updateButtons();
    },
    
    /**
     * 撤销到上一个状态
     */
    undo: function() {
        if (this.canUndo()) {
            this.currentIndex--;
            annotations = JSON.parse(JSON.stringify(this.stack[this.currentIndex]));
            isDirty = true;
            
            AnnotationTool.redrawAll();
            AnnotationTool.updateAnnotationList();
            AnnotationTool.updateAnnotationCount();
            
            this.updateButtons();
            Utils.showMessage(getI18nText('operation_undone'), 'info', 1000);
        }
    },
    
    /**
     * 重做到下一个状态
     */
    redo: function() {
        if (this.canRedo()) {
            this.currentIndex++;
            annotations = JSON.parse(JSON.stringify(this.stack[this.currentIndex]));
            isDirty = true;
            
            AnnotationTool.redrawAll();
            AnnotationTool.updateAnnotationList();
            AnnotationTool.updateAnnotationCount();
            
            this.updateButtons();
            Utils.showMessage(getI18nText('operation_redone'), 'info', 1000);
        }
    },
    
    /**
     * 检查是否可以撤销
     */
    canUndo: function() {
        return this.currentIndex > 0;
    },
    
    /**
     * 检查是否可以重做
     */
    canRedo: function() {
        return this.currentIndex < this.stack.length - 1;
    },
    
    /**
     * 更新撤销/重做按钮状态
     */
    updateButtons: function() {
        const undoBtn = document.getElementById('undoBtn');
        const redoBtn = document.getElementById('redoBtn');
        
        if (undoBtn) {
            undoBtn.disabled = !this.canUndo();
        }
        if (redoBtn) {
            redoBtn.disabled = !this.canRedo();
        }
    },
    
    /**
     * 清空历史
     */
    clear: function() {
        this.stack = [];
        this.currentIndex = -1;
        this.updateButtons();
    },
    
    /**
     * 初始化历史管理器
     */
    init: function() {
        // 保存初始状态
        this.saveState();
    }
};

/**
 * 几何计算工具模块
 * 支持带洞多边形的各种几何运算
 */
const GeometryUtils = {
    /**
     * 判断点是否在多边形内（不考虑洞）
     * 使用射线投射算法
     */
    pointInPolygon: function(point, polygon) {
        const x = point.x, y = point.y;
        let inside = false;
        
        for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            const xi = polygon[i].x, yi = polygon[i].y;
            const xj = polygon[j].x, yj = polygon[j].y;
            
            if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
                inside = !inside;
            }
        }
        
        return inside;
    },

    /**
     * 判断点是否在带洞多边形内
     * 点在外边界内且不在任何洞内时返回true
     */
    pointInComplexPolygon: function(point, annotation) {
        if (!annotation.points || annotation.points.length < 3) {
            return false;
        }
        
        // 首先检查是否在外边界内
        if (!this.pointInPolygon(point, annotation.points)) {
            return false;
        }
        

        
        return true;
    },

    /**
     * 判断圆形区域是否与多边形相交
     */
    circleIntersectsPolygon: function(center, radius, polygon) {
        // 检查圆心是否在多边形内
        if (this.pointInPolygon(center, polygon)) {
            return true;
        }
        
        // 检查圆是否与多边形的任何边相交
        for (let i = 0; i < polygon.length; i++) {
            const j = (i + 1) % polygon.length;
            const p1 = polygon[i];
            const p2 = polygon[j];
            
            if (this.distancePointToLineSegment(center, p1, p2) <= radius) {
                return true;
            }
        }
        
        return false;
    },

    /**
     * 计算点到线段的最短距离
     */
    distancePointToLineSegment: function(point, lineStart, lineEnd) {
        const A = point.x - lineStart.x;
        const B = point.y - lineStart.y;
        const C = lineEnd.x - lineStart.x;
        const D = lineEnd.y - lineStart.y;

        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        
        if (lenSq === 0) {
            // 线段退化为点
            return Math.sqrt(A * A + B * B);
        }
        
        let param = dot / lenSq;
        
        let xx, yy;
        if (param < 0) {
            xx = lineStart.x;
            yy = lineStart.y;
        } else if (param > 1) {
            xx = lineEnd.x;
            yy = lineEnd.y;
        } else {
            xx = lineStart.x + param * C;
            yy = lineStart.y + param * D;
        }

        const dx = point.x - xx;
        const dy = point.y - yy;
        return Math.sqrt(dx * dx + dy * dy);
    },



    /**
     * 将圆形转换为正多边形点数组
     */
    circleToPolygon: function(center, radius, segments = 16) {
        const points = [];
        for (let i = 0; i < segments; i++) {
            const angle = (i / segments) * 2 * Math.PI;
            points.push({
                x: center.x + radius * Math.cos(angle),
                y: center.y + radius * Math.sin(angle)
            });
        }
        return points;
    },

    /**
     * 计算多边形质心（考虑洞）
     */
    getPolygonCenter: function(points) {
        if (!points || points.length === 0) {
            return { x: 0, y: 0 };
        }
        
        let totalX = 0;
        let totalY = 0;
        
        for (let point of points) {
            totalX += point.x;
            totalY += point.y;
        }
        
        return {
            x: totalX / points.length,
            y: totalY / points.length
        };
    }
};

// 增强版标注工具主类
const AnnotationTool = {
    /**
     * 加载国际化数据
     */
    loadI18nData: function() {
        try {
            const i18nElement = document.getElementById('i18nData');
            if (i18nElement) {
                i18nData = JSON.parse(i18nElement.textContent);
            }
        } catch (e) {
            console.warn('Failed to load i18n data:', e);
            i18nData = {};
        }
    },

    /**
     * 初始化标注工具
     */
    init: function() {
        // 加载国际化数据
        this.loadI18nData();

        this.setupCanvas();
        this.loadImage();
        this.setupEventListeners();
        this.loadExistingAnnotations();
        this.updateClassDescription();
        this.updateAnnotationList();
        this.updateToolButtons();
        this.updateToolControls();
        
        // 设置初始光标样式
        annotationCanvas.style.cursor = 'default';
        
        // 初始化历史管理器
        HistoryManager.init();
    },

    /**
     * 设置双画布系统
     */
    setupCanvas: function() {
        bgCanvas = document.getElementById('bgCanvas');
        annotationCanvas = document.getElementById('annotationCanvas');
        
        if (!bgCanvas || !annotationCanvas) {
            Utils.showMessage(getI18nText('canvas_init_failed'), 'error');
            return;
        }

        bgCtx = bgCanvas.getContext('2d');
        annotCtx = annotationCanvas.getContext('2d');
        
        // 设置Canvas事件
        this.setupCanvasEvents();
        
        // 初始调整Canvas大小
        this.resizeCanvas();
    },

    /**
     * 设置Canvas事件
     */
    setupCanvasEvents: function() {
        const container = document.querySelector('.position-relative');
        
        // 鼠标事件
        annotationCanvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        annotationCanvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        annotationCanvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        annotationCanvas.addEventListener('click', this.handleCanvasClick.bind(this));
        annotationCanvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
        
        // 滚轮缩放
        container.addEventListener('wheel', this.handleWheel.bind(this));
        
        // 右键菜单事件（用于拖动）
        annotationCanvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });
        
        // 添加鼠标进入/离开事件，优化光标体验
        annotationCanvas.addEventListener('mouseenter', (e) => {
            const rect = annotationCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            // 更新鼠标位置
            currentMousePos = { x: mouseX, y: mouseY };
            
            MouseHandler.updateCursor(mouseX, mouseY);
        });
        
        annotationCanvas.addEventListener('mouseleave', () => {
            annotationCanvas.style.cursor = 'default';
            currentMousePos = null; // 清除鼠标位置
        });
    },

    /**
     * 加载图像
     */
    loadImage: function() {
        if (!window.imageData || !window.imageData.path) {
            Utils.showMessage(getI18nText('image_data_load_failed'), 'error');
            return;
        }

        imageObj.onload = () => {
            this.resetView();
            this.redrawAll();
            Utils.showMessage(getI18nText('image_load_success'), 'success', 2000);
        };

        imageObj.onerror = () => {
            Utils.showMessage(getI18nText('image_load_failed'), 'error');
        };

        imageObj.src = window.imageData.path;
    },

    /**
     * 调整Canvas大小
     */
    resizeCanvas: function() {
        const container = document.querySelector('.canvas-container');
        if (!container) return;
        
        // 使用容器的实际尺寸
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        bgCanvas.width = width;
        bgCanvas.height = height;
        bgCanvas.style.width = width + 'px';
        bgCanvas.style.height = height + 'px';
        
        annotationCanvas.width = width;
        annotationCanvas.height = height;
        annotationCanvas.style.width = width + 'px';
        annotationCanvas.style.height = height + 'px';
    },

    /**
     * 重置视图到初始状态
     */
    resetView: function() {
        if (!imageObj.complete) return;
        
        const containerWidth = bgCanvas.width;
        const containerHeight = bgCanvas.height;
        
        // 计算适合的缩放比例
        const scaleX = containerWidth / imageObj.width;
        const scaleY = containerHeight / imageObj.height;
        scale = Math.min(scaleX, scaleY, 1); // 不超过1倍
        
        // 居中显示
        offsetX = 0;
        offsetY = 0;
        
        this.redrawAll();
    },

    /**
     * 重绘所有内容
     */
    redrawAll: function() {
        this.drawBackground();
        this.drawAnnotations();
    },

    /**
     * 绘制背景图像
     */
    drawBackground: function() {
        if (!bgCtx || !imageObj.complete) return;
        
        // 清除背景Canvas
        bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
        
        // 计算图像绘制位置和大小
        const imgWidth = imageObj.width * scale;
        const imgHeight = imageObj.height * scale;
        const imgX = (bgCanvas.width - imgWidth) / 2 + offsetX;
        const imgY = (bgCanvas.height - imgHeight) / 2 + offsetY;
        
        // 绘制图像
        bgCtx.drawImage(imageObj, imgX, imgY, imgWidth, imgHeight);
    },

    /**
     * 绘制所有标注
     */
    drawAnnotations: function() {
        if (!annotCtx || !window.cellClasses) return;
        
        // 清除标注Canvas
        annotCtx.clearRect(0, 0, annotationCanvas.width, annotationCanvas.height);
        
        annotations.forEach((annotation, index) => {
            this.drawSingleAnnotation(annotation, index);
        });
        
        // 绘制正在创建的多边形
        if (isDrawingPolygon && currentPolygon.length > 0) {
            this.drawPolygonPreview();
        }
        

    },

    /**
     * 绘制单个标注
     */
    drawSingleAnnotation: function(annotation, index) {
        const classInfo = window.cellClasses[annotation.class] || window.cellClasses.other;
        const isSelected = index === selectedIndex;
        
        if (annotation.type === 'circle') {
            this.drawCircleAnnotation(annotation, classInfo, index, isSelected);
        } else if (annotation.type === 'polygon') {
            this.drawPolygonAnnotation(annotation, classInfo, index, isSelected);
        }
    },

    /**
     * 绘制圆形标注
     */
    drawCircleAnnotation: function(annotation, classInfo, index, isSelected) {
        const screenPos = this.imageToScreen(annotation.x, annotation.y);
        const screenRadius = annotation.radius * scale;
        
        annotCtx.beginPath();
        annotCtx.arc(screenPos.x, screenPos.y, screenRadius, 0, 2 * Math.PI);
        
        // 填充（蜂巢类别只显示边框，不填充）
        if (annotation.class !== 'honeycomb') {
            // 将颜色转换为极浅的透明色（审查模式）
            const baseColor = this.hexToRgba(classInfo.border, isSelected ? 0.15 : 0.05);
            annotCtx.fillStyle = baseColor;
            annotCtx.fill();
        }
        
        // 边框
        annotCtx.strokeStyle = isSelected ? '#ff0000' : classInfo.border;
        annotCtx.lineWidth = isSelected ? 3 : 2;
        annotCtx.stroke();
        
        // 标注编号
        annotCtx.fillStyle = '#000';
        annotCtx.font = '12px Arial';
        annotCtx.textAlign = 'center';
        annotCtx.fillText((index + 1).toString(), screenPos.x, screenPos.y + 4);
    },

    /**
     * 绘制多边形标注
     */
    drawPolygonAnnotation: function(annotation, classInfo, index, isSelected) {
        if (!annotation.points || annotation.points.length < 3) return;
        
        // 绘制简单多边形
        this.drawSimplePolygon(annotation, classInfo, index, isSelected);
    },

    /**
     * 绘制简单多边形（无洞）
     */
    drawSimplePolygon: function(annotation, classInfo, index, isSelected) {
        annotCtx.beginPath();
        const firstPoint = this.imageToScreen(annotation.points[0].x, annotation.points[0].y);
        annotCtx.moveTo(firstPoint.x, firstPoint.y);
        
        for (let i = 1; i < annotation.points.length; i++) {
            const point = this.imageToScreen(annotation.points[i].x, annotation.points[i].y);
            annotCtx.lineTo(point.x, point.y);
        }
        annotCtx.closePath();
        
        // 填充（蜂巢类别只显示边框，不填充）
        if (annotation.class !== 'honeycomb') {
            // 将颜色转换为极浅的透明色（审查模式）
            const baseColor = this.hexToRgba(classInfo.border, isSelected ? 0.15 : 0.05);
            annotCtx.fillStyle = baseColor;
            annotCtx.fill();
        }
        
        // 边框
        annotCtx.strokeStyle = isSelected ? '#ff0000' : classInfo.border;
        annotCtx.lineWidth = isSelected ? 3 : 2;
        annotCtx.stroke();
        
        // 标注编号（在质心位置）
        const center = GeometryUtils.getPolygonCenter(annotation.points);
        const screenCenter = this.imageToScreen(center.x, center.y);
        annotCtx.fillStyle = '#000';
        annotCtx.font = '12px Arial';
        annotCtx.textAlign = 'center';
        annotCtx.fillText((index + 1).toString(), screenCenter.x, screenCenter.y + 4);
    },



    /**
     * 处理Canvas点击事件
     */
    handleCanvasClick: function(e) {
        // 忽略右键点击和拖动后的点击
        if (isDraggingView || isDraggingAnnotation || e.button === 2 || hasDragged) return;
        
        const rect = annotationCanvas.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        if (currentTool === 'circle') {
            this.createCircleAnnotation(screenX, screenY);
        } else if (currentTool === 'polygon') {
            this.handlePolygonClick(screenX, screenY);
        }
    },



    /**
     * 处理双击事件
     */
    handleDoubleClick: function(e) {
        if (isDrawingPolygon) {
            this.finishPolygon();
        }
    },

    /**
     * 鼠标滚轮事件
     */
    handleWheel: function(e) {
        ViewControl.handleWheel(e);
    },

    /**
     * 鼠标按下事件
     */
    handleMouseDown: function(e) {
        MouseHandler.handleMouseDown(e);
    },

    /**
     * 鼠标移动事件
     */
    handleMouseMove: function(e) {
        const rect = annotationCanvas.getBoundingClientRect();
        currentMousePos = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        // 如果正在绘制多边形，需要重绘以显示预览线段
        if (isDrawingPolygon) {
            this.redrawAll();
        }
        
        // 处理拖动和光标更新
        MouseHandler.handleMouseMove(e);
        
        // 如果不在拖动状态，更新光标
        if (!isDraggingView && !isDraggingAnnotation) {
            MouseHandler.updateCursor(currentMousePos.x, currentMousePos.y);
        }
    },

    /**
     * 鼠标抬起事件
     */
    handleMouseUp: function(e) {
        MouseHandler.handleMouseUp(e);
    },

    /**
     * 创建圆形标注
     */
    createCircleAnnotation: function(screenX, screenY) {
        // 检查是否点击了现有标注
        const hitIndex = MouseHandler.getHitAnnotation(screenX, screenY);
        if (hitIndex !== -1) {
            selectedIndex = hitIndex;
            this.updateAnnotationList();
            this.redrawAll();
            return;
        }
        
        // 转换为图像坐标
        const imagePos = AnnotationUtils.screenToImage(screenX, screenY);
        
        // 检查是否在图像范围内
        if (imagePos.x < 0 || imagePos.x > imageObj.width || 
            imagePos.y < 0 || imagePos.y > imageObj.height) {
            Utils.showMessage(getI18nText('click_within_image'), 'warning', 2000);
            return;
        }
        
        // 创建新标注
        const annotation = {
            type: 'circle',
            x: imagePos.x,
            y: imagePos.y,
            radius: currentRadius,
            class: currentClass,
            timestamp: new Date().toISOString()
        };
        
        annotations.push(annotation);
        selectedIndex = annotations.length - 1;
        isDirty = true;
        
        this.redrawAll();
        this.updateAnnotationList();
        this.updateAnnotationCount();
        
        // 保存状态到历史
        HistoryManager.saveState();
        
        Utils.showMessage(getI18nText('annotation_added').replace('{type}', window.cellClasses[currentClass].name), 'success', 1000);
    },

    /**
     * 处理多边形点击
     */
    handlePolygonClick: function(screenX, screenY) {
        // 转换为图像坐标
        const imagePos = AnnotationUtils.screenToImage(screenX, screenY);
        
        // 检查是否在图像范围内
        if (imagePos.x < 0 || imagePos.x > imageObj.width || 
            imagePos.y < 0 || imagePos.y > imageObj.height) {
            Utils.showMessage(getI18nText('click_within_image'), 'warning', 2000);
            return;
        }
        
        if (!isDrawingPolygon) {
            // 开始新多边形
            this.startPolygon(imagePos.x, imagePos.y);
        } else {
            // 添加点到当前多边形
            this.addPolygonPoint(imagePos.x, imagePos.y);
        }
    },

    /**
     * 开始绘制多边形
     */
    startPolygon: function(x, y) {
        isDrawingPolygon = true;
        currentPolygon = [{x: x, y: y}];
        Utils.showMessage(getI18nText('polygon_start'), 'info', 3000);
        this.redrawAll();
    },

    /**
     * 添加多边形点
     */
    addPolygonPoint: function(x, y) {
        currentPolygon.push({x: x, y: y});
        this.redrawAll();
    },

    /**
     * 完成多边形绘制
     */
    finishPolygon: function() {
        if (currentPolygon.length < 3) {
            Utils.showMessage(getI18nText('polygon_min_points'), 'warning', 2000);
            return;
        }
        
        // 创建多边形标注
        const annotation = {
            type: 'polygon',
            points: [...currentPolygon],
            class: currentClass,
            timestamp: new Date().toISOString()
        };
        
        annotations.push(annotation);
        selectedIndex = annotations.length - 1;
        isDirty = true;
        
        // 重置多边形绘制状态
        isDrawingPolygon = false;
        currentPolygon = [];
        
        this.redrawAll();
        this.updateAnnotationList();
        this.updateAnnotationCount();
        
        // 保存状态到历史
        HistoryManager.saveState();
        
        Utils.showMessage(getI18nText('polygon_added').replace('{type}', window.cellClasses[currentClass].name), 'success', 1000);
    },

    /**
     * 取消多边形绘制
     */
    cancelPolygon: function() {
        isDrawingPolygon = false;
        currentPolygon = [];
        this.redrawAll();
        Utils.showMessage(getI18nText('polygon_cancelled'), 'info', 1000);
    },

    /**
     * 绘制多边形预览
     */
    drawPolygonPreview: function() {
        if (currentPolygon.length < 1) return;
        
        const classInfo = window.cellClasses[currentClass] || window.cellClasses.other;
        
        annotCtx.strokeStyle = classInfo.border;
        annotCtx.lineWidth = 2;
        annotCtx.setLineDash([5, 5]);
        
        annotCtx.beginPath();
        const firstPoint = AnnotationUtils.imageToScreen(currentPolygon[0].x, currentPolygon[0].y);
        annotCtx.moveTo(firstPoint.x, firstPoint.y);
        
        for (let i = 1; i < currentPolygon.length; i++) {
            const point = AnnotationUtils.imageToScreen(currentPolygon[i].x, currentPolygon[i].y);
            annotCtx.lineTo(point.x, point.y);
        }
        
        // 如果有鼠标位置，绘制到当前鼠标的预览线段
        if (currentMousePos && currentPolygon.length > 0) {
            const lastPoint = AnnotationUtils.imageToScreen(
                currentPolygon[currentPolygon.length - 1].x, 
                currentPolygon[currentPolygon.length - 1].y
            );
            annotCtx.moveTo(lastPoint.x, lastPoint.y);
            annotCtx.lineTo(currentMousePos.x, currentMousePos.y);
        }
        
        annotCtx.stroke();
        annotCtx.setLineDash([]);
        
        // 绘制顶点
        currentPolygon.forEach((point, index) => {
            const screenPoint = AnnotationUtils.imageToScreen(point.x, point.y);
            annotCtx.beginPath();
            annotCtx.arc(screenPoint.x, screenPoint.y, 4, 0, 2 * Math.PI);
            annotCtx.fillStyle = index === 0 ? '#ff0000' : classInfo.color;
            annotCtx.fill();
            annotCtx.strokeStyle = '#000';
            annotCtx.lineWidth = 1;
            annotCtx.stroke();
        });
    },



    /**
     * 删除标注
     */
    removeAnnotation: function(index) {
        if (index >= 0 && index < annotations.length) {
            const removed = annotations.splice(index, 1)[0];
            isDirty = true;
            
            this.redrawAll();
            this.updateAnnotationList();
            this.updateAnnotationCount();
            
            // 保存状态到历史
            HistoryManager.saveState();
            
            Utils.showMessage(getI18nText('annotation_deleted').replace('{type}', window.cellClasses[removed.class].name), 'warning', 1000);
        }
    },

    /**
     * 工具切换
     */
    setTool: function(toolName) {
        // 取消当前多边形绘制
        if (isDrawingPolygon) {
            this.cancelPolygon();
        }
        

        
        currentTool = toolName;
        selectedIndex = -1;
        this.updateToolButtons();
        this.updateToolControls();
        this.redrawAll(); // 这会清除之前工具的预览效果
        
        // 重置光标样式
        annotationCanvas.style.cursor = 'default';
        
        // 更新提示信息
        const toolMap = {
            'move': getI18nText('move_mode_tip'),
            'circle': getI18nText('circle_mode_tip'),
            'polygon': getI18nText('polygon_mode_tip')
        };

        Utils.showMessage(toolMap[toolName] || '', 'info', 3000);
    },

    /**
     * 更新工具按钮状态
     */
    updateToolButtons: function() {
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-tool="${currentTool}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    },

    /**
     * 调整圆形半径
     */
    setRadius: function(radius) {
        currentRadius = Math.max(5, Math.min(100, radius));
        
        // 如果有选中的圆形标注，更新其半径
        if (selectedIndex !== -1 && annotations[selectedIndex] && 
            annotations[selectedIndex].type === 'circle') {
            annotations[selectedIndex].radius = currentRadius;
            isDirty = true;
            this.redrawAll();
        }
        
        this.updateRadiusDisplay();
    },

    /**
     * 更新半径显示
     */
    updateRadiusDisplay: function() {
        const radiusSlider = document.getElementById('radiusSlider');
        const radiusValue = document.getElementById('radiusValue');
        
        if (radiusSlider) radiusSlider.value = currentRadius;
        if (radiusValue) radiusValue.textContent = currentRadius;
    },



    /**
     * 更新工具控制器显示
     */
    updateToolControls: function() {
        const radiusControl = document.getElementById('radiusControl');
        
        if (radiusControl) {
            radiusControl.style.display = 'flex';
        }
    },

    /**
     * 更新缩放显示
     */
    updateZoomDisplay: function() {
        const zoomValue = document.getElementById('zoomValue');
        if (zoomValue) {
            zoomValue.textContent = Math.round(scale * 100) + '%';
        }
    },

    /**
     * 坐标转换方法（兼容性）
     */
    imageToScreen: function(imageX, imageY) {
        return AnnotationUtils.imageToScreen(imageX, imageY);
    },

    getPolygonCenter: function(points) {
        return AnnotationUtils.getPolygonCenter(points);
    },

    /**
     * 获取类别显示名称
     */
    getClassDisplayName: function(classKey) {
        return window.cellClasses[classKey]?.name || '未知类别';
    },

    /**
     * 将hex颜色转换为rgba格式
     */
    hexToRgba: function(hex, alpha) {
        // 移除#号
        hex = hex.replace('#', '');
        
        // 处理3位hex颜色
        if (hex.length === 3) {
            hex = hex.split('').map(c => c + c).join('');
        }
        
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },

    /**
     * 更换标注类别
     */
    changeAnnotationClass: function(index, newClass) {
        if (index >= 0 && index < annotations.length) {
            const oldClass = annotations[index].class;
            annotations[index].class = newClass;
            annotations[index].timestamp = new Date().toISOString();
            isDirty = true;
            
            this.redrawAll();
            this.updateAnnotationList();
            
            // 保存状态到历史
            HistoryManager.saveState();
            
            const oldName = window.cellClasses[oldClass]?.name || '未知';
            const newName = window.cellClasses[newClass]?.name || '未知';
            Utils.showMessage(getI18nText('class_changed').replace('{oldClass}', oldName).replace('{newClass}', newName), 'success', 2000);
        }
    },

    /**
     * 选择标注
     */
    selectAnnotation: function(index) {
        selectedIndex = index;
        this.updateAnnotationList();
        this.redrawAll();
    },

    /**
     * 删除选中标注
     */
    deleteSelectedAnnotation: function() {
        if (selectedIndex !== -1 && annotations[selectedIndex]) {
            this.removeAnnotation(selectedIndex);
            selectedIndex = -1;
        }
    },

    /**
     * 设置事件监听器
     */
    setupEventListeners: function() {
        // 类别选择
        document.querySelectorAll('input[name="cellClass"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                currentClass = e.target.value;
                this.updateClassDescription();
            });
        });
        
        // 工具按钮
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.target.dataset.tool || e.target.closest('.tool-btn').dataset.tool;
                this.setTool(tool);
            });
        });
        
        // 视图控制按钮
        document.getElementById('zoomIn')?.addEventListener('click', () => ViewControl.zoomIn());
        document.getElementById('zoomOut')?.addEventListener('click', () => ViewControl.zoomOut());
        document.getElementById('zoomFit')?.addEventListener('click', () => ViewControl.zoomToFit());
        
        // 半径滑块
        document.getElementById('radiusSlider')?.addEventListener('input', (e) => {
            this.setRadius(parseInt(e.target.value));
        });
        

        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveAnnotations();
            } else if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                HistoryManager.undo();
            } else if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                HistoryManager.redo();
            } else if (e.key === 'Delete' || e.key === 'Backspace') {
                e.preventDefault();
                this.deleteSelectedAnnotation();
            } else if (e.key === 'Escape') {
                if (isDrawingPolygon) {
                    this.cancelPolygon();
                } else {
                    selectedIndex = -1;
                    this.redrawAll();
                }
            } else if (e.key === '1') {
                this.setTool('move');
            } else if (e.key === '2') {
                this.setTool('circle');
            } else if (e.key === '3') {
                this.setTool('polygon');
            }
        });
        
        // 窗口大小变化
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.redrawAll();
        });
        
        // 页面离开警告
        window.addEventListener('beforeunload', (e) => {
            if (isDirty) {
                e.preventDefault();
                e.returnValue = '您有未保存的标注，确定要离开吗？';
            }
        });
    },

    /**
     * 加载现有标注
     */
    loadExistingAnnotations: function() {
        if (window.existingAnnotations && Array.isArray(window.existingAnnotations)) {
            annotations = [...window.existingAnnotations];
            this.updateAnnotationList();
            this.updateAnnotationCount();
        }
    },

    /**
     * 更新类别描述
     */
    updateClassDescription: function() {
        const descElement = document.getElementById('classDescription');
        if (descElement && window.cellClasses && window.cellClasses[currentClass]) {
            const classInfo = window.cellClasses[currentClass];
            descElement.innerHTML = `
                <div style="color: ${classInfo.border}; font-weight: bold;">${classInfo.name}</div>
                <div>${classInfo.description}</div>
            `;
        }
    },

    /**
     * 更新标注列表
     */
    updateAnnotationList: function() {
        const listElement = document.getElementById('annotationList');
        if (!listElement) return;
        
        if (annotations.length === 0) {
            listElement.innerHTML = `<div class="text-muted text-center p-3">${getI18nText('no_annotations')}</div>`;
            return;
        }
        
        const listHTML = annotations.map((annotation, index) => {
            const classInfo = window.cellClasses[annotation.class] || window.cellClasses.other;
            
            // 根据标注类型显示不同的坐标信息
            let coordInfo = '';
            if (annotation.type === 'circle') {
                coordInfo = `${getI18nText('circle')} (${Math.round(annotation.x)}, ${Math.round(annotation.y)}) r=${annotation.radius}`;
            } else if (annotation.type === 'polygon' && annotation.points) {
                const center = GeometryUtils.getPolygonCenter(annotation.points);
                coordInfo = `${getI18nText('polygon')} (${Math.round(center.x)}, ${Math.round(center.y)}) ${annotation.points.length}${getI18nText('points')}`;
            } else {
                coordInfo = getI18nText('unknown_type');
            }
            
            // 生成类别选择下拉框
            const classOptions = Object.keys(window.cellClasses).map(classKey => {
                const selected = classKey === annotation.class ? 'selected' : '';
                return `<option value="${classKey}" ${selected}>${window.cellClasses[classKey].name}</option>`;
            }).join('');
            
            return `
                <div class="annotation-item ${index === selectedIndex ? 'selected' : ''}" 
                     onclick="AnnotationTool.selectAnnotation(${index})" style="cursor: pointer;">
                    <div class="d-flex align-items-center justify-content-between">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center">
                                <span class="annotation-dot me-2" style="background-color: ${classInfo.border};"></span>
                                <span class="fw-bold">${index + 1}.</span>
                            </div>
                            <small class="text-muted d-block">${coordInfo}</small>
                        </div>
                        <div class="d-flex align-items-center gap-1">
                            <select class="form-select form-select-sm annotation-class-select" 
                                    style="min-width: 80px; font-size: 0.75rem;"
                                    onchange="event.stopPropagation(); AnnotationTool.changeAnnotationClass(${index}, this.value)"
                                    onclick="event.stopPropagation()">
                                ${classOptions}
                            </select>
                            <button class="btn btn-sm btn-outline-danger delete-annotation"
                                    onclick="event.stopPropagation(); AnnotationTool.removeAnnotation(${index})"
                                    title="${getI18nText('delete_annotation')}">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        listElement.innerHTML = listHTML;
    },

    /**
     * 更新标注计数
     */
    updateAnnotationCount: function() {
        const countElement = document.getElementById('annotationCount');
        if (countElement) {
            countElement.textContent = annotations.length;
        }
    },

    /**
     * 保存标注
     */
    saveAnnotations: async function() {
        if (!window.imageData || !window.imageData.id) {
            Utils.showMessage(getI18nText('image_data_invalid'), 'error');
            return;
        }
        
        try {
            // 显示加载状态
            const saveBtn = document.querySelector('button[onclick="saveAnnotations()"]');
            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<i class="bi bi-spinner spin"></i> 保存中...';
            }
            
            const response = await API.post('/api/save_annotation', {
                image_id: window.imageData.id,
                annotations: annotations
            });
            
            if (response.success) {
                isDirty = false;
                Utils.showMessage(response.message, 'success');
                
                // 显示成功模态框
                const modal = new bootstrap.Modal(document.getElementById('saveSuccessModal'));
                document.getElementById('saveMessage').textContent = response.message;
                modal.show();
            } else {
                Utils.showMessage(response.error || getI18nText('save_failed'), 'error');
            }
            
        } catch (error) {
            console.error('保存标注失败:', error);
            Utils.showMessage(getI18nText('save_failed_retry'), 'error');
        } finally {
            // 恢复按钮状态
            const saveBtn = document.querySelector('button[onclick="saveAnnotations()"]');
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="bi bi-save"></i> 保存标注';
            }
        }
    },

    /**
     * 清空所有标注
     */
    clearAllAnnotations: function() {
        if (annotations.length === 0) {
            Utils.showMessage(getI18nText('no_annotations_to_clear'), 'warning');
            return;
        }
        
        if (confirm(getI18nText('clear_all_confirm').replace('{count}', annotations.length))) {
            annotations = [];
            isDirty = true;
            this.redrawAll();
            this.updateAnnotationList();
            this.updateAnnotationCount();
            Utils.showMessage(getI18nText('all_annotations_cleared'), 'warning');
        }
    },

    /**
     * 撤销最后一个标注
     */
    undoLastAnnotation: function() {
        if (annotations.length === 0) {
            Utils.showMessage(getI18nText('no_annotations_to_undo'), 'warning');
            return;
        }
        
        const removed = annotations.pop();
        isDirty = true;
        this.redrawAll();
        this.updateAnnotationList();
        this.updateAnnotationCount();
        
        Utils.showMessage(getI18nText('annotation_undone').replace('{type}', window.cellClasses[removed.class].name), 'info', 1500);
    }
};

// 全局函数（供HTML调用）
function saveAnnotations() {
    AnnotationTool.saveAnnotations();
}

function clearAllAnnotations() {
    AnnotationTool.clearAllAnnotations();
}

function undoLastAnnotation() {
    AnnotationTool.undoLastAnnotation();
}

function initializeAnnotationTool() {
    AnnotationTool.init();
}

// 导出到全局
window.annotationTool = AnnotationTool; 