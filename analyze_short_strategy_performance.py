import json
import pandas as pd
import numpy as np

# 读取JSON文件
with open('indicator_analysis_results_BTC_20250919_131040.json', 'r') as f:
    data = json.load(f)

# 提取indicators部分
indicators = data.get('indicators', {})

# 创建列表存储符合条件的做空指标
short_qualified = []
all_short_data = []

print("=" * 80)
print("做空策略分析 - 不同市场状态下的表现")
print("=" * 80)

for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    
    # 遍历所有百分位
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict) or 'strategies' not in percentile_data:
            continue
        
        strategies = percentile_data['strategies']
        if 'short' not in strategies:
            continue
        
        short_strategy = strategies['short']
        if 'regime_performance' not in short_strategy:
            continue
        
        regime_perf = short_strategy['regime_performance']
        
        # 收集所有做空数据
        regime_returns = {}
        regime_excess_returns = {}
        regime_sharpe = {}
        
        for regime in ['bull', 'bear', 'sideways']:
            if regime in regime_perf:
                regime_info = regime_perf[regime]
                regime_returns[regime] = regime_info.get('strategy_return', 0)
                regime_excess_returns[regime] = regime_info.get('excess_return', 0)
                regime_sharpe[regime] = regime_info.get('sharpe', 0)
        
        if len(regime_returns) == 3:  # 确保有所有三个市场状态的数据
            all_short_data.append({
                'indicator': indicator_name,
                'percentile': int(percentile),
                'threshold': percentile_data.get('threshold', 0),
                'bull_return': regime_returns.get('bull', 0),
                'bull_excess': regime_excess_returns.get('bull', 0),
                'bull_sharpe': regime_sharpe.get('bull', 0),
                'bear_return': regime_returns.get('bear', 0),
                'bear_excess': regime_excess_returns.get('bear', 0),
                'bear_sharpe': regime_sharpe.get('bear', 0),
                'sideways_return': regime_returns.get('sideways', 0),
                'sideways_excess': regime_excess_returns.get('sideways', 0),
                'sideways_sharpe': regime_sharpe.get('sideways', 0),
                'avg_return': np.mean(list(regime_returns.values())),
                'avg_excess': np.mean(list(regime_excess_returns.values()))
            })
        
        # 检查是否在所有市场状态下都有正超额收益（做空）
        all_positive_excess = True
        all_positive_return = True
        
        for regime in ['bull', 'bear', 'sideways']:
            if regime in regime_excess_returns:
                if regime_excess_returns[regime] <= 0:
                    all_positive_excess = False
                if regime_returns[regime] <= 0:
                    all_positive_return = False
        
        if all_positive_excess and all_positive_return and len(regime_returns) == 3:
            optimal_data = indicator_data.get('optimal', {})
            short_qualified.append({
                'indicator': indicator_name,
                'percentile': int(percentile),
                'threshold': percentile_data.get('threshold', 0),
                'bull_return': regime_returns['bull'],
                'bull_excess': regime_excess_returns['bull'],
                'bear_return': regime_returns['bear'],
                'bear_excess': regime_excess_returns['bear'],
                'sideways_return': regime_returns['sideways'],
                'sideways_excess': regime_excess_returns['sideways'],
                'avg_return': np.mean(list(regime_returns.values())),
                'avg_excess': np.mean(list(regime_excess_returns.values())),
                'min_excess': min(regime_excess_returns.values()),
                'max_rank_ic': optimal_data.get('max_rank_ic', 0)
            })

# 分析1: 全天候做空策略（所有市场状态下都有正超额收益）
print("\n" + "=" * 80)
print("全天候做空策略 - 在牛市、熊市、震荡市都有正超额收益")
print("=" * 80)

if short_qualified:
    df_qualified = pd.DataFrame(short_qualified)
    df_qualified_sorted = df_qualified.sort_values('avg_excess', ascending=False)
    
    print(f"\n找到 {len(df_qualified)} 个全天候做空策略\n")
    
    for i, (idx, row) in enumerate(df_qualified_sorted.head(20).iterrows(), 1):
        print(f"排名 {i}: {row['indicator']} (百分位={row['percentile']})")
        print(f"  牛市: 收益率={row['bull_return']:.2%}, 超额={row['bull_excess']:.2%}")
        print(f"  熊市: 收益率={row['bear_return']:.2%}, 超额={row['bear_excess']:.2%}")
        print(f"  震荡: 收益率={row['sideways_return']:.2%}, 超额={row['sideways_excess']:.2%}")
        print(f"  平均超额收益: {row['avg_excess']:.2%}")
        print(f"  最小超额收益: {row['min_excess']:.2%}")
        print("-" * 40)
    
    df_qualified_sorted.to_csv('all_weather_short_strategies.csv', index=False)
    print(f"\n结果已保存到: all_weather_short_strategies.csv")
