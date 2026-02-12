"""
网络搜索模块
"""
from duckduckgo_search import DDGS
from typing import List, Dict


class WebSearcher:
    """网络搜索器"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索网络
        返回: [{"title": "xxx", "url": "xxx", "body": "xxx"}, ...]
        """
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", "")
                }
                for r in results
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """搜索新闻"""
        try:
            results = list(self.ddgs.news(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "body": r.get("body", ""),
                    "source": r.get("source", ""),
                    "date": r.get("date", "")
                }
                for r in results
            ]
        except Exception as e:
            return [{"error": str(e)}]


def search_and_summarize(query: str, llm_client, max_results: int = 5) -> str:
    """搜索并用LLM总结"""
    searcher = WebSearcher()
    results = searcher.search(query, max_results)
    
    if not results or "error" in results[0]:
        return "搜索失败，请稍后重试"
    
    # 格式化搜索结果
    search_content = "\n\n".join([
        f"来源: {r['title']}\n{r['body']}"
        for r in results
    ])
    
    prompt = f"""基于以下搜索结果回答问题：{query}

搜索结果：
{search_content}

请综合以上信息，给出简洁准确的回答。如果信息不足，请说明。"""
    
    return llm_client.simple_chat(prompt)
