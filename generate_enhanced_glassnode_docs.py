#!/usr/bin/env python3
"""
生成增强版Glassnode API中文文档
先显示英文原文，然后提供详细的中文解释
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any

def load_endpoints(file_path: str) -> Dict[str, List[Dict]]:
    """加载API端点数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_category_info() -> Dict[str, Dict]:
    """获取所有类别的中文信息"""
    return {
        'addresses': {
            'name_zh': '地址指标',
            'description': '分析网络中地址的行为、分布和特征，包括活跃地址、余额分布、盈亏状态等核心指标。'
        },
        'blockchain': {
            'name_zh': '区块链基础数据',
            'description': '提供区块链的基础运行数据，包括区块信息、UTXO集、网络状态等底层指标。'
        },
        'market': {
            'name_zh': '市场数据',
            'description': '全面的市场数据分析，涵盖价格、交易量、市值、已实现价值等市场核心指标。'
        },
        'supply': {
            'name_zh': '供应量指标',
            'description': '追踪加密货币的供应动态，包括流通量、锁定量、销毁量等供应端指标。'
        },
        'transactions': {
            'name_zh': '交易数据',
            'description': '深入分析链上交易活动，包括交易量、转账金额、交易类型等交易层面数据。'
        },
        'mining': {
            'name_zh': '挖矿数据',
            'description': '挖矿行业全景数据，包括算力、难度、矿工收入、区块奖励等挖矿相关指标。'
        },
        'fees': {
            'name_zh': '手续费分析',
            'description': '手续费市场分析，包括平均费用、总费用、费用压力等费用相关指标。'
        },
        'derivatives': {
            'name_zh': '衍生品市场',
            'description': '衍生品市场数据，包括期货、期权的持仓量、资金费率、清算等衍生品指标。'
        },
        'defi': {
            'name_zh': 'DeFi协议数据',
            'description': '去中心化金融协议数据，包括TVL、借贷、DEX交易量等DeFi生态指标。'
        },
        'entities': {
            'name_zh': '实体分析',
            'description': '链上实体识别和分析，包括交易所、矿池、巨鲸等实体的行为追踪。'
        },
        'distribution': {
            'name_zh': '分布统计',
            'description': '各类分布统计数据，包括余额分布、持币时间分布等统计指标。'
        },
        'indicators': {
            'name_zh': '技术指标',
            'description': '技术分析指标，包括MVRV、SOPR、NVT等链上特有的分析指标。'
        },
        'institutions': {
            'name_zh': '机构数据',
            'description': '机构投资者相关数据，包括灰度、ETF、上市公司持仓等机构指标。'
        },
        'eth2': {
            'name_zh': '以太坊2.0',
            'description': '以太坊2.0质押和验证者数据，包括质押量、验证者数量、奖励等。'
        },
        'lightning': {
            'name_zh': '闪电网络',
            'description': '比特币闪电网络数据，包括节点数、通道容量、路由等二层网络指标。'
        },
        'bridges': {
            'name_zh': '跨链桥数据',
            'description': '跨链桥协议数据，包括锁定量、跨链交易量等桥接相关指标。'
        },
        'breakdowns': {
            'name_zh': '细分数据',
            'description': '各类数据的细分统计，提供更精细的数据维度划分。'
        },
        'mempool': {
            'name_zh': '内存池',
            'description': '内存池状态监控，包括待确认交易、拥堵程度等内存池指标。'
        },
        'protocols': {
            'name_zh': '协议数据',
            'description': '各类协议的专属数据，包括特定协议的使用量、锁定量等。'
        },
        'signals': {
            'name_zh': '交易信号',
            'description': '交易信号和预警指标，提供买卖信号、风险预警等决策支持。'
        }
    }

