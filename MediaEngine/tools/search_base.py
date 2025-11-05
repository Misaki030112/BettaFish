"""
搜索提供商抽象基类
提供统一的接口，支持多种搜索 API 后端
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class WebpageResult:
    """网页搜索结果"""
    name: str
    url: str
    snippet: str
    display_url: Optional[str] = None
    date_last_crawled: Optional[str] = None


@dataclass
class ImageResult:
    """图片搜索结果"""
    name: str
    content_url: str
    host_page_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class StructuredDataResult:
    """
    统一的结构化数据结果
    兼容 Bocha 的模态卡和其他 API 的结构化数据
    """
    data_type: str  # 例如: weather, stock, knowledge_graph, instant_answer
    content: Dict[str, Any]
    source: Optional[str] = None  # 数据来源：bocha, serpapi, duckduckgo 等


@dataclass
class UnifiedSearchResponse:
    """
    统一的搜索响应格式
    适配所有搜索提供商
    """
    query: str
    conversation_id: Optional[str] = None
    answer: Optional[str] = None  # AI生成的摘要
    follow_ups: List[str] = field(default_factory=list)  # 建议的追问
    webpages: List[WebpageResult] = field(default_factory=list)
    images: List[ImageResult] = field(default_factory=list)
    structured_data: List[StructuredDataResult] = field(default_factory=list)
    provider: Optional[str] = None  # 使用的提供商名称
    

class SearchProviderBase(ABC):
    """
    搜索提供商抽象基类
    所有搜索 API 实现都应继承此类
    """
    
    @abstractmethod
    def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
        """
        全面综合搜索
        返回网页、图片、AI总结和结构化数据
        """
        pass
    
    @abstractmethod
    def web_search_only(self, query: str, max_results: int = 15) -> UnifiedSearchResponse:
        """
        纯网页搜索
        只返回网页结果，不生成 AI 摘要
        """
        pass
    
    @abstractmethod
    def search_for_structured_data(self, query: str) -> UnifiedSearchResponse:
        """
        结构化数据查询
        专门用于查询天气、股票、汇率等结构化信息
        """
        pass
    
    @abstractmethod
    def search_last_24_hours(self, query: str) -> UnifiedSearchResponse:
        """
        搜索24小时内信息
        """
        pass
    
    @abstractmethod
    def search_last_week(self, query: str) -> UnifiedSearchResponse:
        """
        搜索本周信息
        """
        pass
    
    def get_provider_name(self) -> str:
        """返回提供商名称"""
        return self.__class__.__name__
