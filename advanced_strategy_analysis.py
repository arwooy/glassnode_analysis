import json
import pandas as pd
import numpy as np
import os

# 读取JSON文件
print("正在加载数据...")
# with open('indicator_analysis_results_BTC_20250919_152957.json', 'r') as f:
#     data = json.load(f)

with open('indicator_analysis_results_ETH_20250919_155001.json', 'r') as f:
    data = json.load(f)
    
# 获取指标数量信息
metadata = data.get('metadata', {})
indicators = data.get('indicators', {})
indicators_list = metadata.get('indicators_list', [])

# 统计总指标数和测试的指标数
total_indicators = len(indicators_list) if indicators_list else 0
tested_indicators = len(indicators)

# 读取Glassnode平台的所有端点信息
platform_total_endpoints = 0
platform_category_breakdown = {}
if os.path.exists('glassnode_endpoints_detailed.json'):
    with open('glassnode_endpoints_detailed.json', 'r') as f:
        endpoints_data = json.load(f)
        for category, endpoints in endpoints_data.items():
            if isinstance(endpoints, list):
                count = len(endpoints)
                platform_category_breakdown[category] = count
                platform_total_endpoints += count

print(f"\n【指标统计】")
print(f"  Glassnode平台总指标数: {platform_total_endpoints}")
if platform_category_breakdown:
    # 显示主要类别
    main_categories = ['addresses', 'indicators', 'derivatives', 'transactions', 'supply']
    print(f"  主要类别分布:")
    for cat in main_categories:
        if cat in platform_category_breakdown:
            print(f"    - {cat}: {platform_category_breakdown[cat]}个")
print(f"  实际测试的指标数: {tested_indicators}")

if platform_total_endpoints > 0:
    coverage_rate = (total_indicators / platform_total_endpoints) * 100
    print(f"  平台覆盖率: {coverage_rate:.1f}%")

# =============================================================================
# 1. 基准市场表现分析
# =============================================================================
print("\n" + "=" * 80)
print("基准市场表现分析（Benchmark Performance）")
print("=" * 80)

market_data = data.get('market', {})
benchmark_metrics = market_data.get('benchmark_metrics', {})

# 做多基准
if 'long' in benchmark_metrics:
    long_bench = benchmark_metrics['long']
    print("\n【做多基准表现 (Buy & Hold)】")
    print(f"  总收益率 (Total Return): {long_bench.get('total_return', 0)*100:.2f}%")
    print(f"  年化收益率 (Annual Return): {long_bench.get('annualized_return', 0)*100:.2f}%")
    print(f"  夏普比率 (Sharpe Ratio): {long_bench.get('sharpe_ratio', 0):.3f}")
    print(f"  最大回撤 (Max Drawdown): {long_bench.get('max_drawdown', 0)*100:.2f}%")
    print(f"  年化波动率 (Annual Volatility): {long_bench.get('annual_volatility', 0)*100:.2f}%")

# 做空基准
if 'short' in benchmark_metrics:
    short_bench = benchmark_metrics['short']
    print("\n【做空基准表现 (Short)】")
    print(f"  总收益率 (Total Return): {short_bench.get('total_return', 0)*100:.2f}%")
    print(f"  年化收益率 (Annual Return): {short_bench.get('annualized_return', 0)*100:.2f}%")
    print(f"  夏普比率 (Sharpe Ratio): {short_bench.get('sharpe_ratio', 0):.3f}")
    print(f"  最大回撤 (Max Drawdown): {short_bench.get('max_drawdown', 0)*100:.2f}%")
    print(f"  年化波动率 (Annual Volatility): {short_bench.get('annual_volatility', 0)*100:.2f}%")

# =============================================================================
# 2. 各市场状态下的基准表现
# =============================================================================
print("\n" + "=" * 80)
print("各市场状态下的基准表现")
print("=" * 80)

# 获取市场状态时间段信息
market_regime = market_data.get('market_regime', {})
print("\n【市场状态时间段】")

