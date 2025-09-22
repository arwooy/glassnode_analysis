#!/usr/bin/env python3
"""
生成带有增强Mermaid图表的Glassnode API中文文档
包含高对比度颜色方案和详细的指标说明
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any

def load_endpoints(file_path: str) -> Dict[str, List[Dict]]:
    """加载API端点数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_category_summary(category: str, endpoints: List[Dict]) -> Dict[str, Any]:
    """获取类别摘要信息"""
    # 类别中文映射
    category_names = {
        'addresses': '地址指标',
        'blockchain': '区块链基础数据',
        'breakdowns': '细分数据',
        'bridges': '跨链桥数据',
        'defi': 'DeFi协议数据',
        'derivatives': '衍生品市场',
        'distribution': '分布统计',
        'entities': '实体分析',
        'eth2': '以太坊2.0',
        'fees': '手续费分析',
        'indicators': '技术指标',
        'institutions': '机构数据',
        'lightning': '闪电网络',
        'market': '市场数据',
        'mempool': '内存池',
        'mining': '挖矿数据',
        'protocols': '协议数据',
        'signals': '交易信号',
        'supply': '供应量指标',
        'transactions': '交易数据'
    }
    
    # 类别描述
    category_descriptions = {
        'addresses': '分析网络中地址的行为、分布和特征，包括活跃地址、余额分布、盈亏状态等核心指标。',
        'blockchain': '提供区块链的基础运行数据，包括区块信息、UTXO集、网络状态等底层指标。',
        'market': '全面的市场数据分析，涵盖价格、交易量、市值、已实现价值等市场核心指标。',
        'supply': '追踪加密货币的供应动态，包括流通量、锁定量、销毁量等供应端指标。',
        'transactions': '深入分析链上交易活动，包括交易量、转账金额、交易类型等交易层面数据。',
        'mining': '挖矿行业全景数据，包括算力、难度、矿工收入、区块奖励等挖矿相关指标。',
        'fees': '手续费市场分析，包括平均费用、总费用、费用压力等费用相关指标。',
        'derivatives': '衍生品市场数据，包括期货、期权的持仓量、资金费率、清算等衍生品指标。',
        'defi': '去中心化金融协议数据，包括TVL、借贷、DEX交易量等DeFi生态指标。',
        'entities': '链上实体识别和分析，包括交易所、矿池、巨鲸等实体的行为追踪。',
        'distribution': '各类分布统计数据，包括余额分布、持币时间分布等统计指标。',
        'indicators': '技术分析指标，包括MVRV、SOPR、NVT等链上特有的分析指标。',
        'institutions': '机构投资者相关数据，包括灰度、ETF、上市公司持仓等机构指标。',
        'eth2': '以太坊2.0质押和验证者数据，包括质押量、验证者数量、奖励等。',
        'lightning': '比特币闪电网络数据，包括节点数、通道容量、路由等二层网络指标。',
        'bridges': '跨链桥协议数据，包括锁定量、跨链交易量等桥接相关指标。',
        'breakdowns': '各类数据的细分统计，提供更精细的数据维度划分。',
        'mempool': '内存池状态监控，包括待确认交易、拥堵程度等内存池指标。',
        'protocols': '各类协议的专属数据，包括特定协议的使用量、锁定量等。',
        'signals': '交易信号和预警指标，提供买卖信号、风险预警等决策支持。'
    }
    
    # 统计子指标 - 按前缀分组
    subcategories = defaultdict(list)
    for endpoint in endpoints:
        metric = endpoint.get('metric', '')
        # 尝试多种分组方式
        if '_' in metric:
            # 按第一个下划线前的前缀分组
            prefix = metric.split('_')[0]
            subcategories[prefix].append(endpoint)
        else:
            # 没有下划线的直接用整个metric作为key
            subcategories[metric].append(endpoint)
    
    return {
        'name_zh': category_names.get(category, category),
        'name_en': category,
        'description': category_descriptions.get(category, ''),
        'total_endpoints': len(endpoints),
        'subcategories': dict(subcategories),
        'endpoints': endpoints
    }

