# BettaFish 全球搜索与中文输出机制分析

## 用户问题

> AI获取的信息来源通过搜索引擎，我在中国，但是中国的搜索引擎一般获取不到所有国外的消息。因此我更偏向使用全球比如 google 这样的搜索引擎，来获取更加宽泛的消息。但是最后的结果应该是中文呈现给我的，即使给AI的是英文信息源。

## 系统当前实现分析

### 1. 搜索引擎配置

#### QueryEngine - 使用 Tavily API

**文件**: `QueryEngine/tools/search.py`

```python
# Line 99: Tavily 配置
kwargs['topic'] = 'general'  # ✅ 使用通用搜索，不限制地区
```

**特点**:
- ✅ **全球搜索**: `topic='general'` 可以获取全球新闻
- ✅ **不受地域限制**: Tavily 默认提供全球范围的搜索结果
- ✅ **支持多语言**: 可以搜索英文、中文等多种语言的内容

#### MediaEngine - 使用 Bocha API

**文件**: `MediaEngine/tools/search.py`

```python
# Bocha API 配置
BASE_URL = "https://api.bochaai.com/v1/ai-search"
```

**特点**:
- ✅ **多模态搜索**: 支持网页、图片、结构化数据
- ✅ **AI 摘要**: Bocha 会生成中文摘要
- ⚠️ **地域限制**: 可能偏向中文内容

### 2. 提示词中的语言约束

#### MediaEngine 提示词

**文件**: `MediaEngine/prompts/prompts.py`

```python
# Line 174
请按照以下JSON模式定义格式化输出（文字请使用中文）：

# Line 248-252: 语言表达要求
8. **语言表达要求**：
   - 准确、客观、具有分析深度
   - 既要专业又要生动有趣
   - 充分体现多模态信息的丰富性
   - 逻辑清晰，条理分明
```

#### QueryEngine 提示词

**文件**: `QueryEngine/prompts/prompts.py`

```python
# Line 186
请按照以下JSON模式定义格式化输出（文字请使用中文）：

# Line 254-258: 语言表达标准
7. **语言表达标准**：
   - 客观、准确、具有新闻专业性
   - 条理清晰，逻辑严密
   - 信息量大，避免冗余和套话
   - 既要专业又要易懂
```

#### InsightEngine 提示词

**文件**: `InsightEngine/prompts/prompts.py`

```python
# Line 259
请按照以下JSON模式定义格式化输出（文字请使用中文）：
```

**结论**: ✅ **所有 Agent 的提示词都明确要求输出中文**

### 3. 我实现的 SerpAPI 提供商配置

**文件**: `MediaEngine/tools/search_serpapi.py`

```python
# Line 127-133: 当前配置
params = {
    "q": query,
    "api_key": self.api_key,
    "engine": "google",       # ✅ 使用 Google 搜索引擎
    "num": max_results,
    "gl": "cn",               # ⚠️ 地区设置为中国
    "hl": "zh-cn"             # 语言偏好设置为中文
}
```

**问题识别**:
- ✅ `engine="google"` - 正确，使用 Google 全球搜索
- ⚠️ `gl="cn"` - **这会限制搜索结果偏向中国地区**
- ⚠️ `hl="zh-cn"` - 这只是界面语言，不影响搜索范围

## 系统工作流程

### 当前流程

```
用户查询 → 搜索引擎 → 英文/中文搜索结果 → LLM (DeepSeek/OpenAI) → 中文分析报告
           (全球范围)   (多语言内容)        (提示词要求中文)    (用户看到)
```

### 语言转换机制

**没有特殊的"黑科技"，依赖的是**:

1. **LLM 的多语言能力**
   - DeepSeek、OpenAI、Gemini 都支持多语言理解
   - 可以理解英文内容，用中文输出

2. **提示词约束**
   - 所有提示词都明确要求 "文字请使用中文"
   - LLM 会自动将英文信息源翻译成中文分析

3. **没有额外的翻译步骤**
   - 不需要调用翻译 API
   - 直接由 LLM 在生成分析时使用中文

## 推荐配置调整

