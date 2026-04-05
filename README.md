# 🧹 AI Photo Dedup - AI 智能清理重复照片

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>

一个基于 **感知哈希（Perceptual Hashing）** 和 **深度特征提取** 的智能重复照片清理工具。不再依赖文件名或大小，而是真正"看"照片内容来判断重复。

## ✨ 特性

- 🔍 **感知哈希检测** — 使用 pHash / dHash / aHash 多算法交叉验证
- 🧠 **AI 深度特征** — 可选使用 CNN 模型提取图像深度特征进行比对
- 📊 **相似度评分** — 输出每对照片的相似度分数，精准控制清理阈值
- 🗂️ **智能分组** — 自动将相似照片分组，每组保留最佳的一张
- 🖼️ **元数据感知** — 优先保留分辨率最高、文件最大的版本
- 📋 **详细报告** — 生成 HTML 格式的清理报告，包含缩略图对比
- ⚡ **多线程扫描** — 大量照片也能快速处理
- 🔄 **安全模式** — 默认只移动到回收文件夹，不直接删除

## 🚀 快速开始

### 安装依赖

```bash
git clone https://github.com/seettm/ai-photo-dedup.git
cd ai-photo-dedup
pip install -r requirements.txt
```

### 基础用法

```bash
# 扫描目录，查找重复照片
python dedup.py scan /path/to/photos

# 扫描并自动清理（移到回收文件夹）
python dedup.py clean /path/to/photos --threshold 0.9

# 使用 AI 模式（更精准，但更慢）
python dedup.py clean /path/to/photos --mode ai --threshold 0.85

# 生成 HTML 报告
python dedup.py report /path/to/photos --output report.html
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `scan/clean/report` | 操作模式 | - |
| `--threshold` | 相似度阈值 (0-1) | 0.9 |
| `--mode` | `hash` 或 `ai` | `hash` |
| `--hash-type` | `phash`, `dhash`, `ahash`, `all` | `all` |
| `--workers` | 线程数 | 4 |
| `--output` | 报告输出路径 | `./dedup_report.html` |
| `--dry-run` | 只扫描不执行 | `False` |
| `--keep-best` | 保留策略 (`quality`/`size`/`first`) | `quality` |

## 🏗️ 项目结构

```
ai-photo-dedup/
├── dedup.py           # 主入口 CLI
├── scanner.py         # 文件扫描与哈希计算
├── comparator.py      # 照片比较引擎
├── cleaner.py         # 清理执行器
├── reporter.py        # HTML 报告生成
├── models.py          # AI 特征提取模型
├── utils.py           # 工具函数
├── requirements.txt   # 依赖
├── tests/             # 测试
│   ├── test_scanner.py
│   └── test_comparator.py
└── README.md
```

## 📄 License

MIT License © 2026 seettm
