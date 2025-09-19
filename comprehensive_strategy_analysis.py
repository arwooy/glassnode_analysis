import json
import pandas as pd
import numpy as np
from datetime import datetime

# 读取JSON文件
print("正在加载数据...")
with open('indicator_analysis_results_BTC_20250919_131040.json', 'r') as f:
    data = json.load(f)

# =============================================================================
# 1. 分析基准市场表现
# =============================================================================
print("\n" + "=" * 80)
print("基准市场表现分析")
print("=" * 80)

# 获取市场数据
market_data = data.get('market', {})
benchmark_metrics = market_data.get('benchmark_metrics', {})
full_regime_benchmarks = market_data.get('full_regime_benchmarks', {})

# 基准收益统计 - 做多基准
if 'long' in benchmark_metrics:
    long_benchmark = benchmark_metrics['long']
    print("\n【整体市场表现 - 买入持有策略】")
    print(f"总收益率: {long_benchmark.get('total_return', 0):.2f}%")
    print(f"年化收益率: {long_benchmark.get('annualized_return', 0):.2f}%")
    print(f"夏普比率: {long_benchmark.get('sharpe_ratio', 0):.3f}")
    print(f"最大回撤: {long_benchmark.get('max_drawdown', 0):.2f}%")
    print(f"波动率: {long_benchmark.get('annual_volatility', 0):.2f}%")

# 做空基准
if 'short' in benchmark_metrics:
    short_benchmark = benchmark_metrics['short']
    print("\n【整体市场表现 - 做空策略】")
    print(f"总收益率: {short_benchmark.get('total_return', 0):.2f}%")
    print(f"年化收益率: {short_benchmark.get('annualized_return', 0):.2f}%")

# 不同市场状态下的基准表现
print("\n【不同市场状态下的基准表现】")
if 'long' in full_regime_benchmarks:
    regime_data = full_regime_benchmarks['long']
    
    for regime in ['bull', 'bear', 'sideways']:
        if regime in regime_data:
            regime_info = regime_data[regime]
            print(f"\n{regime.upper()}市场 (买入持有):")
            print(f"  持续天数: {regime_info.get('days', 0):.0f}天")
            print(f"  基准收益率: {regime_info.get('benchmark_return', 0):.2f}%")
            print(f"  最大回撤: {regime_info.get('benchmark_max_drawdown', 0):.2f}%")
            print(f"  夏普比率: {regime_info.get('sharpe_ratio', 0):.3f}")

# =============================================================================
# 2. 收集所有策略数据
# =============================================================================
print("\n正在收集策略数据...")

indicators = data.get('indicators', {})
all_strategies = []

