"""
文档索引与检索模块 - 基于ChromaDB
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path
import hashlib
import json

from .document_processor import DocumentProcessor


class DocumentIndex:
    """文档索引管理器"""
    
    def __init__(self, persist_path: str = "./data/chroma"):
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.persist_path))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "文档内容索引"}
        )
        
        self.doc_processor = DocumentProcessor()
        self._load_file_index()
    
    def _load_file_index(self):
        """加载文件索引"""
        index_file = self.persist_path / "file_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                self.file_index = json.load(f)
        else:
            self.file_index = {}
    
    def _save_file_index(self):
        """保存文件索引"""
        index_file = self.persist_path / "file_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(self.file_index, f, ensure_ascii=False, indent=2)
    
    def add_document(self, file_path: str) -> Dict:
        """
        添加文档到索引
        返回: {"file": "xxx.pdf", "pages": 10, "status": "success"}
        """
        file_hash = self.doc_processor.get_file_hash(file_path)
        filename = Path(file_path).name
        
        # 检查是否已索引
        if file_hash in self.file_index:
            return {"file": filename, "status": "already_indexed", "pages": self.file_index[file_hash]["pages"]}
        
        # 提取文本
        pages = self.doc_processor.extract_text(file_path)
        
        if not pages:
            return {"file": filename, "status": "no_content", "pages": 0}
        
        # 添加到向量数据库
        ids = []
        documents = []
        metadatas = []
        
        for page in pages:
            doc_id = f"{file_hash}_p{page['page']}"
            ids.append(doc_id)
            documents.append(page['content'])
            metadatas.append({
                "file": filename,
                "file_path": file_path,
                "page": page['page'],
                "file_hash": file_hash
            })
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # 更新文件索引
        self.file_index[file_hash] = {
            "file": filename,
            "file_path": file_path,
            "pages": len(pages)
        }
        self._save_file_index()
        
        return {"file": filename, "status": "success", "pages": len(pages)}
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索文档
        返回: [{"file": "xxx.pdf", "page": 1, "content": "...", "score": 0.9}, ...]
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results['documents'][0]:
            return []
        
        search_results = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if results.get('distances') else 0
            
            search_results.append({
                "file": metadata['file'],
                "file_path": metadata.get('file_path', ''),
                "page": metadata['page'],
                "content": doc[:500] + "..." if len(doc) > 500 else doc,
                "score": 1 - distance  # 转换为相似度
            })
        
        return search_results
    
    def get_all_files(self) -> List[Dict]:
        """获取所有已索引的文件"""
        return [
            {"file": info["file"], "pages": info["pages"], "hash": h}
            for h, info in self.file_index.items()
        ]
    
    def remove_document(self, file_hash: str) -> bool:
        """从索引中移除文档"""
        if file_hash not in self.file_index:
            return False
        
        # 从向量数据库删除
        info = self.file_index[file_hash]
        ids_to_delete = [f"{file_hash}_p{i}" for i in range(1, info['pages'] + 1)]
        
        try:
            self.collection.delete(ids=ids_to_delete)
        except:
            pass
        
        # 从索引删除
        del self.file_index[file_hash]
        self._save_file_index()
        
        return True
    
    def summarize_document(self, file_path: str, llm_client) -> str:
        """使用LLM总结文档"""
        pages = self.doc_processor.extract_text(file_path)
        
        if not pages:
            return "无法提取文档内容"
        
        # 合并内容（限制长度）
        full_content = "\n\n".join([
            f"[第{p['page']}页]\n{p['content']}" 
            for p in pages[:20]  # 限制前20页
        ])
        
        if len(full_content) > 15000:
            full_content = full_content[:15000] + "\n...(内容过长，已截断)"
        
        prompt = f"""请总结以下文档的主要内容：

{full_content}

请用中文提供一个结构化的总结，包括：
1. 文档类型和主题
2. 主要内容要点
3. 关键信息"""

        return llm_client.simple_chat(prompt)
