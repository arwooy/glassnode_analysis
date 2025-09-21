# 闪电网络 (lightning)

## 📋 概述

比特币闪电网络数据，包括节点数、通道容量、路由等二层网络指标。

本类别共包含 **10** 个API端点，分为 **7** 个子类别。

## 🗂️ 指标分类

| 子类别 | 指标数量 | 主要功能 |
|--------|----------|----------|
| CHANNEL | 2 | 提供专门的数据分析 |
| GINI | 2 | 提供专门的数据分析 |
| 数量统计 | 2 | 各类地址数量统计 |
| BASE | 1 | 提供专门的数据分析 |
| NETWORK | 1 | 提供专门的数据分析 |
| 手续费 | 1 | 提供专门的数据分析 |
| NODE | 1 | 提供专门的数据分析 |

## 🎨 指标体系结构图

```mermaid
graph TD
    A["闪电网络<br/>共10个指标"]
    A:::mainNode
    
    A --> B1["CHANNEL<br/>2个指标"]
    B1:::categoryNode
    B1 --> C1_1["Lightning Network Channel Size<br/><i>channel_size_mean</i>"]
    C1_1:::metricNode
    C1_1 --> D1_1["Lightning Network Channel Size (Mean)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_1:::descNode
    B1 --> C1_2["Lightning Network Channel Size<br/><i>channel_size_median</i>"]
    C1_2:::metricNode
    C1_2 --> D1_2["Lightning Network Channel Size (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D1_2:::descNode
    A --> B2["GINI<br/>2个指标"]
    B2:::categoryNode
    B2 --> C2_1["Lightning Network Gini Capacit<br/><i>gini_capacity_distribution</i>"]
    C2_1:::metricNode
    C2_1 --> D2_1["Lightning Network Gini Capacity Distribution。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和"]
    D2_1:::descNode
    B2 --> C2_2["Lightning Network Gini Channel<br/><i>gini_channel_distribution</i>"]
    C2_2:::metricNode
    C2_2 --> D2_2["Lightning Network Gini Channel Distribution。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网"]
    D2_2:::descNode
    A --> B3["数量统计<br/>2个指标"]
    B3:::categoryNode
    B3 --> C3_1["Lightning Network Number of Ch<br/><i>channels_count</i>"]
    C3_1:::metricNode
    C3_1 --> D3_1["Lightning Network Number of Channels。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D3_1:::descNode
    B3 --> C3_2["Lightning Network Number of No<br/><i>nodes_count</i>"]
    C3_2:::metricNode
    C3_2 --> D3_2["Lightning Network Number of Nodes。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D3_2:::descNode
    A --> B4["BASE<br/>1个指标"]
    B4:::categoryNode
    B4 --> C4_1["Lightning Network Base Fee (Me<br/><i>base_fee_median</i>"]
    C4_1:::metricNode
    C4_1 --> D4_1["Lightning Network Base Fee (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D4_1:::descNode
    A --> B5["NETWORK<br/>1个指标"]
    B5:::categoryNode
    B5 --> C5_1["Lightning Network Capacity<br/><i>network_capacity_sum</i>"]
    C5_1:::metricNode
    C5_1 --> D5_1["Lightning Network Capacity。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D5_1:::descNode
    A --> B6["手续费<br/>1个指标"]
    B6:::categoryNode
    B6 --> C6_1["Lightning Network Fee Rate (Me<br/><i>fee_rate_median</i>"]
    C6_1:::metricNode
    C6_1 --> D6_1["Lightning Network Fee Rate (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D6_1:::descNode
    
    %% 高对比度样式
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef descNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000,font-size:10px
```

## 📂 详细指标说明

### 📊 CHANNEL（2个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Channel Size

- **指标代码**: `channel_size_mean`
- **API路径**: `/v1/metrics/lightning/channel_size_mean`
- **英文名称**: Lightning Network Channel Size (Mean)

**📝 详细说明**：
Lightning Network Channel Size (Mean)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Channel Size数据
df = client.get_metric(
    "/v1/metrics/lightning/channel_size_mean",
    asset="BTC",
    resolution="24h"
)
```

---

#### 2. Lightning Network Channel Size

- **指标代码**: `channel_size_median`
- **API路径**: `/v1/metrics/lightning/channel_size_median`
- **英文名称**: Lightning Network Channel Size (Median)

**📝 详细说明**：
Lightning Network Channel Size (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Channel Size数据
df = client.get_metric(
    "/v1/metrics/lightning/channel_size_median",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 GINI（2个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Gini Capacit

- **指标代码**: `gini_capacity_distribution`
- **API路径**: `/v1/metrics/lightning/gini_capacity_distribution`
- **英文名称**: Lightning Network Gini Capacity Distribution

**📝 详细说明**：
Lightning Network Gini Capacity Distribution。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Gini Capacit数据
df = client.get_metric(
    "/v1/metrics/lightning/gini_capacity_distribution",
    asset="BTC",
    resolution="24h"
)
```