def get_subcategory_info() -> Dict[str, str]:
    """获取子类别的中文名称映射"""
    return {
        'active': '活跃度指标',
        'count': '数量统计',
        'balance': '余额分析',
        'supply': '供应量分布',
        'accumulation': '累积地址',
        'min': '最小余额门槛',
        'holder': '持有者分析',
        'profit': '盈利地址',
        'loss': '亏损地址',
        'sending': '发送活动',
        'receiving': '接收活动',
        'new': '新增地址',
        'non': '非零地址',
        'zero': '零余额地址',
        'activity': '活动模式',
        'price': '价格指标',
        'volume': '交易量',
        'marketcap': '市值',
        'realized': '已实现价值',
        'mvrv': 'MVRV指标',
        'sopr': 'SOPR指标',
        'transaction': '交易统计',
        'transfer': '转账分析',
        'rate': '交易率',
        'hash': '哈希率',
        'difficulty': '挖矿难度',
        'revenue': '矿工收入',
        'block': '区块数据',
        'fee': '手续费',
        'gas': 'Gas费用',
        'mean': '平均费用',
        'median': '中位数费用',
        'total': '总计',
        'exchange': '交易所',
        'whale': '巨鲸',
        'shrimp': '小户',
        'long': '长期持有',
        'short': '短期持有',
        'stablecoin': '稳定币',
        'defi': 'DeFi相关',
        'eth2': 'ETH2.0',
        'lightning': '闪电网络'
    }

def generate_chinese_description(metric: str, summary: str, description: str) -> str:
    """生成详细的中文描述，包含英文原文"""
    
    # 清理英文描述
    if description:
        clean_desc = description.split('\n\n[View')[0].strip()
        clean_desc = clean_desc.replace('&#x3D;', '=')
        # 移除markdown链接但保留文字
        import re
        clean_desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_desc)
    else:
        clean_desc = summary if summary else "No description available"
    
    # 生成中文解释
    chinese_exp = generate_specific_chinese_explanation(metric, summary)
    
    # 组合完整描述
    full_description = f"""**英文原文：**
{clean_desc}

**中文解释：**
{chinese_exp}"""
    
    return full_description

