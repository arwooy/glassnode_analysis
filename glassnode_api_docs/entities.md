# 实体分析 (entities)

## 📋 概述

链上实体识别和分析，包括交易所、矿池、巨鲸等实体的行为追踪。

本类别共包含 **18** 个API端点，分为 **8** 个子类别。

## 🗂️ 指标分类

| 子类别 | 指标数量 | 主要功能 |
|--------|----------|----------|
| 供应量分布 | 11 | 供应量在不同地址组的分布 |
| 活跃度指标 | 1 | 追踪网络活跃度和用户参与度 |
| 数量统计 | 1 | 各类地址数量统计 |
| 新增地址 | 1 | 新增地址的增长趋势 |
| 最小余额门槛 | 1 | 按余额门槛统计地址分布 |
| 盈利地址 | 1 | 分析盈利地址的规模和特征 |
| 接收活动 | 1 | 接收交易活动统计 |
| 发送活动 | 1 | 发送交易活动统计 |

## 🎨 指标体系结构图

```mermaid
graph TD
    A["实体分析<br/>共18个指标"]
    A:::mainNode
    
    A --> B1["供应量分布<br/>11个指标"]
    B1:::categoryNode
    B1 --> C1_1["相对供应量分布<br/><i>supply_distribution_relative</i>"]
    C1_1:::metricNode
    C1_1 --> D1_1["展示不同地址组别持有的币量占总供应量的百分比分布。这个指标用于分析财富集中度和市场结构，可以识别大户控盘程度。通过追踪供应量在不同规模地址间的分布变化，可以判断"]
    D1_1:::descNode
    B1 --> C1_2["余额<0.001币的地址持有量<br/><i>supply_balance_less_0001</i>"]
    C1_2:::metricNode
    C1_2 --> D1_2["统计余额小于0.001个币的所有地址持有的总供应量。这些通常是粉尘地址或废弃地址，其供应量占比反映了网络中无效或休眠资金的规模"]
    D1_2:::descNode
    B1 --> C1_3["余额>10万币的地址持有量<br/><i>supply_balance_more_100k</i>"]
    C1_3:::metricNode
    C1_3 --> D1_3["统计余额超过100000个币的地址持有的总供应量。这些是最大的持有者，包括交易所、托管机构和超级巨鲸，其行为可以主导市场走向"]
    D1_3:::descNode
    A --> B2["活跃度指标<br/>1个指标"]
    B2:::categoryNode
    B2 --> C2_1["活跃地址数<br/><i>active_count</i>"]
    C2_1:::metricNode
    C2_1 --> D2_1["统计在指定时间窗口内（通常为24小时）至少发生过一次交易（发送或接收）的独立地址数量。这是衡量网络活跃度和用户参与度的核心指标，能够反映网络的健康状况和成长趋势"]
    D2_1:::descNode
    A --> B3["数量统计<br/>1个指标"]
    B3:::categoryNode
    B3 --> C3_1["Entities Net Growth<br/><i>net_growth_count</i>"]
    C3_1:::metricNode
    C3_1 --> D3_1["Entities Net Growth。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况"]
    D3_1:::descNode
    A --> B4["新增地址<br/>1个指标"]
    B4:::categoryNode
    B4 --> C4_1["新增地址数<br/><i>new_count</i>"]
    C4_1:::metricNode
    C4_1 --> D4_1["统计在指定时间内首次在区块链上出现的新地址数量。反映新用户的加入速度和网络的增长动力，是预测未来发展趋势的先行指标。新地址激增可能预示着市场兴趣增加或新应用的推"]
    D4_1:::descNode
    A --> B5["最小余额门槛<br/>1个指标"]
    B5:::categoryNode
    B5 --> C5_1["持有≥1000币的地址数<br/><i>min_1k_count</i>"]
    C5_1:::metricNode
    C5_1 --> D5_1["余额大于或等于1000个原生币的地址数量。反映"巨鲸"级别持有者的数量，这些地址的行为可能对市场产生重大影响，其增减是市场集中度的重要指标"]
    D5_1:::descNode
    A --> B6["盈利地址<br/>1个指标"]
    B6:::categoryNode
    B6 --> C6_1["盈利地址占比<br/><i>profit_relative</i>"]
    C6_1:::metricNode
    C6_1 --> D6_1["盈利地址占所有非零余额地址的百分比。这个相对指标能够更好地反映市场整体的盈利状况，当该比例过高时，可能预示着短期调整风险"]
    D6_1:::descNode
    
    %% 高对比度样式
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef descNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000,font-size:10px
```

