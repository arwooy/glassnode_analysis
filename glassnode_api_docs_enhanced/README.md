# 📊 Glassnode API 中文文档

## 🌟 概述

这是Glassnode API的完整中文文档，包含了所有734个链上数据指标的详细说明。每个指标都提供了：

- 📝 英文原文描述
- 🇨🇳 详细中文解释
- 💡 使用场景说明
- 🔍 数据解读指南
- 💻 代码示例

## 📚 文档结构

本文档按照API类别进行组织，共包含20个主要类别：

| 类别 | 中文名称 | 指标数量 | 文档链接 |
|------|----------|----------|----------|
| indicators | 技术指标 | 158 | [查看文档](./indicators.md) |
| transactions | 交易数据 | 94 | [查看文档](./transactions.md) |
| supply | 供应量指标 | 61 | [查看文档](./supply.md) |
| derivatives | 衍生品市场 | 58 | [查看文档](./derivatives.md) |
| protocols | 协议数据 | 58 | [查看文档](./protocols.md) |
| addresses | 地址指标 | 50 | [查看文档](./addresses.md) |
| distribution | 分布统计 | 42 | [查看文档](./distribution.md) |
| breakdowns | 细分数据 | 39 | [查看文档](./breakdowns.md) |
| market | 市场数据 | 32 | [查看文档](./market.md) |
| fees | 手续费分析 | 28 | [查看文档](./fees.md) |
| eth2 | 以太坊2.0 | 22 | [查看文档](./eth2.md) |
| blockchain | 区块链基础数据 | 18 | [查看文档](./blockchain.md) |
| entities | 实体分析 | 18 | [查看文档](./entities.md) |
| signals | 交易信号 | 14 | [查看文档](./signals.md) |
| lightning | 闪电网络 | 10 | [查看文档](./lightning.md) |
| mempool | 内存池 | 10 | [查看文档](./mempool.md) |
| mining | 挖矿数据 | 9 | [查看文档](./mining.md) |
| institutions | 机构数据 | 7 | [查看文档](./institutions.md) |
| bridges | 跨链桥数据 | 5 | [查看文档](./bridges.md) |
| defi | DeFi协议数据 | 1 | [查看文档](./defi.md) |



## 🕐 PIT (Point in Time) API

特殊的历史数据查询接口，用于获取特定历史时间点的数据快照：

- [PIT API 完整文档](./pit_api.md) - 时间点数据查询，用于回测和历史分析

## 📊 统计信息

- **总指标数量**: 734
- **类别数量**: 20
- **最后更新**: 2024年12月

## 🚀 快速开始

### 1. 获取API密钥

访问 [Glassnode官网](https://glassnode.com) 注册账户并获取API密钥。

### 2. 安装SDK

```bash
pip install glassnode
```

### 3. 使用示例

```python
from glassnode import GlassnodeClient

# 初始化客户端
client = GlassnodeClient(api_key="YOUR_API_KEY")

# 获取比特币活跃地址数
data = client.get(
    "/v1/metrics/addresses/active_count",
    asset="BTC",
    resolution="24h"
)

print(f"活跃地址数: {data[-1]['v']}")
```

## 🔍 如何使用本文档

1. **按类别浏览**: 点击上方表格中的文档链接，查看特定类别的所有指标
2. **搜索特定指标**: 使用浏览器的搜索功能（Ctrl+F）查找特定指标
3. **理解指标含义**: 每个指标都包含详细的中文解释和使用场景
4. **查看代码示例**: 每个类别文档都包含完整的Python代码示例

## 📝 指标解读指南

### 关键指标分类

1. **基础指标**: 活跃地址、交易量、手续费等
2. **市场指标**: MVRV、SOPR、已实现价格等
3. **行为指标**: 累积地址、盈亏分布、持有时间等
4. **衍生指标**: NVT、难度调整、矿工收入等

### 数据更新频率

- **实时数据**: 区块确认后立即更新
- **日度数据**: 每日UTC 00:00更新
- **小时数据**: 每小时更新

## 🤝 贡献

欢迎提交Issue或Pull Request来改进文档。

## 📄 许可证

本文档基于Glassnode官方API文档翻译和扩展。

## 🔗 相关链接

- [Glassnode官网](https://glassnode.com)
- [官方API文档](https://docs.glassnode.com)
- [Glassnode Studio](https://studio.glassnode.com)
- [Glassnode Academy](https://academy.glassnode.com)

---

*本文档由自动化脚本生成，如有错误请及时反馈*
