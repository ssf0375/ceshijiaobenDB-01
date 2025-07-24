import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PyQt5.QtCore import QThread, pyqtSignal

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.scripts.chrome_automation import ChromeAutomation
from src.config.app_config import AppConfig

logger = logging.getLogger(__name__)


class BrowserAutomationTask(QThread):
    """浏览器自动化任务类"""
    
    # 信号定义
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    task_finished = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.config = AppConfig()
        self.chrome_automation = None
        self.is_running = False
        self.task_results = []
        
    def run(self):
        """执行浏览器自动化任务"""
        try:
            self.is_running = True
            self.log_message.emit("开始执行浏览器自动化任务...")
            
            # 步骤1: 检测Chrome实例
            self.progress_updated.emit(10)
            self.log_message.emit("正在检测Chrome实例...")
            chrome_instances = self.detect_chrome_instances()
            
            if not chrome_instances:
                self.log_message.emit("未检测到可用的Chrome实例，将启动新实例")
                chrome_instances = [9222]  # 默认端口
            
            # 步骤2: 初始化Chrome自动化
            self.progress_updated.emit(20)
            self.chrome_automation = ChromeAutomation()
            
            # 步骤3: 执行自动化任务
            for i, port in enumerate(chrome_instances):
                self.log_message.emit(f"正在处理Chrome实例 {port}...")
                
                try:
                    # 连接Chrome实例
                    if self.chrome_automation.connect_to_chrome(port):
                        self.log_message.emit(f"成功连接到Chrome实例 {port}")
                        
                        # 执行具体的自动化操作
                        result = self.perform_automation_tasks(port)
                        self.task_results.append(result)
                        
                        # 更新进度
                        progress = 20 + (i + 1) * 60 // len(chrome_instances)
                        self.progress_updated.emit(progress)
                        
                    else:
                        self.log_message.emit(f"无法连接到Chrome实例 {port}", level="warning")
                        
                except Exception as e:
                    self.log_message.emit(f"处理Chrome实例 {port} 时出错: {str(e)}", level="error")
                    continue
            
            # 步骤4: 生成报告
            self.progress_updated.emit(90)
            self.log_message.emit("正在生成任务报告...")
            report = self.generate_report()
            
            # 步骤5: 清理资源
            self.progress_updated.emit(100)
            self.cleanup()
            
            # 发送完成信号
            success = len(self.task_results) > 0
            message = f"任务完成！处理了 {len(self.task_results)} 个Chrome实例"
            self.task_finished.emit(success, message)
            
            self.log_message.emit(message)
            
        except Exception as e:
            error_msg = f"浏览器自动化任务执行失败: {str(e)}"
            self.log_message.emit(error_msg, level="error")
            self.task_finished.emit(False, error_msg)
            self.cleanup()
            
        finally:
            self.is_running = False
    
    def detect_chrome_instances(self) -> List[int]:
        """检测可用的Chrome实例"""
        try:
            # 使用netstat检测端口
            import psutil
            chrome_ports = []
            
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN':
                    port = conn.laddr.port
                    if 9222 <= port <= 9232:  # Chrome调试端口范围
                        chrome_ports.append(port)
            
            # 去重并排序
            chrome_ports = sorted(list(set(chrome_ports)))
            
            if not chrome_ports:
                # 尝试默认端口
                chrome_ports = [9222]
            
            self.log_message.emit(f"检测到 {len(chrome_ports)} 个Chrome实例: {chrome_ports}")
            return chrome_ports
            
        except Exception as e:
            self.log_message.emit(f"检测Chrome实例失败: {str(e)}", level="warning")
            return [9222]  # 返回默认端口
    
    def perform_automation_tasks(self, port: int) -> Dict:
        """执行具体的自动化操作"""
        result = {
            'port': port,
            'start_time': datetime.now().isoformat(),
            'status': 'success',
            'actions': [],
            'screenshots': [],
            'error': None
        }
        
        try:
            # 任务1: 打开百度并搜索
            self.log_message.emit(f"在端口 {port} 上执行百度搜索任务...")
            
            # 导航到百度
            self.chrome_automation.navigate_to_url("https://www.baidu.com")
            time.sleep(2)
            
            # 搜索关键词
            search_query = "浏览器自动化测试"
            self.chrome_automation.perform_search(search_query)
            time.sleep(3)
            
            # 截图保存
            screenshot_path = self.take_screenshot(port, "baidu_search")
            result['screenshots'].append(screenshot_path)
            
            result['actions'].append({
                'action': 'baidu_search',
                'query': search_query,
                'screenshot': screenshot_path
            })
            
            # 任务2: 滚动页面
            self.log_message.emit(f"在端口 {port} 上执行页面滚动...")
            self.chrome_automation.scroll_page()
            time.sleep(1)
            
            # 任务3: 获取页面信息
            page_info = self.chrome_automation.get_page_info()
            result['page_info'] = page_info
            
            self.log_message.emit(f"端口 {port} 的自动化任务执行完成")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.log_message.emit(f"端口 {port} 的自动化任务失败: {str(e)}", level="error")
            
        finally:
            result['end_time'] = datetime.now().isoformat()
            
        return result
    
    def take_screenshot(self, port: int, action_name: str) -> str:
        """截图并保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{port}_{action_name}_{timestamp}.png"
            
            # 确保截图目录存在
            screenshot_dir = os.path.join(project_root, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            screenshot_path = os.path.join(screenshot_dir, filename)
            
            if self.chrome_automation.take_screenshot(screenshot_path):
                self.log_message.emit(f"截图已保存: {screenshot_path}")
                return screenshot_path
            else:
                self.log_message.emit("截图失败", level="warning")
                return ""
                
        except Exception as e:
            self.log_message.emit(f"截图出错: {str(e)}", level="error")
            return ""
    
    def generate_report(self) -> str:
        """生成任务报告"""
        try:
            report = {
                'task_summary': {
                    'total_instances': len(self.task_results),
                    'successful_instances': len([r for r in self.task_results if r['status'] == 'success']),
                    'failed_instances': len([r for r in self.task_results if r['status'] == 'failed']),
                    'start_time': datetime.now().isoformat()
                },
                'detailed_results': self.task_results
            }
            
            # 保存报告到文件
            report_dir = os.path.join(project_root, "reports")
            os.makedirs(report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(report_dir, f"automation_report_{timestamp}.json")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.log_message.emit(f"任务报告已保存: {report_path}")
            return report_path
            
        except Exception as e:
            self.log_message.emit(f"生成报告失败: {str(e)}", level="error")
            return ""
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.chrome_automation:
                self.chrome_automation.close()
                self.chrome_automation = None
                
            self.log_message.emit("资源清理完成")
            
        except Exception as e:
            self.log_message.emit(f"清理资源时出错: {str(e)}", level="warning")
    
    def stop(self):
        """停止任务"""
        self.is_running = False
        self.cleanup()
        self.log_message.emit("任务已停止")