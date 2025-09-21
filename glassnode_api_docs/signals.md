# 交易信号 (signals)

## 📋 概述

交易信号和预警指标，提供买卖信号、风险预警等决策支持。

本类别共包含 **14** 个API端点，分为 **5** 个子类别。

## 🗂️ 指标分类

| 子类别 | 指标数量 | 主要功能 |
|--------|----------|----------|
| BTC | 10 | 提供专门的数据分析 |
| ALTCOIN | 1 | 提供专门的数据分析 |
| ECOSYSTEM | 1 | 提供专门的数据分析 |
| MCAP | 1 | 提供专门的数据分析 |
| L1 | 1 | 提供专门的数据分析 |

## 🎨 指标体系结构图

```mermaid
graph TD
    A["交易信号<br/>共14个指标"]
    A:::mainNode
    
    A --> B1["BTC<br/>10个指标"]
    B1:::categoryNode
    B1 --> C1_1["Bitcoin Risk Signal<br/><i>btc_risk_index</i>"]
    C1_1:::metricNode
    C1_1 --> D1_1["Bitcoin Risk Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_1:::descNode
    B1 --> C1_2["Bitcoin Sharpe Signal<br/><i>btc_sharpe_signal</i>"]
    C1_2:::metricNode
    C1_2 --> D1_2["Bitcoin Sharpe Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_2:::descNode
    B1 --> C1_3["Bitcoin Sharpe Signal - Indica<br/><i>btc_bss_indicator_1</i>"]
    C1_3:::metricNode
    C1_3 --> D1_3["Bitcoin Sharpe Signal - Indicator I。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_3:::descNode
    A --> B2["ALTCOIN<br/>1个指标"]
    B2:::categoryNode
    B2 --> C2_1["Altcoin Cycle Signal<br/><i>altcoin_index</i>"]
    C2_1:::metricNode
    C2_1 --> D2_1["Altcoin Cycle Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D2_1:::descNode
    A --> B3["ECOSYSTEM<br/>1个指标"]
    B3:::categoryNode
    B3 --> C3_1["Ecosystem Momentum Signal<br/><i>ecosystem_momentum_index</i>"]
    C3_1:::metricNode
    C3_1 --> D3_1["Ecosystem Momentum Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D3_1:::descNode
    A --> B4["MCAP<br/>1个指标"]
    B4:::categoryNode
    B4 --> C4_1["Marketcap returns vs BTC<br/><i>mcap_returns_vs_btc</i>"]
    C4_1:::metricNode
    C4_1 --> D4_1["Marketcap returns vs BTC。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D4_1:::descNode
    A --> B5["L1<br/>1个指标"]
    B5:::categoryNode
    B5 --> C5_1["Token returns vs BTC<br/><i>l1_native_tokens_returns_vs_btc</i>"]
    C5_1:::metricNode
    C5_1 --> D5_1["Token returns vs BTC。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D5_1:::descNode
    
    %% 高对比度样式
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef descNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000,font-size:10px
```

## 📂 详细指标说明

### 📊 BTC（10个指标）

本子类别包含以下详细指标：

#### 1. Bitcoin Risk Signal

- **指标代码**: `btc_risk_index`
- **API路径**: `/v1/metrics/signals/btc_risk_index`
- **英文名称**: Bitcoin Risk Signal

**📝 详细说明**：
Bitcoin Risk Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Risk Signal数据
df = client.get_metric(
    "/v1/metrics/signals/btc_risk_index",
    asset="BTC",
    resolution="24h"
)
```

---

#### 2. Bitcoin Sharpe Signal

- **指标代码**: `btc_sharpe_signal`
- **API路径**: `/v1/metrics/signals/btc_sharpe_signal`
- **英文名称**: Bitcoin Sharpe Signal

**📝 详细说明**：
Bitcoin Sharpe Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Sharpe Signal数据
df = client.get_metric(
    "/v1/metrics/signals/btc_sharpe_signal",
    asset="BTC",
    resolution="24h"
)
```

