#!/usr/bin/env python3
"""
生成完整的Glassnode API中文文档
保持原有的类别分类结构，同时提供完整详细的指标说明
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
        # 地址相关
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
        
        # 市场相关
        'price': '价格指标',
        'volume': '交易量',
        'marketcap': '市值',
        'realized': '已实现价值',
        'mvrv': 'MVRV指标',
        'sopr': 'SOPR指标',
        
        # 交易相关
        'transaction': '交易统计',
        'transfer': '转账分析',
        'rate': '交易率',
        
        # 挖矿相关
        'hash': '哈希率',
        'difficulty': '挖矿难度',
        'revenue': '矿工收入',
        'block': '区块数据',
        
        # 费用相关
        'fee': '手续费',
        'gas': 'Gas费用',
        'mean': '平均费用',
        'median': '中位数费用',
        'total': '总计',
        
        # 其他
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

def get_comprehensive_metric_descriptions() -> Dict[str, Dict]:
    """获取全面的指标中文描述"""
    return {
        # 地址类指标 - 活跃度
        'active_count': {
            'name': '活跃地址数',
            'desc': '统计在指定时间窗口内（通常为24小时）至少发生过一次交易（发送或接收）的独立地址数量。这是衡量网络活跃度和用户参与度的核心指标，能够反映网络的健康状况和成长趋势。高活跃地址数通常表示网络使用率高，生态系统活跃'
        },
        'active_count_with_contracts': {
            'name': '包含合约的活跃地址数',
            'desc': '统计包括智能合约地址在内的所有活跃地址数量。这个指标更全面地反映了网络活动，特别适用于以太坊等支持智能合约的区块链，能够捕捉DeFi、NFT和其他dApp的活动。对于评估整个生态系统的活跃度非常重要'
        },
        'activity_retention_rate': {
            'name': '地址活跃保留率',
            'desc': '衡量在特定时间段内活跃的地址在后续时间段继续保持活跃的比例。这个指标反映用户粘性和网络的持续吸引力，高保留率表明用户对网络有持续的使用需求，是评估网络长期价值的重要指标'
        },
        'activity_retention_monthly': {
            'name': '月度活跃保留率',
            'desc': '统计上个月活跃的地址在本月继续保持活跃的比例。这是评估用户长期参与度的关键指标，能够帮助识别网络的用户留存情况和生态系统的健康程度'
        },
        
        # 地址类指标 - 累积
        'accumulation_count': {
            'name': '累积地址总数',
            'desc': '从创世区块以来所有曾经持有过该资产的独立地址总数。反映了网络的历史参与度和累计用户规模，是评估网络长期增长和采用度的重要指标。这个数字只会增加不会减少，代表了网络的总体覆盖范围'
        },
        'accumulation_balance': {
            'name': '累积地址余额分布',
            'desc': '展示不同余额区间的累积地址数量分布。帮助分析财富集中度和持币结构的历史演变，可以识别鲸鱼地址和散户的分布情况。通过这个指标可以了解网络的财富分配是否健康'
        },
        
        # 地址类指标 - 新增
        'new': {
            'name': '新增地址数',
            'desc': '统计在指定时间内首次在区块链上出现的新地址数量。反映新用户的加入速度和网络的增长动力，是预测未来发展趋势的先行指标。新地址激增可能预示着市场兴趣增加或新应用的推出'
        },
        
        # 地址类指标 - 余额状态
        'non_zero_count': {
            'name': '非零余额地址数',
            'desc': '当前余额大于0的所有地址数量。反映实际持有该资产的用户总规模，是衡量真实用户基础的关键指标。这个数字的增长表明更多用户选择持有而非清空其资产'
        },
        'zero_balance_count': {
            'name': '零余额地址数',
            'desc': '当前余额为0但曾经持有过该资产的地址数量。反映历史用户流失情况，帮助分析用户留存和资产流动性。大量零余额地址可能表明用户流失或资产集中化'
        },
        
        # 地址类指标 - 交易活动
        'sending_count': {
            'name': '发送地址数',
            'desc': '在指定时间内至少发送过一次转账的地址数量。反映主动交易用户的规模，是衡量网络交易活跃度的重要指标。高发送地址数表明用户积极使用网络进行价值转移'
        },
        'receiving_count': {
            'name': '接收地址数',
            'desc': '在指定时间内至少接收过一次转账的地址数量。反映资金流入的分布广度，帮助判断资金的集中或分散程度。大量接收地址可能表示资金分散流入，市场参与度高'
        },
        
        # 地址类指标 - 盈亏状态
        'profit_count': {
            'name': '盈利地址数',
            'desc': '当前持币成本低于市场价格的地址数量。反映市场中处于账面盈利状态的投资者规模，是判断市场情绪和潜在卖压的重要指标。高比例的盈利地址可能带来获利了结的压力'
        },
        'profit_relative': {
            'name': '盈利地址占比',
            'desc': '盈利地址占所有非零余额地址的百分比。这个相对指标能够更好地反映市场整体的盈利状况，当该比例过高时，可能预示着短期调整风险'
        },
        'loss_count': {
            'name': '亏损地址数',
            'desc': '当前持币成本高于市场价格的地址数量。反映市场中处于账面亏损状态的投资者规模，帮助识别支撑位和套牢盘分布。大量亏损地址可能形成重要的心理支撑位'
        },
        'loss_relative': {
            'name': '亏损地址占比',
            'desc': '亏损地址占所有非零余额地址的百分比。高亏损占比通常出现在市场底部区域，可能是反转信号的先兆'
        },
        
        # 供应量分布指标
        'supply_distribution_relative': {
            'name': '相对供应量分布',
            'desc': '展示不同地址组别持有的币量占总供应量的百分比分布。这个指标用于分析财富集中度和市场结构，可以识别大户控盘程度。通过追踪供应量在不同规模地址间的分布变化，可以判断市场是在集中还是分散'
        },
        'supply_balance_less_0001': {
            'name': '余额<0.001币的地址持有量',
            'desc': '统计余额小于0.001个币的所有地址持有的总供应量。这些通常是粉尘地址或废弃地址，其供应量占比反映了网络中无效或休眠资金的规模'
        },
        'supply_balance_0001_001': {
            'name': '余额0.001-0.01币的地址持有量',
            'desc': '统计余额在0.001到0.01个币之间的地址持有的总供应量。这个区间通常包含小额试用用户或新用户，反映了网络的基础用户参与情况'
        },
        'supply_balance_001_01': {
            'name': '余额0.01-0.1币的地址持有量',
            'desc': '统计余额在0.01到0.1个币之间的地址持有的总供应量。这个区间代表了小额投资者的参与度，是评估散户市场的重要指标'
        },
        'supply_balance_01_1': {
            'name': '余额0.1-1币的地址持有量',
            'desc': '统计余额在0.1到1个币之间的地址持有的总供应量。这个区间的持有者通常是认真的个人投资者，其变化反映了零售投资者的信心'
        },
        'supply_balance_1_10': {
            'name': '余额1-10币的地址持有量',
            'desc': '统计余额在1到10个币之间的地址持有的总供应量。这是中等规模投资者的主要区间，其供应量变化能够反映市场的中坚力量动向'
        },
        'supply_balance_10_100': {
            'name': '余额10-100币的地址持有量',
            'desc': '统计余额在10到100个币之间的地址持有的总供应量。这个区间包含了较大的个人投资者和小型机构，是市场的重要组成部分'
        },
        'supply_balance_100_1k': {
            'name': '余额100-1000币的地址持有量',
            'desc': '统计余额在100到1000个币之间的地址持有的总供应量。这些是大额持有者，其行为对市场价格有显著影响'
        },
        'supply_balance_1k_10k': {
            'name': '余额1千-1万币的地址持有量',
            'desc': '统计余额在1000到10000个币之间的地址持有的总供应量。这个区间主要是巨鲸和机构投资者，其资金流向是市场的风向标'
        },
        'supply_balance_10k_100k': {
            'name': '余额1万-10万币的地址持有量',
            'desc': '统计余额在10000到100000个币之间的地址持有的总供应量。这些超大户的动向对市场有决定性影响，需要密切关注'
        },
        'supply_balance_more_100k': {
            'name': '余额>10万币的地址持有量',
            'desc': '统计余额超过100000个币的地址持有的总供应量。这些是最大的持有者，包括交易所、托管机构和超级巨鲸，其行为可以主导市场走向'
        },
        
        # 最小余额门槛系列 - 币数量
        'min_1_count': {
            'name': '持有≥1币的地址数',
            'desc': '余额大于或等于1个原生币的地址数量。追踪"整币持有者"群体的规模变化，是评估币种分布广度的重要指标。整币持有者的增加通常被视为积极信号，表明更多人愿意持有完整单位的资产'
        },
        'min_10_count': {
            'name': '持有≥10币的地址数',
            'desc': '余额大于或等于10个原生币的地址数量。反映中等规模持有者的数量变化，这个群体通常是市场的中坚力量，其增减能够反映市场信心的变化'
        },
        'min_100_count': {
            'name': '持有≥100币的地址数',
            'desc': '余额大于或等于100个原生币的地址数量。追踪大额持有者群体的规模，这些地址的累积或分散行为能够预示市场趋势的变化'
        },
        'min_1k_count': {
            'name': '持有≥1000币的地址数',
            'desc': '余额大于或等于1000个原生币的地址数量。反映"巨鲸"级别持有者的数量，这些地址的行为可能对市场产生重大影响，其增减是市场集中度的重要指标'
        },
        'min_10k_count': {
            'name': '持有≥10000币的地址数',
            'desc': '余额大于或等于10000个原生币的地址数量。追踪超大型持有者（机构或早期投资者）的规模和动向，这个群体的变化往往预示着市场的长期趋势'
        },
        'min_100k_count': {
            'name': '持有≥100000币的地址数',
            'desc': '余额大于或等于100000个原生币的地址数量。这些是市场中的超级巨鲸，包括大型机构、交易所冷钱包等，其数量变化反映了机构参与度'
        },
        
        # 最小余额门槛系列 - 美元价值
        'min_1_usd_count': {
            'name': '持有≥1美元的地址数',
            'desc': '以美元计价余额大于或等于1美元的地址数量。这个指标评估实际有经济价值的地址规模，过滤掉粉尘地址，更准确地反映真实用户数量'
        },
        'min_10_usd_count': {
            'name': '持有≥10美元的地址数',
            'desc': '以美元计价余额大于或等于10美元的地址数量。筛选出有一定经济意义的活跃用户，这个门槛通常能够过滤掉测试地址和无意义的小额地址'
        },
        'min_100_usd_count': {
            'name': '持有≥100美元的地址数',
            'desc': '以美元计价余额大于或等于100美元的地址数量。反映有实质性投资的用户群体规模，这个级别的持有者通常对价格波动有一定承受能力'
        },
        'min_1k_usd_count': {
            'name': '持有≥1千美元的地址数',
            'desc': '以美元计价余额大于或等于1000美元的地址数量。追踪中等投资者的参与度，这个群体是市场流动性的重要提供者'
        },
        'min_10k_usd_count': {
            'name': '持有≥1万美元的地址数',
            'desc': '以美元计价余额大于或等于10000美元的地址数量。反映高净值投资者的数量变化，这个指标是判断机构和专业投资者兴趣的风向标'
        },
        'min_100k_usd_count': {
            'name': '持有≥10万美元的地址数',
            'desc': '以美元计价余额大于或等于100000美元的地址数量。追踪富裕投资者和小型机构的参与程度，其增长通常预示着市场的成熟和机构化'
        },
        'min_1m_usd_count': {
            'name': '持有≥100万美元的地址数',
            'desc': '以美元计价余额大于或等于1000000美元的地址数量。监控百万富翁级别投资者和大型机构的数量变化，是市场机构化程度的重要指标'
        },
        'min_10m_usd_count': {
            'name': '持有≥1000万美元的地址数',
            'desc': '以美元计价余额大于或等于10000000美元的地址数量。追踪超高净值个人和大型机构投资者的动向，这些地址的变化对市场有重大影响'
        },
        
        # 持有者分析
        'holder_accumulation_ratio': {
            'name': '持有者累积比率',
            'desc': '衡量地址累积（增加持仓）与分发（减少持仓）的相对强度。正值表示净累积，负值表示净分发。这个指标能够识别市场是处于累积阶段还是分发阶段'
        },
        'holder_retention_rate': {
            'name': '持有者保留率',
            'desc': '统计在特定时间段内继续持有资产未卖出的地址比例。高保留率表明持有者对资产有长期信心，是市场稳定性的积极信号'
        },
        'holder_growth_rate': {
            'name': '持有者增长率',
            'desc': '衡量持有者数量的增长速度。正增长率表示新持有者的加入速度超过了退出速度，是网络扩张的标志'
        }
    }

def get_metric_chinese_description(endpoint: Dict) -> str:
    """获取指标的完整中文描述"""
    metric = endpoint.get('metric', '')
    summary = endpoint.get('summary', '')
    description = endpoint.get('description', '')
    
    # 获取详细描述库
    descriptions = get_comprehensive_metric_descriptions()
    
    # 尝试精确匹配
    if metric in descriptions:
        return descriptions[metric]['desc']
    
    # 尝试部分匹配
    for key, value in descriptions.items():
        if key in metric:
            return value['desc']
    
    # 如果没有预定义的中文描述，根据英文描述生成
    if description and len(description) > 0:
        # 基于常见模式生成中文描述
        if 'active' in metric.lower():
            return f'统计网络中的活跃地址相关指标。{summary}。此指标帮助评估网络的使用率和用户参与度，是判断生态系统健康度的重要参考'
        elif 'balance' in metric.lower():
            return f'分析地址余额的分布情况。{summary}。通过追踪不同余额区间的地址分布，可以了解网络的财富集中度和用户结构'
        elif 'supply' in metric.lower():
            return f'追踪供应量在不同地址组的分布。{summary}。此指标有助于分析市场结构和识别重要的市场参与者群体'
        elif 'profit' in metric.lower() or 'loss' in metric.lower():
            return f'分析地址的盈亏状态。{summary}。通过追踪盈亏地址的数量和分布，可以评估市场情绪和潜在的买卖压力'
        elif 'new' in metric.lower():
            return f'统计新增地址的情况。{summary}。新地址的增长速度是网络扩张和新用户采用的重要指标'
        elif 'holder' in metric.lower():
            return f'分析持有者的行为和特征。{summary}。深入了解不同类型持有者的动态，有助于预测市场趋势'
        else:
            return f'{summary}。此指标提供了链上数据的重要洞察，帮助投资者和分析师更好地理解市场动态和网络状况'
    
    # 默认描述
    return f'提供{summary if summary else metric}相关的链上数据分析。通过追踪和分析这个指标，可以获得对网络活动、用户行为和市场趋势的深入理解'

def get_metric_full_info(endpoint: Dict) -> Dict[str, str]:
    """获取指标的完整信息"""
    metric = endpoint.get('metric', '')
    summary = endpoint.get('summary', '')
    
    # 获取详细描述库
    descriptions = get_comprehensive_metric_descriptions()
    
    # 尝试精确匹配
    if metric in descriptions:
        return {
            'name': descriptions[metric]['name'],
            'desc': descriptions[metric]['desc']
        }
    
    # 尝试部分匹配
    for key, value in descriptions.items():
        if key in metric:
            return {
                'name': value['name'],
                'desc': value['desc']
            }
    
    # 返回基于summary的信息
    return {
        'name': summary[:30] if summary else metric,
        'desc': get_metric_chinese_description(endpoint)
    }

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
            # 使用第一个下划线前的部分作为子类别
            if '_' in metric:
                prefix = metric.split('_')[0]
                subcategories[prefix].append(endpoint)
            else:
                subcategories['other'].append(endpoint)
    
    return dict(subcategories)

def generate_complete_mermaid_diagram(category: str, endpoints: List[Dict], subcategories: Dict[str, List[Dict]]) -> str:
    """生成完整的Mermaid图表，按子类别组织"""
    category_info = get_category_info()
    subcat_info = get_subcategory_info()
    
    cat_zh = category_info[category]['name_zh']
    
    # 按数量排序子类别
    sorted_subcats = sorted(subcategories.items(), key=lambda x: len(x[1]), reverse=True)[:6]
    
    mermaid = f"""```mermaid
graph TD
    A["{cat_zh}<br/>共{len(endpoints)}个指标"]
    A:::mainNode
    """
    
    for i, (subcat, subcat_endpoints) in enumerate(sorted_subcats, 1):
        subcat_zh = subcat_info.get(subcat, subcat.upper())
        
        # 添加子类别节点
        mermaid += f"""
    A --> B{i}["{subcat_zh}<br/>{len(subcat_endpoints)}个指标"]
    B{i}:::categoryNode"""
        
        # 为每个子类别添加前3个指标的详细信息
        for j, endpoint in enumerate(subcat_endpoints[:3], 1):
            metric_info = get_metric_full_info(endpoint)
            metric = endpoint.get('metric', '')
            
            # 截取描述的前80个字符用于图表显示
            desc_display = metric_info['desc'][:80] if len(metric_info['desc']) > 80 else metric_info['desc']
            
            mermaid += f"""
    B{i} --> C{i}_{j}["{metric_info['name']}<br/><i>{metric}</i>"]
    C{i}_{j}:::metricNode
    C{i}_{j} --> D{i}_{j}["{desc_display}"]
    D{i}_{j}:::descNode"""
    
    # 样式定义
    mermaid += """
    
    %% 高对比度样式
    classDef mainNode fill:#1e3a8a,stroke:#ffffff,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef categoryNode fill:#0891b2,stroke:#ffffff,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef metricNode fill:#059669,stroke:#ffffff,stroke-width:2px,color:#ffffff
    classDef descNode fill:#fbbf24,stroke:#92400e,stroke-width:1px,color:#000000,font-size:10px
```"""
    
    return mermaid

def generate_subcategory_detailed_section(subcat: str, endpoints: List[Dict]) -> str:
    """生成子类别的详细文档部分"""
    subcat_info = get_subcategory_info()
    subcat_zh = subcat_info.get(subcat, subcat.upper())
    
    section = f"""### 📊 {subcat_zh}（{len(endpoints)}个指标）

