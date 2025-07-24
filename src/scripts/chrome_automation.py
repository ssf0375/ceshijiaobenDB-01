import os
import sys
import json
import time
import logging
import subprocess
from typing import Optional, Dict, Any, List
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    logging.warning("Playwright未安装，浏览器自动化功能将不可用")

logger = logging.getLogger(__name__)


class ChromeAutomation:
    """Chrome浏览器自动化类"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_connected = False
        
    def start_chrome_with_debug_port(self, port: int = 9222, user_data_dir: str = None) -> bool:
        """
        启动Chrome浏览器并开启调试端口
        
        Args:
            port: 调试端口号，默认9222
            user_data_dir: Chrome用户数据目录
            
        Returns:
            bool: 启动是否成功
        """
        try:
            # 构建Chrome启动命令
            chrome_path = self._find_chrome_executable()
            if not chrome_path:
                logger.error("未找到Chrome可执行文件")
                return False
            
            # 设置用户数据目录
            if not user_data_dir:
                user_data_dir = os.path.join(project_root, "Chrome_UserData")
            
            # 确保目录存在
            os.makedirs(user_data_dir, exist_ok=True)
            
            # 构建启动参数
            cmd = [
                chrome_path,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-popup-blocking",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--enable-automation",
                "--password-store=basic",
                "--use-mock-keychain",
                "about:blank"
            ]
            
            # 启动Chrome进程
            logger.info(f"启动Chrome: {' '.join(cmd)}")
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 等待Chrome启动
            time.sleep(3)
            
            # 测试连接
            return self.connect_to_chrome(port)
            
        except Exception as e:
            logger.error(f"启动Chrome失败: {str(e)}")
            return False
    
    def connect_to_chrome(self, port: int = 9222) -> bool:
        """
        连接到已启动的Chrome实例
        
        Args:
            port: 调试端口号
            
        Returns:
            bool: 连接是否成功
        """
        if not HAS_PLAYWRIGHT:
            logger.error("Playwright未安装，无法连接Chrome")
            return False
            
        try:
            # 关闭之前的连接
            self.close()
            
            # 启动Playwright
            self.playwright = sync_playwright().start()
            
            # 连接到Chrome
            self.browser = self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{port}"
            )
            
            # 获取第一个上下文，如果没有则创建
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
            else:
                self.context = self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080}
                )
            
            # 获取或创建页面
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = self.context.new_page()
            
            self.is_connected = True
            logger.info(f"成功连接到Chrome实例 (端口: {port})")
            return True
            
        except Exception as e:
            logger.error(f"连接Chrome失败: {str(e)}")
            self.close()
            return False
    
    def navigate_to_url(self, url: str, timeout: int = 30) -> bool:
        """
        导航到指定URL
        
        Args:
            url: 目标URL
            timeout: 超时时间（秒）
            
        Returns:
            bool: 导航是否成功
        """
        if not self.is_connected or not self.page:
            logger.error("未连接到Chrome")
            return False
            
        try:
            logger.info(f"导航到: {url}")
            self.page.goto(url, timeout=timeout * 1000)
            return True
            
        except Exception as e:
            logger.error(f"导航失败: {str(e)}")
            return False
    
    def perform_search(self, query: str, selector: str = "input[name='wd']") -> bool:
        """
        执行搜索操作
        
        Args:
            query: 搜索关键词
            selector: 搜索框选择器
            
        Returns:
            bool: 搜索是否成功
        """
        if not self.page:
            logger.error("页面未初始化")
            return False
            
        try:
            # 等待搜索框出现
            self.page.wait_for_selector(selector, timeout=5000)
            
            # 输入搜索词
            self.page.fill(selector, query)
            
            # 按回车键搜索
            self.page.press(selector, "Enter")
            
            # 等待页面加载
            self.page.wait_for_load_state("networkidle")
            
            logger.info(f"搜索完成: {query}")
            return True
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return False
    
    def scroll_page(self, direction: str = "down", pixels: int = 500) -> bool:
        """
        滚动页面
        
        Args:
            direction: 滚动方向 (up/down/left/right)
            pixels: 滚动像素数
            
        Returns:
            bool: 滚动是否成功
        """
        if not self.page:
            return False
            
        try:
            scroll_map = {
                "down": (0, pixels),
                "up": (0, -pixels),
                "left": (-pixels, 0),
                "right": (pixels, 0)
            }
            
            x, y = scroll_map.get(direction, (0, pixels))
            self.page.evaluate(f"window.scrollBy({x}, {y})")
            
            logger.info(f"页面滚动: {direction} {pixels}px")
            return True
            
        except Exception as e:
            logger.error(f"滚动失败: {str(e)}")
            return False
    
    def click_element(self, selector: str, timeout: int = 5) -> bool:
        """
        点击元素
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（秒）
            
        Returns:
            bool: 点击是否成功
        """
        if not self.page:
            return False
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout * 1000)
            self.page.click(selector)
            logger.info(f"点击元素: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"点击失败: {str(e)}")
            return False
    
    def get_element_text(self, selector: str) -> Optional[str]:
        """
        获取元素文本
        
        Args:
            selector: CSS选择器
            
        Returns:
            str: 元素文本，失败返回None
        """
        if not self.page:
            return None
            
        try:
            element = self.page.query_selector(selector)
            if element:
                return element.text_content()
            return None
            
        except Exception as e:
            logger.error(f"获取元素文本失败: {str(e)}")
            return None
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        获取页面信息
        
        Returns:
            dict: 页面信息
        """
        if not self.page:
            return {}
            
        try:
            return {
                'url': self.page.url,
                'title': self.page.title(),
                'viewport': {
                    'width': self.page.viewport_size['width'],
                    'height': self.page.viewport_size['height']
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取页面信息失败: {str(e)}")
            return {}
    
    def take_screenshot(self, filename: str = None, full_page: bool = True) -> Optional[str]:
        """
        截图
        
        Args:
            filename: 文件名，如果为None则自动生成
            full_page: 是否截取整个页面
            
        Returns:
            str: 截图文件路径，失败返回None
        """
        if not self.page:
            return None
            
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # 确保截图目录存在
            screenshot_dir = os.path.join(project_root, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            filepath = os.path.join(screenshot_dir, filename)
            
            self.page.screenshot(path=filepath, full_page=full_page)
            logger.info(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return None
    
    def wait_for_selector(self, selector: str, timeout: int = 10) -> bool:
        """
        等待元素出现
        
        Args:
            selector: CSS选择器
            timeout: 超时时间（秒）
            
        Returns:
            bool: 元素是否出现
        """
        if not self.page:
            return False
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout * 1000)
            return True
            
        except Exception as e:
            logger.error(f"等待元素超时: {str(e)}")
            return False
    
    def get_all_links(self) -> List[Dict[str, str]]:
        """
        获取页面所有链接
        
        Returns:
            list: 链接列表，每个元素包含text和href
        """
        if not self.page:
            return []
            
        try:
            links = self.page.query_selector_all('a[href]')
            return [
                {
                    'text': link.text_content().strip(),
                    'href': link.get_attribute('href')
                }
                for link in links
            ]
            
        except Exception as e:
            logger.error(f"获取链接失败: {str(e)}")
            return []
    
    def close(self):
        """关闭浏览器连接"""
        try:
            if self.page:
                self.page.close()
                self.page = None
                
            if self.context:
                self.context.close()
                self.context = None
                
            if self.browser:
                self.browser.close()
                self.browser = None
                
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
                
            self.is_connected = False
            logger.info("Chrome连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭连接失败: {str(e)}")
    
    def _find_chrome_executable(self) -> Optional[str]:
        """
        查找Chrome可执行文件路径
        
        Returns:
            str: Chrome可执行文件路径，找不到返回None
        """
        chrome_paths = [
            # Windows
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            
            # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            
            # Linux
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        
        # 尝试从PATH查找
        try:
            import shutil
            chrome_path = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chromium")
            return chrome_path
        except:
            pass
            
        return None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()