import os
import json
from typing import Dict, Any


class AppConfig:
    """应用程序配置类"""
    
    def __init__(self):
        self.config_file = self._get_config_path()
        self.config = self._load_config()
    
    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, "config", "app_config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "chrome": {
                "debug_port": 9222,
                "executable_path": None,
                "user_data_dir": "Chrome_UserData",
                "headless": False,
                "window_size": {"width": 1920, "height": 1080}
            },
            "paths": {
                "logs": "logs",
                "screenshots": "screenshots",
                "reports": "reports",
                "downloads": "downloads"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_rotation": True,
                "max_file_size": "10MB",
                "backup_count": 5
            },
            "automation": {
                "default_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 2,
                "screenshot_on_error": True
            },
            "ocr": {
                "language": "chi_sim+eng",
                "config": "--oem 3 --psm 6"
            },
            "image_recognition": {
                "confidence_threshold": 0.8,
                "model_path": None
            }
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并配置
                return self._merge_config(default_config, user_config)
            else:
                # 创建默认配置文件
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return default_config
                
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return default_config
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """合并配置"""
        merged = default.copy()
        
        def merge_dict(d1: Dict, d2: Dict) -> Dict:
            """递归合并字典"""
            for key, value in d2.items():
                if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                    d1[key] = merge_dict(d1[key], value)
                else:
                    d1[key] = value
            return d1
        
        return merge_dict(merged, user)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    def save(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_chrome_config(self) -> Dict[str, Any]:
        """获取Chrome配置"""
        return self.get('chrome', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def get_automation_config(self) -> Dict[str, Any]:
        """获取自动化配置"""
        return self.get('automation', {})
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR配置"""
        return self.get('ocr', {})
    
    def get_image_recognition_config(self) -> Dict[str, Any]:
        """获取图像识别配置"""
        return self.get('image_recognition', {})
    
    def get_path(self, path_type: str) -> str:
        """获取路径配置"""
        path = self.get(f'paths.{path_type}', '')
        if not os.path.isabs(path):
            # 相对路径转换为绝对路径
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(current_dir, path)
        
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        return path
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()


# 全局配置实例
app_config = AppConfig()