## 📂 详细指标说明

### 📊 供应量分布（11个指标）

本子类别包含以下详细指标：

#### 1. 相对供应量分布

- **指标代码**: `supply_distribution_relative`
- **API路径**: `/v1/metrics/entities/supply_distribution_relative`
- **英文名称**: Entities Supply Distribution

**📝 详细说明**：
展示不同地址组别持有的币量占总供应量的百分比分布。这个指标用于分析财富集中度和市场结构，可以识别大户控盘程度。通过追踪供应量在不同规模地址间的分布变化，可以判断市场是在集中还是分散

**使用示例**：
```python
# 获取相对供应量分布数据
df = client.get_metric(
    "/v1/metrics/entities/supply_distribution_relative",
    asset="BTC",
    resolution="24h"
)
```

---

#### 2. 余额<0.001币的地址持有量

- **指标代码**: `supply_balance_less_0001`
- **API路径**: `/v1/metrics/entities/supply_balance_less_0001`
- **英文名称**: Supply Held by Entities with Balance < 0.001

**📝 详细说明**：
统计余额小于0.001个币的所有地址持有的总供应量。这些通常是粉尘地址或废弃地址，其供应量占比反映了网络中无效或休眠资金的规模

**使用示例**：
```python
# 获取余额<0.001币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_less_0001",
    asset="BTC",
    resolution="24h"
)
```

---

#### 3. 余额>10万币的地址持有量

- **指标代码**: `supply_balance_more_100k`
- **API路径**: `/v1/metrics/entities/supply_balance_more_100k`
- **英文名称**: Supply Held by Entities with Balance > 100k

**📝 详细说明**：
统计余额超过100000个币的地址持有的总供应量。这些是最大的持有者，包括交易所、托管机构和超级巨鲸，其行为可以主导市场走向

**使用示例**：
```python
# 获取余额>10万币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_more_100k",
    asset="BTC",
    resolution="24h"
)
```

---

#### 4. 余额0.001-0.01币的地址持有量

- **指标代码**: `supply_balance_0001_001`
- **API路径**: `/v1/metrics/entities/supply_balance_0001_001`
- **英文名称**: Supply Held by Entities with Balance 0.001 - 0.01

**📝 详细说明**：
统计余额在0.001到0.01个币之间的地址持有的总供应量。这个区间通常包含小额试用用户或新用户，反映了网络的基础用户参与情况

**使用示例**：
```python
# 获取余额0.001-0.01币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_0001_001",
    asset="BTC",
    resolution="24h"
)
```

---

#### 5. 余额0.01-0.1币的地址持有量

- **指标代码**: `supply_balance_001_01`
- **API路径**: `/v1/metrics/entities/supply_balance_001_01`
- **英文名称**: Supply Held by Entities with Balance 0.01 - 0.1

**📝 详细说明**：
统计余额在0.01到0.1个币之间的地址持有的总供应量。这个区间代表了小额投资者的参与度，是评估散户市场的重要指标

**使用示例**：
```python
# 获取余额0.01-0.1币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_001_01",
    asset="BTC",
    resolution="24h"
)
```

---

#### 6. 余额0.1-1币的地址持有量

- **指标代码**: `supply_balance_01_1`
- **API路径**: `/v1/metrics/entities/supply_balance_01_1`
- **英文名称**: Supply Held by Entities with Balance 0.1 - 1

**📝 详细说明**：
统计余额在0.1到1个币之间的地址持有的总供应量。这个区间的持有者通常是认真的个人投资者，其变化反映了零售投资者的信心

**使用示例**：
```python
# 获取余额0.1-1币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_01_1",
    asset="BTC",
    resolution="24h"
)
```

---

#### 7. 余额1-10币的地址持有量

