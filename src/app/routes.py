#!/usr/bin/env python3
"""
蜂格标注工具路由
"""

import os
import json
from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from app.config import *
from app.models import get_image_list, load_annotations, save_annotations, export_all_annotations, get_upload_dir, get_images_dir, allowed_file, get_annotation_file_path
from app.i18n import _, i18n
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
bp = Blueprint('main', __name__)

def get_localized_cell_classes():
    """Get cell classes with localized names"""
    from app.config import CELL_CLASSES
    localized_classes = {}
    for key, class_info in CELL_CLASSES.items():
        localized_info = class_info.copy()
        localized_info['name'] = i18n.gettext(class_info['name_key'])
        localized_info['description'] = i18n.gettext(class_info['description_key'])
        localized_classes[key] = localized_info
    return localized_classes

@bp.route('/')
def index():
    """Home page: display image list with pagination"""
    # 确保所有目录存在
    Config.init_directories()
    
    # 注释掉自动复制功能，用户手动控制图片
    # copied_count = copy_existing_images()
    copied_count = 0
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # 默认每页20张
    
    # 限制每页数量
    per_page = min(per_page, 50)  # 最多50张/页
    
    # 获取图像列表和统计信息
    images, stats, pagination = get_image_list(page=page, per_page=per_page)
    
    return render_template('index.html', 
                         images=images, 
                         stats=stats,
                         pagination=pagination,
                         per_page=per_page,
                         annotated_count=stats['annotated_images'],
                         copied_count=copied_count,
                         cell_classes=get_localized_cell_classes())

@bp.route('/annotate/<image_id>')
def annotate(image_id):
    """Annotation page"""
    # 获取图像信息（不分页，获取所有）
    images, _, _ = get_image_list(page=1, per_page=9999)
    image_info = None
    current_index = -1
    
    # 找到当前图像和其在列表中的位置
    for i, img in enumerate(images):
        if img['id'] == image_id:
            image_info = img
            current_index = i
            break
    
    if not image_info:
        flash(_('messages.image_not_found'), 'error')
        return redirect(url_for('main.index'))
    
    # 确定上一张和下一张图像
    prev_image = images[current_index - 1] if current_index > 0 else None
    next_image = images[current_index + 1] if current_index < len(images) - 1 else None
    
    # 加载现有标注
    annotations = load_annotations(image_id)
    
    # 导航信息
    navigation_info = {
        'total_images': len(images),
        'current_position': current_index + 1,
        'prev_image': prev_image,
        'next_image': next_image
    }
    
    return render_template('annotate.html',
                         image=image_info,
                         annotations=annotations,
                         cell_classes=get_localized_cell_classes(),
                         navigation=navigation_info)

@bp.route('/api/save_annotation', methods=['POST'])
def save_annotation():
    """Save annotation API"""
    try:
        data = request.get_json()
        
        if not data or 'image_id' not in data or 'annotations' not in data:
            return jsonify({'success': False, 'error': _('validation.required_field')})
        
        image_id = data['image_id']
        annotations = data['annotations']
        
        # 保存标注
        count = save_annotations(image_id, annotations)
        
        return jsonify({
            'success': True,
            'message': f'成功保存 {count} 个标注点',
            'count': count
        })
        
    except Exception as e:
        logger.error(f"保存标注失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/load_annotation/<image_id>')
def load_annotation(image_id):
    """加载标注API"""
    try:
        annotations = load_annotations(image_id)
        return jsonify({
            'success': True,
            'annotations': annotations
        })
    except Exception as e:
        logger.error(f"加载标注失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/upload', methods=['POST'])
def upload_file():
    """文件上传"""
    if 'file' not in request.files:
        flash('没有选择文件', 'error')
        return redirect(url_for('main.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件', 'error')
        return redirect(url_for('main.index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_dir = get_upload_dir()
        file_path = os.path.join(upload_dir, filename)
        
        try:
            file.save(file_path)
            flash(f'文件 {filename} 上传成功', 'success')
        except Exception as e:
            flash(f'文件上传失败: {e}', 'error')
    else:
        flash('文件格式不支持', 'error')
    
    return redirect(url_for('main.index'))

@bp.route('/download/<image_id>/<file_type>')
def download_annotation(image_id, file_type):
    """下载标注文件"""
    file_path = get_annotation_file_path(image_id, file_type)
    
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('标注文件不存在', 'error')
        return redirect(url_for('main.index'))

@bp.route('/export')
def export_dataset():
    """导出整个数据集"""
    try:
        export_path = export_all_annotations()
        
        if export_path and os.path.exists(export_path):
            return send_file(export_path, as_attachment=True)
        else:
            flash('没有可导出的标注数据', 'error')
            return redirect(url_for('main.index'))
            
    except Exception as e:
        flash(f'导出失败: {e}', 'error')
        return redirect(url_for('main.index'))

@bp.route('/api/stats')
def get_stats():
    """获取统计信息API"""
    try:
        _, stats, _ = get_image_list(page=1, per_page=9999)
        
        # 统计各类别数量
        from app.config import CELL_CLASSES
        from app.models import get_annotations_dir
        class_counts = {class_key: 0 for class_key in CELL_CLASSES.keys()}

        annotations_dir = get_annotations_dir()
        if os.path.exists(annotations_dir):
            for filename in os.listdir(annotations_dir):
                if filename.endswith('.json'):
                    annotation_path = os.path.join(annotations_dir, filename)
                    try:
                        with open(annotation_path, 'r', encoding='utf-8') as f:
                            annotations = json.load(f)
                            for annotation in annotations:
                                class_key = annotation.get('class', 'other')
                                if class_key in class_counts:
                                    class_counts[class_key] += 1
                    except:
                        pass
        
        stats['class_distribution'] = class_counts
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/delete_annotation/<image_id>', methods=['POST'])
def delete_annotation(image_id):
    """删除标注"""
    try:
        json_path = os.path.join(ANNOTATIONS_DIR, f"{image_id}.json")
        csv_path = os.path.join(ANNOTATIONS_DIR, f"{image_id}.csv")
        
        deleted_files = []
        if os.path.exists(json_path):
            os.remove(json_path)
            deleted_files.append('JSON')
        
        if os.path.exists(csv_path):
            os.remove(csv_path)
            deleted_files.append('CSV')
        
        if deleted_files:
            flash(f'已删除标注文件 ({", ".join(deleted_files)})', 'success')
        else:
            flash('没有找到标注文件', 'warning')
            
    except Exception as e:
        flash(f'删除失败: {e}', 'error')
    
    return redirect(url_for('main.index'))

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    upload_dir = get_upload_dir()
    abs_upload_dir = os.path.abspath(upload_dir)
    return send_from_directory(abs_upload_dir, filename)

@bp.route('/images/<filename>')
def image_file(filename):
    """Serve images from images directory"""
    images_dir = get_images_dir()
    abs_images_dir = os.path.abspath(images_dir)
    return send_from_directory(abs_images_dir, filename)

@bp.route('/set_language/<language>')
def set_language(language):
    """Set language preference"""
    from flask import session
    from config import Config

    # 验证语言是否支持
    if language in Config.SUPPORTED_LANGUAGES:
        session['language'] = language
        i18n.set_language(language)
        flash(_('messages.language_changed'), 'success')
    else:
        flash(_('messages.language_not_supported'), 'error')

    # 返回到之前的页面
    return redirect(request.referrer or url_for('main.index'))