def generate_specific_chinese_explanation(metric: str, summary: str) -> str:
    """根据metric类型生成具体的中文解释"""
    
    metric_lower = metric.lower()
    
    # 地址类指标
    if 'active' in metric_lower:
        if 'count' in metric_lower:
            return "统计在特定时间段内（通常为24小时）参与发送或接收交易的独立地址数量。活跃地址数是衡量网络使用率和用户参与度的核心指标。高活跃地址数通常表示：1）网络被广泛使用；2）生态系统健康发展；3）用户对网络有实际需求。活跃地址的变化趋势可以帮助判断网络的成长阶段和市场周期。"
        elif 'retention' in metric_lower:
            return "衡量地址的持续活跃程度，计算在上一个时间段活跃的地址在当前时间段继续保持活跃的比例。例如，70%的保留率意味着10个先前活跃的地址中有7个继续交易。高保留率表明：1）用户粘性强；2）网络具有持续的使用价值；3）生态系统稳定。这个指标对于评估网络的长期可持续性非常重要。"
        else:
            return "分析网络中地址的活跃模式和行为特征。通过多维度的活跃度分析，包括活跃频率、活跃时段、活跃类型等，可以深入理解用户行为模式，预测网络发展趋势，识别异常活动。"
    
    elif 'accumulation' in metric_lower:
        if 'count' in metric_lower:
            return "统计累积型地址的数量。累积地址定义为：1）至少有2次非粉尘转入；2）从未花费过资金；3）排除交易所地址；4）排除矿工地址；5）排除7年以上未活跃的地址（可能已丢失）。这类地址代表了长期看涨的投资者，他们的行为通常被视为强烈的看涨信号。"
        elif 'balance' in metric_lower:
            return "计算所有累积地址持有的总资金量。这个指标反映了长期投资者的总体持仓规模。累积余额的增长表明：1）市场信心增强；2）长期投资者在建仓；3）可能接近市场底部。相反，累积余额下降可能预示市场顶部。"
        else:
            return "全面追踪累积行为的各个方面。累积是市场底部形成的重要特征，通过监测累积地址的数量、余额、分布等多个维度，可以识别聪明钱的动向，预判市场转折点。"
    
    elif 'supply' in metric_lower and 'distribution' in metric_lower:
        return "展示不同余额区间的供应量分布情况。例如：持有0.001-0.01 BTC、0.01-0.1 BTC、0.1-1 BTC等不同规模的地址群体各持有多少比例的总供应量。这个指标帮助分析：1）财富集中度（基尼系数）；2）不同规模投资者的相对影响力；3）市场结构的演变。供应分布的变化可以揭示资金从散户到机构（或相反）的流动。"
    
    elif 'profit' in metric_lower:
        if 'count' in metric_lower:
            return "统计当前持币成本低于市场价格的地址数量。买入价格通过币最后一次移动时的价格确定。盈利地址比例高表明：1）市场情绪乐观；2）可能存在获利回吐压力；3）牛市特征明显。当盈利地址比例极高（>95%）时，往往预示短期顶部。"
        elif 'relative' in metric_lower:
            return "计算盈利地址占所有持币地址的百分比。这是一个标准化的指标，便于不同时期和不同资产之间的比较。历史数据显示，当该比例低于50%时，通常接近市场底部；高于90%时，需要警惕回调风险。"
        else:
            return "深入分析地址的盈利状况，包括盈利幅度、盈利持续时间、盈利地址的行为模式等。通过了解投资者的盈利情况，可以评估市场的获利回吐压力和持续上涨的潜力。"
    
    elif 'loss' in metric_lower:
        if 'count' in metric_lower:
            return "统计当前持币成本高于市场价格的地址数量。大量亏损地址通常出现在：1）熊市底部；2）剧烈回调后；3）投降性抛售阶段。历史经验表明，亏损地址比例极高时，往往是绝佳的买入时机。"
        elif 'relative' in metric_lower:
            return "计算亏损地址占所有持币地址的百分比。当该比例超过50%时，表明多数投资者处于亏损状态，市场可能接近底部。这个指标是识别市场极端情绪和转折点的重要工具。"
        else:
            return "全面评估地址的亏损状况。亏损数据帮助识别：1）投降性抛售的强度；2）市场底部的形成；3）支撑位的强弱。深度亏损往往伴随着市场的极度恐慌，这通常是反向投资的良机。"
    
    elif 'balance' in metric_lower:
        if 'min_' in metric_lower or 'minimum' in metric_lower:
            return "统计余额超过特定门槛的地址数据。例如，余额≥0.1 BTC、≥1 BTC、≥10 BTC等。这些门槛帮助识别不同规模的投资者群体：散户（<1 BTC）、中户（1-100 BTC）、大户（100-1000 BTC）、巨鲸（>1000 BTC）。通过追踪不同群体的行为，可以理解市场的资金流向。"
        else:
            return "分析地址余额的各个方面，包括余额分布、余额变化、余额集中度等。余额分析揭示了网络的财富结构和演变趋势，是理解市场力量对比的关键。"
    
    elif 'new' in metric_lower:
        return "统计首次在区块链上出现的新地址数量。新地址激增通常发生在：1）牛市早期（新用户涌入）；2）重大利好消息后；3）新应用或功能推出时。新地址增长是网络扩张的先行指标，但需要结合活跃度来判断是真实增长还是虚假繁荣。"
    
    elif 'non_zero' in metric_lower or 'nonzero' in metric_lower:
        return "统计当前余额大于0的所有地址数量。这是衡量实际持币用户规模的关键指标。非零地址的持续增长表明：1）更多用户选择持有而非卖出；2）网络的价值存储功能得到认可；3）长期采用趋势向好。这个指标过滤了所有已清空的地址，反映真实的用户基础。"
    
    elif 'zero' in metric_lower and 'balance' in metric_lower:
        return "统计余额为0但曾经持有过资产的地址数量。零余额地址增加可能因为：1）用户完全退出（看跌信号）；2）资金整合到其他地址（中性）；3）转移到交易所（可能卖出）。大量地址清零通常发生在市场恐慌时期。"
    
    # 交易和转账指标
    elif 'transaction' in metric_lower or 'transfer' in metric_lower:
        if 'count' in metric_lower:
            return "统计区块链上的交易或转账数量。交易数量反映网络的使用频率和采用程度。高交易量表明：1）网络功能被积极使用；2）经济活动活跃；3）可能的网络拥堵。交易数量的趋势变化是评估网络健康度的基础指标。"
        elif 'volume' in metric_lower:
            return "计算交易或转账的总价值。交易量反映经济活动的规模，是网络价值流动的直接体现。异常高的交易量可能因为：1）大户移动资金；2）交易所之间转账；3）市场剧烈波动期间的活跃交易。需要结合其他指标判断交易量的性质。"
        elif 'rate' in metric_lower:
            return "计算交易发生的速率或频率。交易率的变化反映网络活动的节奏变化，可以用于识别异常活动模式或网络使用的周期性规律。"
        else:
            return "全面分析链上交易活动的各个维度，包括交易类型、交易规模、交易频率等。交易数据是理解网络经济活动的基础，通过深入分析可以识别市场趋势和用户行为模式。"
    
    # UTXO相关指标
    elif 'utxo' in metric_lower:
        if 'created' in metric_lower:
            if 'value' in metric_lower:
                return "统计新创建UTXO的价值。当交易产生新的输出时，就创建了新的UTXO。高创建价值表明：1）大额交易活跃；2）资金正在分散；3）可能的分发或空投活动。UTXO创建模式可以揭示资金的流动方向和市场参与者的意图。"
            else:
                return "统计新创建UTXO的数量。大量UTXO创建表明：1）交易活动频繁；2）资金碎片化加剧；3）更多的独立资金单位被创建。这可能预示着资金的分散化趋势。"
        elif 'spent' in metric_lower:
            if 'value' in metric_lower:
                return "统计被花费UTXO的价值。UTXO被花费意味着之前的输出被用作新交易的输入。高花费价值可能因为：1）长期持有者开始移动资金；2）大额资金整合；3）交易所或机构的资金管理。老旧UTXO的花费特别值得关注，因为可能预示市场转折。"
            else:
                return "统计被花费UTXO的数量。大量UTXO被花费通常伴随着：1）资金整合活动；2）批量交易处理；3）钱包优化操作。通过分析UTXO的年龄分布，可以了解不同持有期的投资者行为。"
        else:
            return "UTXO（未花费交易输出）是比特币等基于UTXO模型的区块链的基础数据结构。每个UTXO代表一个可以被花费的资金单位。UTXO的创建、花费、分布等数据提供了对链上经济活动的深入洞察。UTXO分析可以揭示资金流动、持有模式和市场周期。"
    
    # 挖矿相关指标
    elif 'mining' in metric_lower or 'hash' in metric_lower:
        if 'rate' in metric_lower or 'hashrate' in metric_lower:
            return "衡量全网的总计算能力，以每秒哈希运算次数表示。哈希率是网络安全性的直接指标：1）高哈希率意味着攻击网络的成本极高；2）哈希率增长表明矿工对未来有信心；3）哈希率下降可能因为挖矿不再盈利。哈希率与价格通常存在正相关关系。"
        elif 'difficulty' in metric_lower:
            return "挖矿难度动态调整以维持稳定的出块时间。难度上升表明：1）更多算力加入网络；2）矿工竞争加剧；3）网络安全性提高。难度调整机制确保了区块链的稳定运行，是中本聪共识的核心组成部分。"
        elif 'revenue' in metric_lower:
            return "计算矿工的总收入，包括区块奖励和交易手续费。矿工收入影响：1）算力的进入和退出；2）网络的安全预算；3）挖矿产业的可持续性。当矿工收入低于成本时，可能导致算力外流和网络安全降低。"
        else:
            return "全面追踪挖矿生态系统的各个方面。挖矿数据反映了网络的安全投入、矿工的盈利状况和产业的健康度。通过分析挖矿指标，可以预判算力变化趋势和网络的长期安全性。"
    
    # 费用相关指标
    elif 'fee' in metric_lower or 'gas' in metric_lower:
        if 'mean' in metric_lower or 'average' in metric_lower:
            return "计算网络交易费用的平均值。平均费用反映：1）网络的拥堵程度；2）用户的支付意愿；3）区块空间的供需关系。高费用期间，只有高价值交易才会上链；低费用期间，更多小额交易变得可行。费用市场是评估网络使用需求的重要指标。"
        elif 'median' in metric_lower:
            return "计算交易费用的中位数。相比平均值，中位数不受极端高额费用的影响，更能反映典型用户的费用负担。中位数费用是评估网络可用性和普通用户体验的关键指标。"
        elif 'total' in metric_lower or 'sum' in metric_lower:
            return "统计支付给矿工或验证者的总手续费。总费用反映：1）网络的安全预算；2）用户对区块空间的总需求；3）矿工/验证者的收入来源。在区块奖励减少的情况下，手续费将成为维护网络安全的主要激励。"
        else:
            return "分析网络费用市场的动态。费用数据揭示了区块空间的稀缺性、用户的紧急程度和网络的经济可持续性。通过费用分析，可以优化交易时机，评估网络的采用程度。"
    
    # 市场相关指标
    elif 'price' in metric_lower or 'market' in metric_lower:
        if 'realized' in metric_lower:
            return "计算已实现市值或已实现价格。已实现价格是所有币按最后移动时的价格加权平均得出，反映了市场的成本基础。当市场价格高于已实现价格时，市场整体盈利；反之则整体亏损。这是判断市场周期位置的重要指标。"
        elif 'mvrv' in metric_lower:
            return "MVRV（市值与已实现价值比率）衡量当前市值与已实现价值的比率。MVRV > 1表示市场整体盈利，值越高表示盈利越多；MVRV < 1表示市场整体亏损。历史数据显示，MVRV > 3.5常见于市场顶部，MVRV < 1常见于市场底部。"
        elif 'sopr' in metric_lower:
            return "SOPR（花费输出利润率）衡量被移动的币的盈亏状态。SOPR > 1表示移动的币平均盈利，SOPR < 1表示平均亏损。SOPR回归1.0常作为支撑/阻力位。在牛市中，SOPR很少跌破1.0；在熊市中，SOPR难以持续高于1.0。"
        else:
            return "追踪市场价格和估值指标。市场数据提供价格发现、估值参考和市场情绪评估。通过结合链上数据和市场数据，可以获得更全面的市场洞察。"
    
    # 交易所相关指标
    elif 'exchange' in metric_lower:
        if 'inflow' in metric_lower:
            return "追踪流入交易所的资金量。大量资金流入交易所通常预示：1）投资者准备卖出（看跌）；2）追加保证金（中性）；3）套利交易（短期）。持续的交易所流入是潜在抛压的预警信号。"
        elif 'outflow' in metric_lower:
            return "追踪从交易所流出的资金量。资金流出交易所表明：1）投资者转为长期持有（看涨）；2）提现到冷钱包保管（减少流通）；3）DeFi或其他链上应用需求。大规模流出通常被视为供应减少的信号。"
        elif 'balance' in metric_lower:
            return "监测交易所持有的总余额。交易所余额是可立即交易的供应量指标。余额下降表示：1）可售供应减少；2）投资者偏好自托管；3）长期持有意愿增强。历史低位的交易所余额常预示供应短缺导致的价格上涨。"
        else:
            return "全面分析交易所相关的链上活动。交易所是连接链上和链下市场的关键节点，其资金流动直接影响市场供需。通过监测交易所数据，可以预判短期价格压力和市场情绪变化。"
    
    # 默认描述
    return f"分析{summary if summary else metric}相关的链上数据。这个指标通过追踪区块链上的实时数据，提供了传统金融分析无法获得的透明度和洞察力。链上数据的优势在于：1）数据真实可验证；2）实时更新无延迟；3）覆盖所有参与者。通过综合分析多个链上指标，投资者可以做出更明智的决策，研究人员可以深入理解市场机制。"

