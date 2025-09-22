#!/usr/bin/env python3
"""
生成Glassnode API中文文档
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
    
    # 统计子指标
    subcategories = defaultdict(list)
    for endpoint in endpoints:
        metric = endpoint.get('metric', '')
        if '_' in metric:
            prefix = metric.split('_')[0]
            subcategories[prefix].append(endpoint)
    
    return {
        'name_zh': category_names.get(category, category),
        'name_en': category,
        'description': category_descriptions.get(category, ''),
        'total_endpoints': len(endpoints),
        'subcategories': dict(subcategories),
        'endpoints': endpoints
    }

def generate_mermaid_diagram(category_info: Dict) -> str:
    """生成Mermaid图表"""
    name_zh = category_info['name_zh']
    subcats = category_info['subcategories']
    
    # 限制显示的子类别数量
    top_subcats = sorted(subcats.items(), key=lambda x: len(x[1]), reverse=True)[:8]
    
    mermaid = f"""```mermaid
graph TB
    A["{name_zh}"] --> B["核心指标分类"]
    """
    
    for i, (subcat, endpoints) in enumerate(top_subcats, 1):
        count = len(endpoints)
        # 子类别中文映射
        subcat_names = {
            'active': '活跃度',
            'count': '数量统计',
            'balance': '余额',
            'supply': '供应量',
            'price': '价格',
            'volume': '交易量',
            'fee': '手续费',
            'hash': '哈希率',
            'block': '区块',
            'transaction': '交易'
        }
        subcat_zh = subcat_names.get(subcat, subcat)
        # 使用引号包裹，避免特殊字符问题
        mermaid += f"""
    B --> C{i}["{subcat_zh} - {count}个指标"]"""
    
    mermaid += """

    style A fill:#f9f,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#333,stroke-width:2px
```"""
    
    return mermaid

def generate_endpoint_table(endpoints: List[Dict], limit: int = 10) -> str:
    """生成端点表格"""
    table = """| 指标名称 | API路径 | 描述 |
|---------|---------|------|
"""
    
    for endpoint in endpoints[:limit]:
        metric = endpoint.get('metric', '')
        path = endpoint.get('path', '')
        summary = endpoint.get('summary', '')
        description = endpoint.get('description', '')[:100] + '...' if len(endpoint.get('description', '')) > 100 else endpoint.get('description', '')
        
        # 清理描述中的链接
        description = description.replace('[View in Studio]', '').split('\n')[0]
        
        table += f"| {summary} | `{path}` | {description} |\n"
    
    if len(endpoints) > limit:
        table += f"| ... | ... | 共{len(endpoints)}个指标 |\n"
    
    return table

def generate_example_code(category: str, endpoint: Dict) -> str:
    """生成示例代码"""
    path = endpoint.get('path', '')
    metric = endpoint.get('metric', '')
    
    return f"""### Python 示例

```python
import requests

# API配置
api_key = "YOUR_API_KEY"
base_url = "https://api.glassnode.com"

# 请求参数
params = {{
    "a": "BTC",  # 资产符号
    "api_key": api_key,
    "s": "1d",   # 时间粒度: 1h, 24h, 1d, 1w, 1month
    "i": "24h"   # 时间间隔（部分指标需要）
}}

# 发送请求
response = requests.get(
    f"{{base_url}}{path}",
    params=params
)

# 处理响应
if response.status_code == 200:
    data = response.json()
    for item in data[:5]:  # 显示前5条数据
        print(f"时间: {{item['t']}}, 值: {{item['v']}}")
else:
    print(f"请求失败: {{response.status_code}}")
```

### cURL 示例

```bash
curl -G "https://api.glassnode.com{path}" \\
  -d "a=BTC" \\
  -d "api_key=YOUR_API_KEY" \\
  -d "s=1d"
```"""

def generate_category_markdown(category: str, endpoints: List[Dict]) -> str:
    """生成类别的Markdown文档"""
    info = get_category_summary(category, endpoints)
    
    # 选择代表性的端点作为示例
    example_endpoint = endpoints[0] if endpoints else None
    
    markdown = f"""# {info['name_zh']} ({info['name_en']})

