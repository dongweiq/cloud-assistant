"""
配置管理模块 - 支持界面配置
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """配置管理器 - 保存到本地JSON文件"""
    
    DEFAULT_CONFIG = {
        "llm": {
            "provider": "openai",
            "openai_api_key": "",
            "openai_base_url": "https://api.openai.com/v1",
            "openai_model": "gpt-4o-mini",
            "zhipu_api_key": "",
            "zhipu_model": "glm-4-flash",
            "moonshot_api_key": "",
            "moonshot_model": "moonshot-v1-8k",
            "deepseek_api_key": "",
            "deepseek_model": "deepseek-chat"
        },
        "email": {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "address": "",
            "password": ""
        },
        "general": {
            "language": "zh-CN",
            "theme": "light"
        }
    }
    
    def __init__(self, config_path: str = "./data/config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                # 合并默认配置（保证新增字段有默认值）
                self.config = self._merge_config(self.DEFAULT_CONFIG, saved_config)
            except:
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict, saved: Dict) -> Dict:
        """合并配置，保留默认值"""
        result = default.copy()
        for key, value in saved.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_config(result[key], value)
                else:
                    result[key] = value
        return result
    
    def save(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """设置配置项"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_section(self, section: str) -> Dict:
        """获取整个配置节"""
        return self.config.get(section, {})
    
    def set_section(self, section: str, data: Dict):
        """设置整个配置节"""
        self.config[section] = data
    
    # ===== 便捷方法 =====
    
    def get_llm_config(self) -> Dict:
        """获取当前LLM配置"""
        llm = self.config.get("llm", {})
        provider = llm.get("provider", "openai")
        
        if provider == "openai":
            return {
                "provider": provider,
                "api_key": llm.get("openai_api_key", ""),
                "base_url": llm.get("openai_base_url", "https://api.openai.com/v1"),
                "model": llm.get("openai_model", "gpt-4o-mini")
            }
        elif provider == "zhipu":
            return {
                "provider": provider,
                "api_key": llm.get("zhipu_api_key", ""),
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": llm.get("zhipu_model", "glm-4-flash")
            }
        elif provider == "moonshot":
            return {
                "provider": provider,
                "api_key": llm.get("moonshot_api_key", ""),
                "base_url": "https://api.moonshot.cn/v1",
                "model": llm.get("moonshot_model", "moonshot-v1-8k")
            }
        elif provider == "deepseek":
            return {
                "provider": provider,
                "api_key": llm.get("deepseek_api_key", ""),
                "base_url": "https://api.deepseek.com/v1",
                "model": llm.get("deepseek_model", "deepseek-chat")
            }
        else:
            return {"provider": provider, "api_key": "", "base_url": "", "model": ""}
    
    def is_llm_configured(self) -> bool:
        """检查LLM是否已配置"""
        config = self.get_llm_config()
        return bool(config.get("api_key"))
    
    def get_email_config(self) -> Dict:
        """获取邮件配置"""
        return self.config.get("email", {})
    
    def is_email_configured(self) -> bool:
        """检查邮件是否已配置"""
        email = self.get_email_config()
        return bool(email.get("address") and email.get("password"))


# 全局配置实例
_config_manager: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
