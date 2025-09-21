# Glassnode API 中文文档（完整版）

## 📚 文档概览

本文档集包含Glassnode API所有 **734** 个端点的完整中文说明，分为 **20** 个类别。

## 📁 文档目录

| 类别 | 中文名称 | 端点数量 | 文档链接 |
|------|----------|----------|----------|
| addresses | 地址指标 | 50 | [查看文档](./addresses.md) |
| blockchain | 区块链基础数据 | 18 | [查看文档](./blockchain.md) |
| breakdowns | 细分数据 | 39 | [查看文档](./breakdowns.md) |
| bridges | 跨链桥数据 | 5 | [查看文档](./bridges.md) |
| defi | DeFi协议数据 | 1 | [查看文档](./defi.md) |
| derivatives | 衍生品市场 | 58 | [查看文档](./derivatives.md) |
| distribution | 分布统计 | 42 | [查看文档](./distribution.md) |
| entities | 实体分析 | 18 | [查看文档](./entities.md) |
| eth2 | 以太坊2.0 | 22 | [查看文档](./eth2.md) |
| fees | 手续费分析 | 28 | [查看文档](./fees.md) |
| indicators | 技术指标 | 158 | [查看文档](./indicators.md) |
| institutions | 机构数据 | 7 | [查看文档](./institutions.md) |
| lightning | 闪电网络 | 10 | [查看文档](./lightning.md) |
| market | 市场数据 | 32 | [查看文档](./market.md) |
| mempool | 内存池 | 10 | [查看文档](./mempool.md) |
| mining | 挖矿数据 | 9 | [查看文档](./mining.md) |
| protocols | 协议数据 | 58 | [查看文档](./protocols.md) |
| signals | 交易信号 | 14 | [查看文档](./signals.md) |
| supply | 供应量指标 | 61 | [查看文档](./supply.md) |
| transactions | 交易数据 | 94 | [查看文档](./transactions.md) |


## 🚀 快速开始

### 1. 获取API密钥

访问 [Glassnode](https://glassnode.com) 注册账号并获取API密钥。

### 2. 安装依赖

```bash
pip install requests pandas matplotlib aiohttp
```

### 3. 基本使用

```python
import requests

api_key = "YOUR_API_KEY"
url = "https://api.glassnode.com/v1/metrics/addresses/active_count"
params = {
    "a": "BTC",
    "api_key": api_key,
    "s": "24h"
}

response = requests.get(url, params=params)
data = response.json()
```

## 📊 指标分类体系

所有指标按功能分为以下主要类别：

### 链上数据类
- **地址指标**: 地址活动、余额分布、盈亏状态
- **交易数据**: 交易量、转账金额、交易类型
- **供应量指标**: 流通量、锁定量、分布情况
- **挖矿数据**: 算力、难度、矿工收入

### 市场数据类
- **市场数据**: 价格、市值、交易量
- **衍生品市场**: 期货、期权、清算
- **技术指标**: MVRV、SOPR、NVT等

### 实体分析类
- **实体分析**: 交易所、矿工、巨鲸
- **机构数据**: 灰度、ETF、上市公司

### 协议数据类
- **DeFi协议**: TVL、借贷、DEX
- **以太坊2.0**: 质押、验证者
- **闪电网络**: 节点、通道容量

## 🎯 主要特性

- ✅ 完整的中文翻译和详细说明
- ✅ 详细的指标分类和组织
- ✅ 高对比度的可视化图表
- ✅ 丰富的代码示例
- ✅ 完整的API参数说明

## 📈 数据更新

- 实时指标：10分钟更新
- 日度指标：每日UTC 00:00更新
- 历史数据：可追溯至币种创建时间

## ⚠️ 使用限制

| 账户类型 | 请求限制 |
|----------|----------|
| 免费版 | 10请求/分钟 |
| 基础版 | 30请求/分钟 |
| 专业版 | 120请求/分钟 |
| 机构版 | 自定义 |

## 🔗 相关链接

- [Glassnode官网](https://glassnode.com)
- [官方API文档](https://docs.glassnode.com)
- [Glassnode Studio](https://studio.glassnode.com)
- [Discord社区](https://discord.gg/glassnode)

---

*文档版本: 5.0 完整版*  
*更新时间: 2024年*  
*特性: 完整分类 + 详细中文说明 + 高对比度图表*