# 如果market_regime是日期字典，处理并统计各市场状态
if market_regime:
    # 统计各市场状态的天数和时间段
    # 映射数值到市场状态：1.0=bull, -1.0=bear, 0.0=sideways
    regime_map = {1.0: 'bull', -1.0: 'bear', 0.0: 'sideways'}
    regime_stats = {'bull': [], 'bear': [], 'sideways': []}
    current_regime_val = None
    current_start = None
    
    sorted_dates = sorted(market_regime.keys())
    
    for date in sorted_dates:
        regime_val = market_regime[date]
        
        if regime_val != current_regime_val:
            # 保存上一个时间段
            if current_regime_val is not None and current_start:
                regime_name = regime_map.get(current_regime_val, 'unknown')
                if regime_name != 'unknown':
                    regime_stats[regime_name].append({
                        'start': current_start,
                        'end': prev_date,
                        'days': (pd.to_datetime(prev_date) - pd.to_datetime(current_start)).days + 1
                    })
            
            # 开始新的时间段
            current_regime_val = regime_val
            current_start = date
        
        prev_date = date
    
    # 保存最后一个时间段
    if current_regime_val is not None and current_start:
        regime_name = regime_map.get(current_regime_val, 'unknown')
        if regime_name != 'unknown':
            regime_stats[regime_name].append({
                'start': current_start,
                'end': prev_date,
                'days': (pd.to_datetime(prev_date) - pd.to_datetime(current_start)).days + 1
            })
    
    # 输出统计信息
    for regime in ['bull', 'bear', 'sideways']:
        periods = regime_stats[regime]
        total_days = sum(p['days'] for p in periods)
        print(f"\n  {regime.upper()}市场:")
        print(f"    总天数: {total_days}天")
        print(f"    时间段数: {len(periods)}个")
        if periods:
            # 显示前3个时间段作为示例
            for i, period in enumerate(periods, 1):
                print(f"      段{i}: {period['start'][:10]} 至 {period['end'][:10]} ({period['days']}天)")

full_regime_benchmarks = market_data.get('full_regime_benchmarks', {})

if 'long' in full_regime_benchmarks:
    print("\n【做多基准 - 不同市场状态】")
    long_regimes = full_regime_benchmarks['long']
    for regime in ['bull', 'bear', 'sideways']:
        if regime in long_regimes:
            r = long_regimes[regime]
            print(f"\n  {regime.upper()}市场:")
            print(f"    天数: {r.get('total_days', 0):.0f}天")
            print(f"    累计收益率: {r.get('benchmark_cumulative', 0)*100:.2f}%")
            print(f"    年化收益率: {r.get('benchmark_annual_return', 0)*100:.2f}%")
            print(f"    年化波动率: {r.get('benchmark_annual_volatility', 0)*100:.2f}%")
            print(f"    最大回撤: {r.get('benchmark_max_drawdown', 0)*100:.2f}%")
            print(f"    夏普比率: {r.get('benchmark_sharpe', 0):.3f}")

if 'short' in full_regime_benchmarks:
    print("\n【做空基准 - 不同市场状态】")
    short_regimes = full_regime_benchmarks['short']
    for regime in ['bull', 'bear', 'sideways']:
        if regime in short_regimes:
            r = short_regimes[regime]
            print(f"\n  {regime.upper()}市场:")
            print(f"    天数: {r.get('total_days', 0):.0f}天")
            print(f"    累计收益率: {r.get('benchmark_cumulative', 0)*100:.2f}%")
            print(f"    年化收益率: {r.get('benchmark_annual_return', 0)*100:.2f}%")
            print(f"    年化波动率: {r.get('benchmark_annual_volatility', 0)*100:.2f}%")
            print(f"    最大回撤: {r.get('benchmark_max_drawdown', 0)*100:.2f}%")
            print(f"    夏普比率: {r.get('benchmark_sharpe', 0):.3f}")

# =============================================================================
# 3. 寻找全市场正收益策略
# =============================================================================
print("\n" + "=" * 80)
print("全市场正收益策略分析")
print("=" * 80)

indicators = data.get('indicators', {})

# 收集所有符合条件的策略
all_weather_positive_long = []
all_weather_positive_short = []