- **指标代码**: `supply_balance_1_10`
- **API路径**: `/v1/metrics/entities/supply_balance_1_10`
- **英文名称**: Supply Held by Entities with Balance 1 - 10

**📝 详细说明**：
统计余额在1到10个币之间的地址持有的总供应量。这是中等规模投资者的主要区间，其供应量变化能够反映市场的中坚力量动向

**使用示例**：
```python
# 获取余额1-10币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_1_10",
    asset="BTC",
    resolution="24h"
)
```

---

#### 8. 余额10-100币的地址持有量

- **指标代码**: `supply_balance_10_100`
- **API路径**: `/v1/metrics/entities/supply_balance_10_100`
- **英文名称**: Supply Held by Entities with Balance 10 - 100

**📝 详细说明**：
统计余额在10到100个币之间的地址持有的总供应量。这个区间包含了较大的个人投资者和小型机构，是市场的重要组成部分

**使用示例**：
```python
# 获取余额10-100币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_10_100",
    asset="BTC",
    resolution="24h"
)
```

---

#### 9. 余额100-1000币的地址持有量

- **指标代码**: `supply_balance_100_1k`
- **API路径**: `/v1/metrics/entities/supply_balance_100_1k`
- **英文名称**: Supply Held by Entities with Balance 100 - 1k

**📝 详细说明**：
统计余额在100到1000个币之间的地址持有的总供应量。这些是大额持有者，其行为对市场价格有显著影响

**使用示例**：
```python
# 获取余额100-1000币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_100_1k",
    asset="BTC",
    resolution="24h"
)
```

---

#### 10. 余额1万-10万币的地址持有量

- **指标代码**: `supply_balance_10k_100k`
- **API路径**: `/v1/metrics/entities/supply_balance_10k_100k`
- **英文名称**: Supply Held by Entities with Balance 10k - 100k

**📝 详细说明**：
统计余额在10000到100000个币之间的地址持有的总供应量。这些超大户的动向对市场有决定性影响，需要密切关注

**使用示例**：
```python
# 获取余额1万-10万币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_10k_100k",
    asset="BTC",
    resolution="24h"
)
```

---

#### 11. 余额1千-1万币的地址持有量

- **指标代码**: `supply_balance_1k_10k`
- **API路径**: `/v1/metrics/entities/supply_balance_1k_10k`
- **英文名称**: Supply Held by Entities with Balance 1k - 10k

**📝 详细说明**：
统计余额在1000到10000个币之间的地址持有的总供应量。这个区间主要是巨鲸和机构投资者，其资金流向是市场的风向标