for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    optimal_data = indicator_data.get('optimal', {})
    
    # 遍历所有百分位
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict) or 'strategies' not in percentile_data:
            continue
        
        strategies = percentile_data['strategies']
        threshold = percentile_data.get('threshold', 0)
        
        # 处理做多策略
        if 'long' in strategies:
            long_strategy = strategies['long']
            if 'regime_performance' in long_strategy:
                regime_perf = long_strategy['regime_performance']
                
                # 收集各市场状态表现
                strategy_info = {
                    'indicator': indicator_name,
                    'strategy_type': 'long',
                    'percentile': int(percentile),
                    'threshold': threshold,
                    'optimal_horizon': long_strategy.get('optimal_horizon', 0),
                    'max_rank_ic': optimal_data.get('max_rank_ic', 0),
                    'max_pearson_ic': optimal_data.get('max_pearson_ic', 0),
                    'max_ig': optimal_data.get('max_ig', 0)
                }
                
                # 添加各市场状态数据
                for regime in ['bull', 'bear', 'sideways']:
                    if regime in regime_perf:
                        regime_info = regime_perf[regime]
                        strategy_info[f'{regime}_return'] = regime_info.get('strategy_return', 0)
                        strategy_info[f'{regime}_excess'] = regime_info.get('excess_return', 0)
                        strategy_info[f'{regime}_sharpe'] = regime_info.get('sharpe', 0)
                        strategy_info[f'{regime}_win_rate'] = regime_info.get('excess_return_win_rate', 0)
                
                # 计算综合指标
                if all(f'{r}_return' in strategy_info for r in ['bull', 'bear', 'sideways']):
                    strategy_info['avg_return'] = np.mean([
                        strategy_info['bull_return'],
                        strategy_info['bear_return'],
                        strategy_info['sideways_return']
                    ])
                    strategy_info['avg_excess'] = np.mean([
                        strategy_info.get('bull_excess', 0),
                        strategy_info.get('bear_excess', 0),
                        strategy_info.get('sideways_excess', 0)
                    ])
                    strategy_info['min_excess'] = min([
                        strategy_info.get('bull_excess', 0),
                        strategy_info.get('bear_excess', 0),
                        strategy_info.get('sideways_excess', 0)
                    ])
                    
                    # 判断是否全天候策略
                    strategy_info['all_weather_positive'] = all([
                        strategy_info.get(f'{r}_excess', 0) > 0 
                        for r in ['bull', 'bear', 'sideways']
                    ])
                    
                    all_strategies.append(strategy_info)
        
        # 处理做空策略
        if 'short' in strategies:
            short_strategy = strategies['short']
            if 'regime_performance' in short_strategy:
                regime_perf = short_strategy['regime_performance']
                
                strategy_info = {
                    'indicator': indicator_name,
                    'strategy_type': 'short',
                    'percentile': int(percentile),
                    'threshold': threshold,
                    'optimal_horizon': short_strategy.get('optimal_horizon', 0),
                    'max_rank_ic': optimal_data.get('max_rank_ic', 0),
                    'max_pearson_ic': optimal_data.get('max_pearson_ic', 0),
                    'max_ig': optimal_data.get('max_ig', 0)
                }
                
                # 添加各市场状态数据
                for regime in ['bull', 'bear', 'sideways']:
                    if regime in regime_perf:
                        regime_info = regime_perf[regime]
                        strategy_info[f'{regime}_return'] = regime_info.get('strategy_return', 0)
                        strategy_info[f'{regime}_excess'] = regime_info.get('excess_return', 0)
                        strategy_info[f'{regime}_sharpe'] = regime_info.get('sharpe', 0)
                        strategy_info[f'{regime}_win_rate'] = regime_info.get('excess_return_win_rate', 0)
                
                # 计算综合指标
                if all(f'{r}_return' in strategy_info for r in ['bull', 'bear', 'sideways']):
                    strategy_info['avg_return'] = np.mean([
                        strategy_info['bull_return'],
                        strategy_info['bear_return'],
                        strategy_info['sideways_return']
                    ])
                    strategy_info['avg_excess'] = np.mean([
                        strategy_info.get('bull_excess', 0),
                        strategy_info.get('bear_excess', 0),
                        strategy_info.get('sideways_excess', 0)
                    ])
                    strategy_info['min_excess'] = min([
                        strategy_info.get('bull_excess', 0),
                        strategy_info.get('bear_excess', 0),
                        strategy_info.get('sideways_excess', 0)
                    ])
                    
                    # 判断是否全天候策略
                    strategy_info['all_weather_positive'] = all([
                        strategy_info.get(f'{r}_excess', 0) > 0 
                        for r in ['bull', 'bear', 'sideways']
                    ])
                    
                    all_strategies.append(strategy_info)

# 转换为DataFrame
df_strategies = pd.DataFrame(all_strategies)

# =============================================================================
# 3. Top做多策略分析
# =============================================================================
print("\n" + "=" * 80)
print("TOP 做多策略详细分析")
print("=" * 80)

# 筛选做多策略
df_long = df_strategies[df_strategies['strategy_type'] == 'long'].copy()

# 按平均超额收益排序
df_long_sorted = df_long.sort_values('avg_excess', ascending=False)

print(f"\n总共找到 {len(df_long)} 个做多策略")
print(f"其中全天候正超额策略: {df_long['all_weather_positive'].sum()} 个")