for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    optimal_data = indicator_data.get('optimal', {})
    
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict) or 'strategies' not in percentile_data:
            continue
        
        strategies = percentile_data['strategies']
        
        # 处理做多策略
        if 'long' in strategies:
            long_strategy = strategies['long']
            if 'regime_performance' in long_strategy:
                regime_perf = long_strategy['regime_performance']
                
                # 检查是否所有市场都有正收益和正超额
                all_positive = True
                regime_results = {}
                
                for regime in ['bull', 'bear', 'sideways']:
                    if regime in regime_perf:
                        r = regime_perf[regime]
                        strategy_return = r.get('strategy_return', 0)
                        excess_return = r.get('excess_return', 0)
                        
                        regime_results[regime] = {
                            'return': strategy_return,
                            'excess': excess_return,
                            'sharpe': r.get('sharpe', 0),
                            'win_rate': r.get('excess_return_win_rate', 0)
                        }
                        
                        if strategy_return <= 0 or excess_return <= 0:
                            all_positive = False
                    else:
                        all_positive = False
                
                if all_positive:
                    # 获取相关性信息
                    correlation_type = percentile_data.get('correlation_type', 'unknown')
                    correlation_value = percentile_data.get('correlation_value', 0)
                    
                    all_weather_positive_long.append({
                        'indicator': indicator_name,
                        'percentile': int(percentile),
                        'threshold': percentile_data.get('threshold', 0),
                        'correlation_type': correlation_type,
                        'correlation_value': correlation_value,
                        'bull_return': regime_results['bull']['return'],
                        'bull_excess': regime_results['bull']['excess'],
                        'bull_sharpe': regime_results['bull']['sharpe'],
                        'bear_return': regime_results['bear']['return'],
                        'bear_excess': regime_results['bear']['excess'],
                        'bear_sharpe': regime_results['bear']['sharpe'],
                        'sideways_return': regime_results['sideways']['return'],
                        'sideways_excess': regime_results['sideways']['excess'],
                        'sideways_sharpe': regime_results['sideways']['sharpe'],
                        'avg_excess': np.mean([regime_results[r]['excess'] for r in ['bull', 'bear', 'sideways']]),
                        'min_excess': min([regime_results[r]['excess'] for r in ['bull', 'bear', 'sideways']]),
                        'max_rank_ic': optimal_data.get('max_rank_ic', 0),
                        'max_pearson_ic': optimal_data.get('max_pearson_ic', 0)
                    })
        
        # 处理做空策略
        if 'short' in strategies:
            short_strategy = strategies['short']
            if 'regime_performance' in short_strategy:
                regime_perf = short_strategy['regime_performance']
                
                # 检查是否所有市场都有正收益和正超额
                all_positive = True
                regime_results = {}
                
                for regime in ['bull', 'bear', 'sideways']:
                    if regime in regime_perf:
                        r = regime_perf[regime]
                        strategy_return = r.get('strategy_return', 0)
                        excess_return = r.get('excess_return', 0)
                        
                        regime_results[regime] = {
                            'return': strategy_return,
                            'excess': excess_return,
                            'sharpe': r.get('sharpe', 0),
                            'win_rate': r.get('excess_return_win_rate', 0)
                        }
                        
                        if strategy_return <= 0 or excess_return <= 0:
                            all_positive = False
                    else:
                        all_positive = False
                
                if all_positive:
                    # 获取相关性信息
                    correlation_type = percentile_data.get('correlation_type', 'unknown')
                    correlation_value = percentile_data.get('correlation_value', 0)
                    
                    all_weather_positive_short.append({
                        'indicator': indicator_name,
                        'percentile': int(percentile),
                        'threshold': percentile_data.get('threshold', 0),
                        'correlation_type': correlation_type,
                        'correlation_value': correlation_value,
                        'bull_return': regime_results['bull']['return'],
                        'bull_excess': regime_results['bull']['excess'],
                        'bull_sharpe': regime_results['bull']['sharpe'],
                        'bear_return': regime_results['bear']['return'],
                        'bear_excess': regime_results['bear']['excess'],
                        'bear_sharpe': regime_results['bear']['sharpe'],
                        'sideways_return': regime_results['sideways']['return'],
                        'sideways_excess': regime_results['sideways']['excess'],
                        'sideways_sharpe': regime_results['sideways']['sharpe'],
                        'avg_excess': np.mean([regime_results[r]['excess'] for r in ['bull', 'bear', 'sideways']]),
                        'min_excess': min([regime_results[r]['excess'] for r in ['bull', 'bear', 'sideways']]),
                        'max_rank_ic': optimal_data.get('max_rank_ic', 0),
                        'max_pearson_ic': optimal_data.get('max_pearson_ic', 0)
                    })

# 输出做多全天候策略
print(f"\n【做多策略 - 全市场正收益】")
print(f"找到 {len(all_weather_positive_long)} 个策略\n")

