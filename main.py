#!/usr/bin/env python3
"""
主程序入口
浏览器自动化测试脚本项目的主启动文件
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.common.logging_config import setup_logging


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()