---

#### 3. Bitcoin Sharpe Signal - Indica

- **指标代码**: `btc_bss_indicator_1`
- **API路径**: `/v1/metrics/signals/btc_bss_indicator_1`
- **英文名称**: Bitcoin Sharpe Signal - Indicator I

**📝 详细说明**：
Bitcoin Sharpe Signal - Indicator I。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Sharpe Signal - Indica数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_indicator_1",
    asset="BTC",
    resolution="24h"
)
```

---

#### 4. Bitcoin Sharpe Signal - Indica

- **指标代码**: `btc_bss_indicator_2`
- **API路径**: `/v1/metrics/signals/btc_bss_indicator_2`
- **英文名称**: Bitcoin Sharpe Signal - Indicator II

**📝 详细说明**：
Bitcoin Sharpe Signal - Indicator II。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Sharpe Signal - Indica数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_indicator_2",
    asset="BTC",
    resolution="24h"
)
```

---

#### 5. Bitcoin Sharpe Signal - Indica

- **指标代码**: `btc_bss_indicator_3`
- **API路径**: `/v1/metrics/signals/btc_bss_indicator_3`
- **英文名称**: Bitcoin Sharpe Signal - Indicator III

**📝 详细说明**：
Bitcoin Sharpe Signal - Indicator III。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Sharpe Signal - Indica数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_indicator_3",
    asset="BTC",
    resolution="24h"
)
```

---

#### 6. Bitcoin Sharpe Signal - Indica

- **指标代码**: `btc_bss_indicator_4`
- **API路径**: `/v1/metrics/signals/btc_bss_indicator_4`
- **英文名称**: Bitcoin Sharpe Signal - Indicator IV

**📝 详细说明**：
Bitcoin Sharpe Signal - Indicator IV。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Sharpe Signal - Indica数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_indicator_4",
    asset="BTC",
    resolution="24h"
)
```

---

#### 7. Bitcoin Sharpe Signal Short

- **指标代码**: `btc_bss_short`
- **API路径**: `/v1/metrics/signals/btc_bss_short`
- **英文名称**: Bitcoin Sharpe Signal Short

**📝 详细说明**：
Bitcoin Sharpe Signal Short。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Bitcoin Sharpe Signal Short数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_short",
    asset="BTC",
    resolution="24h"
)
```

---

#### 8. BSS Goldilocks Short Signal

- **指标代码**: `btc_bss_goldilocks_short`
- **API路径**: `/v1/metrics/signals/btc_bss_goldilocks_short`
- **英文名称**: BSS Goldilocks Short Signal

**📝 详细说明**：
BSS Goldilocks Short Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取BSS Goldilocks Short Signal数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_goldilocks_short",
    asset="BTC",
    resolution="24h"
)
```

---

#### 9. BSS Goldilocks Signal

- **指标代码**: `btc_bss_goldilocks`
- **API路径**: `/v1/metrics/signals/btc_bss_goldilocks`
- **英文名称**: BSS Goldilocks Signal