## 概述

{info['description']}

本类别包含 **{info['total_endpoints']}** 个API端点，提供全面的{info['name_zh']}数据支持。

## 指标体系结构

{generate_mermaid_diagram(info)}

## 主要指标分类

"""
    
    # 添加子类别说明
    for subcat, subcat_endpoints in sorted(info['subcategories'].items(), 
                                          key=lambda x: len(x[1]), reverse=True)[:5]:
        markdown += f"""### {subcat.upper()} 相关指标 ({len(subcat_endpoints)}个)

"""
        # 列出该子类别的前3个指标
        for endpoint in subcat_endpoints[:3]:
            summary = endpoint.get('summary', '')
            markdown += f"- **{summary}**: {endpoint.get('metric', '')}\n"
        
        if len(subcat_endpoints) > 3:
            markdown += f"- ...还有{len(subcat_endpoints)-3}个指标\n"
        
        markdown += "\n"
    
    # 添加详细指标列表
    markdown += f"""## 指标列表

以下是{info['name_zh']}类别中的主要指标：

{generate_endpoint_table(endpoints)}

## 使用示例

以下展示如何调用{info['name_zh']}相关的API：

{generate_example_code(category, example_endpoint) if example_endpoint else ''}

## 数据更新频率

大部分{info['name_zh']}指标支持以下时间粒度：
- **1h**: 小时级数据
- **24h**: 日级数据  
- **1w**: 周级数据
- **1month**: 月级数据

部分实时指标支持10分钟级别的更新。

## 注意事项

1. **API限制**: 请注意API的调用频率限制，避免过于频繁的请求
2. **数据延迟**: 某些指标可能有几分钟到几小时的数据延迟
3. **资产支持**: 不同指标支持的资产类型不同，请查阅具体文档
4. **历史数据**: 部分指标的历史数据可能有限制

## 相关资源

