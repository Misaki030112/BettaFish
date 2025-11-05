# 搜索 API 抽象层使用指南

本指南介绍如何使用新的搜索提供商抽象层，支持多种搜索 API 后端。

## 📋 目录

1. [概述](#概述)
2. [支持的搜索提供商](#支持的搜索提供商)
3. [安装依赖](#安装依赖)
4. [快速开始](#快速开始)
5. [配置说明](#配置说明)
6. [API 参考](#api-参考)
7. [迁移指南](#迁移指南)
8. [常见问题](#常见问题)

---

## 概述

为了提高系统的灵活性和降低对单一搜索 API 的依赖，我们设计了统一的搜索提供商抽象层。

### 架构设计

```
SearchProviderBase (抽象基类)
    ├── BochaSearchProvider (Bocha AI Search)
    ├── SerpAPISearchProvider (Google Search via SerpAPI)
    └── DuckDuckGoSearchProvider (DuckDuckGo Instant Answer)
```

### 核心文件

```
MediaEngine/tools/
├── search_base.py          # 抽象基类和统一数据结构
├── search_bocha.py         # Bocha API 实现
├── search_serpapi.py       # SerpAPI 实现
├── search_duckduckgo.py    # DuckDuckGo 实现
└── search_factory.py       # 工厂模式，创建提供商实例
```

---

## 支持的搜索提供商

### 1. Bocha AI Search（默认）⭐⭐⭐⭐⭐

**优势**：
- ✅ 强大的多模态能力
- ✅ 支持结构化数据卡片（天气、股票、百科等）
- ✅ AI 摘要生成
- ✅ 追问建议
- ✅ 中文优化

**劣势**：
- ❌ 需要付费 API Key
- ❌ 免费额度有限

**申请地址**：https://open.bochaai.com/

### 2. SerpAPI（Google Search）⭐⭐⭐⭐

**优势**：
- ✅ 基于 Google 搜索，结果质量高
- ✅ 支持知识图谱、答案框
- ✅ 功能全面

**劣势**：
- ❌ 需要付费 API Key
- ❌ 免费额度较少（100次/月）
- ❌ 需要安装额外依赖

**申请地址**：https://serpapi.com/

### 3. DuckDuckGo Instant Answer⭐⭐⭐

**优势**：
- ✅ 完全免费
- ✅ 无需 API Key
- ✅ 无请求限制
- ✅ 适合查询定义、百科

**劣势**：
- ❌ 功能相对有限
- ❌ 中文支持一般
- ❌ 不支持时间过滤

**官方文档**：https://duckduckgo.com/api

---

## 安装依赖

### 基础依赖（必需）

```bash
pip install requests
```

### Bocha API（默认）

无需额外依赖，使用 `requests` 库即可。

### SerpAPI（可选）

```bash
pip install google-search-results
```

### DuckDuckGo（可选）

无需额外依赖，使用 `requests` 库即可。

---

## 快速开始

### 方法 1：使用工厂函数（推荐）

```python
from MediaEngine.tools.search_factory import create_search_provider

# 创建 Bocha 提供商（默认）
provider = create_search_provider(
    provider_type="bocha",
    api_key="your_bocha_api_key"
)

# 创建 DuckDuckGo 提供商（免费）
provider = create_search_provider(provider_type="duckduckgo")

# 创建 SerpAPI 提供商（全球搜索，推荐）
provider = create_search_provider(
    provider_type="serpapi",
    api_key="your_serpapi_key",
    region="us"  # 美国地区，获取全球化结果
)

# 创建 SerpAPI 提供商（不限制地区，最全球化）
provider = create_search_provider(
    provider_type="serpapi",
    api_key="your_serpapi_key",
    region=None  # 不限制地区
)

# 执行搜索
result = provider.comprehensive_search("人工智能最新进展")
print(f"找到 {len(result.webpages)} 个网页")
print(f"找到 {len(result.structured_data)} 个结构化数据")
```

### 方法 2：直接实例化

```python
from MediaEngine.tools.search_bocha import BochaSearchProvider
from MediaEngine.tools.search_duckduckgo import DuckDuckGoSearchProvider

# Bocha
bocha = BochaSearchProvider(api_key="your_api_key")
result = bocha.comprehensive_search("天气查询")

# DuckDuckGo
ddg = DuckDuckGoSearchProvider()
result = ddg.search_for_structured_data("Python programming language")
```

---

## 配置说明

### 在 config.py 中配置

```python
# 搜索提供商配置
MEDIA_ENGINE_SEARCH_PROVIDER = "bocha"  # 可选: bocha, serpapi, duckduckgo

# API 密钥
BOCHA_API_KEY = "your_bocha_api_key"
SERPAPI_API_KEY = "your_serpapi_key"  # 如果使用 SerpAPI
# DuckDuckGo 无需 API Key
```

### 在 MediaEngine 中使用

修改 `MediaEngine/agent.py`：

```python
from .tools.search_factory import create_search_provider

class DeepSearchAgent:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        
        # 根据配置创建搜索提供商
        provider_type = getattr(config, 'media_search_provider', 'bocha')
        
        if provider_type == "bocha":
            api_key = config.bocha_api_key
        elif provider_type == "serpapi":
            api_key = getattr(config, 'serpapi_api_key', None)
        else:
            api_key = None
        
        self.search_agency = create_search_provider(
            provider_type=provider_type,
            api_key=api_key
        )
```

---

## API 参考

所有搜索提供商都实现了以下统一接口：

### 1. comprehensive_search()

```python
def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
    """
    全面综合搜索
    返回网页、图片、AI总结和结构化数据
    """
```

**示例**：
```python
result = provider.comprehensive_search("人工智能对未来教育的影响", max_results=10)
```

### 2. web_search_only()

```python
def web_search_only(self, query: str, max_results: int = 15) -> UnifiedSearchResponse:
    """
    纯网页搜索
    只返回网页结果，不生成 AI 摘要
    """
```

### 3. search_for_structured_data()

```python
def search_for_structured_data(self, query: str) -> UnifiedSearchResponse:
    """
    结构化数据查询
    专门用于查询天气、股票、汇率等结构化信息
    """
```

**示例**：
```python
result = provider.search_for_structured_data("上海明天天气")
for sd in result.structured_data:
    print(f"数据类型: {sd.data_type}")
    print(f"内容: {sd.content}")
```

### 4. search_last_24_hours()

```python
def search_last_24_hours(self, query: str) -> UnifiedSearchResponse:
    """
    搜索24小时内信息
    """
```

### 5. search_last_week()

```python
def search_last_week(self, query: str) -> UnifiedSearchResponse:
    """
    搜索本周信息
    """
```

### 统一响应格式

```python
@dataclass
class UnifiedSearchResponse:
    query: str                              # 搜索查询
    conversation_id: Optional[str] = None   # 会话 ID（如果支持）
    answer: Optional[str] = None            # AI 生成的摘要
    follow_ups: List[str] = []              # 建议的追问
    webpages: List[WebpageResult] = []      # 网页结果
    images: List[ImageResult] = []          # 图片结果
    structured_data: List[StructuredDataResult] = []  # 结构化数据
    provider: Optional[str] = None          # 使用的提供商
```

---

## 迁移指南

### 从原始 BochaMultimodalSearch 迁移

**之前**：
```python
from .tools import BochaMultimodalSearch

self.search_agency = BochaMultimodalSearch(api_key=self.config.bocha_api_key)
result = self.search_agency.comprehensive_search("查询内容")

# 访问结果
for webpage in result.webpages:
    print(webpage.name)

for card in result.modal_cards:  # ← 注意这里
    print(card.card_type)
```

**之后**（使用抽象层）：
```python
from .tools.search_factory import create_search_provider

self.search_agency = create_search_provider(
    provider_type="bocha",
    api_key=self.config.bocha_api_key
)
result = self.search_agency.comprehensive_search("查询内容")

# 访问结果
for webpage in result.webpages:
    print(webpage.name)

for sd in result.structured_data:  # ← 改为 structured_data
    print(sd.data_type)
```

**关键变化**：
1. `BochaMultimodalSearch` → `create_search_provider()`
2. `BochaResponse` → `UnifiedSearchResponse`
3. `modal_cards` → `structured_data`

---

## 常见问题

### Q1: 如何切换搜索提供商？

**A**: 修改配置文件 `config.py`：

```python
# 使用 Bocha（默认）
MEDIA_ENGINE_SEARCH_PROVIDER = "bocha"

# 切换为 DuckDuckGo（免费）
MEDIA_ENGINE_SEARCH_PROVIDER = "duckduckgo"

# 切换为 SerpAPI
MEDIA_ENGINE_SEARCH_PROVIDER = "serpapi"
```

### Q2: 不同提供商的功能有差异吗？

**A**: 是的。功能对比：

| 功能 | Bocha | SerpAPI | DuckDuckGo |
|-----|-------|---------|------------|
| 网页搜索 | ✅ | ✅ | ⚠️ 有限 |
| 图片搜索 | ✅ | ✅ | ⚠️ 有限 |
| AI 摘要 | ✅ | ⚠️ 部分 | ⚠️ 部分 |
| 结构化数据 | ✅ 丰富 | ✅ | ⚠️ 有限 |
| 时间过滤 | ✅ | ✅ | ❌ |
| 中文优化 | ✅ | ⚠️ | ⚠️ |
| 成本 | 付费 | 付费 | 免费 |

### Q3: 如何处理 API 配额用完的情况？

**A**: 实施降级策略：

```python
try:
    # 优先使用 Bocha
    provider = create_search_provider("bocha", api_key=bocha_key)
    result = provider.comprehensive_search(query)
except Exception as e:
    print(f"Bocha 搜索失败，降级到 DuckDuckGo: {e}")
    # 降级到免费的 DuckDuckGo
    provider = create_search_provider("duckduckgo")
    result = provider.comprehensive_search(query)
```

### Q4: 如何添加新的搜索提供商？

**A**: 按以下步骤：

1. 创建新文件 `search_yourprovider.py`
2. 继承 `SearchProviderBase`
3. 实现所有抽象方法
4. 在 `search_factory.py` 中注册

示例：
```python
# MediaEngine/tools/search_yourprovider.py
from .search_base import SearchProviderBase, UnifiedSearchResponse

class YourProviderSearchProvider(SearchProviderBase):
    def __init__(self, api_key):
        self.api_key = api_key
    
    def comprehensive_search(self, query, max_results=10):
        # 实现搜索逻辑
        pass
    
    # ... 实现其他方法
```

### Q5: 性能如何？不同提供商速度差异大吗？

**A**: 实际测试结果（参考值）：

- **Bocha**: 约 2-4 秒（包含 AI 摘要生成）
- **SerpAPI**: 约 1-2 秒（Google 搜索很快）
- **DuckDuckGo**: 约 0.5-1 秒（但功能有限）

建议根据任务需求选择：
- 需要结构化数据 → Bocha
- 需要快速网页搜索 → SerpAPI
- 简单查询 → DuckDuckGo

---

## 示例代码

### 完整示例：对比三种提供商

```python
from MediaEngine.tools.search_factory import create_search_provider

query = "人工智能最新进展"

providers = [
    ("bocha", {"api_key": "your_bocha_key"}),
    ("serpapi", {"api_key": "your_serpapi_key"}),
    ("duckduckgo", {})
]

for provider_type, kwargs in providers:
    print(f"\n{'='*60}")
    print(f"使用 {provider_type.upper()} 搜索")
    print('='*60)
    
    try:
        provider = create_search_provider(provider_type, **kwargs)
        result = provider.comprehensive_search(query, max_results=5)
        
        print(f"查询: {result.query}")
        print(f"提供商: {result.provider}")
        print(f"网页结果: {len(result.webpages)} 条")
        print(f"结构化数据: {len(result.structured_data)} 个")
        
        if result.answer:
            print(f"AI摘要: {result.answer[:100]}...")
        
        if result.structured_data:
            print(f"结构化数据类型: {[sd.data_type for sd in result.structured_data]}")
        
    except Exception as e:
        print(f"错误: {e}")
```

---

## 全球搜索与中文输出

### 语言处理机制

BettaFish 系统支持**全球搜索 + 中文输出**的工作模式：

```
英文搜索结果 → LLM (DeepSeek/OpenAI) → 中文分析报告
  (全球范围)        (理解英文)         (输出中文)
```

#### 工作原理

1. **搜索引擎获取全球信息**
   - Tavily: 默认全球搜索
   - SerpAPI: 可配置地区（推荐 `region="us"` 或 `region=None`）
   - Bocha: 多模态搜索

2. **LLM 自动语言转换**
   - 所有提示词都明确要求："文字请使用中文"
   - LLM 理解英文内容，用中文表达分析
   - 无需额外翻译 API

3. **无"黑科技"，依赖标准能力**
   - ✅ LLM 的多语言理解能力
   - ✅ 提示词中的语言约束
   - ✅ 一步到位，质量更高

### SerpAPI 地区配置

为获取全球化的搜索结果，推荐配置：

```python
# 方案 1: 美国地区（推荐，平衡全球化和质量）
provider = create_search_provider(
    provider_type="serpapi",
    api_key="your_key",
    region="us"  # 美国地区
)

# 方案 2: 不限制地区（最全球化）
provider = create_search_provider(
    provider_type="serpapi",
    api_key="your_key",
    region=None  # 无地区限制
)

# 方案 3: 中国地区（偏向中文内容）
provider = create_search_provider(
    provider_type="serpapi",
    api_key="your_key",
    region="cn"  # 中国地区
)
```

**地区参数说明**：
- `region="us"`: 获取国际新闻和全球化内容（推荐）
- `region="cn"`: 偏向中国本地内容
- `region="uk"`: 英国地区
- `region=None`: 完全不限制地区（最全球化）

**注意**：无论选择哪个地区，LLM 都会用中文输出分析报告。

### 配置示例

在 `config.py` 中添加：

```python
# 搜索提供商配置
MEDIA_ENGINE_SEARCH_PROVIDER = "serpapi"  # 使用 SerpAPI

# SerpAPI 配置
SERPAPI_API_KEY = "your_serpapi_key"
SERPAPI_REGION = "us"  # 或 None, "cn", "uk" 等
```

在代码中使用：

```python
from MediaEngine.tools import create_search_provider
import config

provider = create_search_provider(
    provider_type=config.MEDIA_ENGINE_SEARCH_PROVIDER,
    api_key=config.SERPAPI_API_KEY,
    region=getattr(config, 'SERPAPI_REGION', 'us')
)

# 搜索全球新闻，获得中文分析
result = provider.comprehensive_search("latest AI developments")
# LLM 会理解英文搜索结果，生成中文分析报告
```

---

## 总结

搜索 API 抽象层提供了：

✅ **灵活性**：轻松切换不同的搜索提供商  
✅ **可维护性**：统一的接口，降低维护成本  
✅ **可扩展性**：容易添加新的搜索提供商  
✅ **降级策略**：付费 API 失败时可降级到免费 API  

建议在生产环境中保留 Bocha 作为主要提供商，DuckDuckGo 作为备选方案。
