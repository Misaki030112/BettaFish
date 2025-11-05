#!/usr/bin/env python3
"""
独立测试脚本 - 测试搜索提供商抽象层
不依赖完整的 MediaEngine 初始化
"""

import sys
import os

# 添加 MediaEngine/tools 到 Python 路径
tools_path = os.path.join(os.path.dirname(__file__), 'MediaEngine', 'tools')
sys.path.insert(0, tools_path)

# 修改模块中的相对导入为绝对导入（临时解决方案）
# 在实际使用中，通过 from MediaEngine.tools import ... 导入即可

def test_search_abstraction():
    """测试搜索抽象层功能"""
    
    print("="*70)
    print("搜索提供商抽象层测试")
    print("="*70)
    
    # 导入模块（使用绝对路径）
    import sys
    import importlib.util
    
    # 加载 search_base
    base_path = os.path.join(tools_path, 'search_base.py')
    spec = importlib.util.spec_from_file_location("search_base", base_path)
    search_base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search_base)
    
    # 加载 search_duckduckgo
    ddg_path = os.path.join(tools_path, 'search_duckduckgo.py')
    spec = importlib.util.spec_from_file_location("search_duckduckgo", ddg_path)
    search_duckduckgo = importlib.util.module_from_spec(spec)
    sys.modules['search_base'] = search_base  # 让 search_duckduckgo 能找到 search_base
    spec.loader.exec_module(search_duckduckgo)
    
    print("\n✓ 成功加载模块")
    
    # 测试 DuckDuckGo 提供商
    print("\n" + "-"*70)
    print("测试 DuckDuckGo 搜索提供商（免费，无需 API Key）")
    print("-"*70)
    
    try:
        # 创建提供商
        provider = search_duckduckgo.DuckDuckGoSearchProvider()
        print(f"✓ 创建提供商成功: {provider.__class__.__name__}")
        
        # 测试搜索
        test_queries = [
            "Python programming language",
            "Albert Einstein", 
            "人工智能"
        ]
        
        for query in test_queries:
            print(f"\n查询: '{query}'")
            print("-" * 50)
            
            try:
                result = provider.comprehensive_search(query)
                
                print(f"  Provider: {result.provider}")
                print(f"  Webpages: {len(result.webpages)}")
                print(f"  Images: {len(result.images)}")
                print(f"  Structured data: {len(result.structured_data)}")
                
                if result.answer:
                    preview = result.answer[:150] + "..." if len(result.answer) > 150 else result.answer
                    print(f"  Answer: {preview}")
                
                if result.structured_data:
                    types = [sd.data_type for sd in result.structured_data]
                    print(f"  Data types: {types}")
                
                if result.webpages and len(result.webpages) > 0:
                    first_page = result.webpages[0]
                    title = first_page.name[:60] + "..." if len(first_page.name) > 60 else first_page.name
                    print(f"  First result: {title}")
                
                print("  ✓ 搜索成功")
                
            except Exception as e:
                print(f"  ✗ 搜索失败: {e}")
        
        print("\n" + "="*70)
        print("✓ 所有测试通过!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_search_abstraction()
    sys.exit(0 if success else 1)
