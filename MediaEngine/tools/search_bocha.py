"""
Bocha API 搜索提供商实现
封装现有的 BochaMultimodalSearch，使其符合统一接口
"""

from typing import Optional
from .search_base import (
    SearchProviderBase, 
    UnifiedSearchResponse, 
    WebpageResult,
    ImageResult,
    StructuredDataResult
)
from .search import BochaMultimodalSearch, BochaResponse


class BochaSearchProvider(SearchProviderBase):
    """
    Bocha API 搜索提供商
    封装现有的 BochaMultimodalSearch 客户端
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Bocha 搜索提供商
        
        Args:
            api_key: Bocha API 密钥
        """
        self.client = BochaMultimodalSearch(api_key=api_key)
    
    def _convert_to_unified(self, bocha_response: BochaResponse) -> UnifiedSearchResponse:
        """
        将 Bocha 的响应转换为统一格式
        
        Args:
            bocha_response: Bocha API 的原始响应
            
        Returns:
            统一格式的搜索响应
        """
        # 转换网页结果（已经是 WebpageResult 类型，直接使用）
        webpages = bocha_response.webpages
        
        # 转换图片结果（已经是 ImageResult 类型，直接使用）
        images = bocha_response.images
        
        # 转换模态卡为结构化数据
        structured_data = [
            StructuredDataResult(
                data_type=card.card_type,
                content=card.content,
                source="bocha"
            )
            for card in bocha_response.modal_cards
        ]
        
        return UnifiedSearchResponse(
            query=bocha_response.query,
            conversation_id=bocha_response.conversation_id,
            answer=bocha_response.answer,
            follow_ups=bocha_response.follow_ups,
            webpages=webpages,
            images=images,
            structured_data=structured_data,
            provider="Bocha"
        )
    
    def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
        """全面综合搜索"""
        result = self.client.comprehensive_search(query=query, max_results=max_results)
        return self._convert_to_unified(result)
    
    def web_search_only(self, query: str, max_results: int = 15) -> UnifiedSearchResponse:
        """纯网页搜索"""
        result = self.client.web_search_only(query=query, max_results=max_results)
        return self._convert_to_unified(result)
    
    def search_for_structured_data(self, query: str) -> UnifiedSearchResponse:
        """结构化数据查询"""
        result = self.client.search_for_structured_data(query=query)
        return self._convert_to_unified(result)
    
    def search_last_24_hours(self, query: str) -> UnifiedSearchResponse:
        """搜索24小时内信息"""
        result = self.client.search_last_24_hours(query=query)
        return self._convert_to_unified(result)
    
    def search_last_week(self, query: str) -> UnifiedSearchResponse:
        """搜索本周信息"""
        result = self.client.search_last_week(query=query)
        return self._convert_to_unified(result)
