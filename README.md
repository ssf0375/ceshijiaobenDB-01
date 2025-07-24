# 浏览器自动化测试脚本项目

一个集成文件管理、UI自动化、系统命令调用、网页操作和图像识别功能的Python项目。

## 功能特点

- **浏览器自动化**: 基于Playwright实现Chrome浏览器自动化操作
- **图像识别**: 集成OpenCV和PyTorch进行图像匹配和检测
- **OCR文字识别**: 使用Tesseract实现图像文字提取
- **文件管理**: 提供文件操作、目录遍历等功能
- **GUI界面**: 基于PyQt5的图形用户界面
- **系统命令**: 支持系统命令调用和执行

## 环境要求

- Python 3.11+
- Windows/Linux/macOS
- Chrome浏览器（用于自动化测试）

## 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/ssf0375/ceshijiaobenDB-01.git
cd ceshijiaobenDB-01
```

### 2. 创建虚拟环境
```bash
# 使用uv（推荐）
uv venv
.\.venv\Scripts\activate  # Windows

# 或使用venv
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
# 使用uv
uv pip install -r requirements.txt
uv run playwright install

# 或使用pip
pip install -r requirements.txt
playwright install
```

## 使用说明

### 启动GUI界面
```bash
python main.py
```

### 示例1按钮功能说明

**核心功能**：
- 自动执行预设的网页操作流程
- 支持多Chrome实例批量操作
- 集成异常处理与状态反馈机制

**使用方法**：
1. 确保已正确配置Chrome实例（可自动检测已打开的Chrome）
2. 点击GUI界面中的"示例1"按钮启动任务
3. 任务执行期间避免用户输入干扰
4. 查看`logs/app.log`获取详细执行记录

**注意事项**：
- 执行期间请勿手动操作浏览器窗口
- 建议在稳定的网络环境下运行
- 任务完成后可通过截图查看执行结果
- 支持断点续传，异常中断后可重新执行

### 命令行使用
```bash
# 运行测试
pytest tests/

# 运行示例
python examples/combined_demo.py

# 查看帮助
python main.py --help
```

## 项目结构

```
ceshijiaobenDB-01/
├── src/                    # 核心源码
│   ├── common/            # 通用工具
│   ├── config/            # 配置管理
│   ├── file_management/   # 文件操作
│   ├── gui/               # GUI界面
│   ├── image_recognition/ # 图像识别
│   ├── ocr/              # OCR功能
│   ├── playwright_utils/  # Playwright工具
│   ├── scripts/           # 自动化脚本
│   └── ui_automation/     # UI自动化
├── tests/                 # 测试套件
├── examples/              # 使用示例
├── logs/                  # 日志文件
├── screenshots/           # 截图目录
├── requirements.txt       # 依赖列表
├── pyproject.toml        # 项目配置
└── README.md             # 项目说明
```

## 配置说明

### Chrome配置
在`src/config/app_config.py`中配置Chrome相关参数：
- Chrome调试端口：默认9222
- 用户数据目录：Chrome_UserData/
- 截图保存目录：screenshots/

### 日志配置
日志文件保存在`logs/`目录：
- 应用日志：`app.log`
- 错误日志：`error.log`
- 调试日志：`debug.log`

## API文档

### 主要模块

#### 1. Chrome自动化 (`src/scripts/chrome_automation.py`)
提供Chrome浏览器自动化操作功能：
- 启动/连接Chrome实例
- 执行网页操作
- 截图保存

#### 2. 图像识别 (`src/image_recognition/`)
- `image_matcher.py`: 图像匹配功能
- `pytorch_detector.py`: PyTorch目标检测

#### 3. OCR识别 (`src/ocr/ocr_recognizer.py`)
- 图像文字提取
- 多语言支持

## 测试指南

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行特定测试
```bash
pytest tests/test_chrome_automation.py -v
pytest tests/test_file_operations.py -v
```

### 覆盖率测试
```bash
pytest --cov=src tests/
```

## 故障排除

### 常见问题

1. **Chrome启动失败**
   - 检查Chrome是否已安装
   - 确认Chrome版本兼容性
   - 检查端口是否被占用

2. **Playwright安装失败**
   - 运行`playwright install`重新安装
   - 检查网络连接
   - 使用管理员权限运行

3. **OCR识别失败**
   - 确认Tesseract已安装
   - 检查图像质量
   - 调整识别参数

### 日志分析
查看`logs/app.log`获取详细错误信息和调试信息。

## 贡献指南

1. Fork本项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 联系方式

如有问题或建议，请通过GitHub Issues提交反馈。