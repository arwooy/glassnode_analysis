#!/usr/bin/env python3
"""
生成Glassnode PIT (Point in Time) API中文文档
基于 https://docs.glassnode.com/basic-api/endpoints/pit
"""

def generate_pit_documentation():
    """生成PIT端点文档"""
    
    doc = """# 📊 Glassnode PIT (Point in Time) API 中文文档

## 🌟 概述

PIT (Point in Time) API 提供了在特定历史时间点查询链上数据的能力。这对于回测策略、历史分析和避免数据回填偏差至关重要。

## 🎨 PIT API 概念图

```mermaid
graph LR
    A[PIT API<br/>时间点数据查询] 
    A:::mainNode
    
    A --> B1[历史数据快照]
    A --> B2[避免前视偏差]
    A --> B3[策略回测]
    A --> B4[数据一致性]
    
    B1 --> C1[特定时间点<br/>数据值]
    B1 --> C2[原始计算<br/>结果]
    B1 --> C3[无后续<br/>修正]
    
    B2 --> D1[公平回测]
    B2 --> D2[真实历史<br/>重现]
    B2 --> D3[准确分析]
    
    B3 --> E1[交易策略<br/>验证]
    B3 --> E2[风险模型<br/>测试]
    B3 --> E3[绩效评估]
    
    B4 --> F1[链重组<br/>处理]
    B4 --> F2[方法论<br/>更新隔离]
    B4 --> F3[数据修正<br/>隔离]
    
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef subNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef detailNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000
    
    class A mainNode
    class B1,B2,B3,B4 categoryNode
    class C1,C2,C3,D1,D2,D3,E1,E2,E3,F1,F2,F3 subNode
```

## 📝 什么是 PIT API？

**英文原文：**
The Point in Time (PIT) API allows you to query on-chain metrics as they were calculated at a specific point in history. This is crucial for backtesting strategies and historical analysis, as it prevents look-ahead bias that can occur when using current data that may have been revised or updated.

**中文解释：**
PIT（时间点）API 允许您查询特定历史时间点的链上指标数据，获取的是该时间点实际计算出的值，而不是后来修正或更新的值。这对于以下场景至关重要：

1. **策略回测**：确保使用的是历史上实际可获得的数据，避免使用未来数据造成的前视偏差
2. **历史分析**：准确重现历史市场状况和指标状态
3. **数据一致性**：避免因数据修正导致的分析偏差
4. **合规报告**：提供特定时间点的准确数据快照

## 🔍 PIT API 的重要性

### 为什么需要 PIT 数据？

在链上数据分析中，某些指标可能会因为以下原因发生变化：

1. **链重组（Chain Reorg）**：区块链可能发生小规模重组，导致历史数据变化
2. **数据修正**：发现计算错误后的修正
3. **方法论更新**：指标计算方法的改进
4. **延迟数据到达**：某些数据源可能延迟提供信息

### 数据修正影响示例

```mermaid
timeline
    title 数据修正对历史分析的影响时间线

    section 2024年1月
        原始数据采集开始
        : 常规API显示原始值
        : PIT API T1时间点记录

    section 2024年2月
        发现计算错误并修正
        : 常规API更新为修正值
        : PIT API T2保持原始值
        : PIT API T3记录修正值

    section 2024年3月
        方法论更新和重算
        : 常规API显示重算值
        : PIT API T4记录重算值
        : 历史PIT数据保持不变
```

或使用流程图展示：

```mermaid
graph LR
    subgraph "时间演变"
        T1[2024-01-15<br/>原始数据] --> T2[2024-01-30<br/>原始数据]
        T2 --> T3[2024-02-15<br/>数据修正]
        T3 --> T4[2024-03-15<br/>方法更新]
    end
    
    subgraph "常规API返回值"
        A1[原始值] --> A2[修正后值]
        A2 --> A3[重算后值]
        A3 --> A4[当前最新值]
    end
    
    subgraph "PIT API返回值"
        P1[T1: 原始值] -.-> P1
        P2[T2: 原始值] -.-> P2
        P3[T3: 修正值] -.-> P3
        P4[T4: 重算值] -.-> P4
    end
    
    T1 -.-> A1
    T3 -.-> A2
    T4 -.-> A3
    
    T1 ==> P1
    T2 ==> P2
    T3 ==> P3
    T4 ==> P4
    
    style T3 fill:#ef4444,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style T4 fill:#f59e0b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    style A4 fill:#10b981,stroke:#ffffff,stroke-width:2px,color:#ffffff
    
    classDef timeNode fill:#3b82f6,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef apiNode fill:#8b5cf6,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef pitNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    
    class T1,T2 timeNode
    class A1,A2,A3 apiNode
    class P1,P2,P3,P4 pitNode
```

使用 PIT API 可以确保您获得的是在特定时间点实际可用的数据，这对于公平的策略回测和历史分析至关重要。

## 📚 PIT 端点列表

### PIT 端点体系结构

```mermaid
graph LR
    A[PIT 端点<br/>时间点查询]
    A:::mainNode
    
    A --> B1[地址指标<br/>5个端点]
    A --> B2[市场指标<br/>4个端点]
    A --> B3[链上指标<br/>3个端点]
    A --> B4[挖矿指标<br/>待添加]
    
    B1 --> C1[active_count<br/>活跃地址]
    B1 --> C2[new<br/>新增地址]
    B1 --> C3[non_zero_count<br/>非零地址]
    B1 --> C4[profit_count<br/>盈利地址]
    B1 --> C5[loss_count<br/>亏损地址]
    
    B2 --> D1[mvrv<br/>MVRV比率]
    B2 --> D2[price_realized<br/>已实现价格]
    B2 --> D3[sopr<br/>SOPR指标]
    B2 --> D4[marketcap_usd<br/>市值]
    
    B3 --> E1[volume_sum<br/>交易量]
    B3 --> E2[count<br/>交易数]
    B3 --> E3[fees/volume_sum<br/>手续费]
    
    B4 --> F1[hashrate<br/>哈希率]
    B4 --> F2[difficulty<br/>难度]
    B4 --> F3[revenue<br/>矿工收入]
    
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef endpointNode fill:#059669,stroke:#ffffff,stroke-width:1px,color:#ffffff
    classDef futureNode fill:#94a3b8,stroke:#64748b,stroke-width:1px,color:#ffffff,stroke-dasharray: 5 5
    
    class A mainNode
    class B1,B2,B3,B4 categoryNode
    class C1,C2,C3,C4,C5,D1,D2,D3,D4,E1,E2,E3 endpointNode
    class F1,F2,F3 futureNode
```

### 1. 地址指标 PIT 端点

| 指标名称 | API 路径 | 描述 |
|---------|----------|------|
| 活跃地址数 | `/v2/pit/addresses/active_count` | 获取特定历史时间点的活跃地址数 |
| 新增地址数 | `/v2/pit/addresses/new` | 获取特定历史时间点的新增地址数 |
| 非零地址数 | `/v2/pit/addresses/non_zero_count` | 获取特定历史时间点的非零余额地址数 |
| 盈利地址数 | `/v2/pit/addresses/profit_count` | 获取特定历史时间点的盈利地址数 |
| 亏损地址数 | `/v2/pit/addresses/loss_count` | 获取特定历史时间点的亏损地址数 |

### 2. 市场指标 PIT 端点

| 指标名称 | API 路径 | 描述 |
|---------|----------|------|
| MVRV | `/v2/pit/market/mvrv` | 获取特定历史时间点的MVRV比率 |
| 已实现价格 | `/v2/pit/market/price_realized` | 获取特定历史时间点的已实现价格 |
| SOPR | `/v2/pit/market/sopr` | 获取特定历史时间点的SOPR值 |
| 市值 | `/v2/pit/market/marketcap_usd` | 获取特定历史时间点的市值 |

### 3. 链上指标 PIT 端点

| 指标名称 | API 路径 | 描述 |
|---------|----------|------|
| 交易量 | `/v2/pit/transactions/volume_sum` | 获取特定历史时间点的交易量 |
| 交易数 | `/v2/pit/transactions/count` | 获取特定历史时间点的交易数 |
| 手续费 | `/v2/pit/fees/volume_sum` | 获取特定历史时间点的手续费总额 |

## 💻 使用示例

### Python 代码示例

```python
import requests
from datetime import datetime, timedelta

class GlassnodePITClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com"
    
    def get_pit_metric(self, path, timestamp, asset="BTC"):
        \"\"\"Get metric data at specific point in time
        
        Args:
            path: PIT API path
            timestamp: Unix timestamp or datetime object
            asset: Asset code (default: BTC)
        
        Returns:
            Metric value at that point in time
        \"\"\"
        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())
        
        url = f"{self.base_url}{path}"
        params = {
            "a": asset,
            "api_key": self.api_key,
            "timestamp": timestamp
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def backtest_strategy(self, start_date, end_date, metrics, interval_days=1):
        \"\"\"Backtest strategy using PIT data
        
        Args:
            start_date: Start date
            end_date: End date  
            metrics: List of metrics to fetch
            interval_days: Sampling interval in days
        
        Returns:
            Historical data as list of dicts
        \"\"\"
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            timestamp = int(current_date.timestamp())
            daily_data = {"date": current_date}
            
            for metric_path in metrics:
                try:
                    value = self.get_pit_metric(metric_path, timestamp)
                    metric_name = metric_path.split('/')[-1]
                    daily_data[metric_name] = value
                except Exception as e:
                    print(f"Error fetching {metric_path} for {current_date}: {e}")
                    daily_data[metric_name] = None
            
            results.append(daily_data)
            current_date += timedelta(days=interval_days)
        
        return results

# 使用示例
client = GlassnodePITClient("YOUR_API_KEY")

# 获取2023年1月1日的活跃地址数（如该时间点所知）
historical_date = datetime(2023, 1, 1)
active_addresses = client.get_pit_metric(
    "/v2/pit/addresses/active_count",
    historical_date
)
print(f"2023年1月1日的活跃地址数: {active_addresses}")

# 进行历史回测
start = datetime(2023, 1, 1)
end = datetime(2023, 1, 31)
metrics_to_track = [
    "/v2/pit/addresses/active_count",
    "/v2/pit/market/mvrv",
    "/v2/pit/transactions/volume_sum"
]

backtest_data = client.backtest_strategy(
    start, end, metrics_to_track, interval_days=7
)

# 分析结果
for data_point in backtest_data:
    print(f"日期: {data_point['date'].strftime('%Y-%m-%d')}")
    print(f"  活跃地址: {data_point.get('active_count', 'N/A')}")
    print(f"  MVRV: {data_point.get('mvrv', 'N/A')}")
    print(f"  交易量: {data_point.get('volume_sum', 'N/A')}")
```

## 🔄 PIT vs 常规 API 的区别

### 数据查询流程对比

```mermaid
graph TB
    subgraph "常规 API 查询流程"
        A1[用户请求] --> B1[API服务器]
        B1 --> C1[返回最新数据]
        C1 --> D1[包含所有修正<br/>和更新]
        D1 --> E1[用户获得<br/>当前视角数据]
        
        style E1 fill:#ef4444,stroke:#ffffff,stroke-width:2px,color:#ffffff
    end
    
    subgraph "PIT API 查询流程"
        A2[用户请求<br/>+时间戳] --> B2[API服务器]
        B2 --> C2[历史数据库]
        C2 --> D2[查找时间点<br/>快照]
        D2 --> E2[返回原始<br/>历史数据]
        E2 --> F2[用户获得<br/>历史视角数据]
        
        style F2 fill:#10b981,stroke:#ffffff,stroke-width:2px,color:#ffffff
    end
    
    G[关键区别]
    G --> H1[常规: 当前最优数据]
    G --> H2[PIT: 历史真实数据]
    
    H1 --> I1[适用: 实时监控]
    H2 --> I2[适用: 回测分析]
    
    classDef requestNode fill:#3b82f6,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef processNode fill:#8b5cf6,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef resultNode fill:#f59e0b,stroke:#ffffff,stroke-width:2px,color:#ffffff
    
    class A1,A2 requestNode
    class B1,B2,C1,C2,D1,D2,E2 processNode
    class G,H1,H2,I1,I2 resultNode
```

| 特性 | 常规 API | PIT API |
|------|----------|---------|
| 数据状态 | 当前最新值 | 历史时间点值 |
| 数据修正 | 包含所有修正 | 保持历史原始值 |
| 用途 | 实时监控 | 回测和历史分析 |
| 时间参数 | 可选时间范围 | 必需特定时间点 |
| 响应格式 | 时间序列 | 单一时间点值 |

## ⚠️ 使用注意事项

### 1. API 限制
- PIT API 可能有更严格的速率限制
- 某些历史时间点的数据可能不可用
- 需要更高级别的API订阅

### 2. 最佳实践
- **缓存历史数据**：PIT数据不会改变，应该缓存以减少API调用
- **批量查询**：尽可能批量获取数据以提高效率
- **错误处理**：某些历史时间点可能没有数据，需要妥善处理
- **时区处理**：确保正确处理时区，API通常使用UTC

### 3. 数据完整性
- 早期历史数据可能不完整
- 某些指标的PIT数据可能从特定日期开始提供
- 建议验证关键时间点的数据可用性

## 📊 典型应用场景

### 应用场景概览

```mermaid
graph LR
    A[PIT API<br/>应用场景]
    A:::mainNode
    
    A --> B1[策略回测]
    A --> B2[历史研究]
    A --> B3[风险分析]
    A --> B4[合规报告]
    
    B1 --> C1[交易策略<br/>验证]
    B1 --> C2[参数优化]
    B1 --> C3[绩效评估]
    
    B2 --> D1[事件影响<br/>分析]
    B2 --> D2[相关性<br/>研究]
    B2 --> D3[市场周期<br/>分析]
    
    B3 --> E1[VaR计算]
    B3 --> E2[压力测试]
    B3 --> E3[情景分析]
    
    B4 --> F1[审计追踪]
    B4 --> F2[历史报表]
    B4 --> F3[监管合规]
    
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef subNode fill:#059669,stroke:#ffffff,stroke-width:1px,color:#ffffff
    
    class A mainNode
    class B1,B2,B3,B4 categoryNode
    class C1,C2,C3,D1,D2,D3,E1,E2,E3,F1,F2,F3 subNode
```

### 1. 策略回测
```python
# Example: MVRV-based trading strategy backtest
def backtest_mvrv_strategy(client, start_date, end_date):
    \"\"\"Backtest simple MVRV-based trading strategy
    MVRV > 3.5: Sell signal
    MVRV < 1.0: Buy signal
    \"\"\"
    results = []
    current_date = start_date
    position = None  # None, 'long', 'short'
    
    while current_date <= end_date:
        # Get MVRV value at this time point
        mvrv = client.get_pit_metric(
            "/v2/pit/market/mvrv",
            current_date
        )
        
        # Get price
        price = client.get_pit_metric(
            "/v2/pit/market/price_usd",
            current_date
        )
        
        # Trading logic
        signal = None
        if mvrv > 3.5 and position != 'short':
            signal = 'SELL'
            position = 'short'
        elif mvrv < 1.0 and position != 'long':
            signal = 'BUY'
            position = 'long'
        
        results.append({
            'date': current_date,
            'mvrv': mvrv,
            'price': price,
            'signal': signal,
            'position': position
        })
        
        current_date += timedelta(days=1)
    
    return results
```

### 2. 历史相关性分析
```python
# Example: Analyze historical correlation between active addresses and price
def analyze_historical_correlation(client, start_date, end_date):
    \"\"\"Analyze historical correlation between active addresses and price
    Use PIT data to avoid look-ahead bias
    \"\"\"
    import pandas as pd
    import numpy as np
    
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        active = client.get_pit_metric(
            "/v2/pit/addresses/active_count",
            current_date
        )
        price = client.get_pit_metric(
            "/v2/pit/market/price_usd",
            current_date
        )
        
        data.append({
            'date': current_date,
            'active_addresses': active,
            'price': price
        })
        
        current_date += timedelta(days=1)
    
    df = pd.DataFrame(data)
    
    # Calculate correlation
    correlation = df['active_addresses'].corr(df['price'])
    
    # Calculate rolling correlation
    df['rolling_corr'] = df['active_addresses'].rolling(30).corr(df['price'])
    
    return df, correlation
```

### 3. 事件研究
```python
# Example: Study the impact of specific events on on-chain metrics
def event_study(client, event_date, days_before=30, days_after=30):
    \"\"\"Study on-chain metrics changes before and after specific events
    Use PIT data to get real data at the event time
    \"\"\"
    metrics = [
        "/v2/pit/addresses/active_count",
        "/v2/pit/transactions/volume_sum",
        "/v2/pit/market/mvrv",
        "/v2/pit/fees/volume_sum"
    ]
    
    start_date = event_date - timedelta(days=days_before)
    end_date = event_date + timedelta(days=days_after)
    
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_data = {
            'date': current_date,
            'days_from_event': (current_date - event_date).days
        }
        
        for metric_path in metrics:
            metric_name = metric_path.split('/')[-1]
            value = client.get_pit_metric(metric_path, current_date)
            daily_data[metric_name] = value
        
        results.append(daily_data)
        current_date += timedelta(days=1)
    
    return pd.DataFrame(results)
```

## 🔗 相关资源

- [Glassnode官方PIT API文档](https://docs.glassnode.com/basic-api/endpoints/pit)
- [避免回测偏差的最佳实践](https://academy.glassnode.com/backtesting)
- [链上数据的时间一致性](https://insights.glassnode.com/point-in-time-data)

## 📝 总结

PIT API 是进行严谨历史分析和策略回测的必备工具。通过使用历史时间点的实际数据，可以：

1. ✅ 避免前视偏差（Look-ahead bias）
2. ✅ 确保回测结果的真实性
3. ✅ 准确重现历史市场状况
4. ✅ 进行公平的策略比较
5. ✅ 生成合规的历史报告

在进行任何涉及历史数据的分析时，强烈建议使用 PIT API 而不是常规 API，以确保分析结果的准确性和可重现性。

---

*最后更新：2024年12月*
"""
    
    return doc

