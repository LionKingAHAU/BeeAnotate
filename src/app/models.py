#!/usr/bin/env python3
"""
蜂格标注工具数据模型
"""

import os
import json
import csv
import shutil
from datetime import datetime
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Configuration helpers
def get_images_dir():
    """Get images directory from Flask config"""
    return current_app.config.get('IMAGES_DIR', 'data/images')

def get_annotations_dir():
    """Get annotations directory from Flask config"""
    return current_app.config.get('ANNOTATIONS_DIR', 'data/annotations')

def get_exports_dir():
    """Get exports directory from Flask config"""
    return current_app.config.get('EXPORTS_DIR', 'data/exports')

def get_allowed_extensions():
    """Get allowed file extensions"""
    return {'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'}

# Legacy support - check for uploads directory
def get_upload_dir():
    """Get upload directory, checking both new config and legacy uploads folder"""
    images_dir = get_images_dir()
    legacy_uploads = 'data/uploads'

    # If legacy uploads directory exists and has files, use it
    if os.path.exists(legacy_uploads) and os.listdir(legacy_uploads):
        return legacy_uploads

    # Otherwise use configured images directory
    return images_dir

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in get_allowed_extensions()

def normalize_path(path):
    """规范化路径，统一使用正斜杠"""
    return path.replace('\\', '/')

def copy_existing_images():
    """复制现有的蜂巢图像到上传文件夹"""
    source_imgs_dir = 'imgs'  # Legacy source directory
    upload_dir = get_upload_dir()

    if os.path.exists(source_imgs_dir):
        logger.info("复制现有蜂巢图像...")
        copied_count = 0

        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)

        for filename in os.listdir(source_imgs_dir):
            if filename.endswith('.JPG') or filename.endswith('.jpg'):
                src_path = os.path.join(source_imgs_dir, filename)
                dst_path = os.path.join(upload_dir, filename)
                
                if not os.path.exists(dst_path):
                    try:
                        shutil.copy2(src_path, dst_path)
                        copied_count += 1
                    except Exception as e:
                        logger.error(f"复制文件失败 {filename}: {e}")
                        
        logger.info(f"复制了 {copied_count} 张蜂巢图像")
        return copied_count
    else:
        logger.warning("未找到imgs文件夹")
        return 0

def get_image_list(page=1, per_page=20):
    """获取图像列表和统计信息（支持分页）"""
    images = []
    total_annotations = 0

    upload_dir = get_upload_dir()
    annotations_dir = get_annotations_dir()

    if not os.path.exists(upload_dir):
        return images, {'total_images': 0, 'annotated_images': 0, 'total_annotations': 0}, {}

    for filename in os.listdir(upload_dir):
        if allowed_file(filename):
            # Use relative path based on actual directory
            if 'uploads' in upload_dir:
                image_path = normalize_path(os.path.join('uploads', filename))
            else:
                image_path = normalize_path(os.path.join('images', filename))
            image_id = os.path.splitext(filename)[0]

            # 检查是否有对应的标注
            annotation_path = os.path.join(annotations_dir, f"{image_id}.json")
            annotation_count = 0
            
            if os.path.exists(annotation_path):
                try:
                    with open(annotation_path, 'r', encoding='utf-8') as f:
                        annotations = json.load(f)
                        annotation_count = len(annotations)
                        total_annotations += annotation_count
                except:
                    pass
            
            images.append({
                'id': image_id,
                'path': image_path,
                'filename': filename,
                'annotation_count': annotation_count,
                'has_annotation': annotation_count > 0
            })
    
    # 按标注数量排序（已标注的在前）
    images.sort(key=lambda x: (-x['annotation_count'], x['filename']))
    
    # 计算分页信息
    total_images = len(images)
    total_pages = (total_images + per_page - 1) // per_page  # 向上取整
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # 获取当前页的图像
    paginated_images = images[start_idx:end_idx]
    
    # 统计信息
    stats = {
        'total_images': total_images,
        'annotated_images': len([img for img in images if img['has_annotation']]),
        'total_annotations': total_annotations
    }
    
    # 分页信息
    pagination = {
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_images,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'start_index': start_idx + 1,
        'end_index': min(end_idx, total_images)
    }
    
    return paginated_images, stats, pagination

def load_annotations(image_id):
    """加载指定图像的标注数据"""
    annotations_dir = get_annotations_dir()
    annotation_path = os.path.join(annotations_dir, f"{image_id}.json")
    
    if os.path.exists(annotation_path):
        try:
            with open(annotation_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"JSON解析错误: {annotation_path}")
            return []
    
    return []

def save_annotations(image_id, annotations):
    """保存标注数据"""
    annotations_dir = get_annotations_dir()

    # 确保annotations目录存在
    os.makedirs(annotations_dir, exist_ok=True)

    # 添加时间戳
    for annotation in annotations:
        annotation['timestamp'] = datetime.now().isoformat()

    # 保存为JSON
    json_path = os.path.join(annotations_dir, f"{image_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    # 保存为CSV（扩展格式包含类别）
    csv_path = os.path.join(annotations_dir, f"{image_id}.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['class', 'x', 'y', 'timestamp'])
        for annotation in annotations:
            writer.writerow([
                annotation.get('class', 'other'),
                annotation.get('x', 0),
                annotation.get('y', 0),
                annotation.get('timestamp', '')
            ])
    
    logger.info(f"标注已保存: {json_path}")
    return len(annotations)

def export_all_annotations():
    """导出所有标注数据"""
    from app.config import CELL_CLASSES  # Import here to avoid circular imports

    annotations_dir = get_annotations_dir()
    all_annotations = {}
    total_count = 0
    class_counts = {class_key: 0 for class_key in CELL_CLASSES.keys()}

    if not os.path.exists(annotations_dir):
        return None

    for filename in os.listdir(annotations_dir):
        if filename.endswith('.json'):
            image_id = os.path.splitext(filename)[0]
            annotation_path = os.path.join(annotations_dir, filename)
            
            try:
                with open(annotation_path, 'r', encoding='utf-8') as f:
                    annotations = json.load(f)
                    all_annotations[image_id] = annotations
                    total_count += len(annotations)
                    
                    # 统计各类别数量
                    for annotation in annotations:
                        class_key = annotation.get('class', 'other')
                        if class_key in class_counts:
                            class_counts[class_key] += 1
            except:
                logger.error(f"读取标注文件失败: {annotation_path}")
    
    # 创建导出数据
    export_data = {
        'dataset_info': {
            'export_time': datetime.now().isoformat(),
            'total_images': len(all_annotations),
            'total_annotations': total_count,
            'class_distribution': class_counts,
            'cell_classes': CELL_CLASSES
        },
        'annotations': all_annotations
    }
    
    # 确保导出目录存在
    exports_dir = get_exports_dir()
    os.makedirs(exports_dir, exist_ok=True)

    # 保存导出文件
    export_filename = f"bee_dataset_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    export_path = os.path.join(exports_dir, export_filename)
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"数据集已导出: {export_path}")
    return export_path

def get_annotation_file_path(image_id, file_type='csv'):
    """获取标注文件路径"""
    annotations_dir = get_annotations_dir()
    if file_type == 'csv':
        return os.path.join(annotations_dir, f"{image_id}.csv")
    elif file_type == 'json':
        return os.path.join(annotations_dir, f"{image_id}.json")
    else:
        return None