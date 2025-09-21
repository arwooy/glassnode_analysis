# 挖矿数据 (mining)

## 📋 概述

挖矿行业全景数据，包括算力、难度、矿工收入、区块奖励等挖矿相关指标。

本类别共包含 **9** 个API端点，分为 **8** 个子类别。

## 🗂️ 指标分类

| 子类别 | 指标数量 | 主要功能 |
|--------|----------|----------|
| 矿工收入 | 2 | 提供专门的数据分析 |
| 挖矿难度 | 1 | 提供专门的数据分析 |
| 哈希率 | 1 | 提供专门的数据分析 |
| 市值 | 1 | 提供专门的数据分析 |
| MINERS | 1 | 提供专门的数据分析 |
| 交易量 | 1 | 提供专门的数据分析 |
| 供应量分布 | 1 | 供应量在不同地址组的分布 |
| OTHER | 1 | 提供专门的数据分析 |

## 🎨 指标体系结构图

```mermaid
graph TD
    A["挖矿数据<br/>共9个指标"]
    A:::mainNode
    
    A --> B1["矿工收入<br/>2个指标"]
    B1:::categoryNode
    B1 --> C1_1["Miner Revenue (Fees)<br/><i>revenue_from_fees</i>"]
    C1_1:::metricNode
    C1_1 --> D1_1["Miner Revenue (Fees)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_1:::descNode
    B1 --> C1_2["Miner Revenue (Total)<br/><i>revenue_sum</i>"]
    C1_2:::metricNode
    C1_2 --> D1_2["Miner Revenue (Total)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_2:::descNode
    A --> B2["挖矿难度<br/>1个指标"]
    B2:::categoryNode
    B2 --> C2_1["Difficulty<br/><i>difficulty_latest</i>"]
    C2_1:::metricNode
    C2_1 --> D2_1["Difficulty。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D2_1:::descNode
    A --> B3["哈希率<br/>1个指标"]
    B3:::categoryNode
    B3 --> C3_1["Hash Rate<br/><i>hash_rate_mean</i>"]
    C3_1:::metricNode
    C3_1 --> D3_1["Hash Rate。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D3_1:::descNode
    A --> B4["市值<br/>1个指标"]
    B4:::categoryNode
    B4 --> C4_1["Market Cap to Thermocap Ratio<br/><i>marketcap_thermocap_ratio</i>"]
    C4_1:::metricNode
    C4_1 --> D4_1["Market Cap to Thermocap Ratio。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D4_1:::descNode
    A --> B5["MINERS<br/>1个指标"]
    B5:::categoryNode
    B5 --> C5_1["Miner Outflow Multiple<br/><i>miners_outflow_multiple</i>"]
    C5_1:::metricNode
    C5_1 --> D5_1["Miner Outflow Multiple。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D5_1:::descNode
    A --> B6["交易量<br/>1个指标"]
    B6:::categoryNode
    B6 --> C6_1["Miner Revenue (Block Rewards)<br/><i>volume_mined_sum</i>"]
    C6_1:::metricNode
    C6_1 --> D6_1["Miner Revenue (Block Rewards)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D6_1:::descNode
    
    %% 高对比度样式
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef descNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000,font-size:10px
```

## 📂 详细指标说明

### 📊 矿工收入（2个指标）

本子类别包含以下详细指标：

#### 1. Miner Revenue (Fees)

- **指标代码**: `revenue_from_fees`
- **API路径**: `/v1/metrics/mining/revenue_from_fees`
- **英文名称**: Miner Revenue (Fees)