if all_weather_positive_long:
    df_long = pd.DataFrame(all_weather_positive_long)
    df_long_sorted = df_long.sort_values('avg_excess', ascending=False)
    
    for i, row in df_long_sorted.head(10).iterrows():
        print(f"{list(df_long_sorted.index).index(i)+1}. {row['indicator']} (百分位={row['percentile']}%)")
        print(f"   阈值: {row['threshold']:.6f}")
        print(f"   相关性: {row['correlation_type']} (相关系数={row['correlation_value']:.4f})")
        print(f"   牛市: 收益={row['bull_return']*100:.2f}%, 超额={row['bull_excess']*100:.2f}%, 夏普={row['bull_sharpe']:.2f}")
        print(f"   熊市: 收益={row['bear_return']*100:.2f}%, 超额={row['bear_excess']*100:.2f}%, 夏普={row['bear_sharpe']:.2f}")
        print(f"   震荡: 收益={row['sideways_return']*100:.2f}%, 超额={row['sideways_excess']*100:.2f}%, 夏普={row['sideways_sharpe']:.2f}")
        print(f"   平均超额: {row['avg_excess']*100:.2f}%, 最小超额: {row['min_excess']*100:.2f}%")
        print(f"   Rank IC: {row['max_rank_ic']:.4f}, Pearson IC: {row['max_pearson_ic']:.4f}")
        print("-" * 40)
    
    # 保存结果
    df_long_sorted.to_csv('all_weather_positive_long_strategies.csv', index=False)

# 输出做空全天候策略
print(f"\n【做空策略 - 全市场正收益】")
print(f"找到 {len(all_weather_positive_short)} 个策略\n")

if all_weather_positive_short:
    df_short = pd.DataFrame(all_weather_positive_short)
    df_short_sorted = df_short.sort_values('avg_excess', ascending=False)
    
    for i, row in df_short_sorted.head(10).iterrows():
        print(f"{list(df_short_sorted.index).index(i)+1}. {row['indicator']} (百分位={row['percentile']}%)")
        print(f"   阈值: {row['threshold']:.6f}")
        print(f"   相关性: {row['correlation_type']} (相关系数={row['correlation_value']:.4f})")
        print(f"   牛市: 收益={row['bull_return']*100:.2f}%, 超额={row['bull_excess']*100:.2f}%, 夏普={row['bull_sharpe']:.2f}")
        print(f"   熊市: 收益={row['bear_return']*100:.2f}%, 超额={row['bear_excess']*100:.2f}%, 夏普={row['bear_sharpe']:.2f}")
        print(f"   震荡: 收益={row['sideways_return']*100:.2f}%, 超额={row['sideways_excess']*100:.2f}%, 夏普={row['sideways_sharpe']:.2f}")
        print(f"   平均超额: {row['avg_excess']*100:.2f}%, 最小超额: {row['min_excess']*100:.2f}%")
        print(f"   Rank IC: {row['max_rank_ic']:.4f}, Pearson IC: {row['max_pearson_ic']:.4f}")
        print("-" * 40)
    
    # 保存结果
    df_short_sorted.to_csv('all_weather_positive_short_strategies.csv', index=False)

# =============================================================================
# 4. 寻找100%准确度的信号
# =============================================================================
print("\n" + "=" * 80)
print("100%准确度信号分析 (Signal Accuracy = 100%)")
print("=" * 80)

perfect_signals = []

