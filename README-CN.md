# PDFConcat

**[English](README.md)** | **[中文](README-CN.md)**

一个轻量级的 Python 工具，将 PDF 页面排列为有序的缩略图网格。适用于创建文档预览、校对排版或生成紧凑的文档摘要。

## 功能特性

- **拖拽式 GUI**：现代化界面，支持拖放 PDF 文件
- **智能布局**：自动计算最佳页面尺寸，减少空白区域
- **灵活配置**：可自定义网格行列数
- **快速预设**：提供常用布局（3×2、4×3、5×3、单行、单列、自动布局）
- **质量控制**：可调节 DPI、间距和边距
- **命令行支持**：CLI 接口，适合批量处理
- **独立可执行文件**：Windows .exe 文件，无需安装

## 快速开始

### Windows 用户

从 [Releases](https://github.com/Explorer-cc/PDFConcat/releases) 下载 `PDFConcat.exe`，双击运行即可。

### 开发者

**前提条件：** Python 3.12+，[uv](https://docs.astral.sh/uv/) 包管理器

```bash
# 克隆仓库
git clone https://github.com/Explorer-cc/PDFConcat.git
cd PDFConcat

# 安装依赖
uv sync

# 运行 GUI
uv run src/gui.py

# 运行 CLI
uv run python concat_pdf.py input.pdf output.pdf -n 3 -m 2
```

## 构建可执行文件

```bash
# 安装 PyInstaller 开发依赖
uv add pyinstaller --dev

# 构建（输出到 dist/PDFConcat.exe）
uv run python build.py
```

## 使用说明

### GUI

1. **选择 PDF** — 点击拖放区域或拖入 PDF 文件
2. **配置网格** — 设置列数、行数、DPI、间距和边距
3. **快速预设** — 选择常用布局或自动计算行数
4. **处理** — 点击 "Start Processing"，完成后点击 "Open Output File" 查看

### CLI

```bash
uv run python concat_pdf.py input.pdf output.pdf -n 4 -m 3 --dpi 200 --gap 2 --padding 5
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-n` | 必填 | 网格列数 |
| `-m` | 自动 | 网格行数（省略则自动计算） |
| `--page-size` | auto | 输出页面尺寸：auto、A4、A3、A5、Letter |
| `--orientation` | landscape | 页面方向：portrait 或 landscape |
| `--dpi` | 150 | 缩略图 DPI |
| `--gap` | 3 | 缩略图间距（磅） |
| `--padding` | 10 | 页面边距（磅） |

## 依赖

- **PyMuPDF** — PDF 处理与渲染
- **Pillow** — 图像处理
- **NumPy** — 数值运算
- **tkinterdnd2** — tkinter GUI 拖放支持

## 许可证

本项目为开源项目，详见 LICENSE 文件。
