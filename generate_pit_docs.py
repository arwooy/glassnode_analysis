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

使用 PIT API 可以确保您获得的是在特定时间点实际可用的数据，这对于公平的策略回测和历史分析至关重要。

## 📚 PIT 端点列表

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