print("\n【TOP 20 做多策略 - 按平均超额收益排序】")
for i, row in df_long_sorted.head(20).iterrows():
    print(f"\n{list(df_long_sorted.index).index(i)+1}. {row['indicator']}")
    print(f"   百分位: {row['percentile']}%, 阈值: {row['threshold']:.4f}")
    print(f"   最优预测周期: {row['optimal_horizon']}天")
    print(f"   Rank IC: {row['max_rank_ic']:.4f}, Pearson IC: {row['max_pearson_ic']:.4f}")
    print(f"   牛市: 收益={row['bull_return']:.2%}, 超额={row['bull_excess']:.2%}, 胜率={row.get('bull_win_rate', 0):.2%}")
    print(f"   熊市: 收益={row['bear_return']:.2%}, 超额={row['bear_excess']:.2%}, 胜率={row.get('bear_win_rate', 0):.2%}")
    print(f"   震荡: 收益={row['sideways_return']:.2%}, 超额={row['sideways_excess']:.2%}, 胜率={row.get('sideways_win_rate', 0):.2%}")
    print(f"   平均超额: {row['avg_excess']:.2%}, 全天候: {'✓' if row['all_weather_positive'] else '✗'}")

# =============================================================================
# 4. Top做空策略分析
# =============================================================================
print("\n" + "=" * 80)
print("TOP 做空策略详细分析")
print("=" * 80)

# 筛选做空策略
df_short = df_strategies[df_strategies['strategy_type'] == 'short'].copy()

# 按平均超额收益排序
df_short_sorted = df_short.sort_values('avg_excess', ascending=False)

print(f"\n总共找到 {len(df_short)} 个做空策略")
print(f"其中全天候正超额策略: {df_short['all_weather_positive'].sum()} 个")

print("\n【TOP 20 做空策略 - 按平均超额收益排序】")
for i, row in df_short_sorted.head(20).iterrows():
    print(f"\n{list(df_short_sorted.index).index(i)+1}. {row['indicator']}")
    print(f"   百分位: {row['percentile']}%, 阈值: {row['threshold']:.4f}")
    print(f"   最优预测周期: {row['optimal_horizon']}天")
    print(f"   Rank IC: {row['max_rank_ic']:.4f}, Pearson IC: {row['max_pearson_ic']:.4f}")
    print(f"   牛市: 收益={row['bull_return']:.2%}, 超额={row['bull_excess']:.2%}, 胜率={row.get('bull_win_rate', 0):.2%}")
    print(f"   熊市: 收益={row['bear_return']:.2%}, 超额={row['bear_excess']:.2%}, 胜率={row.get('bear_win_rate', 0):.2%}")
    print(f"   震荡: 收益={row['sideways_return']:.2%}, 超额={row['sideways_excess']:.2%}, 胜率={row.get('sideways_win_rate', 0):.2%}")
    print(f"   平均超额: {row['avg_excess']:.2%}, 全天候: {'✓' if row['all_weather_positive'] else '✗'}")

# =============================================================================
# 5. 寻找100%准确度的策略
# =============================================================================
print("\n" + "=" * 80)
print("100% 准确度策略分析")
print("=" * 80)

# 定义100%准确度的标准：某个市场状态下胜率=100%
perfect_strategies = []

for _, row in df_strategies.iterrows():
    perfect_markets = []
    
    # 检查各市场状态的胜率
    for regime in ['bull', 'bear', 'sideways']:
        win_rate_key = f'{regime}_win_rate'
        if win_rate_key in row and row[win_rate_key] >= 0.99:  # 99%以上视为100%
            perfect_markets.append({
                'regime': regime,
                'win_rate': row[win_rate_key],
                'return': row[f'{regime}_return'],
                'excess': row[f'{regime}_excess']
            })
    
    if perfect_markets:
        perfect_strategies.append({
            'indicator': row['indicator'],
            'strategy_type': row['strategy_type'],
            'percentile': row['percentile'],
            'threshold': row['threshold'],
            'optimal_horizon': row['optimal_horizon'],
            'perfect_markets': perfect_markets,
            'avg_excess': row['avg_excess']
        })