def translate_metric_name(metric: str, summary: str) -> str:
    """翻译指标名称为中文"""
    # 常见指标中文映射
    translations = {
        'active_count': '活跃地址数量',
        'sending_count': '发送地址数量',
        'receiving_count': '接收地址数量',
        'count': '地址总数',
        'new': '新增地址',
        'balance': '余额分布',
        'supply': '供应量',
        'profit': '盈利地址',
        'loss': '亏损地址',
        'accumulation': '累积地址',
        'distribution': '分布统计',
        'mean': '平均值',
        'median': '中位数',
        'min': '最小值',
        'max': '最大值',
        'hash_rate': '哈希率',
        'difficulty': '挖矿难度',
        'block_height': '区块高度',
        'block_size': '区块大小',
        'block_time': '区块时间',
        'price_usd': '美元价格',
        'volume': '交易量',
        'marketcap': '市值',
        'realized_value': '已实现价值',
        'fee': '手续费',
        'transactions': '交易数',
        'transfers': '转账数',
        'utxo': 'UTXO集',
        'spent': '花费',
        'created': '创建',
        'mvrv': 'MVRV比率',
        'sopr': 'SOPR指标',
        'nvt': 'NVT比率',
        'rhodl': 'RHODL比率',
        'puell': 'Puell倍数',
        'nupl': 'NUPL指标',
        'stablecoin': '稳定币',
        'exchange': '交易所',
        'miner': '矿工',
        'whale': '巨鲸',
        'shrimp': '小户',
        'holder': '持有者',
        'long_term': '长期',
        'short_term': '短期',
        'realized': '已实现',
        'unrealized': '未实现',
        'total': '总计',
        'average': '平均',
        'relative': '相对',
        'absolute': '绝对',
        'percent': '百分比',
        'ratio': '比率',
        'index': '指数'
    }
    
    # 尝试根据metric找到对应的中文翻译
    for key, value in translations.items():
        if key in metric.lower():
            return value
    
    # 如果没有找到，使用summary的前20个字符
    if summary and len(summary) > 0:
        return summary[:20] if len(summary) > 20 else summary
    
    return metric

def get_metric_description(endpoint: Dict) -> str:
    """获取指标的中文描述"""
    metric = endpoint.get('metric', '')
    summary = endpoint.get('summary', '')
    description = endpoint.get('description', '')
    
    # 中文描述映射
    descriptions = {
        'active_count': '统计在指定时间内有交易活动的地址数量',
        'sending_count': '统计在指定时间内发起交易的地址数量',
        'receiving_count': '统计在指定时间内接收交易的地址数量',
        'new': '统计首次出现在区块链上的新地址数量',
        'non_zero_count': '统计余额大于零的地址总数',
        'min_1': '统计余额大于等于1个币的地址数量',
        'min_10': '统计余额大于等于10个币的地址数量',
        'min_100': '统计余额大于等于100个币的地址数量',
        'min_1k': '统计余额大于等于1000个币的地址数量',
        'min_10k': '统计余额大于等于10000个币的地址数量',
        'profit_count': '统计当前处于盈利状态的地址数量',
        'loss_count': '统计当前处于亏损状态的地址数量',
        'supply_held': '统计特定类型地址持有的币量占总供应量的比例',
        'price_usd_close': '每日收盘时的美元价格',
        'price_usd_ohlc': '包含开盘价、最高价、最低价、收盘价的价格数据',
        'marketcap_usd': '以美元计算的总市值',
        'volume_sum': '链上交易的总转账金额',
        'transaction_count': '链上交易的总数量',
        'fee_total': '支付给矿工的总手续费',
        'hash_rate_mean': '网络的平均哈希率',
        'difficulty_latest': '当前的挖矿难度',
        'block_height': '区块链的当前高度',
        'mvrv': '市值与已实现价值的比率，用于判断市场估值',
        'sopr': '花费产出利润率，反映市场整体盈亏状态',
        'nvt': '网络价值与交易量比率，类似于市盈率',
        'nupl': '净未实现盈亏指标，反映市场情绪',
        'rhodl': '已实现HODL比率，识别市场周期顶部和底部',
        'exchange_balance': '存储在交易所的币量',
        'exchange_netflow': '流入和流出交易所的净流量',
        'miner_revenue': '矿工的总收入（区块奖励+手续费）',
        'miner_outflow': '从矿工地址流出的币量'
    }
    
    # 根据metric查找描述
    for key, desc in descriptions.items():
        if key in metric.lower():
            return desc
    
    # 如果没有找到特定描述，尝试生成通用描述
    if 'count' in metric:
        return '统计符合特定条件的地址或交易数量'
    elif 'balance' in metric:
        return '分析地址余额的分布和变化情况'
    elif 'supply' in metric:
        return '追踪币的供应量和分布变化'
    elif 'price' in metric:
        return '市场价格数据和价格相关指标'
    elif 'volume' in metric:
        return '交易量和转账金额相关数据'
    elif 'fee' in metric:
        return '网络手续费相关数据'
    elif 'hash' in metric or 'mining' in metric:
        return '挖矿和网络算力相关数据'
    elif 'exchange' in metric:
        return '交易所相关的资金流动数据'
    
    # 使用原始描述的前100个字符
    if description:
        desc = description.replace('[View in Studio]', '').split('\n')[0]
        return desc[:100] + '...' if len(desc) > 100 else desc
    
    return '提供链上数据分析和市场洞察'