for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict) or 'strategies' not in percentile_data:
            continue
        
        strategies = percentile_data['strategies']
        
        # 检查做多策略的信号准确度
        if 'long' in strategies:
            long_strategy = strategies['long']
            if 'signal_ig_analysis' in long_strategy:
                sig_analysis = long_strategy['signal_ig_analysis']
                
                for horizon, horizon_data in sig_analysis.items():
                    if isinstance(horizon_data, dict):
                        accuracy = horizon_data.get('signal_accuracy', 0)
                        if accuracy >= 0.999:  # 99.9%以上视为100%
                            # 获取相关性信息
                            correlation = horizon_data.get('correlation', 0)
                            correlation_type = percentile_data.get('correlation_type', 'positive' if correlation > 0 else 'negative')
                            
                            perfect_signals.append({
                                'indicator': indicator_name,
                                'strategy_type': 'long',
                                'percentile': int(percentile),
                                'threshold': percentile_data.get('threshold', 0),
                                'correlation': correlation,
                                'correlation_type': correlation_type,
                                'horizon': horizon,
                                'signal_accuracy': accuracy,
                                'signal_count': horizon_data.get('signal_count', 0),
                                'information_gain': horizon_data.get('information_gain', 0),
                                'total_days': horizon_data.get('total_days', 0)
                            })
        
        # 检查做空策略的信号准确度
        if 'short' in strategies:
            short_strategy = strategies['short']
            if 'signal_ig_analysis' in short_strategy:
                sig_analysis = short_strategy['signal_ig_analysis']
                
                for horizon, horizon_data in sig_analysis.items():
                    if isinstance(horizon_data, dict):
                        accuracy = horizon_data.get('signal_accuracy', 0)
                        if accuracy >= 0.999:  # 99.9%以上视为100%
                            # 获取相关性信息
                            correlation = horizon_data.get('correlation', 0)
                            correlation_type = percentile_data.get('correlation_type', 'positive' if correlation > 0 else 'negative')
                            
                            perfect_signals.append({
                                'indicator': indicator_name,
                                'strategy_type': 'short',
                                'percentile': int(percentile),
                                'threshold': percentile_data.get('threshold', 0),
                                'correlation': correlation,
                                'correlation_type': correlation_type,
                                'horizon': horizon,
                                'signal_accuracy': accuracy,
                                'signal_count': horizon_data.get('signal_count', 0),
                                'information_gain': horizon_data.get('information_gain', 0),
                                'total_days': horizon_data.get('total_days', 0)
                            })

print(f"\n找到 {len(perfect_signals)} 个100%准确度的信号\n")

