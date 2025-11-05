"""
工具调用模块
提供外部工具接口，如多模态搜索等
"""

# 原始 Bocha 实现（保持向后兼容）
from .search import (
    BochaMultimodalSearch,
    WebpageResult,
    ImageResult,
    ModalCardResult,
    BochaResponse,
    print_response_summary
)

# 新的搜索提供商抽象层
from .search_base import (
    SearchProviderBase,
    UnifiedSearchResponse,
    StructuredDataResult
)

from .search_factory import (
    create_search_provider,
    get_available_providers
)

# 可选：如果需要直接导入具体实现
try:
    from .search_bocha import BochaSearchProvider
    from .search_duckduckgo import DuckDuckGoSearchProvider
    from .search_serpapi import SerpAPISearchProvider
except ImportError:
    # SerpAPI 可能未安装依赖
    BochaSearchProvider = None
    DuckDuckGoSearchProvider = None
    SerpAPISearchProvider = None

__all__ = [
    # 原始接口（向后兼容）
    "BochaMultimodalSearch",
    "WebpageResult", 
    "ImageResult",
    "ModalCardResult",
    "BochaResponse",
    "print_response_summary",
    
    # 新的抽象层
    "SearchProviderBase",
    "UnifiedSearchResponse",
    "StructuredDataResult",
    "create_search_provider",
    "get_available_providers",
    
    # 具体实现
    "BochaSearchProvider",
    "DuckDuckGoSearchProvider",
    "SerpAPISearchProvider",
]