**📝 详细说明**：
BSS Goldilocks Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取BSS Goldilocks Signal数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_goldilocks",
    asset="BTC",
    resolution="24h"
)
```

---

#### 10. Intraday Bitcoin Sharpe Signal

- **指标代码**: `btc_bss_v2`
- **API路径**: `/v1/metrics/signals/btc_bss_v2`
- **英文名称**: Intraday Bitcoin Sharpe Signal

**📝 详细说明**：
Intraday Bitcoin Sharpe Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Intraday Bitcoin Sharpe Signal数据
df = client.get_metric(
    "/v1/metrics/signals/btc_bss_v2",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 ALTCOIN（1个指标）

本子类别包含以下详细指标：

#### 1. Altcoin Cycle Signal

- **指标代码**: `altcoin_index`
- **API路径**: `/v1/metrics/signals/altcoin_index`
- **英文名称**: Altcoin Cycle Signal

**📝 详细说明**：
Altcoin Cycle Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Altcoin Cycle Signal数据
df = client.get_metric(
    "/v1/metrics/signals/altcoin_index",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 ECOSYSTEM（1个指标）

本子类别包含以下详细指标：

#### 1. Ecosystem Momentum Signal

- **指标代码**: `ecosystem_momentum_index`
- **API路径**: `/v1/metrics/signals/ecosystem_momentum_index`
- **英文名称**: Ecosystem Momentum Signal

**📝 详细说明**：
Ecosystem Momentum Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Ecosystem Momentum Signal数据
df = client.get_metric(
    "/v1/metrics/signals/ecosystem_momentum_index",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 MCAP（1个指标）

本子类别包含以下详细指标：

#### 1. Marketcap returns vs BTC

- **指标代码**: `mcap_returns_vs_btc`
- **API路径**: `/v1/metrics/signals/mcap_returns_vs_btc`
- **英文名称**: Marketcap returns vs BTC

**📝 详细说明**：
Marketcap returns vs BTC。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Marketcap returns vs BTC数据
df = client.get_metric(
    "/v1/metrics/signals/mcap_returns_vs_btc",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 L1（1个指标）

本子类别包含以下详细指标：

#### 1. Token returns vs BTC

- **指标代码**: `l1_native_tokens_returns_vs_btc`
- **API路径**: `/v1/metrics/signals/l1_native_tokens_returns_vs_btc`
- **英文名称**: Token returns vs BTC

**📝 详细说明**：
Token returns vs BTC。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Token returns vs BTC数据
df = client.get_metric(
    "/v1/metrics/signals/l1_native_tokens_returns_vs_btc",
    asset="BTC",
    resolution="24h"
)
```

---

## 📊 完整指标列表

| # | 指标名称 | 指标代码 | API路径 | 说明 |
|---|----------|----------|---------|------|
| 1 | Altcoin Cycle Signal | `altcoin_index` | `/v1/metrics/signals/altcoin_index` | Altcoin Cycle Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 2 | Bitcoin Risk Signal | `btc_risk_index` | `/v1/metrics/signals/btc_risk_index` | Bitcoin Risk Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 3 | Bitcoin Sharpe Signal | `btc_sharpe_signal` | `/v1/metrics/signals/btc_sharpe_signal` | Bitcoin Sharpe Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 4 | Bitcoin Sharpe Signal - Indica | `btc_bss_indicator_1` | `/v1/metrics/signals/btc_bss_indicator_1` | Bitcoin Sharpe Signal - Indicator I。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 5 | Bitcoin Sharpe Signal - Indica | `btc_bss_indicator_2` | `/v1/metrics/signals/btc_bss_indicator_2` | Bitcoin Sharpe Signal - Indicator II。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 6 | Bitcoin Sharpe Signal - Indica | `btc_bss_indicator_3` | `/v1/metrics/signals/btc_bss_indicator_3` | Bitcoin Sharpe Signal - Indicator III。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 7 | Bitcoin Sharpe Signal - Indica | `btc_bss_indicator_4` | `/v1/metrics/signals/btc_bss_indicator_4` | Bitcoin Sharpe Signal - Indicator IV。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 8 | Bitcoin Sharpe Signal Short | `btc_bss_short` | `/v1/metrics/signals/btc_bss_short` | Bitcoin Sharpe Signal Short。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 9 | BSS Goldilocks Short Signal | `btc_bss_goldilocks_short` | `/v1/metrics/signals/btc_bss_goldilocks_short` | BSS Goldilocks Short Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 10 | BSS Goldilocks Signal | `btc_bss_goldilocks` | `/v1/metrics/signals/btc_bss_goldilocks` | BSS Goldilocks Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 11 | Ecosystem Momentum Signal | `ecosystem_momentum_index` | `/v1/metrics/signals/ecosystem_momentum_index` | Ecosystem Momentum Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 12 | Intraday Bitcoin Sharpe Signal | `btc_bss_v2` | `/v1/metrics/signals/btc_bss_v2` | Intraday Bitcoin Sharpe Signal。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 13 | Marketcap returns vs BTC | `mcap_returns_vs_btc` | `/v1/metrics/signals/mcap_returns_vs_btc` | Marketcap returns vs BTC。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 14 | Token returns vs BTC | `l1_native_tokens_returns_vs_btc` | `/v1/metrics/signals/l1_native_tokens_returns_vs_btc` | Token returns vs BTC。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |

