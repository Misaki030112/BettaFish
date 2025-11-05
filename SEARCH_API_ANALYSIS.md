# BettaFish 搜索 API 深度分析报告

## 项目概述

经过深入分析 BettaFish（微舆）项目的代码结构、架构方式和实现方式，本报告将详细评估当前使用的搜索 API，并探讨替换为其他 API 提供商的可行性。

---

## 一、当前搜索 API 使用情况

### 1.1 双搜索引擎架构

项目采用了**双搜索引擎架构**，针对不同的 Agent 使用不同的搜索 API：

#### **MediaEngine（媒体引擎）**
- **使用 API**: Bocha AI Search API
- **文件位置**: `MediaEngine/tools/search.py`
- **客户端类**: `BochaMultimodalSearch`
- **配置项**: `BOCHA_API_KEY` / `BOCHA_Web_Search_API_KEY`

#### **QueryEngine（查询引擎）**
- **使用 API**: Tavily Search API
- **文件位置**: `QueryEngine/tools/search.py`
- **客户端类**: `TavilyNewsAgency`
- **配置项**: `TAVILY_API_KEY`

### 1.2 架构集成方式

```
Flask 主应用 (app.py)
    ↓
配置文件 (config.py) ← 存储所有 API 密钥
    ↓
├─ MediaEngine/agent.py
│   └─ BochaMultimodalSearch (self.search_agency)
│       └─ 5种多模态搜索工具
│
└─ QueryEngine/agent.py
    └─ TavilyNewsAgency (self.search_agency)
        └─ 6种新闻搜索工具
```

---

## 二、Bocha API 实现分析

### 2.1 代码实现方式

**核心文件**: `MediaEngine/tools/search.py` (共 387 行)

#### **技术栈**
```python
import requests  # HTTP 请求
from dataclasses import dataclass  # 数据结构
from retry_helper import with_graceful_retry  # 重试机制
```

#### **API 端点**
```python
BASE_URL = "https://api.bochaai.com/v1/ai-search"
```

#### **认证方式**
```python
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': '*/*'
}
```

### 2.2 核心功能特性

Bocha API 提供了 **5 种专用搜索工具**：

| 工具名称 | 功能描述 | 独特性 |
|---------|---------|--------|
| `comprehensive_search()` | 全面综合搜索 | 返回网页、图片、AI总结、追问建议 |
| `web_search_only()` | 纯网页搜索 | 不请求AI总结，速度快 |
| `search_for_structured_data()` | 结构化数据查询 | **核心特色**：返回模态卡 |
| `search_last_24_hours()` | 24小时内信息 | 时效性过滤 |
| `search_last_week()` | 一周内信息 | 时效性过滤 |

### 2.3 "模态卡"技术 - Bocha 的核心优势

**什么是模态卡（Modal Card）？**

这是 Bocha API 最具特色的功能，能够返回**结构化的多模态数据**：

```python
@dataclass
class ModalCardResult:
    """模态卡结构化数据结果"""
    card_type: str  # 例如: weather_china, stock, baike_pro, medical_common
    content: Dict[str, Any]  # 解析后的JSON内容
```

**支持的模态卡类型**：
- 天气卡片（weather_china）
- 股票卡片（stock）
- 百科卡片（baike_pro）
- 医疗卡片（medical_common）
- 汇率卡片
- 火车票信息
- 汽车参数
- 视频卡片（video）

**实现代码片段**：
```python
# 从 API 响应中解析模态卡
elif msg_type == 'source':
    if content_type == 'webpage':
        # 处理网页结果
    elif content_type == 'image':
        # 处理图片结果
    else:
        # 其他所有类型都视为模态卡
        final_response.modal_cards.append(ModalCardResult(
            card_type=content_type,
            content=content_data
        ))
```

### 2.4 响应数据结构

