/**
 * 蜂格标注工具 - 增强版辅助方法
 */

// 坐标转换和工具方法
const AnnotationUtils = {
    /**
     * 图像坐标转屏幕坐标
     */
    imageToScreen: function(imageX, imageY) {
        const imgWidth = imageObj.width * scale;
        const imgHeight = imageObj.height * scale;
        const imgX = (bgCanvas.width - imgWidth) / 2 + offsetX;
        const imgY = (bgCanvas.height - imgHeight) / 2 + offsetY;
        
        return {
            x: imgX + (imageX / imageObj.width) * imgWidth,
            y: imgY + (imageY / imageObj.height) * imgHeight
        };
    },

    /**
     * 屏幕坐标转图像坐标
     */
    screenToImage: function(screenX, screenY) {
        const imgWidth = imageObj.width * scale;
        const imgHeight = imageObj.height * scale;
        const imgX = (bgCanvas.width - imgWidth) / 2 + offsetX;
        const imgY = (bgCanvas.height - imgHeight) / 2 + offsetY;
        
        return {
            x: ((screenX - imgX) / imgWidth) * imageObj.width,
            y: ((screenY - imgY) / imgHeight) * imageObj.height
        };
    },

    /**
     * 获取多边形质心
     */
    getPolygonCenter: function(points) {
        let totalX = 0, totalY = 0;
        for (let point of points) {
            totalX += point.x;
            totalY += point.y;
        }
        return {
            x: totalX / points.length,
            y: totalY / points.length
        };
    },

    /**
     * 检查点是否在圆形内
     */
    isPointInCircle: function(px, py, cx, cy, radius) {
        const dx = px - cx;
        const dy = py - cy;
        return (dx * dx + dy * dy) <= (radius * radius);
    },

    /**
     * 检查点是否在多边形内
     */
    isPointInPolygon: function(px, py, points) {
        let inside = false;
        for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
            const xi = points[i].x, yi = points[i].y;
            const xj = points[j].x, yj = points[j].y;
            
            if (((yi > py) !== (yj > py)) && 
                (px < (xj - xi) * (py - yi) / (yj - yi) + xi)) {
                inside = !inside;
            }
        }
        return inside;
    },

    /**
     * 限制值在范围内
     */
    clamp: function(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }
};