本子类别包含以下详细指标：

"""
    
    for i, endpoint in enumerate(endpoints, 1):
        metric = endpoint.get('metric', '')
        metric_info = get_metric_full_info(endpoint)
        
        section += f"""#### {i}. {metric_info['name']}

- **指标代码**: `{metric}`
- **API路径**: `{endpoint.get('path', '')}`
- **英文名称**: {endpoint.get('summary', '')}

**📝 详细说明**：
{metric_info['desc']}

**使用示例**：
```python
# 获取{metric_info['name']}数据
df = client.get_metric(
    "{endpoint.get('path', '')}",
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

## 📋 概述

{cat_desc}

本类别共包含 **{len(endpoints)}** 个API端点，分为 **{len(subcategories)}** 个子类别。

## 🗂️ 指标分类

"""
    
    # 生成分类统计表
    doc += """| 子类别 | 指标数量 | 主要功能 |
|--------|----------|----------|
"""
    
    subcat_info = get_subcategory_info()
    sorted_subcats = sorted(subcategories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for subcat, subcat_endpoints in sorted_subcats:
        subcat_zh = subcat_info.get(subcat, subcat.upper())
        doc += f"| {subcat_zh} | {len(subcat_endpoints)} | "
        
        # 添加子类别的主要功能描述
        if subcat == 'active':
            doc += "追踪网络活跃度和用户参与度"
        elif subcat == 'min':
            doc += "按余额门槛统计地址分布"
        elif subcat == 'profit':
            doc += "分析盈利地址的规模和特征"
        elif subcat == 'loss':
            doc += "分析亏损地址的规模和特征"
        elif subcat == 'supply':
            doc += "供应量在不同地址组的分布"
        elif subcat == 'balance':
            doc += "地址余额的详细统计分析"
        elif subcat == 'holder':
            doc += "持有者行为和特征分析"
        elif subcat == 'accumulation':
            doc += "累积地址的历史统计"
        elif subcat == 'new':
            doc += "新增地址的增长趋势"
        elif subcat == 'sending':
            doc += "发送交易活动统计"
        elif subcat == 'receiving':
            doc += "接收交易活动统计"
        elif subcat == 'count':
            doc += "各类地址数量统计"
        elif subcat == 'non':
            doc += "非零余额地址分析"
        elif subcat == 'zero':
            doc += "零余额地址分析"
        else:
            doc += "提供专门的数据分析"
        
        doc += " |\n"
    
    # 添加完整的指标体系图
    doc += f"""
## 🎨 指标体系结构图

{generate_complete_mermaid_diagram(category, endpoints, subcategories)}

## 📂 详细指标说明

"""
    
    # 按子类别生成详细文档
    for subcat, subcat_endpoints in sorted_subcats:
        doc += generate_subcategory_detailed_section(subcat, subcat_endpoints)
    
    # 添加完整的指标列表
    doc += """## 📊 完整指标列表

| # | 指标名称 | 指标代码 | API路径 | 说明 |
|---|----------|----------|---------|------|
"""
    
    for i, endpoint in enumerate(endpoints, 1):
        metric = endpoint.get('metric', '')
        metric_info = get_metric_full_info(endpoint)
        path = endpoint.get('path', '')
        
        # 在表格中显示前100个字符
        desc_display = metric_info['desc'][:100] + '...' if len(metric_info['desc']) > 100 else metric_info['desc']
        
        doc += f"| {i} | {metric_info['name']} | `{metric}` | `{path}` | {desc_display} |\n"
    
    # 添加使用示例
    doc += """
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
"""
    
    return doc

def generate_readme(categories: Dict[str, List[Dict]]) -> str:
    """生成README文件"""
    category_info = get_category_info()
    total_endpoints = sum(len(endpoints) for endpoints in categories.values())
    
    readme = f"""# Glassnode API 中文文档（完整版）

## 📚 文档概览

本文档集包含Glassnode API所有 **{total_endpoints}** 个端点的完整中文说明，分为 **{len(categories)}** 个类别。

## 📁 文档目录

| 类别 | 中文名称 | 端点数量 | 文档链接 |
|------|----------|----------|----------|
"""
    
    for category in sorted(categories.keys()):
        cat_info = category_info.get(category, {})
        cat_zh = cat_info.get('name_zh', category)
        endpoint_count = len(categories[category])
        readme += f"| {category} | {cat_zh} | {endpoint_count} | [查看文档](./{category}.md) |\n"
    
    readme += """

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
"""
    
    return readme

def main():
    """主函数"""
    # 配置
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
        doc = generate_category_document(category, endpoints)
        with open(f"{output_dir}/{category}.md", 'w', encoding='utf-8') as f:
            f.write(doc)
    
    print(f"\n✅ 文档生成完成！")
    print(f"📁 输出目录: {output_dir}/")
    print(f"📄 生成文件: README.md + {len(categories)}个类别文档")
    print(f"🎯 文档特性:")
    print(f"   ✓ 完整的指标分类结构")
    print(f"   ✓ 所有说明均为中文")
    print(f"   ✓ 详细的指标功能描述")
    print(f"   ✓ 高对比度Mermaid图表")
    print(f"   ✓ 按子类别组织的文档结构")

if __name__ == "__main__":
    main()