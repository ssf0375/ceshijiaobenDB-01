import os
import sys
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QGroupBox, QGridLayout, QMessageBox, QFileDialog,
                            QProgressBar, QTabWidget, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.scripts.browser_automation_task import BrowserAutomationTask
from src.common.logging_config import setup_logging

# 设置日志
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.browser_task = None
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('浏览器自动化测试工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 添加主控制标签页
        self.create_control_tab()
        
        # 添加日志标签页
        self.create_log_tab()
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
                background-color: #0078d4;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
    def create_control_tab(self):
        """创建控制标签页"""
        control_tab = QWidget()
        layout = QVBoxLayout()
        control_tab.setLayout(layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧控制面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧状态面板
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.tab_widget.addTab(control_tab, "主控制")
        
    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 窗口管理组
        window_group = QGroupBox("窗口管理")
        window_layout = QVBoxLayout()
        
        # 刷新Chrome实例按钮
        self.refresh_btn = QPushButton("刷新Chrome实例")
        self.refresh_btn.clicked.connect(self.refresh_chrome_instances)
        window_layout.addWidget(self.refresh_btn)
        
        # Chrome实例列表
        self.chrome_list_label = QLabel("检测到的Chrome实例:")
        window_layout.addWidget(self.chrome_list_label)
        
        self.chrome_instances_text = QTextEdit()
        self.chrome_instances_text.setMaximumHeight(100)
        self.chrome_instances_text.setReadOnly(True)
        window_layout.addWidget(self.chrome_instances_text)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        # 脚本任务组
        script_group = QGroupBox("脚本任务")
        script_layout = QVBoxLayout()
        
        # 示例1按钮 - 浏览器自动化任务
        self.script1_btn = QPushButton("示例1")
        self.script1_btn.setToolTip("浏览器自动化任务：自动执行预设的网页操作流程")
        self.script1_btn.clicked.connect(self.run_script_1)
        script_layout.addWidget(self.script1_btn)
        
        # 示例2按钮
        self.script2_btn = QPushButton("示例2")
        self.script2_btn.clicked.connect(self.run_script_2)
        script_layout.addWidget(self.script2_btn)
        
        # 示例3按钮
        self.script3_btn = QPushButton("示例3")
        self.script3_btn.clicked.connect(self.run_script_3)
        script_layout.addWidget(self.script3_btn)
        
        script_group.setLayout(script_layout)
        layout.addWidget(script_group)
        
        # 添加弹簧
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 状态显示
        status_group = QGroupBox("执行状态")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 详细日志
        log_group = QGroupBox("详细日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        return panel
        
    def create_log_tab(self):
        """创建日志标签页"""
        log_tab = QWidget()
        layout = QVBoxLayout()
        log_tab.setLayout(layout)
        
        self.full_log_text = QTextEdit()
        self.full_log_text.setReadOnly(True)
        self.full_log_text.setFont(QFont('Consolas', 10))
        layout.addWidget(self.full_log_text)
        
        # 添加清除日志按钮
        clear_btn = QPushButton("清除日志")
        clear_btn.clicked.connect(self.clear_logs)
        layout.addWidget(clear_btn)
        
        self.tab_widget.addTab(log_tab, "完整日志")
        
    def load_config(self):
        """加载配置"""
        try:
            config_path = os.path.join(project_root, 'config', 'app_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
                
            # 初始化日志
            self.log_message("配置加载完成")
            
        except Exception as e:
            self.log_message(f"配置加载失败: {str(e)}", level="error")
            self.config = {}
            
    def log_message(self, message, level="info"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
        
        # 添加到状态文本框
        self.status_text.append(formatted_message)
        
        # 添加到完整日志
        self.full_log_text.append(formatted_message)
        
        # 记录到文件
        logger.log(getattr(logging, level.upper()), message)
        
    def clear_logs(self):
        """清除日志"""
        self.status_text.clear()
        self.full_log_text.clear()
        self.log_message("日志已清除")
        
    def refresh_chrome_instances(self):
        """刷新Chrome实例列表"""
        try:
            self.log_message("正在刷新Chrome实例...")
            
            # 这里应该调用实际的Chrome检测逻辑
            chrome_instances = ["实例1: localhost:9222", "实例2: localhost:9223"]
            
            self.chrome_instances_text.clear()
            if chrome_instances:
                self.chrome_instances_text.setPlainText("\n".join(chrome_instances))
                self.log_message(f"检测到 {len(chrome_instances)} 个Chrome实例")
            else:
                self.chrome_instances_text.setPlainText("未检测到Chrome实例")
                self.log_message("未检测到Chrome实例")
                
        except Exception as e:
            self.log_message(f"刷新Chrome实例失败: {str(e)}", level="error")
            
    def run_script_1(self):
        """
        执行浏览器自动化任务示例1
        
        功能说明:
        - 自动执行预设的网页操作流程
        - 支持多Chrome实例批量操作
        - 集成异常处理与状态反馈机制
        
        使用流程:
        1. 自动检测可用的Chrome实例
        2. 建立浏览器连接
        3. 执行预设的自动化任务
        4. 保存操作结果和截图
        5. 清理资源并更新状态
        
        参数:
            无
            
        返回:
            无
            
        异常:
            所有异常都会被捕获并通过消息框和日志反馈
            
        示例:
            点击GUI界面中的"示例1"按钮即可启动此任务
        """
        try:
            self.log_message("开始执行示例1任务...")
            
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 创建浏览器自动化任务
            self.browser_task = BrowserAutomationTask()
            
            # 连接信号
            self.browser_task.progress_updated.connect(self.update_progress)
            self.browser_task.log_message.connect(self.log_message)
            self.browser_task.task_finished.connect(self.on_task_finished)
            
            # 启动任务
            self.browser_task.start()
            
            # 更新按钮状态
            self.script1_btn.setEnabled(False)
            
            self.log_message("示例1任务已启动")
            
        except Exception as e:
            error_msg = f"启动示例1任务失败: {str(e)}"
            self.log_message(error_msg, level="error")
            QMessageBox.critical(self, "错误", error_msg)
            self.progress_bar.setVisible(False)
            self.script1_btn.setEnabled(True)
            
    def run_script_2(self):
        """执行示例2任务"""
        self.log_message("示例2任务未实现")
        QMessageBox.information(self, "提示", "示例2任务功能开发中...")
        
    def run_script_3(self):
        """执行示例3任务"""
        self.log_message("示例3任务未实现")
        QMessageBox.information(self, "提示", "示例3任务功能开发中...")
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def on_task_finished(self, success, message):
        """任务完成回调"""
        self.progress_bar.setVisible(False)
        self.script1_btn.setEnabled(True)
        
        if success:
            self.log_message(f"任务完成: {message}")
            QMessageBox.information(self, "成功", f"任务完成！\n{message}")
        else:
            self.log_message(f"任务失败: {message}", level="error")
            QMessageBox.warning(self, "失败", f"任务执行失败！\n{message}")


if __name__ == '__main__':
    import sys
    
    # 设置日志
    setup_logging()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())