def generate_enhanced_mermaid_diagram(category_info: Dict) -> str:
    """生成带有高对比度颜色和详细指标的Mermaid图表"""
    name_zh = category_info['name_zh']
    endpoints = category_info['endpoints']
    
    # 选择最重要的指标（前10个）
    selected_endpoints = endpoints[:10] if len(endpoints) > 10 else endpoints
    
    mermaid = f"""```mermaid
graph TD
    A["{name_zh}<br/>共{len(endpoints)}个指标"]
    A:::mainNode
    """
    
    # 为每个指标创建节点和解释
    for i, endpoint in enumerate(selected_endpoints, 1):
        metric = endpoint.get('metric', '')
        summary = endpoint.get('summary', '')
        chinese_name = translate_metric_name(metric, summary)
        description = get_metric_description(endpoint)
        
        # 创建指标节点和描述节点
        mermaid += f"""
    A --> B{i}["{chinese_name}<br/><i>{metric}</i>"]
    B{i} --> C{i}["{description[:50]}..."]
    B{i}:::metricNode
    C{i}:::descNode"""
    
    # 如果还有更多指标，添加一个提示节点
    if len(endpoints) > 10:
        mermaid += f"""
    A --> MORE["...还有{len(endpoints)-10}个指标"]
    MORE:::moreNode"""
    
    # 添加样式定义 - 高对比度配色方案
    mermaid += """
    
    %% 高对比度样式定义
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef descNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000
    classDef moreNode fill:#dc2626,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-style:italic
```"""
    
    return mermaid

def generate_detailed_tree_diagram(category_info: Dict) -> str:
    """生成详细的树形结构图"""
    name_zh = category_info['name_zh']
    subcats = category_info['subcategories']
    
    # 子类别中文映射
    subcat_names = {
        'active': '活跃度指标',
        'count': '数量统计',
        'balance': '余额分析',
        'supply': '供应量分布',
        'price': '价格指标',
        'volume': '交易量',
        'fee': '费用统计',
        'hash': '哈希率',
        'block': '区块数据',
        'transaction': '交易统计',
        'min': '最小余额',
        'max': '最大值',
        'holder': '持有者分析',
        'profit': '盈利分析',
        'loss': '亏损分析',
        'accumulation': '累积地址',
        'sending': '发送活动',
        'receiving': '接收活动',
        'new': '新增统计',
        'total': '总计统计',
        'non': '非零地址',
        'activity': '活动分析'
    }
    
    mermaid = f"""```mermaid
graph LR
    ROOT["{name_zh}"]
    ROOT:::rootNode
    """
    
    # 按数量排序，取前6个主要子类别
    top_subcats = sorted(subcats.items(), key=lambda x: len(x[1]), reverse=True)[:6]
    
    for i, (subcat, endpoints) in enumerate(top_subcats, 1):
        subcat_zh = subcat_names.get(subcat, subcat.upper())
        
        # 添加子类别节点
        mermaid += f"""
    ROOT --> CAT{i}["{subcat_zh}<br/>({len(endpoints)}个)"]
    CAT{i}:::categoryNode"""
        
        # 为每个子类别添加前3个具体指标
        for j, endpoint in enumerate(endpoints[:3], 1):
            metric = endpoint.get('metric', '')
            summary = endpoint.get('summary', '')
            chinese_name = translate_metric_name(metric, summary)
            
            mermaid += f"""
    CAT{i} --> M{i}_{j}["{chinese_name}"]
    M{i}_{j}:::leafNode"""
            
            # 添加具体描述
            description = get_metric_description(endpoint)
            mermaid += f"""
    M{i}_{j} --> D{i}_{j}["{description[:40]}..."]
    D{i}_{j}:::detailNode"""
    
    # 样式定义
    mermaid += """
    
    %% 高对比度树形图样式
    classDef rootNode fill:#7c3aed,stroke:#ffffff,stroke-width:4px,color:#ffffff,font-weight:bold,font-size:16px
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef leafNode fill:#16a34a,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef detailNode fill:#fde047,stroke:#713f12,stroke-width:1px,color:#000000,font-size:10px
```"""
    
    return mermaid