**📝 详细说明**：
Miner Revenue (Fees)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Miner Revenue (Fees)数据
df = client.get_metric(
    "/v1/metrics/mining/revenue_from_fees",
    asset="BTC",
    resolution="24h"
)
```

---

#### 2. Miner Revenue (Total)

- **指标代码**: `revenue_sum`
- **API路径**: `/v1/metrics/mining/revenue_sum`
- **英文名称**: Miner Revenue (Total)

**📝 详细说明**：
Miner Revenue (Total)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Miner Revenue (Total)数据
df = client.get_metric(
    "/v1/metrics/mining/revenue_sum",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 挖矿难度（1个指标）

本子类别包含以下详细指标：

#### 1. Difficulty

- **指标代码**: `difficulty_latest`
- **API路径**: `/v1/metrics/mining/difficulty_latest`
- **英文名称**: Difficulty

**📝 详细说明**：
Difficulty。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Difficulty数据
df = client.get_metric(
    "/v1/metrics/mining/difficulty_latest",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 哈希率（1个指标）

本子类别包含以下详细指标：

#### 1. Hash Rate

- **指标代码**: `hash_rate_mean`
- **API路径**: `/v1/metrics/mining/hash_rate_mean`
- **英文名称**: Hash Rate

**📝 详细说明**：
Hash Rate。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Hash Rate数据
df = client.get_metric(
    "/v1/metrics/mining/hash_rate_mean",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 市值（1个指标）

本子类别包含以下详细指标：

#### 1. Market Cap to Thermocap Ratio

- **指标代码**: `marketcap_thermocap_ratio`
- **API路径**: `/v1/metrics/mining/marketcap_thermocap_ratio`
- **英文名称**: Market Cap to Thermocap Ratio

**📝 详细说明**：
Market Cap to Thermocap Ratio。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Market Cap to Thermocap Ratio数据
df = client.get_metric(
    "/v1/metrics/mining/marketcap_thermocap_ratio",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 MINERS（1个指标）

本子类别包含以下详细指标：

#### 1. Miner Outflow Multiple

- **指标代码**: `miners_outflow_multiple`
- **API路径**: `/v1/metrics/mining/miners_outflow_multiple`
- **英文名称**: Miner Outflow Multiple

**📝 详细说明**：
Miner Outflow Multiple。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Miner Outflow Multiple数据
df = client.get_metric(
    "/v1/metrics/mining/miners_outflow_multiple",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 交易量（1个指标）

本子类别包含以下详细指标：

#### 1. Miner Revenue (Block Rewards)

- **指标代码**: `volume_mined_sum`
- **API路径**: `/v1/metrics/mining/volume_mined_sum`
- **英文名称**: Miner Revenue (Block Rewards)

**📝 详细说明**：
Miner Revenue (Block Rewards)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Miner Revenue (Block Rewards)数据
df = client.get_metric(
    "/v1/metrics/mining/volume_mined_sum",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 供应量分布（1个指标）

本子类别包含以下详细指标：

#### 1. Miner Unspent Supply

- **指标代码**: `miners_unspent_supply`
- **API路径**: `/v1/metrics/mining/miners_unspent_supply`
- **英文名称**: Miner Unspent Supply

**📝 详细说明**：
追踪供应量在不同地址组的分布。Miner Unspent Supply。此指标有助于分析市场结构和识别重要的市场参与者群体

**使用示例**：
```python
# 获取Miner Unspent Supply数据
df = client.get_metric(
    "/v1/metrics/mining/miners_unspent_supply",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 OTHER（1个指标）

本子类别包含以下详细指标：

#### 1. Thermocap

- **指标代码**: `thermocap`
- **API路径**: `/v1/metrics/mining/thermocap`
- **英文名称**: Thermocap

**📝 详细说明**：
Thermocap。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Thermocap数据
df = client.get_metric(
    "/v1/metrics/mining/thermocap",
    asset="BTC",
    resolution="24h"
)
```

---

## 📊 完整指标列表

| # | 指标名称 | 指标代码 | API路径 | 说明 |
|---|----------|----------|---------|------|
| 1 | Difficulty | `difficulty_latest` | `/v1/metrics/mining/difficulty_latest` | Difficulty。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 2 | Hash Rate | `hash_rate_mean` | `/v1/metrics/mining/hash_rate_mean` | Hash Rate。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 3 | Market Cap to Thermocap Ratio | `marketcap_thermocap_ratio` | `/v1/metrics/mining/marketcap_thermocap_ratio` | Market Cap to Thermocap Ratio。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 4 | Miner Outflow Multiple | `miners_outflow_multiple` | `/v1/metrics/mining/miners_outflow_multiple` | Miner Outflow Multiple。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 5 | Miner Revenue (Block Rewards) | `volume_mined_sum` | `/v1/metrics/mining/volume_mined_sum` | Miner Revenue (Block Rewards)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 6 | Miner Revenue (Fees) | `revenue_from_fees` | `/v1/metrics/mining/revenue_from_fees` | Miner Revenue (Fees)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 7 | Miner Revenue (Total) | `revenue_sum` | `/v1/metrics/mining/revenue_sum` | Miner Revenue (Total)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 8 | Miner Unspent Supply | `miners_unspent_supply` | `/v1/metrics/mining/miners_unspent_supply` | 追踪供应量在不同地址组的分布。Miner Unspent Supply。此指标有助于分析市场结构和识别重要的市场参与者群体 |
| 9 | Thermocap | `thermocap` | `/v1/metrics/mining/thermocap` | Thermocap。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |

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