```python
@dataclass
class BochaResponse:
    query: str
    conversation_id: Optional[str] = None
    answer: Optional[str] = None  # AI生成的总结答案
    follow_ups: List[str] = field(default_factory=list)  # AI生成的追问
    webpages: List[WebpageResult] = field(default_factory=list)
    images: List[ImageResult] = field(default_factory=list)
    modal_cards: List[ModalCardResult] = field(default_factory=list)  # 核心特色
```

### 2.5 重试机制

项目使用了**优雅的重试装饰器**：

```python
@with_graceful_retry(SEARCH_API_RETRY_CONFIG, default_return=BochaResponse(query="搜索失败"))
def _search_internal(self, **kwargs) -> BochaResponse:
    # 实现搜索逻辑
```

**重试配置** (`utils/retry_helper.py`)：
- 使用 `tenacity` 库实现
- 支持指数退避（exponential backoff）
- 网络错误自动重试
- 失败后返回默认值而不是崩溃

---

## 三、是否存在"黑科技"？

### 评估结论：**否，实现非常透明和标准**

#### 3.1 代码质量评估

✅ **优点**：
1. **清晰的抽象层次**：使用 dataclass 定义数据结构
2. **专业的错误处理**：集成重试机制和异常捕获
3. **面向 Agent 的设计**：每个工具都有明确的单一职责
4. **良好的文档**：每个方法都有详细的中文文档字符串
5. **类型提示**：使用 Python 类型注解增强代码可读性

❌ **没有黑科技**：
1. 使用标准的 `requests` 库进行 HTTP 调用
2. 简单的 Bearer Token 认证
3. JSON 格式的请求和响应
4. 没有混淆、加密或特殊的协议

#### 3.2 核心实现逻辑

```python
def _search_internal(self, **kwargs) -> BochaResponse:
    payload = {"stream": False}
    payload.update(kwargs)
    
    # 标准的 HTTP POST 请求
    response = requests.post(
        self.BASE_URL, 
        headers=self._headers, 
        json=payload, 
        timeout=30
    )
    response.raise_for_status()
    
    # 标准的 JSON 解析
    response_dict = response.json()
    
    # 手动解析响应结构
    return self._parse_search_response(response_dict, query)
```

**结论**：这是一个非常标准的 REST API 客户端实现，没有使用任何特殊技术。

---

## 四、替换为其他 API 的可行性分析

### 4.1 替换难度评估：**容易到中等**

由于代码已经有良好的抽象设计，替换 API 是可行的。

### 4.2 需要考虑的因素

#### **功能对比**

| 功能特性 | Bocha API | 替代方案可行性 |
|---------|----------|--------------|
| 网页搜索 | ✅ | ✅ 几乎所有搜索 API 都支持 |
| 图片搜索 | ✅ | ✅ Google, Bing, SerpAPI 等支持 |
| AI 摘要生成 | ✅ | ⚠️ 需要额外集成 LLM（如项目已有的 DeepSeek/OpenAI） |
| 追问建议 | ✅ | ⚠️ 需要额外集成 LLM |
| **模态卡（结构化数据）** | ✅ | ⚠️ **这是最大挑战** |

#### **模态卡的替代方案**

Bocha 的模态卡是其核心优势，替换时需要特别注意：

1. **SerpAPI/Bing API**：
   - 可以获取某些结构化数据（如天气、股票）
   - 但格式和丰富度可能不如 Bocha

2. **自建方案**：
   - 网页搜索 → 使用 SerpAPI/Tavily
   - 结构化数据 → 调用专门的天气 API、股票 API 等
   - AI 摘要 → 使用项目已有的 LLM

### 4.3 推荐的替代 API

#### **选项 1: SerpAPI** ⭐⭐⭐⭐⭐
- **官网**: https://serpapi.com/
- **优势**:
  - 支持 Google、Bing、百度等多个搜索引擎
  - 提供结构化数据（知识图谱、答案框等）
  - 有 Python SDK：`pip install google-search-results`
