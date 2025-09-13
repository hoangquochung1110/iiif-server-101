#!/usr/bin/env python3
"""
Script tự động tạo metadata.csv từ các file ảnh trong thư mục masters/
Tạo object_id thông minh dựa trên tên file và các quy tắc đặt tên
"""

import os
import csv
import hashlib
from pathlib import Path
from PIL import Image
import re

def generate_object_id(image_filename):
    """
    Tạo object_id thông minh từ tên file ảnh
    
    Quy tắc:
    1. Loại bỏ extension (.jpg, .png, etc.)
    2. Thay thế khoảng trắng và ký tự đặc biệt bằng underscore
    3. Chuyển về lowercase
    4. Thêm prefix dựa trên pattern nhận diện
    5. Nếu có số ở cuối, coi như là page number của cùng 1 object
    """
    # Loại bỏ extension
    name_without_ext = Path(image_filename).stem
    
    # Chuẩn hóa tên
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name_without_ext)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_').lower()
    
    # Phát hiện pattern và tạo object_id thông minh
    patterns = {
        r'harvard|university': 'university',
        r'map|atlas|geography': 'map',
        r'manuscript|ms|book': 'manuscript',
        r'painting|art|artwork': 'artwork',
        r'photo|photograph': 'photo',
        r'document|doc|paper': 'document'
    }
    
    prefix = 'item'  # default prefix
    for pattern, category in patterns.items():
        if re.search(pattern, clean_name, re.IGNORECASE):
            prefix = category
            break
    
    # Xử lý số ở cuối (có thể là page number)
    match = re.search(r'(.+?)_?(\d+)$', clean_name)
    if match:
        base_name = match.group(1)
        page_num = match.group(2)
        # Nếu số nhỏ hơn 100, coi như page number của cùng 1 object
        if int(page_num) < 100:
            object_id = f"{prefix}_{base_name}"
        else:
            object_id = f"{prefix}_{clean_name}"
    else:
        object_id = f"{prefix}_{clean_name}"
    
    return object_id

def generate_image_id(image_filename):
    """
    Tạo image_id từ tên file (loại bỏ extension)
    """
    return Path(image_filename).stem

def generate_label(image_filename, object_id):
    """
    Tạo label mô tả từ tên file và object_id
    """
    # Chuyển đổi tên file thành label dễ đọc
    name_without_ext = Path(image_filename).stem
    
    # Thay thế underscore và dash bằng space
    label = re.sub(r'[_-]', ' ', name_without_ext)
    
    # Capitalize từng từ
    label = ' '.join(word.capitalize() for word in label.split())
    
    return label

def get_image_dimensions(image_path):
    """
    Lấy kích thước ảnh (width, height)
    """
    try:
        with Image.open(image_path) as img:
            return img.size  # (width, height)
    except Exception as e:
        print(f"Không thể đọc kích thước ảnh {image_path}: {e}")
        return (0, 0)

def generate_metadata_csv(masters_dir="data/masters", output_file="data/metadata.csv"):
    """
    Tạo file metadata.csv từ các ảnh trong thư mục masters
    """
    masters_path = Path(masters_dir)
    
    if not masters_path.exists():
        print(f"Thư mục {masters_dir} không tồn tại!")
        return
    
    # Tìm tất cả file ảnh
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp'}
    image_files = []
    
    for file_path in masters_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    
    if not image_files:
        print(f"Không tìm thấy file ảnh nào trong {masters_dir}!")
        return
    
    # Sắp xếp file theo tên
    image_files.sort(key=lambda x: x.name)
    
    # Tạo metadata
    metadata_rows = []
    object_groups = {}  # Nhóm các ảnh theo object_id
    
    for image_file in image_files:
        image_filename = image_file.name
        object_id = generate_object_id(image_filename)
        image_id = generate_image_id(image_filename)
        label = generate_label(image_filename, object_id)
        width, height = get_image_dimensions(image_file)
        
        # Nhóm theo object_id
        if object_id not in object_groups:
            object_groups[object_id] = []
        
        object_groups[object_id].append({
            'object_id': object_id,
            'image_id': image_id,
            'label': label,
            'width': width,
            'height': height,
            'filename': image_filename
        })
    
    # Tạo rows cho CSV
    for object_id, images in object_groups.items():
        for i, image_data in enumerate(images):
            # Nếu có nhiều ảnh trong 1 object, thêm page number vào label
            if len(images) > 1:
                page_label = f"{image_data['label']} (Page {i+1})"
            else:
                page_label = image_data['label']
            
            metadata_rows.append({
                'object_id': object_id,
                'image_id': image_data['image_id'],
                'label': page_label,
                'width': image_data['width'],
                'height': image_data['height']
            })
    
    # Ghi file CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['object_id', 'image_id', 'label', 'width', 'height']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in metadata_rows:
            writer.writerow(row)
    
    print(f"Đã tạo {output_file} với {len(metadata_rows)} dòng dữ liệu")
    print(f"Tìm thấy {len(object_groups)} object(s):")
    for object_id, images in object_groups.items():
        print(f"  - {object_id}: {len(images)} ảnh")
    
    return output_path

if __name__ == "__main__":
    # Chạy script
    generate_metadata_csv()