if perfect_signals:
    # 按信息增益排序
    perfect_signals_sorted = sorted(perfect_signals, key=lambda x: x['information_gain'], reverse=True)
    
    # 去重逻辑：对于相同指标、相同策略类型、相同预测周期的信号，保留范围最大的
    deduplicated_signals = {}
    for signal in perfect_signals_sorted:
        # 创建唯一键：指标+策略类型+预测周期+操作方向
        percentile = signal['percentile']
        
        # 判断操作方向
        if signal['strategy_type'] == 'long':
            correlation_type = signal.get('correlation_type', 'unknown')
            if correlation_type == 'positive':
                operation_type = '>='
            else:
                operation_type = '<='
        else:  # short
            if percentile >= 50:
                operation_type = '>='
            else:
                operation_type = '<='
        
        key = (signal['indicator'], signal['strategy_type'], signal['horizon'], operation_type)
        
        if key not in deduplicated_signals:
            deduplicated_signals[key] = signal
        else:
            # 比较阈值，保留范围最大的
            existing = deduplicated_signals[key]
            
            # 对于 >= 操作，保留较小的阈值（范围更大）
            # 对于 <= 操作，保留较大的阈值（范围更大）
            if operation_type == '>=':
                if signal['threshold'] < existing['threshold']:
                    deduplicated_signals[key] = signal
            else:  # <=
                if signal['threshold'] > existing['threshold']:
                    deduplicated_signals[key] = signal
    
    # 转换为列表并按信息增益重新排序
    perfect_signals_dedup = sorted(deduplicated_signals.values(), 
                                  key=lambda x: x['information_gain'], 
                                  reverse=True)
    
    print(f"去重后剩余 {len(perfect_signals_dedup)} 个独特信号（原始 {len(perfect_signals)} 个）\n")
    print("【TOP 20 100%准确度信号】")
    for i, signal in enumerate(perfect_signals_dedup[:20], 1):
        # 判断操作方向
        correlation_type = signal.get('correlation_type', 'unknown')
        correlation_value = signal.get('correlation', 0)
        
        # 根据百分位判断是高分位还是低分位
        # 对于做多策略，通常使用低分位（买入信号）
        # 对于做空策略，通常使用高分位（卖出信号）
        percentile = signal['percentile']
        
        if signal['strategy_type'] == 'long':
            # 做多策略
            if correlation_type == 'positive':
                # 正相关：指标高->价格高，所以高于阈值时做多
                operation = f"指标值 ≥ {signal['threshold']:.6f} 时做多"
            else:
                # 负相关：指标高->价格低，所以低于阈值时做多
                operation = f"指标值 ≤ {signal['threshold']:.6f} 时做多"
        else:  # short
            # 做空策略
            if percentile >= 50:  # 高分位
                # 高分位阈值，指标值>=阈值时触发
                operation = f"指标值 ≥ {signal['threshold']:.6f} 时做空"
            else:  # 低分位
                # 低分位阈值，指标值<=阈值时触发
                operation = f"指标值 ≤ {signal['threshold']:.6f} 时做空"
        
        print(f"\n{i}. {signal['indicator']} ({signal['strategy_type']})")
        print(f"   百分位: {signal['percentile']}%, 阈值: {signal['threshold']:.6f}")
        print(f"   操作: {operation}")
        print(f"   相关性: {correlation_type} (相关系数={correlation_value:.4f})")
        print(f"   预测周期: {signal['horizon']}")
        print(f"   信号准确度: {signal['signal_accuracy']*100:.1f}%")
        print(f"   信号数量: {signal['signal_count']:.0f}")
        print(f"   信息增益: {signal['information_gain']:.6f}")
        print(f"   总天数: {signal['total_days']}")
        print(f"   信号频率: {signal['signal_count']/signal['total_days']*100:.2f}%")
    
    # 保存结果（使用去重后的数据）
    df_perfect = pd.DataFrame(perfect_signals_dedup)
    df_perfect.to_csv('perfect_accuracy_signals.csv', index=False)
    
    # 按指标统计
    print("\n【按指标统计100%准确度信号】")
    indicator_stats = {}
    for signal in perfect_signals:
        ind = signal['indicator']
        if ind not in indicator_stats:
            indicator_stats[ind] = {'count': 0, 'horizons': set(), 'max_ig': 0}
        indicator_stats[ind]['count'] += 1
        indicator_stats[ind]['horizons'].add(signal['horizon'])
        indicator_stats[ind]['max_ig'] = max(indicator_stats[ind]['max_ig'], signal['information_gain'])
    
    # 按数量排序
    sorted_stats = sorted(indicator_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    print("\n最多100%准确信号的指标:")
    for i, (indicator, stats) in enumerate(sorted_stats[:10], 1):
        print(f"{i}. {indicator}: {stats['count']}个信号, "
              f"周期: {', '.join(sorted(stats['horizons']))}, "
              f"最大信息增益: {stats['max_ig']:.6f}")

# =============================================================================
# 5. 相关性类型分析
# =============================================================================
print("\n" + "=" * 80)
print("相关性类型分析")
print("=" * 80)

# 分析所有策略的相关性类型
all_strategies_correlation = []

for indicator_name, indicator_data in indicators.items():
    if 'threshold_impact' not in indicator_data:
        continue
    
    threshold_data = indicator_data['threshold_impact']
    optimal_data = indicator_data.get('optimal', {})
    
    for percentile, percentile_data in threshold_data.items():
        if not isinstance(percentile_data, dict):
            continue
        
        # 获取相关性信息
        correlation_type = percentile_data.get('correlation_type', 'unknown')
        correlation_value = percentile_data.get('correlation_value', 0)
        
        if correlation_type != 'unknown' and 'strategies' in percentile_data:
            strategies = percentile_data['strategies']
            
            # 记录策略信息
            strategy_info = {
                'indicator': indicator_name,
                'percentile': int(percentile),
                'threshold': percentile_data.get('threshold', 0),
                'correlation_type': correlation_type,
                'correlation_value': correlation_value,
                'max_rank_ic': optimal_data.get('max_rank_ic', 0),
                'max_pearson_ic': optimal_data.get('max_pearson_ic', 0)
            }
            
            # 获取做多和做空策略的表现
            if 'long' in strategies:
                long_strategy = strategies['long']
                if 'regime_performance' in long_strategy:
                    regime_perf = long_strategy['regime_performance']
                    if 'bear' in regime_perf:
                        strategy_info['long_bear_excess'] = regime_perf['bear'].get('excess_return', 0)
                    if 'bull' in regime_perf:
                        strategy_info['long_bull_excess'] = regime_perf['bull'].get('excess_return', 0)
            
            if 'short' in strategies:
                short_strategy = strategies['short']
                if 'regime_performance' in short_strategy:
                    regime_perf = short_strategy['regime_performance']
                    if 'bear' in regime_perf:
                        strategy_info['short_bear_excess'] = regime_perf['bear'].get('excess_return', 0)
                    if 'bull' in regime_perf:
                        strategy_info['short_bull_excess'] = regime_perf['bull'].get('excess_return', 0)
            
            all_strategies_correlation.append(strategy_info)

if all_strategies_correlation:
    df_corr = pd.DataFrame(all_strategies_correlation)
    
    # 统计相关性类型
    print("\n【相关性类型统计】")
    correlation_counts = df_corr['correlation_type'].value_counts()
    for corr_type, count in correlation_counts.items():
        print(f"  {corr_type}: {count}个策略")
    
    # 分析正相关策略
    print("\n【正相关策略分析】")
    positive_corr = df_corr[df_corr['correlation_type'] == 'positive']
    if len(positive_corr) > 0:
        print(f"  总数: {len(positive_corr)}个")
        print(f"  平均相关系数: {positive_corr['correlation_value'].mean():.4f}")
        
        # 找出最强正相关的指标
        top_positive = positive_corr.nlargest(5, 'correlation_value')
        print("\n  最强正相关指标TOP 5:")
        for i, row in top_positive.iterrows():
            print(f"    {row['indicator']} (百分位={row['percentile']}%): 相关系数={row['correlation_value']:.4f}")
            if 'long_bear_excess' in row:
                print(f"      做多熊市超额: {row['long_bear_excess']*100:.2f}%")
            if 'short_bull_excess' in row:
                print(f"      做空牛市超额: {row['short_bull_excess']*100:.2f}%")
    
    # 分析负相关策略
    print("\n【负相关策略分析】")
    negative_corr = df_corr[df_corr['correlation_type'] == 'negative']
    if len(negative_corr) > 0:
        print(f"  总数: {len(negative_corr)}个")
        print(f"  平均相关系数: {negative_corr['correlation_value'].mean():.4f}")
        
        # 找出最强负相关的指标
        top_negative = negative_corr.nsmallest(5, 'correlation_value')
        print("\n  最强负相关指标TOP 5:")
        for i, row in top_negative.iterrows():
            print(f"    {row['indicator']} (百分位={row['percentile']}%): 相关系数={row['correlation_value']:.4f}")
            if 'long_bear_excess' in row:
                print(f"      做多熊市超额: {row['long_bear_excess']*100:.2f}%")
            if 'short_bull_excess' in row:
                print(f"      做空牛市超额: {row['short_bull_excess']*100:.2f}%")
    
    # 分析相关性与策略表现的关系
    print("\n【相关性与策略表现关系】")
    
    # 正相关策略在不同市场的表现
    if 'long_bear_excess' in df_corr.columns:
        positive_long_bear = positive_corr[positive_corr['long_bear_excess'] > 0]
        print(f"\n  正相关指标做多策略在熊市有正超额收益: {len(positive_long_bear)}个")
        if len(positive_long_bear) > 0:
            print(f"    平均熊市超额: {positive_long_bear['long_bear_excess'].mean()*100:.2f}%")
    
    if 'short_bull_excess' in df_corr.columns:
        negative_short_bull = negative_corr[negative_corr['short_bull_excess'] > 0]
        print(f"\n  负相关指标做空策略在牛市有正超额收益: {len(negative_short_bull)}个")
        if len(negative_short_bull) > 0:
            print(f"    平均牛市超额: {negative_short_bull['short_bull_excess'].mean()*100:.2f}%")
    
    # 保存相关性分析结果
    df_corr.to_csv('correlation_analysis.csv', index=False)
    print("\n  相关性分析已保存至: correlation_analysis.csv")

# =============================================================================
# 6. 综合统计
# =============================================================================
print("\n" + "=" * 80)
print("综合统计摘要")
print("=" * 80)

print(f"\n全市场正收益策略数量:")
print(f"  做多策略: {len(all_weather_positive_long)}个")
print(f"  做空策略: {len(all_weather_positive_short)}个")

print(f"\n100%准确度信号:")
print(f"  总数: {len(perfect_signals)}个")
if perfect_signals:
    long_signals = [s for s in perfect_signals if s['strategy_type'] == 'long']
    short_signals = [s for s in perfect_signals if s['strategy_type'] == 'short']
    print(f"  做多信号: {len(long_signals)}个")
    print(f"  做空信号: {len(short_signals)}个")
    
    # 找出最常见的周期
    horizons = [s['horizon'] for s in perfect_signals]
    from collections import Counter
    horizon_counts = Counter(horizons)
    print(f"\n  最常见的预测周期:")
    for horizon, count in horizon_counts.most_common(5):
        print(f"    {horizon}: {count}个信号")

print("\n结果文件已保存:")
print("  - all_weather_positive_long_strategies.csv")
print("  - all_weather_positive_short_strategies.csv")
print("  - perfect_accuracy_signals.csv")