- **劣势**:
  - 付费较贵（免费额度 100 次/月）
  - 模态卡丰富度可能不如 Bocha

**实现示例**：
```python
from serpapi import GoogleSearch

class SerpAPISearch:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def comprehensive_search(self, query: str) -> BochaResponse:
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google"  # 或 "baidu"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # 转换为 BochaResponse 格式
        return self._parse_to_bocha_format(results)
```

#### **选项 2: DuckDuckGo Instant Answer API** ⭐⭐⭐⭐
- **官网**: https://duckduckgo.com/api
- **优势**:
  - **完全免费**
  - 提供即时答案（类似模态卡）
  - 无需 API key
- **劣势**:
  - 功能相对有限
  - 中文支持一般

**实现示例**：
```python
import requests

def duckduckgo_search(query):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### **选项 3: Bing Search API** ⭐⭐⭐⭐
- **官网**: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
- **优势**:
  - 官方 API，稳定可靠
  - 支持网页、图片、新闻、视频搜索
  - 有结构化数据（Entities, Computation）
- **劣势**:
  - 免费额度 3000 次/月
  - 需要 Azure 账号

#### **选项 4: 混合方案（推荐）** ⭐⭐⭐⭐⭐
```
- 网页搜索：保留 Tavily（已在 QueryEngine 中使用）
- 结构化数据：
  * 天气：调用免费天气 API（如 OpenWeatherMap）
  * 股票：调用免费股票 API（如 Alpha Vantage）
  * 百科：爬取维基百科或调用百度百科 API
- AI 摘要：使用项目已有的 DeepSeek/OpenAI
```

### 4.4 保持 Bocha 的理由

❌ **不建议替换的情况**：

1. **模态卡是核心需求**：如果项目严重依赖结构化多模态数据
2. **已有 API 额度**：Bocha API 如果已购买且够用
3. **中文优化**：Bocha 对中文搜索优化可能更好
4. **开发成本**：替换需要重写和测试大量代码

---

## 五、实施方案建议

### 5.1 短期方案（保留现状）

**建议**：保留 Bocha API，因为：
1. 模态卡功能难以完美替代
2. 代码已经稳定运行
3. 项目对多模态数据有明确需求

### 5.2 中期方案（增加备选）

**建议**：实现搜索 API 抽象层，支持多种后端

```python
# MediaEngine/tools/search_factory.py
from abc import ABC, abstractmethod

class SearchProvider(ABC):
    @abstractmethod
    def comprehensive_search(self, query: str) -> BochaResponse:
        pass
    
    @abstractmethod
    def search_for_structured_data(self, query: str) -> BochaResponse:
        pass

class BochaProvider(SearchProvider):
    # 现有实现
    pass

class SerpAPIProvider(SearchProvider):
    # 新实现
    pass

def create_search_provider(provider_type: str) -> SearchProvider:
    if provider_type == "bocha":
        return BochaProvider(...)
    elif provider_type == "serpapi":
        return SerpAPIProvider(...)
