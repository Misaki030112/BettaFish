"""
SerpAPI 搜索提供商实现示例
展示如何集成其他搜索 API
"""

import os
from typing import Optional
from .search_base import (
    SearchProviderBase,
    UnifiedSearchResponse,
    WebpageResult,
    ImageResult,
    StructuredDataResult
)

# 注意：需要安装 google-search-results 库
# pip install google-search-results
try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None


class SerpAPISearchProvider(SearchProviderBase):
    """
    SerpAPI 搜索提供商
    使用 Google Search API 作为后端
    
    使用前需要：
    1. 安装依赖：pip install google-search-results
    2. 申请 API Key：https://serpapi.com/
    3. 设置环境变量或传入 api_key
    
    地区设置说明：
    - region="us": 美国地区，获取全球化的搜索结果（推荐用于国际新闻）
    - region="cn": 中国地区，偏向中文内容
    - region="uk": 英国地区
    - region=None: 不限制地区（最全球化）
    """
    
    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None):
        """
        初始化 SerpAPI 搜索提供商
        
        Args:
            api_key: SerpAPI 密钥，若不提供则从环境变量读取
            region: 搜索地区代码（如 "us", "cn", "uk"），默认为 "us"
                   设置为 None 可获取最全球化的结果
        """
        if GoogleSearch is None:
            raise ImportError(
                "SerpAPI 支持需要安装 google-search-results 库。\n"
                "请运行: pip install google-search-results"
            )
        
        if api_key is None:
            api_key = os.getenv("SERPAPI_API_KEY")
            if not api_key:
                raise ValueError(
                    "SerpAPI Key 未找到！\n"
                    "请设置 SERPAPI_API_KEY 环境变量或在初始化时提供"
                )
        
        self.api_key = api_key
        # 默认使用美国地区获取全球化结果，None 表示不限制地区
        self.region = region if region is not None else "us"
    
    def _parse_serpapi_results(self, results: dict, query: str) -> UnifiedSearchResponse:
        """
        解析 SerpAPI 的返回结果
        
        Args:
            results: SerpAPI 返回的字典
            query: 搜索查询
            
        Returns:
            统一格式的搜索响应
        """
        response = UnifiedSearchResponse(
            query=query,
            provider="SerpAPI"
        )
        
        # 解析有机搜索结果（网页）
        organic_results = results.get('organic_results', [])
        for item in organic_results:
            response.webpages.append(WebpageResult(
                name=item.get('title', ''),
                url=item.get('link', ''),
                snippet=item.get('snippet', ''),
                display_url=item.get('displayed_link')
            ))
        
        # 解析图片搜索结果
        images_results = results.get('images_results', [])
        for item in images_results[:10]:  # 限制图片数量
            response.images.append(ImageResult(
                name=item.get('title', ''),
                content_url=item.get('original', ''),
                thumbnail_url=item.get('thumbnail'),
                host_page_url=item.get('link')
            ))
        
        # 解析答案框（类似 Bocha 的模态卡）
        if 'answer_box' in results:
            answer_box = results['answer_box']
            response.structured_data.append(StructuredDataResult(
                data_type='answer_box',
                content=answer_box,
                source='serpapi'
            ))
            # 提取答案作为 AI 摘要
            if 'answer' in answer_box:
                response.answer = answer_box['answer']
            elif 'snippet' in answer_box:
                response.answer = answer_box['snippet']
        
        # 解析知识图谱
        if 'knowledge_graph' in results:
            kg = results['knowledge_graph']
            response.structured_data.append(StructuredDataResult(
                data_type='knowledge_graph',
                content=kg,
                source='serpapi'
            ))
        
        # 解析相关问题（类似追问建议）
        related_questions = results.get('related_questions', [])
        for q in related_questions[:3]:  # 限制数量
            if 'question' in q:
                response.follow_ups.append(q['question'])
        
        return response
    
    def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
        """
        全面综合搜索
        
        注意：搜索结果可能包含英文内容，但 LLM 会根据提示词要求输出中文分析
        """
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": max_results,
        }
        
        # 只有明确指定地区时才添加 gl 参数
        # 不设置 gl 和 hl 可以获得最全球化的搜索结果
        if self.region:
            params["gl"] = self.region
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return self._parse_serpapi_results(results, query)
    
    def web_search_only(self, query: str, max_results: int = 15) -> UnifiedSearchResponse:
        """纯网页搜索"""
        # SerpAPI 默认就是网页搜索
        return self.comprehensive_search(query, max_results)
    
    def search_for_structured_data(self, query: str) -> UnifiedSearchResponse:
        """
        结构化数据查询
        
        对于结构化数据，重点关注答案框和知识图谱
        """
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": 5,
        }
        
        # 只有明确指定地区时才添加 gl 参数
        if self.region:
            params["gl"] = self.region
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return self._parse_serpapi_results(results, query)
    
    def search_last_24_hours(self, query: str) -> UnifiedSearchResponse:
        """搜索24小时内信息"""
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": 10,
            "tbs": "qdr:d"  # 过去一天
        }
        
        # 只有明确指定地区时才添加 gl 参数
        if self.region:
            params["gl"] = self.region
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return self._parse_serpapi_results(results, query)
    
    def search_last_week(self, query: str) -> UnifiedSearchResponse:
        """搜索本周信息"""
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": 10,
            "tbs": "qdr:w"  # 过去一周
        }
        
        # 只有明确指定地区时才添加 gl 参数
        if self.region:
            params["gl"] = self.region
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return self._parse_serpapi_results(results, query)


# 使用示例
if __name__ == "__main__":
    # 确保设置了 SERPAPI_API_KEY 环境变量
    try:
        provider = SerpAPISearchProvider()
        
        # 测试综合搜索
        result = provider.comprehensive_search("人工智能最新进展")
        print(f"查询: {result.query}")
        print(f"找到 {len(result.webpages)} 个网页")
        print(f"找到 {len(result.structured_data)} 个结构化数据")
        
        if result.answer:
            print(f"AI摘要: {result.answer[:100]}...")
        
        if result.structured_data:
            print(f"结构化数据类型: {[sd.data_type for sd in result.structured_data]}")
        
    except Exception as e:
        print(f"测试失败: {e}")