- [Glassnode Studio](https://studio.glassnode.com) - 可视化数据平台
- [API文档](https://docs.glassnode.com) - 完整API文档
- [指标说明](https://academy.glassnode.com) - 详细的指标解释

---

*更新时间: 2024年*
"""
    
    return markdown

def generate_readme(categories: Dict[str, List[Dict]]) -> str:
    """生成总览README文档"""
    
    # 统计信息
    total_endpoints = sum(len(endpoints) for endpoints in categories.values())
    
    readme = f"""# Glassnode API 中文文档

## 📊 概述

Glassnode是领先的链上数据分析平台，提供全面的加密货币链上数据API服务。本文档为Glassnode API的中文技术文档，包含所有API类别的详细说明、使用示例和最佳实践。

### 核心特性

- 🔍 **全面的链上数据**: 覆盖{len(categories)}个主要类别，超过{total_endpoints}个数据端点
- ⚡ **实时更新**: 支持从10分钟到月度的多种时间粒度
- 🌍 **多链支持**: 支持BTC、ETH等主流区块链
- 📈 **专业指标**: 提供MVRV、SOPR等专业链上分析指标

## 📚 文档目录

本文档按照功能类别组织，每个类别都有独立的详细文档：

"""
    
    # 类别目录表格
    readme += """| 类别 | 中文名称 | 端点数量 | 描述 | 文档链接 |
|------|---------|----------|------|----------|
"""
    
    category_info = {}
    for category, endpoints in sorted(categories.items()):
        info = get_category_summary(category, endpoints)
        category_info[category] = info
        
        readme += f"| {category} | {info['name_zh']} | {info['total_endpoints']} | {info['description'][:50]}... | [查看文档](./{category}.md) |\n"
    
    # 添加整体架构图
    readme += """
## 🏗️ API体系架构

```mermaid
graph TB
    subgraph "链上数据层"
        A1[区块链数据]
        A2[交易数据]
        A3[地址数据]
    end
    
    subgraph "市场数据层"
        B1[现货市场]
        B2[衍生品市场]
        B3[DeFi市场]
    end
    
    subgraph "分析指标层"
        C1[技术指标]
        C2[链上指标]
        C3[市场指标]
    end
    
    subgraph "应用层"
        D1[交易信号]
        D2[风险管理]
        D3[投资分析]
    end
    
    A1 --> C1
    A2 --> C2
    A3 --> C2
    B1 --> C3
    B2 --> C3
    B3 --> C3
    C1 --> D1
    C2 --> D2
    C3 --> D3
    
    style A1 fill:#e1f5fe
    style A2 fill:#e1f5fe
    style A3 fill:#e1f5fe
    style B1 fill:#fff3e0
    style B2 fill:#fff3e0
    style B3 fill:#fff3e0
    style C1 fill:#f3e5f5
    style C2 fill:#f3e5f5
    style C3 fill:#f3e5f5
    style D1 fill:#e8f5e9
    style D2 fill:#e8f5e9
    style D3 fill:#e8f5e9
```

## 🚀 快速开始

### 1. 获取API密钥

访问 [Glassnode官网](https://glassnode.com) 注册账户并获取API密钥。

### 2. 安装依赖

```bash
pip install requests pandas
```

### 3. 基础示例

```python
import requests
import pandas as pd

# 配置
API_KEY = "your_api_key_here"
BASE_URL = "https://api.glassnode.com"

def fetch_glassnode_data(endpoint, asset="BTC", resolution="24h"):
    \"\"\"获取Glassnode数据\"\"\"
    params = {
        "a": asset,
        "api_key": API_KEY,
        "s": resolution
    }
    
    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['t'] = pd.to_datetime(df['t'], unit='s')
        return df
    else:
        raise Exception(f"API请求失败: {response.status_code}")

# 使用示例：获取BTC活跃地址数
df = fetch_glassnode_data("/v1/metrics/addresses/active_count")
print(df.tail())
```

## 📊 主要数据类别详解

### 核心链上数据
- **[地址指标](./addresses.md)**: 网络参与者行为分析
- **[交易数据](./transactions.md)**: 链上交易活动追踪
- **[供应量指标](./supply.md)**: 代币经济学分析

### 市场分析
- **[市场数据](./market.md)**: 价格与交易量分析
- **[衍生品市场](./derivatives.md)**: 期货期权数据
- **[DeFi协议](./defi.md)**: 去中心化金融分析

### 网络状态
- **[区块链基础](./blockchain.md)**: 区块和网络数据
- **[挖矿数据](./mining.md)**: 算力与矿工分析
- **[手续费分析](./fees.md)**: 网络使用成本

### 高级分析
- **[技术指标](./indicators.md)**: MVRV、SOPR等专业指标
- **[实体分析](./entities.md)**: 交易所、巨鲸追踪
- **[交易信号](./signals.md)**: 量化交易支持

## ⚙️ API使用规范

### 请求格式

所有API请求都使用GET方法，基础URL为：
```
https://api.glassnode.com/v1/metrics/{category}/{metric}
```

### 通用参数

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| a | string | 是 | 资产符号 | BTC, ETH |
| api_key | string | 是 | API密钥 | your_key |
| s | string | 否 | 时间分辨率 | 1h, 24h, 1w |
| i | string | 否 | 时间间隔 | 24h, 1w |
| f | string | 否 | 数据格式 | JSON, CSV |
| since | int | 否 | 开始时间(Unix) | 1614556800 |
| until | int | 否 | 结束时间(Unix) | 1617235200 |

### 响应格式

```json
[
  {
    "t": 1614556800,  // Unix时间戳
    "v": 123456.78    // 指标值
  },
  {
    "t": 1614643200,
    "v": 124567.89
  }
]
```

## 🔑 最佳实践

### 1. 速率限制
- 免费套餐: 10请求/分钟
- 基础套餐: 30请求/分钟
- 专业套餐: 120请求/分钟

### 2. 数据缓存
建议在本地缓存历史数据，减少API调用：

```python
import pickle
import os
from datetime import datetime, timedelta

def cached_fetch(endpoint, cache_dir="cache"):
    cache_file = f"{cache_dir}/{endpoint.replace('/', '_')}.pkl"
    
    # 检查缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            cached_data = pickle.load(f)
            # 如果缓存未过期，返回缓存数据
            if cached_data['timestamp'] > datetime.now() - timedelta(hours=1):
                return cached_data['data']
    
    # 获取新数据
    data = fetch_glassnode_data(endpoint)
    
    # 保存缓存
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump({
            'timestamp': datetime.now(),
            'data': data
        }, f)
    
    return data
```

### 3. 错误处理

```python
def safe_api_call(endpoint, max_retries=3):
    \"\"\"带重试机制的API调用\"\"\"
    for attempt in range(max_retries):
        try:
            return fetch_glassnode_data(endpoint)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # 指数退避
```

## 🔍 数据质量说明

### 数据来源
- **链上数据**: 直接从区块链全节点获取
- **交易所数据**: 来自主要交易所的API
- **衍生品数据**: 来自期货期权交易平台

### 更新频率
- **实时指标**: 10分钟更新
- **日度指标**: 每日UTC 00:00更新
- **周度指标**: 每周一更新
- **月度指标**: 每月1日更新

### 数据校验
- 所有数据经过多重验证
- 异常值自动标记和处理
- 定期与其他数据源交叉验证

## 📞 支持与帮助

### 技术支持
- 📧 Email: support@glassnode.com
- 💬 Discord: [Glassnode Community](https://discord.gg/glassnode)
- 📖 文档: [docs.glassnode.com](https://docs.glassnode.com)

### 常见问题

1. **如何选择合适的套餐？**
   - 个人研究: 免费套餐
   - 专业交易: 基础套餐
   - 机构投资: 专业套餐

2. **历史数据的可用范围？**
   - BTC: 2009年起
   - ETH: 2015年起
   - 其他资产: 视具体情况

3. **API响应慢怎么办？**
   - 使用缓存机制
   - 批量请求数据
   - 选择合适的时间粒度

## 📄 许可与条款

使用Glassnode API需要遵守其服务条款。数据仅供参考，不构成投资建议。

---

**文档版本**: v1.0  
**更新日期**: 2024年  
**维护者**: Glassnode API中文社区

> 💡 **提示**: 本文档持续更新中，欢迎贡献和反馈！
"""
    
    return readme

def main():
    """主函数"""
    # 加载数据
    endpoints_file = "glassnode_endpoints_simplified.json"
    output_dir = "glassnode_api_docs"
    
    print(f"正在加载 {endpoints_file}...")
    categories = load_endpoints(endpoints_file)
    
    print(f"发现 {len(categories)} 个类别")
    print(f"总共 {sum(len(e) for e in categories.values())} 个端点")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成README
    print("正在生成 README.md...")
    readme = generate_readme(categories)
    with open(f"{output_dir}/README.md", 'w', encoding='utf-8') as f:
        f.write(readme)
    
    # 生成每个类别的文档
    for category, endpoints in categories.items():
        print(f"正在生成 {category}.md...")
        doc = generate_category_markdown(category, endpoints)
        with open(f"{output_dir}/{category}.md", 'w', encoding='utf-8') as f:
            f.write(doc)
    
    print(f"\n✅ 文档生成完成！")
    print(f"📁 输出目录: {output_dir}/")
    print(f"📄 生成文件:")
    print(f"   - README.md (总览)")
    for category in categories.keys():
        print(f"   - {category}.md")

if __name__ == "__main__":
    main()