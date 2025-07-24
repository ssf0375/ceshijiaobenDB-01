import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scripts.chrome_automation import ChromeAutomation


class TestChromeAutomation:
    """Chrome自动化测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.chrome_automation = ChromeAutomation()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.chrome_automation.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        assert self.chrome_automation.playwright is None
        assert self.chrome_automation.browser is None
        assert self.chrome_automation.context is None
        assert self.chrome_automation.page is None
        assert self.chrome_automation.is_connected is False
    
    def test_find_chrome_executable_windows(self):
        """测试在Windows上查找Chrome可执行文件"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.chrome_automation._find_chrome_executable()
            assert result is not None
            assert isinstance(result, str)
    
    def test_find_chrome_executable_not_found(self):
        """测试未找到Chrome可执行文件"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            with patch('shutil.which') as mock_which:
                mock_which.return_value = None
                result = self.chrome_automation._find_chrome_executable()
                assert result is None
    
    @pytest.mark.skipif(
        'playwright' not in sys.modules,
        reason="Playwright未安装"
    )
    def test_connect_to_chrome_without_playwright(self):
        """测试无Playwright时的连接"""
        with patch('src.scripts.chrome_automation.HAS_PLAYWRIGHT', False):
            result = self.chrome_automation.connect_to_chrome()
            assert result is False
    
    def test_take_screenshot_without_page(self):
        """测试无页面时的截图"""
        result = self.chrome_automation.take_screenshot()
        assert result is None
    
    def test_navigate_to_url_without_connection(self):
        """测试未连接时的导航"""
        result = self.chrome_automation.navigate_to_url("https://example.com")
        assert result is False
    
    def test_perform_search_without_page(self):
        """测试无页面时的搜索"""
        result = self.chrome_automation.perform_search("test")
        assert result is False
    
    def test_scroll_page_without_page(self):
        """测试无页面时的滚动"""
        result = self.chrome_automation.scroll_page()
        assert result is False
    
    def test_click_element_without_page(self):
        """测试无页面时的点击"""
        result = self.chrome_automation.click_element("div.test")
        assert result is False
    
    def test_get_element_text_without_page(self):
        """测试无页面时获取元素文本"""
        result = self.chrome_automation.get_element_text("div.test")
        assert result is None
    
    def test_get_page_info_without_page(self):
        """测试无页面时获取页面信息"""
        result = self.chrome_automation.get_page_info()
        assert result == {}
    
    def test_get_all_links_without_page(self):
        """测试无页面时获取所有链接"""
        result = self.chrome_automation.get_all_links()
        assert result == []
    
    def test_wait_for_selector_without_page(self):
        """测试无页面时等待选择器"""
        result = self.chrome_automation.wait_for_selector("div.test")
        assert result is False
    
    def test_close_without_connection(self):
        """测试未连接时的关闭"""
        # 应该不抛出异常
        self.chrome_automation.close()
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with ChromeAutomation() as chrome:
            assert isinstance(chrome, ChromeAutomation)
    
    def test_parse_file_size(self):
        """测试文件大小解析"""
        from src.common.logging_config import _parse_file_size
        
        assert _parse_file_size("10MB") == 10 * 1024 * 1024
        assert _parse_file_size("1GB") == 1024 * 1024 * 1024
        assert _parse_file_size("512KB") == 512 * 1024
        assert _parse_file_size("1024B") == 1024
        assert _parse_file_size("invalid") == 10 * 1024 * 1024  # 默认值


class TestChromeIntegration:
    """Chrome集成测试类"""
    
    @pytest.fixture(scope="class")
    def chrome_instance(self):
        """Chrome实例fixture"""
        chrome = ChromeAutomation()
        yield chrome
        chrome.close()
    
    def test_start_chrome(self):
        """测试启动Chrome"""
        chrome = ChromeAutomation()
        
        # 模拟找到Chrome
        with patch.object(chrome, '_find_chrome_executable', return_value="chrome.exe"):
            with patch('subprocess.Popen') as mock_popen:
                mock_popen.return_value = MagicMock()
                with patch.object(chrome, 'connect_to_chrome', return_value=True):
                    result = chrome.start_chrome_with_debug_port()
                    assert result is True
    
    def test_start_chrome_not_found(self):
        """测试未找到Chrome时的启动"""
        chrome = ChromeAutomation()
        
        with patch.object(chrome, '_find_chrome_executable', return_value=None):
            result = chrome.start_chrome_with_debug_port()
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])