---

#### 2. Lightning Network Gini Channel

- **指标代码**: `gini_channel_distribution`
- **API路径**: `/v1/metrics/lightning/gini_channel_distribution`
- **英文名称**: Lightning Network Gini Channel Distribution

**📝 详细说明**：
Lightning Network Gini Channel Distribution。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Gini Channel数据
df = client.get_metric(
    "/v1/metrics/lightning/gini_channel_distribution",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 数量统计（2个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Number of Ch

- **指标代码**: `channels_count`
- **API路径**: `/v1/metrics/lightning/channels_count`
- **英文名称**: Lightning Network Number of Channels

**📝 详细说明**：
Lightning Network Number of Channels。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Number of Ch数据
df = client.get_metric(
    "/v1/metrics/lightning/channels_count",
    asset="BTC",
    resolution="24h"
)
```

---

#### 2. Lightning Network Number of No

- **指标代码**: `nodes_count`
- **API路径**: `/v1/metrics/lightning/nodes_count`
- **英文名称**: Lightning Network Number of Nodes

**📝 详细说明**：
Lightning Network Number of Nodes。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Number of No数据
df = client.get_metric(
    "/v1/metrics/lightning/nodes_count",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 BASE（1个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Base Fee (Me

- **指标代码**: `base_fee_median`
- **API路径**: `/v1/metrics/lightning/base_fee_median`
- **英文名称**: Lightning Network Base Fee (Median)

**📝 详细说明**：
Lightning Network Base Fee (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Base Fee (Me数据
df = client.get_metric(
    "/v1/metrics/lightning/base_fee_median",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 NETWORK（1个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Capacity

- **指标代码**: `network_capacity_sum`
- **API路径**: `/v1/metrics/lightning/network_capacity_sum`
- **英文名称**: Lightning Network Capacity

**📝 详细说明**：
Lightning Network Capacity。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Capacity数据
df = client.get_metric(
    "/v1/metrics/lightning/network_capacity_sum",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 手续费（1个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Fee Rate (Me

- **指标代码**: `fee_rate_median`
- **API路径**: `/v1/metrics/lightning/fee_rate_median`
- **英文名称**: Lightning Network Fee Rate (Median)

**📝 详细说明**：
Lightning Network Fee Rate (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Fee Rate (Me数据
df = client.get_metric(
    "/v1/metrics/lightning/fee_rate_median",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 NODE（1个指标）

本子类别包含以下详细指标：

#### 1. Lightning Network Node Connect

- **指标代码**: `node_connectivity`
- **API路径**: `/v1/metrics/lightning/node_connectivity`
- **英文名称**: Lightning Network Node Connectivity

**📝 详细说明**：
Lightning Network Node Connectivity。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Lightning Network Node Connect数据
df = client.get_metric(
    "/v1/metrics/lightning/node_connectivity",
    asset="BTC",
    resolution="24h"
)
```

---

## 📊 完整指标列表

| # | 指标名称 | 指标代码 | API路径 | 说明 |
|---|----------|----------|---------|------|
| 1 | Lightning Network Base Fee (Me | `base_fee_median` | `/v1/metrics/lightning/base_fee_median` | Lightning Network Base Fee (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 2 | Lightning Network Capacity | `network_capacity_sum` | `/v1/metrics/lightning/network_capacity_sum` | Lightning Network Capacity。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 3 | Lightning Network Channel Size | `channel_size_mean` | `/v1/metrics/lightning/channel_size_mean` | Lightning Network Channel Size (Mean)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 4 | Lightning Network Channel Size | `channel_size_median` | `/v1/metrics/lightning/channel_size_median` | Lightning Network Channel Size (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 5 | Lightning Network Fee Rate (Me | `fee_rate_median` | `/v1/metrics/lightning/fee_rate_median` | Lightning Network Fee Rate (Median)。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 6 | Lightning Network Gini Capacit | `gini_capacity_distribution` | `/v1/metrics/lightning/gini_capacity_distribution` | Lightning Network Gini Capacity Distribution。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 7 | Lightning Network Gini Channel | `gini_channel_distribution` | `/v1/metrics/lightning/gini_channel_distribution` | Lightning Network Gini Channel Distribution。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 8 | Lightning Network Node Connect | `node_connectivity` | `/v1/metrics/lightning/node_connectivity` | Lightning Network Node Connectivity。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 9 | Lightning Network Number of Ch | `channels_count` | `/v1/metrics/lightning/channels_count` | Lightning Network Number of Channels。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 10 | Lightning Network Number of No | `nodes_count` | `/v1/metrics/lightning/nodes_count` | Lightning Network Number of Nodes。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |

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
