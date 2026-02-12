"""
翻译模块 - 支持长文档翻译
"""
import os
from typing import List, Optional, Generator
from deep_translator import GoogleTranslator
from .llm_client import LLMClient


class DocumentTranslator:
    """文档翻译器"""
    
    LANGUAGE_MAP = {
        "中文": "zh-CN",
        "英文": "en",
        "日文": "ja",
        "韩文": "ko",
        "法文": "fr",
        "德文": "de",
        "西班牙文": "es",
        "俄文": "ru",
        "阿拉伯文": "ar",
        "葡萄牙文": "pt"
    }
    
    def __init__(self, use_llm: bool = False, llm_client: Optional[LLMClient] = None):
        self.use_llm = use_llm
        self.llm_client = llm_client
        self.chunk_size = 4000  # 每块最大字符数
    
    def _split_text(self, text: str) -> List[str]:
        """将长文本分块"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # 如果单个段落超过限制，强制分割
                if len(para) > self.chunk_size:
                    for i in range(0, len(para), self.chunk_size):
                        chunks.append(para[i:i+self.chunk_size])
                    current_chunk = ""
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def translate_text(self, 
                       text: str, 
                       target_lang: str = "中文",
                       source_lang: str = "auto") -> str:
        """翻译单段文本"""
        target_code = self.LANGUAGE_MAP.get(target_lang, target_lang)
        source_code = self.LANGUAGE_MAP.get(source_lang, source_lang)
        if source_code == "auto":
            source_code = "auto"
        
        if self.use_llm and self.llm_client:
            return self._translate_with_llm(text, target_lang, source_lang)
        else:
            return self._translate_with_google(text, target_code, source_code)
    
    def _translate_with_google(self, text: str, target: str, source: str) -> str:
        """使用Google翻译"""
        try:
            translator = GoogleTranslator(source=source, target=target)
            return translator.translate(text)
        except Exception as e:
            return f"[翻译错误: {e}]"
    
    def _translate_with_llm(self, text: str, target_lang: str, source_lang: str) -> str:
        """使用大模型翻译"""
        prompt = f"""请将以下文本翻译成{target_lang}。
要求：
1. 保持原文格式和段落结构
2. 专业术语翻译准确
3. 语句通顺自然

原文：
{text}

翻译："""
        
        return self.llm_client.simple_chat(prompt)
    
    def translate_document(self, 
                          text: str, 
                          target_lang: str = "中文",
                          source_lang: str = "auto",
                          progress_callback=None) -> str:
        """
        翻译长文档
        progress_callback: 进度回调函数 callback(current, total)
        """
        chunks = self._split_text(text)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            translated = self.translate_text(chunk, target_lang, source_lang)
            translated_chunks.append(translated)
            
            if progress_callback:
                progress_callback(i + 1, len(chunks))
        
        return "\n\n".join(translated_chunks)
    
    def translate_document_stream(self, 
                                  text: str, 
                                  target_lang: str = "中文") -> Generator[tuple, None, None]:
        """
        流式翻译文档
        yield: (chunk_index, total_chunks, translated_chunk)
        """
        chunks = self._split_text(text)
        
        for i, chunk in enumerate(chunks):
            translated = self.translate_text(chunk, target_lang)
            yield (i + 1, len(chunks), translated)