def main():
    """生成并保存PIT文档"""
    print("生成 Glassnode PIT API 中文文档...")
    
    doc_content = generate_pit_documentation()
    
    # 保存到glassnode_api_docs_enhanced目录
    output_file = 'glassnode_api_docs_enhanced/pit_api.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ PIT API 文档已保存到: {output_file}")
    
    # 更新README以包含PIT文档链接
    readme_file = 'glassnode_api_docs_enhanced/README.md'
    with open(readme_file, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # 在统计信息之前添加PIT文档部分
    pit_section = """
## 🕐 PIT (Point in Time) API

特殊的历史数据查询接口，用于获取特定历史时间点的数据快照：

- [PIT API 完整文档](./pit_api.md) - 时间点数据查询，用于回测和历史分析
"""
    
    # 查找插入位置
    insert_pos = readme_content.find("## 📊 统计信息")
    if insert_pos > 0:
        readme_content = readme_content[:insert_pos] + pit_section + "\n" + readme_content[insert_pos:]
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ 已更新 README.md 以包含 PIT API 文档链接")
    
    print("\n📚 PIT API 文档生成完成！")
    print("该文档详细介绍了：")
    print("  - PIT API 的概念和重要性")
    print("  - 与常规 API 的区别")
    print("  - 主要端点列表")
    print("  - 使用示例和最佳实践")
    print("  - 典型应用场景（回测、相关性分析、事件研究）")

if __name__ == "__main__":
    main()