#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漫画分镜自动切分工具 - 图形界面版本
提供友好的GUI界面进行漫画分镜检测和切分
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from PIL import Image, ImageTk
import cv2
import numpy as np
from panel_detector import PanelDetector


class PanelDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("漫画分镜自动切分工具")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # 变量
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="output")
        self.min_area = tk.DoubleVar(value=0.02)
        self.max_area = tk.DoubleVar(value=0.8)
        self.current_image = None
        self.preview_image = None
        self.processing = False
        self.input_files = []  # 存储多个文件路径
        self.input_mode = tk.StringVar(value="single")  # single, multiple, folder
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部控制区域
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 输入选择区域
        input_frame = ttk.LabelFrame(top_frame, text="输入选择", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 选择模式
        mode_frame = ttk.Frame(input_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(mode_frame, text="选择模式:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="单张图片", variable=self.input_mode, value="single").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="多张图片", variable=self.input_mode, value="multiple").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="整个文件夹", variable=self.input_mode, value="folder").pack(side=tk.LEFT, padx=5)
        
        # 文件选择
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X)
        ttk.Label(file_frame, text="输入路径:").pack(side=tk.LEFT, padx=(0, 10))
        self.path_entry = ttk.Entry(file_frame, textvariable=self.input_path)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_frame, text="浏览...", command=self.browse_input).pack(side=tk.LEFT)
        
        # 文件列表（多文件模式）
        self.file_listbox = tk.Listbox(input_frame, height=4)
        self.file_listbox.pack(fill=tk.X, pady=(10, 0))
        self.file_listbox.pack_forget()  # 初始隐藏
        
        # 输出目录
        output_frame = ttk.Frame(input_frame)
        output_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(output_frame, text="浏览...", command=self.browse_output).pack(side=tk.LEFT)
        
        # 参数设置区域
        params_frame = ttk.LabelFrame(top_frame, text="检测参数", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        params_grid = ttk.Frame(params_frame)
        params_grid.pack(fill=tk.X)
        
        # 第一行参数
        row1 = ttk.Frame(params_grid)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text="最小面积比例:").pack(side=tk.LEFT, padx=(0, 10))
        self.min_area_scale = ttk.Scale(row1, from_=0.001, to=0.1, variable=self.min_area, 
                                      orient=tk.HORIZONTAL, length=300)
        self.min_area_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.min_area_label = ttk.Label(row1, text=f"{self.min_area.get():.3f}", width=8)
        self.min_area_label.pack(side=tk.LEFT)
        
        # 第二行参数
        row2 = ttk.Frame(params_grid)
        row2.pack(fill=tk.X)
        
        ttk.Label(row2, text="最大面积比例:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_area_scale = ttk.Scale(row2, from_=0.1, to=1.0, variable=self.max_area,
                                      orient=tk.HORIZONTAL, length=300)
        self.max_area_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.max_area_label = ttk.Label(row2, text=f"{self.max_area.get():.3f}", width=8)
        self.max_area_label.pack(side=tk.LEFT)
        
        # 绑定滑块事件
        self.min_area_scale.configure(command=lambda v: self.min_area_label.config(text=f"{float(v):.3f}"))
        self.max_area_scale.configure(command=lambda v: self.max_area_label.config(text=f"{float(v):.3f}"))
        
        # 按钮区域
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="预览图片", command=self.preview_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="打开输出目录", command=self.open_output_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭程序", command=self.close_app).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(top_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # 主内容区域（预览和日志）
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建水平分割的PanedWindow
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：图片预览
        preview_container = ttk.Frame(paned)
        paned.add(preview_container, weight=1)
        
        preview_label_frame = ttk.LabelFrame(preview_container, text="图片预览", padding="10")
        preview_label_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(preview_label_frame, text="请选择图片文件", anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：处理日志
        log_container = ttk.Frame(paned)
        paned.add(log_container, weight=1)
        
        log_label_frame = ttk.LabelFrame(log_container, text="处理日志", padding="10")
        log_label_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_label_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_input(self):
        """浏览输入文件/文件夹"""
        mode = self.input_mode.get()
        
        if mode == "single":
            # 单张图片选择
            filename = filedialog.askopenfilename(
                title="选择漫画图片",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("JPEG文件", "*.jpg *.jpeg"),
                    ("PNG文件", "*.png"),
                    ("WebP文件", "*.webp"),
                    ("所有文件", "*.*")
                ]
            )
            if filename:
                self.input_path.set(filename)
                self.input_files = [filename]
                self.file_listbox.pack_forget()  # 隐藏文件列表
                self.load_preview()
                
        elif mode == "multiple":
            # 多张图片选择
            filenames = filedialog.askopenfilenames(
                title="选择多张漫画图片",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("JPEG文件", "*.jpg *.jpeg"),
                    ("PNG文件", "*.png"),
                    ("WebP文件", "*.webp"),
                    ("所有文件", "*.*")
                ]
            )
            if filenames:
                self.input_files = list(filenames)
                self.input_path.set(f"已选择 {len(filenames)} 个文件")
                self.file_listbox.pack(fill=tk.X, pady=(10, 0))  # 显示文件列表
                self.file_listbox.delete(0, tk.END)
                for filename in filenames:
                    self.file_listbox.insert(tk.END, os.path.basename(filename))
                # 预览第一张图片
                if filenames:
                    self.load_preview(filenames[0])
                    
        elif mode == "folder":
            # 文件夹选择
            dirname = filedialog.askdirectory(title="选择包含漫画图片的文件夹")
            if dirname:
                # 扫描文件夹中的图片文件
                image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
                image_files = []
                
                for root, dirs, files in os.walk(dirname):
                    for file in files:
                        if os.path.splitext(file.lower())[1] in image_extensions:
                            image_files.append(os.path.join(root, file))
                
                if image_files:
                    self.input_files = image_files
                    self.input_path.set(f"已选择 {len(image_files)} 个文件")
                    self.file_listbox.pack(fill=tk.X, pady=(10, 0))  # 显示文件列表
                    self.file_listbox.delete(0, tk.END)
                    for filename in image_files[:10]:  # 只显示前10个文件名
                        self.file_listbox.insert(tk.END, os.path.basename(filename))
                    if len(image_files) > 10:
                        self.file_listbox.insert(tk.END, f"... 还有 {len(image_files) - 10} 个文件")
                    # 预览第一张图片
                    self.load_preview(image_files[0])
                else:
                    messagebox.showwarning("警告", "所选文件夹中没有找到图片文件")
            
    def browse_output(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir.set(dirname)
            
    def load_preview(self, image_path=None):
        """加载图片预览"""
        if not image_path:
            image_path = self.input_path.get()
            
        if not image_path or not os.path.exists(image_path):
            return
            
        try:
            # 使用PIL加载图片并调整大小
            image = Image.open(image_path)
            # 计算缩放比例，保持宽高比
            max_size = 400
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter格式
            self.preview_image = ImageTk.PhotoImage(image)
            self.image_label.configure(image=self.preview_image)
            self.image_label.image = self.preview_image  # 保持引用
            
            self.log(f"已加载图片: {os.path.basename(image_path)}")
            
        except Exception as e:
            self.log(f"加载图片失败: {str(e)}")
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")
            
    def preview_image(self):
        """预览当前选择的图片"""
        self.load_preview()
        
    def start_processing(self):
        """开始处理图片"""
        mode = self.input_mode.get()
        
        if mode == "single":
            if not self.input_path.get() or not os.path.exists(self.input_path.get()):
                messagebox.showerror("错误", "请先选择输入图片")
                return
            self.input_files = [self.input_path.get()]
        else:
            if not self.input_files:
                messagebox.showwarning("警告", "请先选择输入文件或文件夹")
                return
            
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待")
            return
            
        # 在新线程中处理，避免界面卡顿
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()
        
    def process_images(self):
        """处理多个图片的后台线程"""
        self.processing = True
        self.process_button.configure(state='disabled')
        self.progress.start()
        
        try:
            total_files = len(self.input_files)
            self.log(f"开始处理 {total_files} 个文件...")
            
            # 创建检测器
            detector = PanelDetector(
                min_area_ratio=self.min_area.get(),
                max_area_ratio=self.max_area.get()
            )
            
            total_panels = 0
            successful_files = 0
            panel_counter = 1  # 全局分镜计数器
            
            # 创建统一的输出目录
            unified_output_dir = self.output_dir.get()
            unified_panels_dir = os.path.join(unified_output_dir, "panels")
            os.makedirs(unified_panels_dir, exist_ok=True)
            
            for i, image_path in enumerate(self.input_files, 1):
                try:
                    self.log(f"[{i}/{total_files}] 处理: {os.path.basename(image_path)}")
                    
                    # 使用临时目录处理单个文件
                    import tempfile
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # 执行检测
                        result = detector.detect_panels(image_path, temp_dir)
                        
                        # 移动分镜图片到统一目录，并重命名
                        if result['panel_paths']:
                            base_name = os.path.splitext(os.path.basename(image_path))[0]
                            
                            for j, panel_path in enumerate(result['panel_paths']):
                                # 生成新的文件名：原文件名_分镜序号
                                new_filename = f"{base_name}_panel_{j+1:02d}.jpg"
                                new_panel_path = os.path.join(unified_panels_dir, new_filename)
                                
                                # 复制文件到统一目录
                                import shutil
                                shutil.copy2(panel_path, new_panel_path)
                                
                                # 更新全局计数器
                                panel_counter += 1
                            
                            total_panels += result['total_panels']
                            successful_files += 1
                            
                            self.log(f"  ✓ 检测到 {result['total_panels']} 个分镜")
                            
                            # 如果是第一个文件，加载调试结果预览
                            if i == 1:
                                self.load_debug_preview(result['debug_path'])
                            
                            # 保存调试结果到统一目录
                            debug_filename = f"{base_name}_debug.jpg"
                            debug_dest = os.path.join(unified_output_dir, debug_filename)
                            if os.path.exists(result['debug_path']):
                                import shutil
                                shutil.copy2(result['debug_path'], debug_dest)
                            
                            # 保存分镜数据到统一目录
                            data_filename = f"{base_name}_panels_data.json"
                            data_dest = os.path.join(unified_output_dir, data_filename)
                            if os.path.exists(result['panels_data_path']):
                                import shutil
                                shutil.copy2(result['panels_data_path'], data_dest)
                        
                except Exception as e:
                    self.log(f"  ✗ 处理失败: {str(e)}")
                    continue
            
            # 输出总结结果
            self.log(f"\n处理完成！")
            self.log(f"成功处理: {successful_files}/{total_files} 个文件")
            self.log(f"总计检测到: {total_panels} 个分镜")
            self.log(f"所有分镜图片保存在: {unified_panels_dir}")
            self.log(f"调试文件和数据文件保存在: {unified_output_dir}")
            
            # 询问是否打开输出目录
            if successful_files > 0 and messagebox.askyesno("完成", f"处理完成！\n成功处理 {successful_files} 个文件\n总计 {total_panels} 个分镜\n是否打开输出目录？"):
                self.open_output_dir()
                
        except Exception as e:
            self.log(f"处理失败: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")
            
        finally:
            self.processing = False
            self.process_button.configure(state='normal')
            self.progress.stop()
            
    def load_debug_preview(self, debug_path):
        """加载调试结果预览"""
        try:
            if os.path.exists(debug_path):
                image = Image.open(debug_path)
                # 计算缩放比例，保持宽高比
                max_size = 400
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                self.preview_image = ImageTk.PhotoImage(image)
                self.image_label.configure(image=self.preview_image)
                self.image_label.image = self.preview_image
                
                self.log("已加载调试结果预览")
        except Exception as e:
            self.log(f"加载调试预览失败: {str(e)}")
            
    def open_output_dir(self):
        """打开输出目录"""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            os.startfile(output_path)  # Windows
        else:
            messagebox.showwarning("警告", "输出目录不存在")
            
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def close_app(self):
        """关闭应用程序"""
        if self.processing:
            if messagebox.askyesno("确认", "正在处理中，确定要关闭程序吗？"):
                self.root.quit()
        else:
            self.root.quit()
        
    def log(self, message):
        """添加日志信息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()


def main():
    """主函数"""
    root = tk.Tk()
    app = PanelDetectorGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        # root.iconbitmap("icon.ico")  # 可以添加图标文件
        pass
    except:
        pass
        
    # 居中显示窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
