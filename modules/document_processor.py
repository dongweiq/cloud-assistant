"""
文档处理模块 - 支持PDF、Word、Excel等
"""
import os
import fitz  # PyMuPDF
from docx import Document
from typing import List, Dict, Optional, Tuple
import hashlib
from pathlib import Path


class DocumentProcessor:
    """文档处理器"""
    
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls'}
    
    def __init__(self, upload_path: str = "./uploads"):
        self.upload_path = Path(upload_path)
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    def extract_text(self, file_path: str) -> List[Dict]:
        """
        提取文档文本，返回分页内容
        返回: [{"page": 1, "content": "...", "file": "xxx.pdf"}, ...]
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return self._extract_pdf(file_path)
        elif suffix in {'.docx', '.doc'}:
            return self._extract_docx(file_path)
        elif suffix == '.txt':
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
    
    def _extract_pdf(self, file_path: str) -> List[Dict]:
        """提取PDF文本"""
        results = []
        doc = fitz.open(file_path)
        filename = Path(file_path).name
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                results.append({
                    "page": page_num,
                    "content": text,
                    "file": filename,
                    "file_path": file_path
                })
        
        doc.close()
        return results
    
    def _extract_docx(self, file_path: str) -> List[Dict]:
        """提取Word文档文本"""
        doc = Document(file_path)
        filename = Path(file_path).name
        
        # Word文档按段落处理，每10段为一"页"
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        results = []
        
        chunk_size = 10
        for i in range(0, len(paragraphs), chunk_size):
            chunk = paragraphs[i:i+chunk_size]
            page_num = i // chunk_size + 1
            results.append({
                "page": page_num,
                "content": "\n".join(chunk),
                "file": filename,
                "file_path": file_path
            })
        
        return results if results else [{"page": 1, "content": "", "file": filename, "file_path": file_path}]
    
    def _extract_txt(self, file_path: str) -> List[Dict]:
        """提取文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = Path(file_path).name
        return [{"page": 1, "content": content, "file": filename, "file_path": file_path}]
    
    def get_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()


class PDFEditor:
    """PDF编辑器"""
    
    def __init__(self):
        pass
    
    def add_signature(self, 
                      pdf_path: str, 
                      signature_path: str, 
                      target_text: str,
                      output_path: Optional[str] = None,
                      sig_width: int = 80,
                      sig_height: int = 40) -> str:
        """
        在PDF中添加签名
        target_text: 在此文本上方添加签名
        """
        doc = fitz.open(pdf_path)
        output = output_path or pdf_path.replace('.pdf', '_signed.pdf')
        
        for page in doc:
            instances = page.search_for(target_text)
            for rect in instances:
                sig_x = rect.x0 - 10
                sig_y = rect.y0 - sig_height - 5
                sig_rect = fitz.Rect(sig_x, sig_y, sig_x + sig_width, sig_y + sig_height)
                page.insert_image(sig_rect, filename=signature_path)
        
        doc.save(output)
        doc.close()
        return output
    
    def merge_pdfs(self, pdf_paths: List[str], output_path: str) -> str:
        """合并多个PDF"""
        merged = fitz.open()
        
        for pdf_path in pdf_paths:
            doc = fitz.open(pdf_path)
            merged.insert_pdf(doc)
            doc.close()
        
        merged.save(output_path)
        merged.close()
        return output_path
    
    def split_pdf(self, pdf_path: str, output_dir: str, pages_per_file: int = 1) -> List[str]:
        """拆分PDF"""
        doc = fitz.open(pdf_path)
        output_files = []
        base_name = Path(pdf_path).stem
        
        for i in range(0, len(doc), pages_per_file):
            new_doc = fitz.open()
            end_page = min(i + pages_per_file, len(doc))
            new_doc.insert_pdf(doc, from_page=i, to_page=end_page - 1)
            
            output_path = os.path.join(output_dir, f"{base_name}_part{i//pages_per_file + 1}.pdf")
            new_doc.save(output_path)
            new_doc.close()
            output_files.append(output_path)
        
        doc.close()
        return output_files
    
    def add_watermark(self, 
                      pdf_path: str, 
                      watermark_text: str,
                      output_path: Optional[str] = None,
                      opacity: float = 0.3) -> str:
        """添加文字水印"""
        doc = fitz.open(pdf_path)
        output = output_path or pdf_path.replace('.pdf', '_watermarked.pdf')
        
        for page in doc:
            rect = page.rect
            # 在页面中央添加水印
            text_point = fitz.Point(rect.width / 2, rect.height / 2)
            page.insert_text(
                text_point,
                watermark_text,
                fontsize=50,
                rotate=45,
                color=(0.8, 0.8, 0.8),
                overlay=True
            )
        
        doc.save(output)
        doc.close()
        return output
    
    def extract_pages(self, pdf_path: str, page_numbers: List[int], output_path: str) -> str:
        """提取指定页面"""
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(doc):
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
        
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        return output_path