else:
    print("\n未找到在所有市场状态下都有正超额收益的做空策略")

# 分析2: 熊市最佳做空策略
print("\n" + "=" * 80)
print("熊市最佳做空策略（超额收益 > 0）")
print("=" * 80)

if all_short_data:
    df_all = pd.DataFrame(all_short_data)
    
    # 筛选熊市有正超额收益的
    df_bear = df_all[df_all['bear_excess'] > 0].copy()
    df_bear_sorted = df_bear.sort_values('bear_excess', ascending=False)
    
    print(f"\n找到 {len(df_bear)} 个熊市有正超额收益的做空策略\n")
    
    for i, (idx, row) in enumerate(df_bear_sorted.head(20).iterrows(), 1):
        print(f"{i}. {row['indicator']} (百分位={row['percentile']})")
        print(f"   熊市收益率: {row['bear_return']:.2%}")
        print(f"   熊市超额收益: {row['bear_excess']:.2%}")
        print(f"   熊市夏普比率: {row['bear_sharpe']:.2f}")
        print("-" * 40)

# 分析3: 牛市最佳做空策略（逆向指标）
print("\n" + "=" * 80)
print("牛市最佳做空策略（超额收益 > 0）- 逆向指标")
print("=" * 80)

if all_short_data:
    # 筛选牛市有正超额收益的做空策略
    df_bull = df_all[df_all['bull_excess'] > 0].copy()
    df_bull_sorted = df_bull.sort_values('bull_excess', ascending=False)
    
    print(f"\n找到 {len(df_bull)} 个牛市有正超额收益的做空策略（逆向指标）\n")
    
    for i, (idx, row) in enumerate(df_bull_sorted.head(20).iterrows(), 1):
        print(f"{i}. {row['indicator']} (百分位={row['percentile']})")
        print(f"   牛市收益率: {row['bull_return']:.2%}")
        print(f"   牛市超额收益: {row['bull_excess']:.2%}")
        print(f"   牛市夏普比率: {row['bull_sharpe']:.2f}")
        print("-" * 40)

# 分析4: 震荡市最佳做空策略
print("\n" + "=" * 80)
print("震荡市最佳做空策略（超额收益 > 0）")
print("=" * 80)

if all_short_data:
    # 筛选震荡市有正超额收益的做空策略
    df_sideways = df_all[df_all['sideways_excess'] > 0].copy()
    df_sideways_sorted = df_sideways.sort_values('sideways_excess', ascending=False)
    
    print(f"\n找到 {len(df_sideways)} 个震荡市有正超额收益的做空策略\n")
    
    for i, (idx, row) in enumerate(df_sideways_sorted.head(10).iterrows(), 1):
        print(f"{i}. {row['indicator']} (百分位={row['percentile']})")
        print(f"   震荡市收益率: {row['sideways_return']:.2%}")
        print(f"   震荡市超额收益: {row['sideways_excess']:.2%}")
        print("-" * 40)

# 分析5: 综合表现最佳的做空策略
print("\n" + "=" * 80)
print("综合表现最佳的做空策略（按平均超额收益排序）")
print("=" * 80)

if all_short_data:
    df_all_sorted = df_all.sort_values('avg_excess', ascending=False)
    
    print(f"\n所有做空策略中表现最佳的前20个\n")
    
    for i, (idx, row) in enumerate(df_all_sorted.head(20).iterrows(), 1):
        print(f"{i}. {row['indicator']} (百分位={row['percentile']})")
        print(f"   平均超额收益: {row['avg_excess']:.2%}")
        print(f"   牛市超额: {row['bull_excess']:.2%}")
        print(f"   熊市超额: {row['bear_excess']:.2%}")
        print(f"   震荡超额: {row['sideways_excess']:.2%}")
        print("-" * 40)
    
    # 保存综合数据
    df_all_sorted.to_csv('short_strategies_comprehensive.csv', index=False)
    print(f"\n综合分析结果已保存到: short_strategies_comprehensive.csv")

# 统计摘要
print("\n" + "=" * 80)
print("做空策略统计摘要")
print("=" * 80)

if all_short_data:
    print(f"总做空策略数: {len(df_all)}")
    print(f"全天候正超额策略数: {len(short_qualified) if short_qualified else 0}")
    print(f"熊市正超额策略数: {len(df_bear)}")
    print(f"牛市正超额策略数: {len(df_bull)}")
    print(f"震荡市正超额策略数: {len(df_sideways)}")
    print(f"\n平均超额收益范围: {df_all['avg_excess'].min():.2%} 到 {df_all['avg_excess'].max():.2%}")
    print(f"熊市最佳超额收益: {df_bear['bear_excess'].max():.2%}" if len(df_bear) > 0 else "无")
    print(f"牛市最佳超额收益: {df_bull['bull_excess'].max():.2%}" if len(df_bull) > 0 else "无")