**使用示例**：
```python
# 获取余额1千-1万币的地址持有量数据
df = client.get_metric(
    "/v1/metrics/entities/supply_balance_1k_10k",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 活跃度指标（1个指标）

本子类别包含以下详细指标：

#### 1. 活跃地址数

- **指标代码**: `active_count`
- **API路径**: `/v1/metrics/entities/active_count`
- **英文名称**: Active Entities

**📝 详细说明**：
统计在指定时间窗口内（通常为24小时）至少发生过一次交易（发送或接收）的独立地址数量。这是衡量网络活跃度和用户参与度的核心指标，能够反映网络的健康状况和成长趋势。高活跃地址数通常表示网络使用率高，生态系统活跃

**使用示例**：
```python
# 获取活跃地址数数据
df = client.get_metric(
    "/v1/metrics/entities/active_count",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 数量统计（1个指标）

本子类别包含以下详细指标：

#### 1. Entities Net Growth

- **指标代码**: `net_growth_count`
- **API路径**: `/v1/metrics/entities/net_growth_count`
- **英文名称**: Entities Net Growth

**📝 详细说明**：
Entities Net Growth。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况

**使用示例**：
```python
# 获取Entities Net Growth数据
df = client.get_metric(
    "/v1/metrics/entities/net_growth_count",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 新增地址（1个指标）

本子类别包含以下详细指标：

#### 1. 新增地址数

- **指标代码**: `new_count`
- **API路径**: `/v1/metrics/entities/new_count`
- **英文名称**: New Entities

**📝 详细说明**：
统计在指定时间内首次在区块链上出现的新地址数量。反映新用户的加入速度和网络的增长动力，是预测未来发展趋势的先行指标。新地址激增可能预示着市场兴趣增加或新应用的推出

**使用示例**：
```python
# 获取新增地址数数据
df = client.get_metric(
    "/v1/metrics/entities/new_count",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 最小余额门槛（1个指标）

本子类别包含以下详细指标：

#### 1. 持有≥1000币的地址数

- **指标代码**: `min_1k_count`
- **API路径**: `/v1/metrics/entities/min_1k_count`
- **英文名称**: Number of Whales

**📝 详细说明**：
余额大于或等于1000个原生币的地址数量。反映"巨鲸"级别持有者的数量，这些地址的行为可能对市场产生重大影响，其增减是市场集中度的重要指标

**使用示例**：
```python
# 获取持有≥1000币的地址数数据
df = client.get_metric(
    "/v1/metrics/entities/min_1k_count",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 盈利地址（1个指标）

本子类别包含以下详细指标：

#### 1. 盈利地址占比

- **指标代码**: `profit_relative`
- **API路径**: `/v1/metrics/entities/profit_relative`
- **英文名称**: Percent Entities in Profit

**📝 详细说明**：
盈利地址占所有非零余额地址的百分比。这个相对指标能够更好地反映市场整体的盈利状况，当该比例过高时，可能预示着短期调整风险

**使用示例**：
```python
# 获取盈利地址占比数据
df = client.get_metric(
    "/v1/metrics/entities/profit_relative",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 接收活动（1个指标）

本子类别包含以下详细指标：

#### 1. 接收地址数

- **指标代码**: `receiving_count`
- **API路径**: `/v1/metrics/entities/receiving_count`
- **英文名称**: Receiving Entities

**📝 详细说明**：
在指定时间内至少接收过一次转账的地址数量。反映资金流入的分布广度，帮助判断资金的集中或分散程度。大量接收地址可能表示资金分散流入，市场参与度高

**使用示例**：
```python
# 获取接收地址数数据
df = client.get_metric(
    "/v1/metrics/entities/receiving_count",
    asset="BTC",
    resolution="24h"
)
```

---

### 📊 发送活动（1个指标）

本子类别包含以下详细指标：

#### 1. 发送地址数

- **指标代码**: `sending_count`
- **API路径**: `/v1/metrics/entities/sending_count`
- **英文名称**: Sending Entities

**📝 详细说明**：
在指定时间内至少发送过一次转账的地址数量。反映主动交易用户的规模，是衡量网络交易活跃度的重要指标。高发送地址数表明用户积极使用网络进行价值转移

**使用示例**：
```python
# 获取发送地址数数据
df = client.get_metric(
    "/v1/metrics/entities/sending_count",
    asset="BTC",
    resolution="24h"
)
```

---

## 📊 完整指标列表

| # | 指标名称 | 指标代码 | API路径 | 说明 |
|---|----------|----------|---------|------|
| 1 | 活跃地址数 | `active_count` | `/v1/metrics/entities/active_count` | 统计在指定时间窗口内（通常为24小时）至少发生过一次交易（发送或接收）的独立地址数量。这是衡量网络活跃度和用户参与度的核心指标，能够反映网络的健康状况和成长趋势。高活跃地址数通常表示网络使用率高，生态... |
| 2 | Entities Net Growth | `net_growth_count` | `/v1/metrics/entities/net_growth_count` | Entities Net Growth。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况 |
| 3 | 相对供应量分布 | `supply_distribution_relative` | `/v1/metrics/entities/supply_distribution_relative` | 展示不同地址组别持有的币量占总供应量的百分比分布。这个指标用于分析财富集中度和市场结构，可以识别大户控盘程度。通过追踪供应量在不同规模地址间的分布变化，可以判断市场是在集中还是分散 |
| 4 | 新增地址数 | `new_count` | `/v1/metrics/entities/new_count` | 统计在指定时间内首次在区块链上出现的新地址数量。反映新用户的加入速度和网络的增长动力，是预测未来发展趋势的先行指标。新地址激增可能预示着市场兴趣增加或新应用的推出 |
| 5 | 持有≥1000币的地址数 | `min_1k_count` | `/v1/metrics/entities/min_1k_count` | 余额大于或等于1000个原生币的地址数量。反映"巨鲸"级别持有者的数量，这些地址的行为可能对市场产生重大影响，其增减是市场集中度的重要指标 |
| 6 | 盈利地址占比 | `profit_relative` | `/v1/metrics/entities/profit_relative` | 盈利地址占所有非零余额地址的百分比。这个相对指标能够更好地反映市场整体的盈利状况，当该比例过高时，可能预示着短期调整风险 |
| 7 | 接收地址数 | `receiving_count` | `/v1/metrics/entities/receiving_count` | 在指定时间内至少接收过一次转账的地址数量。反映资金流入的分布广度，帮助判断资金的集中或分散程度。大量接收地址可能表示资金分散流入，市场参与度高 |
| 8 | 发送地址数 | `sending_count` | `/v1/metrics/entities/sending_count` | 在指定时间内至少发送过一次转账的地址数量。反映主动交易用户的规模，是衡量网络交易活跃度的重要指标。高发送地址数表明用户积极使用网络进行价值转移 |
| 9 | 余额<0.001币的地址持有量 | `supply_balance_less_0001` | `/v1/metrics/entities/supply_balance_less_0001` | 统计余额小于0.001个币的所有地址持有的总供应量。这些通常是粉尘地址或废弃地址，其供应量占比反映了网络中无效或休眠资金的规模 |
| 10 | 余额>10万币的地址持有量 | `supply_balance_more_100k` | `/v1/metrics/entities/supply_balance_more_100k` | 统计余额超过100000个币的地址持有的总供应量。这些是最大的持有者，包括交易所、托管机构和超级巨鲸，其行为可以主导市场走向 |
| 11 | 余额0.001-0.01币的地址持有量 | `supply_balance_0001_001` | `/v1/metrics/entities/supply_balance_0001_001` | 统计余额在0.001到0.01个币之间的地址持有的总供应量。这个区间通常包含小额试用用户或新用户，反映了网络的基础用户参与情况 |
| 12 | 余额0.01-0.1币的地址持有量 | `supply_balance_001_01` | `/v1/metrics/entities/supply_balance_001_01` | 统计余额在0.01到0.1个币之间的地址持有的总供应量。这个区间代表了小额投资者的参与度，是评估散户市场的重要指标 |
| 13 | 余额0.1-1币的地址持有量 | `supply_balance_01_1` | `/v1/metrics/entities/supply_balance_01_1` | 统计余额在0.1到1个币之间的地址持有的总供应量。这个区间的持有者通常是认真的个人投资者，其变化反映了零售投资者的信心 |
| 14 | 余额1-10币的地址持有量 | `supply_balance_1_10` | `/v1/metrics/entities/supply_balance_1_10` | 统计余额在1到10个币之间的地址持有的总供应量。这是中等规模投资者的主要区间，其供应量变化能够反映市场的中坚力量动向 |
| 15 | 余额10-100币的地址持有量 | `supply_balance_10_100` | `/v1/metrics/entities/supply_balance_10_100` | 统计余额在10到100个币之间的地址持有的总供应量。这个区间包含了较大的个人投资者和小型机构，是市场的重要组成部分 |
| 16 | 余额100-1000币的地址持有量 | `supply_balance_100_1k` | `/v1/metrics/entities/supply_balance_100_1k` | 统计余额在100到1000个币之间的地址持有的总供应量。这些是大额持有者，其行为对市场价格有显著影响 |
| 17 | 余额1万-10万币的地址持有量 | `supply_balance_10k_100k` | `/v1/metrics/entities/supply_balance_10k_100k` | 统计余额在10000到100000个币之间的地址持有的总供应量。这些超大户的动向对市场有决定性影响，需要密切关注 |
| 18 | 余额1千-1万币的地址持有量 | `supply_balance_1k_10k` | `/v1/metrics/entities/supply_balance_1k_10k` | 统计余额在1000到10000个币之间的地址持有的总供应量。这个区间主要是巨鲸和机构投资者，其资金流向是市场的风向标 |

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