### 方案 1: 优化 SerpAPI 配置（推荐）

为了获取真正的全球搜索结果，应该修改 `gl` 参数：

```python
# 修改 MediaEngine/tools/search_serpapi.py

def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
    """全面综合搜索"""
    params = {
        "q": query,
        "api_key": self.api_key,
        "engine": "google",
        "num": max_results,
        # "gl": "cn",         # ❌ 删除或修改
        "gl": "us",           # ✅ 使用美国地区获取更全球化的结果
        # "hl": "zh-cn"       # ❌ 删除，让搜索更国际化
    }
```

**效果**:
- ✅ 搜索结果不受地域限制
- ✅ 可以获取国外新闻和信息
- ✅ LLM 仍然会用中文输出（提示词约束）

### 方案 2: 配置化地区设置

添加配置选项，让用户自己选择：

```python
# config.py 中添加
SEARCH_REGION = "us"  # 或 "global", "cn", "uk" 等
SEARCH_LANGUAGE = "en"  # 搜索偏好语言

# MediaEngine/tools/search_serpapi.py
def comprehensive_search(self, query: str, max_results: int = 10) -> UnifiedSearchResponse:
    params = {
        "q": query,
        "api_key": self.api_key,
        "engine": "google",
        "num": max_results,
        "gl": getattr(config, 'SEARCH_REGION', 'us'),
        "hl": getattr(config, 'SEARCH_LANGUAGE', 'en')
    }
```

### 方案 3: 使用 Tavily 的全球搜索

Tavily 默认就是全球搜索，可以考虑在 MediaEngine 也使用 Tavily：

```python
# 在 config.py 中
MEDIA_ENGINE_SEARCH_PROVIDER = "tavily"  # 改用 Tavily

# Tavily 默认配置就是全球范围
kwargs['topic'] = 'general'  # 已经是全球搜索
```

## 现有的"提示词围栏"

### 发现的语言约束机制

1. **系统提示词中的明确要求**
   ```
   请按照以下JSON模式定义格式化输出（文字请使用中文）
   ```

2. **语言表达标准**
   ```
   语言表达要求：
   - 准确、客观、具有分析深度
   - 既要专业又要生动有趣
   ```

3. **没有额外的"黑科技"**
   - 不使用翻译 API
   - 不进行二次处理
   - 完全依赖 LLM 的多语言能力

### 这种方式的优势

✅ **简单高效**: 一步到位，无需额外翻译
✅ **保持语境**: LLM 理解内容后用中文表达，更自然
✅ **降低成本**: 不需要调用翻译 API
✅ **质量更高**: LLM 可以意译而非直译

## 总结

### 当前状态

| 方面 | 现状 | 评价 |
|-----|------|-----|
| **Tavily 搜索** | 全球范围 | ✅ 优秀 |
| **Bocha 搜索** | 可能偏向中文 | ⚠️ 需要确认 |
| **SerpAPI 搜索** | 限制中国地区 | ❌ 需要修改 |
| **LLM 输出** | 中文 | ✅ 完美 |
| **提示词约束** | 明确要求中文 | ✅ 完善 |

### 建议行动

1. **立即调整**: 修改 SerpAPI 的 `gl` 参数为 `"us"` 或移除
2. **配置化**: 添加可配置的地区和语言设置
3. **验证**: 测试 Bocha API 是否支持全球搜索
4. **文档**: 在配置文件中说明地区设置的影响

### 回答用户问题

**Q: 有没有做提示词围栏？**

**A**: ✅ 有的！所有 Agent 的提示词都明确要求 `文字请使用中文`

**Q: 还是有别的黑科技？**

**A**: ❌ 没有黑科技。依赖的是：
1. LLM 自身的多语言能力（理解英文，输出中文）
2. 提示词中的明确语言要求
3. 这种方式简单、高效、质量高

**Q: 能否使用全球搜索引擎？**

**A**: ✅ 可以！
- Tavily 已经是全球搜索
- SerpAPI 配置需要调整（把 `gl="cn"` 改为 `gl="us"`）
- 调整后，可以获取全球信息，LLM 仍然会用中文输出