def translate_summary(summary: str) -> str:
    """将英文summary翻译为中文名称"""
    common_terms = {
        'Active Addresses': '活跃地址数',
        'Accumulation Addresses': '累积地址数',
        'Accumulation Balance': '累积地址余额',
        'Activity Retention Rate': '活跃保留率',
        'Address Supply Distribution': '地址供应分布',
        'Addresses in Loss': '亏损地址数',
        'Addresses in Profit': '盈利地址数',
        'New Addresses': '新增地址数',
        'Zero Balance Addresses': '零余额地址数',
        'Non-Zero Addresses': '非零地址数',
        'Sending Addresses': '发送地址数',
        'Receiving Addresses': '接收地址数',
        'Balance': '余额',
        'Count': '数量',
        'Volume': '交易量',
        'Value': '价值',
        'Mean': '平均值',
        'Median': '中位数',
        'Sum': '总和',
        'Total': '总计',
        'Distribution': '分布',
        'Relative': '相对',
        'Percentage': '百分比',
        'Rate': '比率',
        'Ratio': '比例',
        'Index': '指数',
        'Score': '评分',
        'with contracts': '（含合约）',
        'UTXO': 'UTXO',
        'Created': '创建',
        'Spent': '花费',
        'Transaction': '交易',
        'Transfer': '转账',
        'Fee': '手续费',
        'Gas': 'Gas费用',
        'Block': '区块',
        'Height': '高度',
        'Size': '大小',
        'Interval': '间隔',
        'Hash Rate': '哈希率',
        'Difficulty': '难度',
        'Mining': '挖矿',
        'Revenue': '收入',
        'Reward': '奖励',
        'Supply': '供应量',
        'Circulating': '流通',
        'Locked': '锁定',
        'Burned': '销毁',
        'Issued': '发行',
        'Inflation': '通胀',
        'Exchange': '交易所',
        'Inflow': '流入',
        'Outflow': '流出',
        'Netflow': '净流量',
        'Whale': '巨鲸',
        'Holder': '持有者',
        'Long-term': '长期',
        'Short-term': '短期',
        'Realized': '已实现',
        'Unrealized': '未实现',
        'Profit': '盈利',
        'Loss': '亏损',
        'MVRV': 'MVRV',
        'SOPR': 'SOPR',
        'NVT': 'NVT',
        'Price': '价格',
        'Market Cap': '市值',
        'Marketcap': '市值'
    }
    
    result = summary
    for eng, chn in common_terms.items():
        result = result.replace(eng, chn)
    
    return result

