#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漫画分镜自动切分工具 (Panel Extraction)
用于 Motion Comic 项目的图像处理核心
"""

import cv2
import numpy as np
import argparse
import os
import json
from typing import List, Tuple, Dict


class PanelDetector:
    def __init__(self, min_area_ratio=0.02, max_area_ratio=0.8):
        """
        初始化面板检测器
        
        Args:
            min_area_ratio: 最小面积比例 (默认2%)
            max_area_ratio: 最大面积比例 (默认80%)
        """
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理：灰度化、自适应二值化、形态学操作
        
        Args:
            image: 输入图像
            
        Returns:
            处理后的二值图像
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 自适应二值化
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # 形态学操作：连接断裂的边框
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # 再次膨胀确保边框连接
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary = cv2.dilate(binary, kernel, iterations=1)
        
        return binary
    
    def filter_contours(self, contours: List, image_area: int) -> List[Tuple[int, int, int, int]]:
        """
        过滤轮廓：基于面积和形状特征
        
        Args:
            contours: 轮廓列表
            image_area: 图像总面积
            
        Returns:
            过滤后的边界框列表 [(x, y, w, h), ...]
        """
        valid_boxes = []
        min_area = image_area * self.min_area_ratio
        max_area = image_area * self.max_area_ratio
        
        for contour in contours:
            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # 面积过滤
            if area < min_area or area > max_area:
                continue
                
            # 宽高比过滤（避免过于细长的噪点）
            aspect_ratio = w / h
            if aspect_ratio < 0.1 or aspect_ratio > 10:
                continue
                
            # 矩形度过滤（确保接近矩形）
            rect_area = w * h
            if area / rect_area < 0.5:  # 轮廓面积占矩形面积的比例
                continue
                
            valid_boxes.append((x, y, w, h))
            
        return valid_boxes
    
    def sort_panels_japanese_style(self, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """
        日式漫画阅读顺序排序：从上到下，同一行内从右到左
        
        Args:
            boxes: 边界框列表 [(x, y, w, h), ...]
            
        Returns:
            排序后的边界框列表
        """
        if not boxes:
            return []
            
        # 计算每个面板的中心点
        centers = [(x + w//2, y + h//2) for x, y, w, h in boxes]
        
        # 按Y坐标分组（确定行）
        rows = {}
        for i, (box, center) in enumerate(zip(boxes, centers)):
            y = center[1]
            # 找到最近的行
            row_key = None
            min_dist = float('inf')
            for existing_y in rows.keys():
                dist = abs(y - existing_y)
                if dist < min_dist and dist < 50:  # 50像素阈值认为是同一行
                    min_dist = dist
                    row_key = existing_y
            
            if row_key is None:
                row_key = y
                rows[row_key] = []
            
            rows[row_key].append((box, center, i))
        
        # 对每行按X坐标从右到左排序，然后按Y坐标从上到下排序
        sorted_boxes = []
        for row_y in sorted(rows.keys()):
            row_items = rows[row_y]
            # 按X坐标从右到左排序
            row_items.sort(key=lambda item: item[1][0], reverse=True)
            for box, center, original_idx in row_items:
                sorted_boxes.append(box)
        
        return sorted_boxes
    
    def extract_panels(self, image: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> List[np.ndarray]:
        """
        从原图中提取面板
        
        Args:
            image: 原始图像
            boxes: 边界框列表
            
        Returns:
            提取的面板图像列表
        """
        panels = []
        for x, y, w, h in boxes:
            panel = image[y:y+h, x:x+w]
            panels.append(panel)
        return panels
    
    def save_panels(self, panels: List[np.ndarray], output_dir: str = "panels", input_format: str = "jpg") -> List[str]:
        """
        保存提取的面板
        
        Args:
            panels: 面板图像列表
            output_dir: 输出目录
            input_format: 输入文件格式，用于确定输出格式
            
        Returns:
            保存的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        # 根据输入格式决定输出格式
        if input_format.lower() in ['webp']:
            output_format = 'webp'
            file_ext = '.webp'
        else:
            output_format = 'jpg'
            file_ext = '.jpg'
        
        for i, panel in enumerate(panels):
            filename = f"panel_{i+1:02d}{file_ext}"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, panel)
            saved_paths.append(filepath)
            
        return saved_paths
    
    def save_panels_data(self, boxes: List[Tuple[int, int, int, int]], output_file: str = "panels_data.json"):
        """
        保存面板数据到JSON文件
        
        Args:
            boxes: 边界框列表
            output_file: 输出文件路径
        """
        panels_data = []
        for i, (x, y, w, h) in enumerate(boxes):
            panels_data.append({
                "panel_id": i + 1,
                "x": x,
                "y": y,
                "width": w,
                "height": h
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(panels_data, f, indent=2, ensure_ascii=False)
    
    def create_debug_image(self, image: np.ndarray, boxes: List[Tuple[int, int, int, int]], 
                          output_file: str = "debug_result.jpg"):
        """
        创建调试图像，在原图上标注识别结果
        
        Args:
            image: 原始图像
            boxes: 边界框列表
            output_file: 输出文件路径
        """
        debug_image = image.copy()
        
        for i, (x, y, w, h) in enumerate(boxes):
            # 绘制彩色边框
            color = (0, 255, 0)  # 绿色
            cv2.rectangle(debug_image, (x, y), (x + w, y + h), color, 2)
            
            # 在左上角标注序号
            text = str(i + 1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            thickness = 2
            
            # 文字背景
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            cv2.rectangle(debug_image, (x, y - 30), (x + text_size[0], y), color, -1)
            
            # 文字内容
            cv2.putText(debug_image, text, (x, y - 5), font, font_scale, (0, 0, 0), thickness)
        
        cv2.imwrite(output_file, debug_image)
    
    def detect_panels(self, image_path: str, output_dir: str = "output") -> Dict:
        """
        主检测流程
        
        Args:
            image_path: 输入图像路径
            output_dir: 输出目录
            
        Returns:
            检测结果字典
        """
        # 检测输入文件格式
        input_format = os.path.splitext(image_path)[1].lower().lstrip('.')
        
        # 读取图像（支持更多格式）
        if input_format.lower() in ['webp']:
            # 对于WebP等格式，使用PIL读取然后转换为OpenCV格式
            from PIL import Image as PILImage
            pil_image = PILImage.open(image_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        else:
            # 传统格式使用OpenCV读取
            image = cv2.imread(image_path)
            
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        # 图像预处理
        binary = self.preprocess_image(image)
        
        # 轮廓检测
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 过滤轮廓
        image_area = image.shape[0] * image.shape[1]
        valid_boxes = self.filter_contours(contours, image_area)
        
        # 日式排序
        sorted_boxes = self.sort_panels_japanese_style(valid_boxes)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 提取并保存面板
        panels = self.extract_panels(image, sorted_boxes)
        panel_paths = self.save_panels(panels, os.path.join(output_dir, "panels"), input_format)
        
        # 保存数据
        panels_data_path = os.path.join(output_dir, "panels_data.json")
        self.save_panels_data(sorted_boxes, panels_data_path)
        
        # 创建调试图像
        debug_filename = f"debug_result.{input_format if input_format in ['jpg', 'png', 'webp'] else 'jpg'}"
        debug_path = os.path.join(output_dir, debug_filename)
        self.create_debug_image(image, sorted_boxes, debug_path)
        
        return {
            "total_panels": len(sorted_boxes),
            "panels": sorted_boxes,
            "panel_paths": panel_paths,
            "panels_data_path": panels_data_path,
            "debug_path": debug_path
        }


def main():
    parser = argparse.ArgumentParser(description="漫画分镜自动切分工具")
    parser.add_argument("--input", "-i", required=True, help="输入漫画图片路径")
    parser.add_argument("--output", "-o", default="output", help="输出目录 (默认: output)")
    parser.add_argument("--min-area", type=float, default=0.02, help="最小面积比例 (默认: 0.02)")
    parser.add_argument("--max-area", type=float, default=0.8, help="最大面积比例 (默认: 0.8)")
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        return
    
    try:
        # 创建检测器
        detector = PanelDetector(min_area_ratio=args.min_area, max_area_ratio=args.max_area)
        
        # 执行检测
        print(f"正在处理图像: {args.input}")
        result = detector.detect_panels(args.input, args.output)
        
        # 输出结果
        print(f"\n检测完成！")
        print(f"共检测到 {result['total_panels']} 个分镜")
        print(f"面板图片保存在: {os.path.join(args.output, 'panels')}")
        print(f"数据文件保存在: {result['panels_data_path']}")
        print(f"调试图像保存在: {result['debug_path']}")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
