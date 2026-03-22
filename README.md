# 漫画分镜自动切分工具 (Panel Extraction)

基于 Python 和 OpenCV 的漫画分镜自动识别与切分系统，专为 Motion Comic 项目开发。

## 功能特性

- 🔍 **智能分镜检测**：使用自适应二值化和形态学操作精确识别漫画边框
- 📐 **面积过滤算法**：自动过滤噪点、文字气泡和整页外框（2%-80%面积范围）
- 📖 **日漫排序**：实现从上到下、同行从右到左的日式漫画阅读顺序
- 📁 **多格式输出**：生成独立面板图片、JSON数据文件和可视化调试图
- ⚙️ **参数可调**：支持命令行自定义面积过滤阈值
- 🎨 **WebP支持**：完整支持WebP格式输入和输出
- 📦 **批量处理**：支持单张图片、多张图片、整个文件夹处理
- 🖱️ **图形界面**：友好的GUI界面，一键启动

## 环境要求

- Python 3.7+
- Windows/Linux/macOS

## 快速开始

### 🚀 一键启动（推荐）

**Windows用户：**
```powershell
# 双击运行或在命令行执行
start.bat
```

**Linux/macOS用户：**
```bash
# 给脚本执行权限并运行
chmod +x start_gui.sh
./start_gui.sh
```

### 手动设置

#### 1. 环境搭建

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 启动应用

```powershell
# 启动GUI界面
python panel_detector_gui.py
```

## 使用方法

### 图形界面版本（推荐）

启动后，你可以选择三种输入模式：

#### 🎯 输入模式
- **单张图片**：选择单个漫画图片文件
- **多张图片**：批量选择多个图片文件  
- **整个文件夹**：自动扫描文件夹中的所有图片

#### 🎨 支持格式
- **输入格式**：`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`
- **输出格式**：自动匹配输入格式（WebP输入输出WebP，其他输出JPG）

#### 📋 操作流程
1. 选择输入模式（单张/多张/文件夹）
2. 点击"浏览..."选择图片或文件夹
3. 调整检测参数（可选）
4. 点击"开始处理"
5. 查看处理结果和日志

### 命令行版本

```powershell
# 处理单张图片
python panel_detector.py --input manga_page.jpg

# 自定义参数
python panel_detector.py --input manga_page.jpg --min-area 0.01 --max-area 0.9
```

## 输出文件说明

### 单文件处理
```
output/
├── panels/
│   ├── panel_01.jpg    # 第1个分镜（格式匹配输入）
│   ├── panel_02.jpg    # 第2个分镜
│   └── ...
├── panels_data.json    # 分镜坐标数据
└── debug_result.jpg    # 调试可视化图
```

### 批量处理（多张图片/文件夹）
```
output/
├── panels/                    # 统一的分镜图片目录
│   ├── 文件名1_panel_01.jpg   # 第1个文件的第1个分镜
│   ├── 文件名1_panel_02.jpg   # 第1个文件的第2个分镜
│   ├── 文件名2_panel_01.jpg   # 第2个文件的第1个分镜
│   └── ...
├── 文件名1_debug.jpg         # 第1个文件的调试图
├── 文件名1_panels_data.json  # 第1个文件的分镜数据
├── 文件名2_debug.jpg         # 第2个文件的调试图
├── 文件名2_panels_data.json  # 第2个文件的分镜数据
└── ...
```

### panels_data.json 格式
```json
[
  {
    "panel_id": 1,
    "x": 100,
    "y": 50,
    "width": 300,
    "height": 200
  }
]
```

## 依赖库

```
opencv-python  # 图像处理核心库
numpy          # 数值计算支持  
Pillow         # 图像处理和显示（支持WebP）
```

## 项目结构

```
mangaAI/
├── panel_detector.py      # 核心检测脚本（命令行版本）
├── panel_detector_gui.py  # GUI界面版本
├── start.bat              # Windows一键启动脚本
├── start_gui.sh           # Linux/macOS启动脚本
├── requirements.txt        # 依赖列表
├── README.md              # 项目说明
└── venv/                  # 虚拟环境目录（自动创建）
```

## 技术原理

### 图像预处理
1. **灰度化**：将彩色图像转换为灰度图
2. **自适应二值化**：使用高斯自适应阈值处理
3. **形态学操作**：闭运算和膨胀连接断裂边框

### 轮廓检测与过滤
- 使用 `cv2.findContours` 检测闭合区域
- 面积过滤：保留占全图面积 2%-80% 的轮廓
- 形状过滤：排除过于细长或不规则的区域

### 日漫排序算法
1. 计算每个面板的中心点坐标
2. 按Y坐标分组确定行
3. 每行内按X坐标从右到左排序
4. 所有行按Y坐标从上到下排序

## 常见问题

### Q: 支持哪些图片格式？
A: 支持 `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp` 格式

### Q: 检测不到某些分镜？
A: 尝试降低最小面积比例参数，或检查图片分辨率是否过低

### Q: 检测到太多噪点？
A: 提高最小面积比例参数，或确保输入图片质量良好

### Q: 排序顺序不正确？
A: 算法针对日漫设计，如需其他排序方式可修改排序算法

### Q: WebP格式如何处理？
A: 系统自动识别WebP格式，输入WebP会输出WebP格式的分镜

### Q: 启动脚本无法运行？
A: 确保已安装Python 3.7+，并检查网络连接以安装依赖

## 许可证

本项目专为 Motion Comic 项目开发，仅供内部使用。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进算法性能和功能。