def group_endpoints_by_subcategory(endpoints: List[Dict]) -> Dict[str, List[Dict]]:
    """按子类别对端点进行分组"""
    subcategories = defaultdict(list)
    
    for endpoint in endpoints:
        metric = endpoint.get('metric', '')
        
        # 尝试识别子类别
        if 'active' in metric or 'activity' in metric:
            subcategories['active'].append(endpoint)
        elif 'min_' in metric:
            subcategories['min'].append(endpoint)
        elif 'profit' in metric:
            subcategories['profit'].append(endpoint)
        elif 'loss' in metric:
            subcategories['loss'].append(endpoint)
        elif 'accumulation' in metric:
            subcategories['accumulation'].append(endpoint)
        elif 'supply' in metric:
            subcategories['supply'].append(endpoint)
        elif 'balance' in metric:
            subcategories['balance'].append(endpoint)
        elif 'holder' in metric:
            subcategories['holder'].append(endpoint)
        elif 'sending' in metric:
            subcategories['sending'].append(endpoint)
        elif 'receiving' in metric:
            subcategories['receiving'].append(endpoint)
        elif 'new' in metric:
            subcategories['new'].append(endpoint)
        elif 'non_zero' in metric:
            subcategories['non'].append(endpoint)
        elif 'zero' in metric:
            subcategories['zero'].append(endpoint)
        elif 'count' in metric:
            subcategories['count'].append(endpoint)
        else:
            if '_' in metric:
                prefix = metric.split('_')[0]
                subcategories[prefix].append(endpoint)
            else:
                subcategories['other'].append(endpoint)
    
    return dict(subcategories)

