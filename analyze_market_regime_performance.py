import json
import pandas as pd
import numpy as np

# 读取JSON文件
with open('indicator_analysis_results_BTC_20250919_131040.json', 'r') as f:
    data = json.load(f)

# 提取indicators部分
indicators = data.get('indicators', {})

# 创建列表存储符合条件的指标
qualified_indicators = []
all_regime_data = []

for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    
    # 遍历所有百分位
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict) or 'strategies' not in percentile_data:
            continue
        
        strategies = percentile_data['strategies']
        if 'long' not in strategies:
            continue
        
        long_strategy = strategies['long']
        if 'regime_performance' not in long_strategy:
            continue
        
        regime_perf = long_strategy['regime_performance']
        
        # 初始化标记
        all_positive_excess = True
        all_positive_return = True
        regime_returns = {}
        regime_excess_returns = {}
        regime_sharpe = {}
        
        # 检查每个市场状态
        for regime in ['bull', 'bear', 'sideways']:
            if regime not in regime_perf:
                all_positive_excess = False
                all_positive_return = False
                break
            
            regime_info = regime_perf[regime]
            
            # 获取策略收益和超额收益
            strategy_return = regime_info.get('strategy_return', 0)
            excess_return = regime_info.get('excess_return', 0)
            sharpe = regime_info.get('sharpe', 0)
            
            regime_returns[regime] = strategy_return
            regime_excess_returns[regime] = excess_return
            regime_sharpe[regime] = sharpe
            
            # 检查是否为正
            if excess_return <= 0:
                all_positive_excess = False
            if strategy_return <= 0:
                all_positive_return = False
        
        # 如果所有市场状态下都有正超额收益和正收益
        if all_positive_excess and all_positive_return:
            # 获取最优参数
            optimal_data = indicator_data.get('optimal', {})
            
            qualified_indicators.append({
                'indicator': indicator_name,
                'percentile': int(percentile),
                'threshold': percentile_data.get('threshold', 0),
                'bull_return': regime_returns['bull'],
                'bull_excess': regime_excess_returns['bull'],
                'bull_sharpe': regime_sharpe['bull'],
                'bear_return': regime_returns['bear'],
                'bear_excess': regime_excess_returns['bear'],
                'bear_sharpe': regime_sharpe['bear'],
                'sideways_return': regime_returns['sideways'],
                'sideways_excess': regime_excess_returns['sideways'],
                'sideways_sharpe': regime_sharpe['sideways'],
                'avg_return': np.mean(list(regime_returns.values())),
                'avg_excess': np.mean(list(regime_excess_returns.values())),
                'avg_sharpe': np.mean(list(regime_sharpe.values())),
                'min_return': min(regime_returns.values()),
                'min_excess': min(regime_excess_returns.values()),
                'max_rank_ic': optimal_data.get('max_rank_ic', 0),
                'max_pearson_ic': optimal_data.get('max_pearson_ic', 0),
                'max_ig': optimal_data.get('max_ig', 0)
            })

# 转换为DataFrame
df = pd.DataFrame(qualified_indicators)

if len(df) == 0:
    print("\n未找到在所有市场状态下都有正超额收益的指标")
else:
    # 按平均超额收益排序
    df_sorted = df.sort_values('avg_excess', ascending=False)
    
    print("\n" + "=" * 80)
    print("在牛市、熊市、震荡市都能产生正超额收益的指标")
    print("=" * 80)
    print(f"\n找到 {len(df)} 个符合条件的指标\n")
    
    for i, (idx, row) in enumerate(df_sorted.head(20).iterrows(), 1):
        print(f"排名 {i}: {row['indicator']}")
        print(f"  牛市: 收益率={row['bull_return']:.2%}, 超额收益={row['bull_excess']:.2%}")
        print(f"  熊市: 收益率={row['bear_return']:.2%}, 超额收益={row['bear_excess']:.2%}")
        print(f"  震荡: 收益率={row['sideways_return']:.2%}, 超额收益={row['sideways_excess']:.2%}")
        print(f"  平均超额收益: {row['avg_excess']:.2%}")
        print(f"  最小超额收益: {row['min_excess']:.2%}")
        print(f"  Rank IC: {row['max_rank_ic']:.4f}, Pearson IC: {row['max_pearson_ic']:.4f}")
        print("-" * 40)
    
    # 保存结果
    df_sorted.to_csv('all_weather_positive_indicators.csv', index=False)
    print(f"\n完整结果已保存到: all_weather_positive_indicators.csv")
    
    # 统计摘要
    print("\n" + "=" * 80)
    print("统计摘要")
    print("=" * 80)
    print(f"符合条件的指标总数: {len(df)}")
    print(f"平均超额收益范围: {df['avg_excess'].min():.2%} - {df['avg_excess'].max():.2%}")
    print(f"最稳定指标（最小超额收益最高）: {df.nlargest(1, 'min_excess')['indicator'].values[0]}")
    print(f"  其最小超额收益: {df['min_excess'].max():.2%}")

# 额外分析：找出在熊市表现特别好的指标
print("\n" + "=" * 80)
print("熊市表现最佳的指标（有正超额收益）")
print("=" * 80)

bear_performers = []
for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    
    # 遍历所有百分位，找最佳熊市表现
    best_bear_excess = -999
    best_bear_return = -999
    best_percentile = 0
    best_threshold = 0
    
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict) or 'strategies' not in percentile_data:
            continue
        
        strategies = percentile_data['strategies']
        if 'long' not in strategies:
            continue
        
        long_strategy = strategies['long']
        if 'regime_performance' not in long_strategy:
            continue
        
        regime_perf = long_strategy['regime_performance']
        if 'bear' not in regime_perf:
            continue
        
        bear_info = regime_perf['bear']
        excess_return = bear_info.get('excess_return', -999)
        strategy_return = bear_info.get('strategy_return', -999)
        
        if excess_return > best_bear_excess:
            best_bear_excess = excess_return
            best_bear_return = strategy_return
            best_percentile = int(percentile)
            best_threshold = percentile_data.get('threshold', 0)
    
    if best_bear_excess > 0 and best_bear_return > 0:
        bear_performers.append({
            'indicator': indicator_name,
            'bear_return': best_bear_return,
            'bear_excess': best_bear_excess,
            'percentile': best_percentile,
            'threshold': best_threshold
        })

if bear_performers:
    bear_df = pd.DataFrame(bear_performers)
    bear_df_sorted = bear_df.sort_values('bear_excess', ascending=False)
    
    print(f"\n找到 {len(bear_df)} 个在熊市有正超额收益的指标\n")
    
    for i, (idx, row) in enumerate(bear_df_sorted.head(20).iterrows(), 1):
        print(f"{i}. {row['indicator']} (百分位={row['percentile']})")
        print(f"   熊市收益率: {row['bear_return']:.2%}")
        print(f"   熊市超额收益: {row['bear_excess']:.2%}")
        print(f"   阈值: {row['threshold']:.4f}")
        print("-" * 40)