// 鼠标事件处理
const MouseHandler = {
    /**
     * 鼠标按下事件
     */
    handleMouseDown: function(e) {
        const rect = annotationCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        lastMouseX = mouseX;
        lastMouseY = mouseY;
        hasDragged = false;
        
        // 右键总是启用视图拖动
        if (e.button === 2) {
            isDraggingView = true;
            annotationCanvas.style.cursor = 'grabbing';
            e.preventDefault();
            return;
        }
        
        // 左键处理
        if (e.button === 0) {
            if (currentTool === 'move') {
                // 移动工具：检查是否点击标注，否则拖动视图
                const hitIndex = this.getHitAnnotation(mouseX, mouseY);
                if (hitIndex !== -1) {
                    isDraggingAnnotation = true;
                    draggingIndex = hitIndex;
                    selectedIndex = hitIndex;
                    AnnotationTool.updateAnnotationList();
                    AnnotationTool.redrawAll();
                } else {
                    isDraggingView = true;
                    annotationCanvas.style.cursor = 'grabbing';
                }
            } else if (currentTool === 'circle') {
                // 圆形工具：检查是否点击了现有标注用于拖拽
                const hitIndex = this.getHitAnnotation(mouseX, mouseY);
                if (hitIndex !== -1) {
                    isDraggingAnnotation = true;
                    draggingIndex = hitIndex;
                    selectedIndex = hitIndex;
                    AnnotationTool.updateAnnotationList();
                    AnnotationTool.redrawAll();
                }
            }
        }
        
        e.preventDefault();
    },

    /**
     * 鼠标移动事件
     */
    handleMouseMove: function(e) {
        const rect = annotationCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        if (isDraggingView) {
            // 平移视图 - 直接响应，无阈值限制
            const deltaX = mouseX - lastMouseX;
            const deltaY = mouseY - lastMouseY;
            
            if (deltaX !== 0 || deltaY !== 0) {
                hasDragged = true;
                offsetX += deltaX;
                offsetY += deltaY;
                AnnotationTool.redrawAll();
                
                lastMouseX = mouseX;
                lastMouseY = mouseY;
            }
        } else if (isDraggingAnnotation && draggingIndex !== -1) {
            // 拖拽标注
            const deltaX = mouseX - lastMouseX;
            const deltaY = mouseY - lastMouseY;
            
            if (annotations[draggingIndex].type === 'circle') {
                const imagePos = AnnotationUtils.screenToImage(mouseX, mouseY);
                annotations[draggingIndex].x = AnnotationUtils.clamp(imagePos.x, 0, imageObj.width);
                annotations[draggingIndex].y = AnnotationUtils.clamp(imagePos.y, 0, imageObj.height);
            } else if (annotations[draggingIndex].type === 'polygon') {
                // 拖拽多边形：移动所有顶点和洞
                const imageDelta = AnnotationUtils.screenToImage(deltaX, deltaY);
                const origin = AnnotationUtils.screenToImage(0, 0);
                const realDeltaX = imageDelta.x - origin.x;
                const realDeltaY = imageDelta.y - origin.y;
                
                // 移动外边界顶点
                annotations[draggingIndex].points.forEach(point => {
                    point.x = AnnotationUtils.clamp(point.x + realDeltaX, 0, imageObj.width);
                    point.y = AnnotationUtils.clamp(point.y + realDeltaY, 0, imageObj.height);
                });
                
                // 移动所有洞的顶点
                if (annotations[draggingIndex].holes && annotations[draggingIndex].holes.length > 0) {
                    annotations[draggingIndex].holes.forEach(hole => {
                        hole.forEach(point => {
                            point.x = AnnotationUtils.clamp(point.x + realDeltaX, 0, imageObj.width);
                            point.y = AnnotationUtils.clamp(point.y + realDeltaY, 0, imageObj.height);
                        });
                    });
                }
            }
            
            lastMouseX = mouseX;
            lastMouseY = mouseY;
            isDirty = true;
            AnnotationTool.redrawAll();
        }
        
        // 更新光标样式
        this.updateCursor(mouseX, mouseY);
        
        e.preventDefault();
    },

    /**
     * 鼠标抬起事件
     */
    handleMouseUp: function(e) {
        const wasViewDragging = isDraggingView;
        
        isDraggingView = false;
        isDraggingAnnotation = false;
        draggingIndex = -1;
        
        // 立即更新光标样式
        this.updateCursor(lastMouseX, lastMouseY);
        
        // 延迟重置拖动状态，避免立即触发点击事件
        if (wasViewDragging) {
            setTimeout(() => {
                hasDragged = false;
            }, 100);
        } else {
            hasDragged = false;
        }
        
        e.preventDefault();
    },

    /**
     * 获取被点击的标注索引
     */
    getHitAnnotation: function(screenX, screenY) {
        for (let i = annotations.length - 1; i >= 0; i--) {
            const annotation = annotations[i];
            
            if (annotation.type === 'circle') {
                const screenPos = AnnotationUtils.imageToScreen(annotation.x, annotation.y);
                const screenRadius = annotation.radius * scale;
                
                // 蜂巢类别只检测边框附近，其他类别检测整个区域
                if (annotation.class === 'honeycomb') {
                    // 只有在边框附近才算命中（边框宽度±5像素）
                    const distance = Math.sqrt(Math.pow(screenX - screenPos.x, 2) + Math.pow(screenY - screenPos.y, 2));
                    const borderWidth = 5; // 边框检测宽度
                    if (distance >= screenRadius - borderWidth && distance <= screenRadius + borderWidth) {
                        return i;
                    }
                } else {
                    // 其他类别检测整个区域
                    if (AnnotationUtils.isPointInCircle(screenX, screenY, screenPos.x, screenPos.y, screenRadius)) {
                        return i;
                    }
                }
            } else if (annotation.type === 'polygon') {
                // 蜂巢类别只检测边框附近，其他类别检测整个区域
                if (annotation.class === 'honeycomb') {
                    const screenPoints = annotation.points.map(p => AnnotationUtils.imageToScreen(p.x, p.y));
                    // 只有在多边形边框附近才算命中
                    if (this.isPointNearPolygonBorder(screenX, screenY, screenPoints, 8)) {
                        return i;
                    }
                } else {
                    // 其他类别检测整个区域，但要考虑洞的存在
                    const imagePos = AnnotationUtils.screenToImage(screenX, screenY);
                    if (GeometryUtils.pointInComplexPolygon(imagePos, annotation)) {
                        return i;
                    }
                }
            }
        }
        return -1;
    },

    /**
     * 检查点是否在多边形边框附近
     */
    isPointNearPolygonBorder: function(x, y, points, threshold = 8) {
        if (points.length < 3) return false;
        
        for (let i = 0; i < points.length; i++) {
            const p1 = points[i];
            const p2 = points[(i + 1) % points.length];
            
            // 计算点到线段的距离
            const distance = this.pointToLineDistance(x, y, p1.x, p1.y, p2.x, p2.y);
            
            if (distance <= threshold) {
                return true;
            }
        }
        return false;
    },

    /**
     * 计算点到线段的距离
     */
    pointToLineDistance: function(px, py, x1, y1, x2, y2) {
        const A = px - x1;
        const B = py - y1;
        const C = x2 - x1;
        const D = y2 - y1;

        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        
        if (lenSq === 0) {
            // 线段是一个点
            return Math.sqrt(A * A + B * B);
        }
        
        let param = dot / lenSq;
        
        let xx, yy;
        
        if (param < 0) {
            xx = x1;
            yy = y1;
        } else if (param > 1) {
            xx = x2;
            yy = y2;
        } else {
            xx = x1 + param * C;
            yy = y1 + param * D;
        }
        
        const dx = px - xx;
        const dy = py - yy;
        return Math.sqrt(dx * dx + dy * dy);
    },

    /**
     * 更新光标样式
     */
    updateCursor: function(mouseX, mouseY) {
        let cursor = 'default';
        
        // 拖动状态优先
        if (isDraggingView) {
            cursor = 'grabbing';
        } else if (isDraggingAnnotation) {
            cursor = 'move';
        } else {
            // 根据工具和悬停状态设置光标
            if (currentTool === 'move') {
                const hitIndex = this.getHitAnnotation(mouseX, mouseY);
                cursor = hitIndex !== -1 ? 'move' : 'grab';
            } else if (currentTool === 'circle') {
                const hitIndex = this.getHitAnnotation(mouseX, mouseY);
                // 只有可以拖动的标注才显示move光标，否则显示crosshair
                cursor = hitIndex !== -1 ? 'move' : 'crosshair';
            } else if (currentTool === 'polygon') {
                const hitIndex = this.getHitAnnotation(mouseX, mouseY);
                // 只有可以拖动的标注才显示move光标，否则显示crosshair
                cursor = hitIndex !== -1 ? 'move' : 'crosshair';
            }
        }
        
        annotationCanvas.style.cursor = cursor;
    }
};