def generate_mermaid_diagram(category: str, endpoints: List[Dict], subcategories: Dict[str, List[Dict]]) -> str:
    """生成Mermaid图表"""
    category_info = get_category_info()
    subcat_info = get_subcategory_info()
    
    cat_zh = category_info[category]['name_zh']
    
    # 按数量排序子类别，取前6个
    sorted_subcats = sorted(subcategories.items(), key=lambda x: len(x[1]), reverse=True)[:6]
    
    mermaid = f"""```mermaid
graph LR
    A["{cat_zh}<br/>共{len(endpoints)}个指标"]
    A:::mainNode
    """
    
    for i, (subcat, subcat_endpoints) in enumerate(sorted_subcats, 1):
        subcat_zh = subcat_info.get(subcat, subcat.upper())
        
        # 添加子类别节点
        mermaid += f"""
    A --> B{i}["{subcat_zh}<br/>{len(subcat_endpoints)}个指标"]
    B{i}:::categoryNode"""
        
        # 为每个子类别添加前3个指标
        for j, endpoint in enumerate(subcat_endpoints[:3], 1):
            metric = endpoint.get('metric', '')
            summary = endpoint.get('summary', metric)
            name_zh = translate_summary(summary)
            
            mermaid += f"""
    B{i} --> C{i}_{j}["{name_zh}"]
    C{i}_{j}:::metricNode"""
    
    # 样式定义
    mermaid += """
    
    %% 高对比度样式
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
```"""
    
    return mermaid

