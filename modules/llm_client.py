"""
大模型客户端 - 支持多个提供商
"""
import os
import httpx
from typing import Optional, Generator
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """统一的大模型客户端"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")
        self._setup_client()
    
    def _setup_client(self):
        """根据提供商配置客户端"""
        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "zhipu":
            self.api_key = os.getenv("ZHIPU_API_KEY")
            self.base_url = "https://open.bigmodel.cn/api/paas/v4"
            self.model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
        elif self.provider == "moonshot":
            self.api_key = os.getenv("MOONSHOT_API_KEY")
            self.base_url = "https://api.moonshot.cn/v1"
            self.model = os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k")
        elif self.provider == "deepseek":
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
            self.base_url = "https://api.deepseek.com/v1"
            self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")
        
        if not self.api_key:
            raise ValueError(f"请在 .env 中配置 {self.provider.upper()} 的 API Key")
    
    def chat(self, 
             messages: list, 
             temperature: float = 0.7,
             max_tokens: int = 4096) -> str:
        """同步聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        with httpx.Client(timeout=120) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def chat_stream(self, 
                    messages: list,
                    temperature: float = 0.7) -> Generator[str, None, None]:
        """流式聊天"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        with httpx.Client(timeout=120) as client:
            with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        content = line[6:]
                        if content == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(content)
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except:
                            pass

    def simple_chat(self, prompt: str, system: str = "你是一个有帮助的助手。") -> str:
        """简单聊天接口"""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        return self.chat(messages)


# 便捷函数
def get_llm(provider: Optional[str] = None) -> LLMClient:
    """获取LLM客户端"""
    return LLMClient(provider)
