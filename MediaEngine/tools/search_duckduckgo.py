"""
DuckDuckGo 搜索提供商实现示例
展示如何使用免费的搜索 API
"""

import os
import requests
from typing import Optional
from .search_base import (
    SearchProviderBase,
    UnifiedSearchResponse,
    WebpageResult,
    ImageResult,
    StructuredDataResult
)


class DuckDuckGoSearchProvider(SearchProviderBase):
    """
    DuckDuckGo Instant Answer API 搜索提供商
    
    优势：
    - 完全免费，无需 API Key
    - 提供即时答案（类似模态卡）
    - 无请求限制
    
    劣势：
    - 功能相对有限
    - 中文支持一般
    - 没有高级搜索功能
    """
    
    INSTANT_ANSWER_API = "https://api.duckduckgo.com/"
    
    def __init__(self):
        """初始化 DuckDuckGo 搜索提供商（无需 API Key）"""
        pass
    
    def _parse_instant_answer(self, data: dict, query: str) -> UnifiedSearchResponse:
        """
        解析 DuckDuckGo Instant Answer API 的返回结果
        
        Args:
            data: API 返回的字典
            query: 搜索查询
            
        Returns:
            统一格式的搜索响应
        """
        response = UnifiedSearchResponse(
            query=query,
            provider="DuckDuckGo"
        )
        
        # 提取抽象答案（即时答案）
        abstract = data.get('Abstract', '')
        if abstract:
            response.answer = abstract
            
            # 添加为结构化数据
            response.structured_data.append(StructuredDataResult(
                data_type='instant_answer',
                content={
                    'abstract': abstract,
                    'abstract_source': data.get('AbstractSource', ''),
                    'abstract_url': data.get('AbstractURL', ''),
                    'heading': data.get('Heading', ''),
                    'image': data.get('Image', '')
                },
                source='duckduckgo'
            ))
        
        # 提取定义（如果有）
        definition = data.get('Definition', '')
        if definition:
            if not response.answer:
                response.answer = definition
            
            response.structured_data.append(StructuredDataResult(
                data_type='definition',
                content={
                    'definition': definition,
                    'definition_source': data.get('DefinitionSource', ''),
                    'definition_url': data.get('DefinitionURL', '')
                },
                source='duckduckgo'
            ))
        
        # 提取相关主题
        related_topics = data.get('RelatedTopics', [])
        for topic in related_topics[:5]:  # 限制数量
            if isinstance(topic, dict) and 'Text' in topic:
                response.webpages.append(WebpageResult(
                    name=topic.get('Text', ''),
                    url=topic.get('FirstURL', ''),
                    snippet=topic.get('Text', '')
                ))
                
                # 添加为追问建议
                if 'Text' in topic and len(response.follow_ups) < 3:
                    response.follow_ups.append(topic['Text'])
        
        # 提取图片
        if data.get('Image'):
            response.images.append(ImageResult(
                name=data.get('Heading', ''),
                content_url=data.get('Image', ''),
                host_page_url=data.get('AbstractURL', '')
            ))
        
        return response
    
    def _search_instant_answer(self, query: str) -> UnifiedSearchResponse:
        """
        使用 DuckDuckGo Instant Answer API 进行搜索
        
        Args:
            query: 搜索查询
            
        Returns:
            统一格式的搜索响应
        """
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        
        try:
            response = requests.get(self.INSTANT_ANSWER_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_instant_answer(data, query)
        
        except requests.exceptions.RequestException as e:
            print(f"DuckDuckGo 搜索错误: {str(e)}")
            # 返回空结果
            return UnifiedSearchResponse(query=query, provider="DuckDuckGo")
    
    def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
        """
        全面综合搜索
        
        注意：DuckDuckGo Instant Answer API 功能有限，
        主要返回即时答案和相关主题，不是完整的网页搜索
        """
        return self._search_instant_answer(query)
    
    def web_search_only(self, query: str, max_results: int = 15) -> UnifiedSearchResponse:
        """纯网页搜索"""
        return self._search_instant_answer(query)
    
    def search_for_structured_data(self, query: str) -> UnifiedSearchResponse:
        """
        结构化数据查询
        
        DuckDuckGo 特别适合查询定义、百科等结构化信息
        """
        return self._search_instant_answer(query)
    
    def search_last_24_hours(self, query: str) -> UnifiedSearchResponse:
        """
        搜索24小时内信息
        
        注意：DuckDuckGo Instant Answer API 不支持时间过滤
        """
        print("警告: DuckDuckGo Instant Answer API 不支持时间过滤")
        return self._search_instant_answer(query)
    
    def search_last_week(self, query: str) -> UnifiedSearchResponse:
        """
        搜索本周信息
        
        注意：DuckDuckGo Instant Answer API 不支持时间过滤
        """
        print("警告: DuckDuckGo Instant Answer API 不支持时间过滤")
        return self._search_instant_answer(query)


# 使用示例
if __name__ == "__main__":
    provider = DuckDuckGoSearchProvider()
    
    # 测试即时答案查询
    queries = [
        "Python programming language",
        "Albert Einstein",
        "weather in Beijing",
        "人工智能"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        
        result = provider.comprehensive_search(query)
        
        if result.answer:
            print(f"即时答案: {result.answer[:150]}...")
        
        print(f"找到 {len(result.webpages)} 个相关主题")
        print(f"找到 {len(result.structured_data)} 个结构化数据")
        
        if result.structured_data:
            print(f"结构化数据类型: {[sd.data_type for sd in result.structured_data]}")
        
        if result.webpages:
            print(f"第一个相关主题: {result.webpages[0].name[:80]}...")