def generate_subcategory_section(subcat: str, endpoints: List[Dict]) -> str:
    """生成子类别的详细文档部分"""
    subcat_info = get_subcategory_info()
    subcat_zh = subcat_info.get(subcat, subcat.upper())
    
    section = f"""### 📊 {subcat_zh}（{len(endpoints)}个指标）

本子类别包含以下详细指标：

"""
    
    for i, endpoint in enumerate(endpoints, 1):
        metric = endpoint.get('metric', '')
        summary = endpoint.get('summary', '')
        description = endpoint.get('description', '')
        path = endpoint.get('path', '')
        
        name_zh = translate_summary(summary) if summary else metric
        full_desc = generate_chinese_description(metric, summary, description)
        
        section += f"""#### {i}. {name_zh}

- **指标代码**: `{metric}`
- **API路径**: `{path}`
- **英文名称**: {summary}

{full_desc}

**使用示例**：
```python
# 获取{name_zh}数据
df = client.get_metric(
    "{path}",
    asset="BTC",
    resolution="24h"
)
```

---

"""
    
    return section

def generate_category_document(category: str, endpoints: List[Dict]) -> str:
    """生成完整的类别文档"""
    category_info = get_category_info()
    cat_info = category_info.get(category, {})
    cat_zh = cat_info.get('name_zh', category)
    cat_desc = cat_info.get('description', '')
    
    # 按子类别分组
    subcategories = group_endpoints_by_subcategory(endpoints)
    
    # 开始生成文档
    doc = f"""# {cat_zh} ({category})

## 📝 类别描述

{cat_desc}

## 📊 指标概览

本类别共包含 **{len(endpoints)}** 个指标，涵盖以下主要子类别：

| 子类别 | 指标数量 | 主要功能 |
|--------|----------|----------|
"""
    
    # 按数量排序子类别
    sorted_subcats = sorted(subcategories.items(), key=lambda x: len(x[1]), reverse=True)
    subcat_info = get_subcategory_info()
    
    for subcat, subcat_endpoints in sorted_subcats[:10]:
        subcat_zh = subcat_info.get(subcat, subcat.upper())
        doc += f"| {subcat_zh} | {len(subcat_endpoints)} | "
        
        # 添加简短描述
        if 'active' in subcat:
            doc += "网络活跃度和用户参与"
        elif 'balance' in subcat:
            doc += "地址余额分布和变化"
        elif 'profit' in subcat:
            doc += "盈利状态分析"
        elif 'loss' in subcat:
            doc += "亏损状态评估"
        elif 'supply' in subcat:
            doc += "供应量分布统计"
        elif 'accumulation' in subcat:
            doc += "累积行为追踪"
        elif 'new' in subcat:
            doc += "新增用户和采用度"
        elif 'transaction' in subcat or 'transfer' in subcat:
            doc += "交易活动分析"
        elif 'fee' in subcat:
            doc += "手续费市场动态"
        elif 'mining' in subcat:
            doc += "挖矿生态监测"
        else:
            doc += "专门数据分析"
        
        doc += " |\n"
    
    # 添加指标体系图
    doc += f"""
## 🎨 指标体系结构图

{generate_mermaid_diagram(category, endpoints, subcategories)}

## 📂 详细指标说明

"""
    
    # 按子类别生成详细文档
    for subcat, subcat_endpoints in sorted_subcats:
        doc += generate_subcategory_section(subcat, subcat_endpoints)
    
    # 添加完整的指标列表
    doc += """## 📊 完整指标列表

| # | 指标名称 | 指标代码 | API路径 |
|---|----------|----------|---------|
"""
    
    for i, endpoint in enumerate(endpoints, 1):
        metric = endpoint.get('metric', '')
        summary = endpoint.get('summary', '')
        path = endpoint.get('path', '')
        name_zh = translate_summary(summary) if summary else metric
        
        doc += f"| {i} | {name_zh} | `{metric}` | `{path}` |\n"
    
    # 添加使用示例
    doc += """
## 💻 代码示例

### Python SDK 使用示例

```python
from glassnode import GlassnodeClient

# 初始化客户端
client = GlassnodeClient(api_key="YOUR_API_KEY")

# 获取单个指标
data = client.get(
    "/v1/metrics/addresses/active_count",
    asset="BTC",
    resolution="24h",
    since="2024-01-01"
)

# 批量获取多个指标
metrics = [
    "active_count",
    "new",
    "non_zero_count"
]

results = {}
for metric in metrics:
    results[metric] = client.get(
        f"/v1/metrics/addresses/{metric}",
        asset="BTC"
    )
```

## 📚 参考资源

- [Glassnode官方文档](https://docs.glassnode.com)
- [Glassnode Studio](https://studio.glassnode.com)
- [API访问说明](https://docs.glassnode.com/basic-api/api)

---

*最后更新：2024年*
"""
    
    return doc