```

**配置文件**：
```python
# config.py
MEDIA_ENGINE_SEARCH_PROVIDER = "bocha"  # 或 "serpapi"
```

### 5.3 长期方案（完全自建）

如果要摆脱对第三方搜索 API 的依赖：

1. **网页搜索**：
   - 自建爬虫（基于 Playwright，项目已有）
   - 使用搜索引擎爬虫库（如 `googlesearch-python`）

2. **结构化数据**：
   - 集成多个免费 API（天气、股票、汇率等）
   - 爬取百科、百度知识图谱

3. **AI 摘要**：
   - 使用项目已有的 LLM（DeepSeek/OpenAI/Gemini）

---

## 六、总结与建议

### 核心发现

1. **实现质量高**：Bocha API 的集成代码质量很好，没有"黑科技"，都是标准实践
2. **架构清晰**：良好的抽象设计使得替换成为可能
3. **模态卡是核心**：这是 Bocha 的最大优势，也是替换的最大障碍
4. **双引擎设计合理**：MediaEngine 用 Bocha，QueryEngine 用 Tavily，各有侧重

### 最终建议

#### 如果预算充足
✅ **保留 Bocha API**
- 功能完整且优化良好
- 模态卡功能独特
- 已有稳定实现

#### 如果需要降低成本
⚠️ **考虑混合方案**
- 普通搜索：SerpAPI 或 DuckDuckGo
- 结构化数据：集成多个免费 API
- AI 摘要：使用项目已有的 LLM

#### 如果要完全开源
🔧 **实施抽象层**
- 定义统一的搜索接口
- 支持多种后端实现
- 可根据查询类型动态选择

### 技术债务评估

当前 Bocha API 的使用**没有造成技术债务**：
- ✅ 代码清晰易维护
- ✅ 依赖关系明确
- ✅ 容易测试和模拟
- ✅ 可以平滑迁移

---

## 七、代码示例：实现搜索抽象层

如果决定支持多种搜索 API，建议使用以下设计：

```python
# MediaEngine/tools/search_base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class UnifiedSearchResponse:
    """统一的搜索响应格式"""
    query: str
    answer: Optional[str] = None
    webpages: List[Dict] = None
    images: List[Dict] = None
    structured_data: List[Dict] = None  # 通用的结构化数据
    
class SearchProviderBase(ABC):
    """搜索提供商基类"""
    
    @abstractmethod
    def comprehensive_search(self, query: str) -> UnifiedSearchResponse:
        pass
    
    @abstractmethod
    def web_search_only(self, query: str) -> UnifiedSearchResponse:
        pass
    
    @abstractmethod
    def search_for_structured_data(self, query: str) -> UnifiedSearchResponse:
        pass

# MediaEngine/tools/search_bocha.py
class BochaSearchProvider(SearchProviderBase):
    """Bocha API 实现"""
    
    def __init__(self, api_key: str):
        self.client = BochaMultimodalSearch(api_key)
    
    def comprehensive_search(self, query: str) -> UnifiedSearchResponse:
        result = self.client.comprehensive_search(query)
        # 转换为统一格式
        return self._convert_to_unified(result)

# MediaEngine/tools/search_serpapi.py
class SerpAPISearchProvider(SearchProviderBase):
    """SerpAPI 实现"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def comprehensive_search(self, query: str) -> UnifiedSearchResponse:
        # SerpAPI 实现
        pass

# MediaEngine/agent.py 修改
from .tools.search_factory import create_search_provider

class DeepSearchAgent:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        
        # 根据配置创建搜索提供商
        provider_type = getattr(config, 'search_provider', 'bocha')
        self.search_agency = create_search_provider(
            provider_type=provider_type,
            config=config
        )
```

---

## 附录：Tavily API 分析

项目同时使用了 Tavily API（在 QueryEngine 中），其实现方式类似：

- **文件**: `QueryEngine/tools/search.py`
- **客户端**: `TavilyNewsAgency`
- **功能**: 6 种新闻搜索工具
- **特点**: 专注于新闻和时效性内容

**与 Bocha 的差异**：
- Tavily 使用官方 SDK：`from tavily import TavilyClient`
- Bocha 使用自建客户端：直接调用 REST API
- Tavily 侧重新闻，Bocha 侧重多模态

---

## 结论

BettaFish 项目的搜索 API 集成**实现优秀、架构合理**，没有使用任何"黑科技"。Bocha API 的核心价值在于其**模态卡功能**，这是其他搜索 API 难以完美替代的特性。

**最终建议**：
1. **短期**：保持现状，Bocha + Tavily 的双引擎架构已经很好
2. **中期**：如有需求，实现搜索抽象层以支持多种后端
3. **长期**：根据业务发展考虑自建搜索能力

替换 API 在技术上**完全可行**，但需要权衡功能完整性和开发成本。
