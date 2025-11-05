"""
搜索提供商工厂
根据配置创建相应的搜索提供商实例
"""

from typing import Optional
from .search_base import SearchProviderBase
from .search_bocha import BochaSearchProvider


def create_search_provider(
    provider_type: str = "bocha",
    api_key: Optional[str] = None,
    region: Optional[str] = None,
    **kwargs
) -> SearchProviderBase:
    """
    根据提供商类型创建搜索提供商实例
    
    Args:
        provider_type: 提供商类型，可选值:
            - "bocha": Bocha AI Search（默认）
            - "serpapi": SerpAPI (Google Search)
            - "duckduckgo": DuckDuckGo Instant Answer（免费）
        api_key: API 密钥（某些提供商需要）
        region: 搜索地区代码（仅 SerpAPI 支持）
            - "us": 美国（推荐用于全球化搜索）
            - "cn": 中国
            - "uk": 英国
            - None: 不限制地区（最全球化）
        **kwargs: 额外的配置参数
        
    Returns:
        搜索提供商实例
        
    Raises:
        ValueError: 不支持的提供商类型
    """
    provider_type = provider_type.lower()
    
    if provider_type == "bocha":
        return BochaSearchProvider(api_key=api_key)
    
    elif provider_type == "serpapi":
        from .search_serpapi import SerpAPISearchProvider
        return SerpAPISearchProvider(api_key=api_key, region=region)
    
    elif provider_type == "duckduckgo":
        from .search_duckduckgo import DuckDuckGoSearchProvider
        return DuckDuckGoSearchProvider()
    
    else:
        raise ValueError(
            f"不支持的搜索提供商类型: {provider_type}\n"
            f"支持的类型: bocha, serpapi, duckduckgo"
        )


def get_available_providers() -> dict:
    """
    获取所有可用的搜索提供商信息
    
    Returns:
        提供商信息字典
    """
    return {
        "bocha": {
            "name": "Bocha AI Search",
            "description": "强大的多模态搜索，支持结构化数据卡片",
            "requires_api_key": True,
            "features": [
                "网页搜索",
                "图片搜索",
                "AI 摘要生成",
                "模态卡（天气、股票、百科等）",
                "追问建议",
                "时间过滤"
            ],
            "url": "https://open.bochaai.com/"
        },
        "serpapi": {
            "name": "SerpAPI",
            "description": "Google 搜索 API，功能全面",
            "requires_api_key": True,
            "features": [
                "网页搜索",
                "图片搜索",
                "知识图谱",
                "答案框",
                "相关问题",
                "时间过滤"
            ],
            "url": "https://serpapi.com/",
            "note": "需要安装: pip install google-search-results"
        },
        "duckduckgo": {
            "name": "DuckDuckGo Instant Answer",
            "description": "免费的即时答案 API",
            "requires_api_key": False,
            "features": [
                "即时答案",
                "定义查询",
                "相关主题",
                "图片（有限）"
            ],
            "url": "https://duckduckgo.com/api",
            "note": "完全免费，但功能有限"
        }
    }


def print_provider_info():
    """打印所有可用提供商的信息"""
    providers = get_available_providers()
    
    print("\n" + "="*70)
    print("可用的搜索提供商")
    print("="*70)
    
    for key, info in providers.items():
        print(f"\n【{key.upper()}】{info['name']}")
        print(f"描述: {info['description']}")
        print(f"需要 API Key: {'是' if info['requires_api_key'] else '否'}")
        print(f"官网: {info['url']}")
        
        if 'note' in info:
            print(f"注意: {info['note']}")
        
        print("功能:")
        for feature in info['features']:
            print(f"  - {feature}")
    
    print("\n" + "="*70)


# 使用示例
if __name__ == "__main__":
    print_provider_info()
    
    print("\n\n创建提供商实例示例:")
    print("-" * 70)
    
    # 示例 1: 创建 Bocha 提供商（需要 API Key）
    print("\n1. Bocha 提供商:")
    try:
        provider = create_search_provider(
            provider_type="bocha",
            api_key="your_bocha_api_key"  # 替换为实际的 API Key
        )
        print(f"   创建成功: {provider.get_provider_name()}")
    except Exception as e:
        print(f"   创建失败: {e}")
    
    # 示例 2: 创建 DuckDuckGo 提供商（免费，无需 API Key）
    print("\n2. DuckDuckGo 提供商:")
    try:
        provider = create_search_provider(provider_type="duckduckgo")
        print(f"   创建成功: {provider.get_provider_name()}")
        
        # 测试搜索
        result = provider.comprehensive_search("Python programming")
        print(f"   测试搜索成功，找到 {len(result.structured_data)} 个结构化数据")
    except Exception as e:
        print(f"   创建/测试失败: {e}")
    
    # 示例 3: 创建 SerpAPI 提供商（需要 API Key）
    print("\n3. SerpAPI 提供商:")
    try:
        provider = create_search_provider(
            provider_type="serpapi",
            api_key="your_serpapi_key"  # 替换为实际的 API Key
        )
        print(f"   创建成功: {provider.get_provider_name()}")
    except Exception as e:
        print(f"   创建失败: {e}")