def generate_subcategory_detail_section(subcat_name: str, endpoints: List[Dict]) -> str:
    """生成子类别的详细文档，包含中文解释"""
    # 子类别中文映射
    subcat_names = {
        'active': '活跃度指标',
        'count': '数量统计',
        'balance': '余额相关',
        'supply': '供应量分布',
        'price': '价格指标',
        'volume': '交易量',
        'fee': '手续费',
        'hash': '哈希率',
        'block': '区块信息',
        'transaction': '交易统计',
        'accumulation': '累积地址',
        'min': '最小余额统计',
        'holder': '持有者分析',
        'profit': '盈亏分析',
        'loss': '亏损分析',
        'sending': '发送活动',
        'receiving': '接收活动',
        'new': '新增统计',
        'total': '总计统计'
    }
    
    subcat_zh = subcat_names.get(subcat_name, subcat_name.upper())
    
    section = f"""### {subcat_zh} ({len(endpoints)}个指标)

#### 📊 指标详解：
"""
    
    # 详细列出每个指标，包含中文名称和解释
    for i, endpoint in enumerate(endpoints, 1):
        metric = endpoint.get('metric', '')
        summary = endpoint.get('summary', '')
        chinese_name = translate_metric_name(metric, summary)
        description = get_metric_description(endpoint)
        
        section += f"""
##### {i}. {chinese_name}
- **英文名称**: {summary}
- **指标代码**: `{metric}`
- **API路径**: `{endpoint.get('path', '')}`
- **中文说明**: {description}
- **数据类型**: 时序数据
- **更新频率**: 每日更新
"""
    
    return section + "\n---\n"

