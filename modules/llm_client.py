"""
大模型客户端 - 支持多个提供商
"""
import httpx
from typing import Optional, Generator, Dict


class LLMClient:
    """统一的大模型客户端"""
    
    def __init__(self, 
                 api_key: str,
                 base_url: str,
                 model: str,
                 provider: str = "openai"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.provider = provider
        
        if not self.api_key:
            raise ValueError("API Key 未配置")
    
    @classmethod
    def from_config(cls, config: Dict) -> 'LLMClient':
        """从配置字典创建客户端"""
        return cls(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", ""),
            model=config.get("model", ""),
            provider=config.get("provider", "openai")
        )
    
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


def test_llm_connection(api_key: str, base_url: str, model: str) -> tuple[bool, str]:
    """测试LLM连接"""
    try:
        client = LLMClient(api_key=api_key, base_url=base_url, model=model)
        response = client.simple_chat("说'连接成功'两个字")
        return True, response[:100]
    except Exception as e:
        return False, str(e)