# 按平均超额收益排序
perfect_strategies = sorted(perfect_strategies, key=lambda x: x['avg_excess'], reverse=True)

print(f"\n找到 {len(perfect_strategies)} 个在特定市场状态下达到100%准确度的策略")

if perfect_strategies:
    print("\n【100%准确度策略详情】")
    for i, strategy in enumerate(perfect_strategies[:20], 1):
        print(f"\n{i}. {strategy['indicator']} ({strategy['strategy_type']})")
        print(f"   百分位: {strategy['percentile']}%, 阈值: {strategy['threshold']:.4f}")
        print(f"   最优周期: {strategy['optimal_horizon']}天")
        print(f"   100%准确的市场状态:")
        for market in strategy['perfect_markets']:
            print(f"     - {market['regime'].upper()}市: 胜率={market['win_rate']:.1%}, "
                  f"收益={market['return']:.2%}, 超额={market['excess']:.2%}")

# =============================================================================
# 6. 综合统计分析
# =============================================================================
print("\n" + "=" * 80)
print("综合统计分析")
print("=" * 80)

print("\n【做多策略统计】")
print(f"总策略数: {len(df_long)}")
print(f"正收益策略数: {(df_long['avg_return'] > 0).sum()}")
print(f"正超额策略数: {(df_long['avg_excess'] > 0).sum()}")
print(f"全天候策略数: {df_long['all_weather_positive'].sum()}")
print(f"平均超额收益: {df_long['avg_excess'].mean():.2%}")
print(f"最佳超额收益: {df_long['avg_excess'].max():.2%}")
print(f"熊市最佳超额: {df_long['bear_excess'].max():.2%}")

print("\n【做空策略统计】")
print(f"总策略数: {len(df_short)}")
print(f"正收益策略数: {(df_short['avg_return'] > 0).sum()}")
print(f"正超额策略数: {(df_short['avg_excess'] > 0).sum()}")
print(f"全天候策略数: {df_short['all_weather_positive'].sum()}")
print(f"平均超额收益: {df_short['avg_excess'].mean():.2%}")
print(f"最佳超额收益: {df_short['avg_excess'].max():.2%}")
print(f"牛市最佳超额: {df_short['bull_excess'].max():.2%}")

# =============================================================================
# 7. 最稳健策略分析（最小超额收益最高）
# =============================================================================
print("\n" + "=" * 80)
print("最稳健策略分析（最小超额收益最高）")
print("=" * 80)

# 做多最稳健
df_long_stable = df_long.sort_values('min_excess', ascending=False)
print("\n【最稳健做多策略 TOP 10】")
for i, row in df_long_stable.head(10).iterrows():
    print(f"{list(df_long_stable.index).index(i)+1}. {row['indicator']} (百分位={row['percentile']})")
    print(f"   最小超额: {row['min_excess']:.2%}, 平均超额: {row['avg_excess']:.2%}")

# 做空最稳健
df_short_stable = df_short.sort_values('min_excess', ascending=False)
print("\n【最稳健做空策略 TOP 10】")
for i, row in df_short_stable.head(10).iterrows():
    print(f"{list(df_short_stable.index).index(i)+1}. {row['indicator']} (百分位={row['percentile']})")
    print(f"   最小超额: {row['min_excess']:.2%}, 平均超额: {row['avg_excess']:.2%}")

# 保存结果
df_long_sorted.to_csv('comprehensive_long_strategies.csv', index=False)
df_short_sorted.to_csv('comprehensive_short_strategies.csv', index=False)

if perfect_strategies:
    pd.DataFrame(perfect_strategies).to_csv('perfect_accuracy_strategies.csv', index=False)

print("\n分析结果已保存到:")
print("  - comprehensive_long_strategies.csv")
print("  - comprehensive_short_strategies.csv")
print("  - perfect_accuracy_strategies.csv")