def generate_enhanced_category_markdown(category: str, endpoints: List[Dict]) -> str:
    """生成增强版的类别Markdown文档"""
    info = get_category_summary(category, endpoints)
    
    markdown = f"""# {info['name_zh']} ({info['name_en']})

## 📋 概述

{info['description']}

**本类别包含 {info['total_endpoints']} 个API端点**，提供全面的{info['name_zh']}数据支持。

## 🎨 指标体系结构图（高对比度）

### 主要指标概览
{generate_enhanced_mermaid_diagram(info)}

### 详细指标树形图
{generate_detailed_tree_diagram(info)}

## 📂 指标分类详情

本类别的指标按功能和用途分为以下几个子类：

"""
    
    # 按子类别数量排序，生成详细的子类别文档
    sorted_subcats = sorted(info['subcategories'].items(), 
                           key=lambda x: len(x[1]), reverse=True)
    
    for subcat, subcat_endpoints in sorted_subcats:
        markdown += generate_subcategory_detail_section(subcat, subcat_endpoints)
    
    # 添加完整的指标对照表
    markdown += """## 📊 完整指标中英对照表

| # | 中文名称 | 英文名称 | 指标代码 | 中文说明 |
|---|---------|---------|---------|---------|
"""
    
    for i, endpoint in enumerate(endpoints, 1):
        metric = endpoint.get('metric', '')
        summary = endpoint.get('summary', '')
        chinese_name = translate_metric_name(metric, summary)
        description = get_metric_description(endpoint)
        
        markdown += f"| {i} | {chinese_name} | {summary} | `{metric}` | {description[:60]}... |\n"
    
    # 添加使用示例
    markdown += """
## 💻 使用示例

### 示例1: 获取单个指标数据

```python
import requests
import pandas as pd

def get_glassnode_metric(metric_path, asset="BTC", api_key="YOUR_API_KEY"):
    \"\"\"获取Glassnode指标数据\"\"\"
    url = f"https://api.glassnode.com{metric_path}"
    params = {
        "a": asset,
        "api_key": api_key,
        "s": "24h"  # 日度数据
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
        df['value'] = df['v']
        return df[['timestamp', 'value']]
    else:
        print(f"错误: {response.status_code}")
        return None
```

### 示例2: 批量获取多个相关指标

```python
import asyncio
import aiohttp

async def fetch_multiple_metrics(metrics_list, api_key):
    \"\"\"异步批量获取多个指标\"\"\"
    async with aiohttp.ClientSession() as session:
        tasks = []
        for metric_path in metrics_list:
            url = f"https://api.glassnode.com{metric_path}"
            params = {"a": "BTC", "api_key": api_key, "s": "24h"}
            tasks.append(session.get(url, params=params))
        
        responses = await asyncio.gather(*tasks)
        results = {}
        for metric_path, response in zip(metrics_list, responses):
            if response.status == 200:
                data = await response.json()
                results[metric_path] = data
        return results
```

### 示例3: 创建可视化仪表板

```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def create_metrics_dashboard(metrics_data):
    \"\"\"创建指标仪表板\"\"\"
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
    plt.rcParams['axes.unicode_minus'] = False
    
    for idx, (metric_name, data) in enumerate(metrics_data.items()):
        if idx >= 9:
            break
        
        ax = fig.add_subplot(gs[idx // 3, idx % 3])
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        
        ax.plot(df['date'], df['v'], linewidth=2, color='#0891b2')
        ax.fill_between(df['date'], df['v'], alpha=0.3, color='#0891b2')
        ax.set_title(metric_name, fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Glassnode 指标仪表板', fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig
```

## ⚙️ API参数说明

### 必需参数
- `a` (asset): 资产符号，如 BTC, ETH
- `api_key`: 你的API密钥

### 可选参数
- `s` (resolution): 时间分辨率 (10m, 1h, 24h, 1w, 1month)
- `i` (interval): 时间间隔
- `f` (format): 输出格式 (JSON, CSV)
- `since`: 开始时间 (Unix时间戳)
- `until`: 结束时间 (Unix时间戳)
- `c` (currency): 货币单位 (native, USD)
- `e` (exchange): 交易所名称

## 📈 数据特性

### 更新频率
- **实时指标**: 10分钟更新
- **日度指标**: UTC 00:00 更新
- **周度指标**: 每周一更新
- **月度指标**: 每月1日更新

### 数据精度
- 数值类型：浮点数
- 时间戳：Unix时间戳（秒）
- 百分比：0-1 或 0-100（视指标而定）

## 🔍 常见应用场景

1. **市场分析**: 跟踪关键链上指标，判断市场趋势
2. **风险管理**: 监控异常指标，及时预警风险
3. **量化交易**: 构建基于链上数据的交易策略
4. **研究报告**: 深入分析历史数据，发现市场规律
5. **实时监控**: 设置自动化告警，捕捉市场机会

## ⚠️ 注意事项

1. **API限制**:
   - 免费版: 10 请求/分钟
   - 专业版: 120 请求/分钟
   - 机构版: 自定义

2. **数据延迟**:
   - 链上数据: 2-6个区块
   - 交易所数据: 1-5分钟

3. **错误处理**:
   - 429: 频率限制
   - 401: API密钥无效
   - 404: 端点不存在
   - 500: 服务器错误

## 📚 相关资源

- [Glassnode官网](https://glassnode.com)
- [API文档](https://docs.glassnode.com)
- [Glassnode Academy](https://academy.glassnode.com)
- [Discord社区](https://discord.gg/glassnode)

---

*文档版本: v3.0 - 增强版*  
*更新日期: 2024年*  
*特性: 高对比度图表 + 详细中文解释*
"""
    
    return markdown

def main():
    """主函数"""
    # 加载数据
    endpoints_file = "glassnode_endpoints_simplified.json"
    output_dir = "glassnode_api_docs_enhanced"
    
    print(f"正在加载 {endpoints_file}...")
    categories = load_endpoints(endpoints_file)
    
    print(f"发现 {len(categories)} 个类别")
    print(f"总共 {sum(len(e) for e in categories.values())} 个端点")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成每个类别的增强版文档
    for category, endpoints in categories.items():
        print(f"正在生成增强版文档 {category}.md...")
        doc = generate_enhanced_category_markdown(category, endpoints)
        with open(f"{output_dir}/{category}.md", 'w', encoding='utf-8') as f:
            f.write(doc)
    
    print(f"\n✅ 增强版文档生成完成！")
    print(f"📁 输出目录: {output_dir}/")
    print(f"🎨 特性:")
    print(f"   - 高对比度Mermaid图表")
    print(f"   - 详细的中文指标名称")
    print(f"   - 完整的中文解释说明")
    print(f"   - 树形结构展示")

if __name__ == "__main__":
    main()