## 💻 代码示例

### Python客户端示例

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

class GlassnodeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com"
    
    def get_metric(self, path, asset="BTC", resolution="24h", **kwargs):
        url = f"{self.base_url}{path}"
        params = {
            "a": asset,
            "api_key": self.api_key,
            "s": resolution,
            **kwargs
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df['datetime'] = pd.to_datetime(df['t'], unit='s')
            df['value'] = df['v']
            return df[['datetime', 'value']]
        else:
            raise Exception(f"API Error: {response.status_code}")

# 使用示例
client = GlassnodeClient("YOUR_API_KEY")

# 获取多个相关指标
metrics = [
    '/v1/metrics/addresses/active_count',
    '/v1/metrics/addresses/new',
    '/v1/metrics/addresses/non_zero_count'
]

data = {}
for metric_path in metrics:
    data[metric_path] = client.get_metric(metric_path)

# 可视化
fig, axes = plt.subplots(3, 1, figsize=(12, 10))
for idx, (path, df) in enumerate(data.items()):
    axes[idx].plot(df['datetime'], df['value'])
    axes[idx].set_title(path.split('/')[-1])
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 批量数据分析

```python
import asyncio
import aiohttp

async def fetch_single(session, url, params, name):
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return name, data
        return name, None

async def fetch_batch_metrics(api_key, metric_configs):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for config in metric_configs:
            url = f"https://api.glassnode.com{config['path']}"
            params = {
                "a": config.get('asset', 'BTC'),
                "api_key": api_key,
                "s": config.get('resolution', '24h')
            }
            tasks.append(fetch_single(session, url, params, config['name']))
        
        return await asyncio.gather(*tasks)

# 配置要获取的指标
metric_configs = [
    {'name': '活跃地址', 'path': '/v1/metrics/addresses/active_count'},
    {'name': '新增地址', 'path': '/v1/metrics/addresses/new'},
    {'name': '非零地址', 'path': '/v1/metrics/addresses/non_zero_count'}
]

# 执行批量获取
api_key = "YOUR_API_KEY"
results = asyncio.run(fetch_batch_metrics(api_key, metric_configs))
```

## ⚙️ API参数说明

| 参数 | 必需 | 类型 | 说明 | 示例 |
|------|------|------|------|------|
| `a` | ✅ | string | 资产符号 | BTC, ETH |
| `api_key` | ✅ | string | API密钥 | your_key |
| `s` | ❌ | string | 时间分辨率 | 10m, 1h, 24h |
| `i` | ❌ | string | 时间间隔 | 24h, 1w |
| `since` | ❌ | integer | 开始时间 | 1614556800 |
| `until` | ❌ | integer | 结束时间 | 1617235200 |
| `c` | ❌ | string | 货币单位 | native, USD |

## 📈 数据特性

- **更新频率**: 10分钟到每日不等
- **历史数据**: 最早可追溯至2009年（BTC）
- **数据格式**: JSON或CSV
- **时区**: UTC

## 🔗 相关资源

- [Glassnode官网](https://glassnode.com)
- [API文档](https://docs.glassnode.com)
- [Glassnode Academy](https://academy.glassnode.com)

---

*文档版本: v5.0*  
*最后更新: 2024年*  