// 缩放和视图控制
const ViewControl = {
    /**
     * 滚轮缩放事件
     */
    handleWheel: function(e) {
        e.preventDefault();
        
        const rect = annotationCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // 计算缩放前的图像坐标
        const beforeZoom = AnnotationUtils.screenToImage(mouseX, mouseY);
        
        // 更新缩放
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = AnnotationUtils.clamp(scale * zoomFactor, 0.1, 5.0);
        
        if (newScale !== scale) {
            scale = newScale;
            
            // 计算缩放后的图像坐标（应该保持不变）
            const afterZoom = AnnotationUtils.screenToImage(mouseX, mouseY);
            
            // 调整偏移量使鼠标位置保持不变
            const deltaImageX = afterZoom.x - beforeZoom.x;
            const deltaImageY = afterZoom.y - beforeZoom.y;
            
            offsetX -= deltaImageX * scale;
            offsetY -= deltaImageY * scale;
            
            AnnotationTool.redrawAll();
            AnnotationTool.updateZoomDisplay();
        }
    },

    /**
     * 缩放到适合大小
     */
    zoomToFit: function() {
        AnnotationTool.resetView();
    },

    /**
     * 放大
     */
    zoomIn: function() {
        const centerX = bgCanvas.width / 2;
        const centerY = bgCanvas.height / 2;
        
        const beforeZoom = AnnotationUtils.screenToImage(centerX, centerY);
        scale = AnnotationUtils.clamp(scale * 1.2, 0.1, 5.0);
        const afterZoom = AnnotationUtils.screenToImage(centerX, centerY);
        
        offsetX -= (afterZoom.x - beforeZoom.x) * scale;
        offsetY -= (afterZoom.y - beforeZoom.y) * scale;
        
        AnnotationTool.redrawAll();
        AnnotationTool.updateZoomDisplay();
    },

    /**
     * 缩小
     */
    zoomOut: function() {
        const centerX = bgCanvas.width / 2;
        const centerY = bgCanvas.height / 2;
        
        const beforeZoom = AnnotationUtils.screenToImage(centerX, centerY);
        scale = AnnotationUtils.clamp(scale * 0.8, 0.1, 5.0);
        const afterZoom = AnnotationUtils.screenToImage(centerX, centerY);
        
        offsetX -= (afterZoom.x - beforeZoom.x) * scale;
        offsetY -= (afterZoom.y - beforeZoom.y) * scale;
        
        AnnotationTool.redrawAll();
        AnnotationTool.updateZoomDisplay();
    }
};

// 导出到全局
window.AnnotationUtils = AnnotationUtils;
window.MouseHandler = MouseHandler;
window.ViewControl = ViewControl; 