def generate_readme(categories: Dict[str, List[Dict]]) -> str:
    """生成README文件"""
    category_info = get_category_info()
    
    readme = """# 📊 Glassnode API 中文文档

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
"""
    
    # 按指标数量排序
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, endpoints in sorted_categories:
        cat_info = category_info.get(category, {})
        cat_zh = cat_info.get('name_zh', category)
        readme += f"| {category} | {cat_zh} | {len(endpoints)} | [查看文档](./{category}.md) |\n"
    
    total_metrics = sum(len(endpoints) for endpoints in categories.values())
    
    readme += f"""

## 📊 统计信息

- **总指标数量**: {total_metrics}
- **类别数量**: {len(categories)}
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

print(f"活跃地址数: {{data[-1]['v']}}")
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
"""
    
    return readme

def main():
    """主函数"""
    # 加载数据
    print("加载API端点数据...")
    endpoints_by_category = load_endpoints('glassnode_endpoints_simplified.json')
    
    # 创建输出目录
    output_dir = 'glassnode_api_docs_enhanced'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成每个类别的文档
    for category, endpoints in endpoints_by_category.items():
        print(f"生成 {category} 类别文档（包含 {len(endpoints)} 个指标）...")
        
        doc_content = generate_category_document(category, endpoints)
        
        # 保存文档
        output_file = os.path.join(output_dir, f'{category}.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"  ✅ 已保存到 {output_file}")
    
    # 生成README
    print("生成 README.md...")
    readme_content = generate_readme(endpoints_by_category)
    readme_file = os.path.join(output_dir, 'README.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"  ✅ 已保存到 {readme_file}")
    
    # 统计信息
    total_metrics = sum(len(endpoints) for endpoints in endpoints_by_category.values())
    print(f"\n✨ 文档生成完成！")
    print(f"  - 总计 {len(endpoints_by_category)} 个类别")
    print(f"  - 总计 {total_metrics} 个指标")
    print(f"  - 输出目录: {output_dir}")

if __name__ == "__main__":
    main()