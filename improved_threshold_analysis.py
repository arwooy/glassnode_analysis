#!/usr/bin/env python3
"""
Improved threshold impact analysis that accounts for market conditions
and provides better factor quality assessment even in bull markets.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats

def analyze_threshold_impact_improved(
    indicator_data: pd.Series,
    price_data: pd.Series,
    percentiles: List[float] = None) -> Dict:
    """
    分析不同阈值过滤后的影响 - 改进版
    
    主要改进：
    1. 与基准（买入持有）对比
    2. 计算超额收益（Alpha）
    3. 信息比率（Information Ratio）
    4. 最大回撤对比
    5. 上涨/下跌市场分离分析
    """
    
    if percentiles is None:
        percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    
    results = {}
    
    # 计算基准收益（买入持有）
    benchmark_returns = calculate_benchmark_returns(price_data)
    
    # 识别市场状态（牛市/熊市/震荡）
    market_regime = identify_market_regime(price_data)
    
    for pct in percentiles:
        try:
            # 计算阈值
            threshold = np.percentile(indicator_data.dropna(), pct)
            
            # 过滤数据 - 高于阈值时持有，否则空仓
            mask = indicator_data >= threshold
            
            # 构建策略信号
            strategy_signal = mask.astype(int)  # 1=持有, 0=空仓
            
            # 计算策略收益
            strategy_returns = calculate_strategy_returns(
                price_data, 
                strategy_signal,
                indicator_data.index
            )
            
            # 计算性能指标
            performance = calculate_performance_metrics(
                strategy_returns,
                benchmark_returns,
                strategy_signal
            )
            
            # 分离牛市和熊市表现
            regime_performance = calculate_regime_performance(
                strategy_returns,
                benchmark_returns,
                market_regime
            )
            
            # 计算因子有效性指标
            factor_quality = calculate_factor_quality(
                indicator_data,
                price_data,
                threshold,
                mask
            )
            
            results[pct] = {
                'threshold': threshold,
                'sample_size': mask.sum(),
                'sample_ratio': mask.sum() / len(indicator_data),
                
                # 绝对性能
                'absolute_performance': {
                    'total_return': strategy_returns['cumulative'].iloc[-1] if len(strategy_returns) > 0 else 0,
                    'annual_return': strategy_returns['annual_return'] if 'annual_return' in strategy_returns else 0,
                    'volatility': strategy_returns['volatility'] if 'volatility' in strategy_returns else 0,
                    'sharpe': performance['sharpe'],
                    'max_drawdown': performance['max_drawdown']
                },
                
                # 相对性能（vs 基准）
                'relative_performance': {
                    'excess_return': performance['excess_return'],
                    'alpha': performance['alpha'],
                    'beta': performance['beta'],
                    'information_ratio': performance['information_ratio'],
                    'win_rate_vs_benchmark': performance['win_rate_vs_benchmark']
                },
                
                # 市场状态下的表现
                'regime_performance': regime_performance,
                
                # 因子质量
                'factor_quality': factor_quality
            }
            
        except Exception as e:
            print(f"Error analyzing percentile {pct}: {e}")
            continue
    
    return results


def calculate_benchmark_returns(price_data: pd.Series) -> pd.DataFrame:
    """计算基准（买入持有）收益"""
    returns = price_data.pct_change().fillna(0)
    cumulative_returns = (1 + returns).cumprod()
    
    return pd.DataFrame({
        'daily': returns,
        'cumulative': cumulative_returns
    })


def identify_market_regime(price_data: pd.Series, window: int = 50) -> pd.Series:
    """
    识别市场状态
    
    Returns:
        pd.Series: 1=牛市, -1=熊市, 0=震荡
    """
    returns = price_data.pct_change()
    
    # 使用移动平均判断趋势
    ma_short = price_data.rolling(window=20).mean()
    ma_long = price_data.rolling(window=50).mean()
    
    # 计算趋势强度
    trend = pd.Series(index=price_data.index, data=0)
    trend[ma_short > ma_long * 1.02] = 1  # 牛市
    trend[ma_short < ma_long * 0.98] = -1  # 熊市
    
    # 计算波动率
    volatility = returns.rolling(window=window).std()
    high_vol_threshold = volatility.quantile(0.75)
    
    # 高波动率时期标记为震荡市
    trend[volatility > high_vol_threshold] = 0
    
    return trend


def calculate_strategy_returns(
    price_data: pd.Series,
    signal: pd.Series,
    index_align: pd.Index) -> Dict:
    """计算策略收益"""
    
    # 对齐数据
    aligned_price = price_data.reindex(index_align).fillna(method='ffill')
    aligned_signal = signal.reindex(index_align).fillna(0)
    
    # 计算日收益率
    daily_returns = aligned_price.pct_change().fillna(0)
    
    # 策略收益 = 信号 * 日收益率
    strategy_returns = aligned_signal.shift(1) * daily_returns  # shift(1)避免前瞻偏差
    
    # 累积收益
    cumulative_returns = (1 + strategy_returns).cumprod()
    
    # 年化收益和波动率
    annual_return = strategy_returns.mean() * 252
    volatility = strategy_returns.std() * np.sqrt(252)
    
    return {
        'daily': strategy_returns,
        'cumulative': cumulative_returns,
        'annual_return': annual_return,
        'volatility': volatility
    }


def calculate_performance_metrics(
    strategy_returns: Dict,
    benchmark_returns: pd.DataFrame,
    signal: pd.Series) -> Dict:
    """计算性能指标"""
    
    if not strategy_returns or 'daily' not in strategy_returns:
        return {
            'sharpe': 0,
            'max_drawdown': 0,
            'excess_return': 0,
            'alpha': 0,
            'beta': 0,
            'information_ratio': 0,
            'win_rate_vs_benchmark': 0
        }
    
    strategy_daily = strategy_returns['daily']
    benchmark_daily = benchmark_returns['daily']
    
    # 对齐数据
    aligned_data = pd.DataFrame({
        'strategy': strategy_daily,
        'benchmark': benchmark_daily
    }).dropna()
    
    if len(aligned_data) < 30:
        return {
            'sharpe': 0,
            'max_drawdown': 0,
            'excess_return': 0,
            'alpha': 0,
            'beta': 0,
            'information_ratio': 0,
            'win_rate_vs_benchmark': 0
        }
    
    # Sharpe Ratio
    sharpe = (aligned_data['strategy'].mean() / aligned_data['strategy'].std() * np.sqrt(252)) if aligned_data['strategy'].std() > 0 else 0
    
    # 最大回撤
    cumulative = (1 + aligned_data['strategy']).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # 超额收益
    excess_returns = aligned_data['strategy'] - aligned_data['benchmark']
    excess_return = excess_returns.mean() * 252
    
    # Alpha 和 Beta (使用线性回归)
    try:
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            aligned_data['benchmark'], 
            aligned_data['strategy']
        )
        beta = slope
        alpha = intercept * 252  # 年化
    except:
        beta = 1
        alpha = 0
    
    # Information Ratio
    tracking_error = excess_returns.std() * np.sqrt(252)
    information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
    
    # 相对于基准的胜率
    win_rate_vs_benchmark = (excess_returns > 0).mean()
    
    return {
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'excess_return': excess_return,
        'alpha': alpha,
        'beta': beta,
        'information_ratio': information_ratio,
        'win_rate_vs_benchmark': win_rate_vs_benchmark
    }


def calculate_regime_performance(
    strategy_returns: Dict,
    benchmark_returns: pd.DataFrame,
    market_regime: pd.Series) -> Dict:
    """计算不同市场状态下的表现"""
    
    if not strategy_returns or 'daily' not in strategy_returns:
        return {}
    
    regime_performance = {}
    
    for regime_value, regime_name in [(1, 'bull'), (-1, 'bear'), (0, 'sideways')]:
        mask = market_regime == regime_value
        
        if mask.sum() > 0:
            strategy_regime = strategy_returns['daily'][mask]
            benchmark_regime = benchmark_returns['daily'][mask]
            
            regime_performance[regime_name] = {
                'days': mask.sum(),
                'strategy_return': strategy_regime.mean() * 252 if len(strategy_regime) > 0 else 0,
                'benchmark_return': benchmark_regime.mean() * 252 if len(benchmark_regime) > 0 else 0,
                'excess_return': (strategy_regime.mean() - benchmark_regime.mean()) * 252 if len(strategy_regime) > 0 else 0,
                'win_rate': (strategy_regime > benchmark_regime).mean() if len(strategy_regime) > 0 else 0
            }
    
    return regime_performance


def calculate_factor_quality(
    indicator_data: pd.Series,
    price_data: pd.Series,
    threshold: float,
    mask: pd.Series) -> Dict:
    """
    计算因子质量指标
    
    这些指标不依赖于整体市场方向，更能反映因子的真实预测能力
    """
    
    # 计算未来收益
    future_returns = {}
    for days in [1, 7, 30]:
        future_returns[f'{days}d'] = price_data.shift(-days) / price_data - 1
    
    # 计算IC (Information Coefficient) - 因子值与未来收益的相关性
    ic_scores = {}
    for period, returns in future_returns.items():
        # Rank IC (更稳健)
        try:
            rank_ic = stats.spearmanr(
                indicator_data.dropna(), 
                returns.reindex(indicator_data.index).dropna()
            )[0]
            ic_scores[f'rank_ic_{period}'] = rank_ic
        except:
            ic_scores[f'rank_ic_{period}'] = 0
    
    # 计算因子单调性 - 不同分位数的收益是否单调递增
    try:
        quantiles = pd.qcut(indicator_data.dropna(), 10, labels=False, duplicates='drop')
        monotonicity_score = calculate_monotonicity(quantiles, future_returns['30d'])
    except:
        monotonicity_score = 0
    
    # 计算因子区分度 - 高低两组的收益差异
    try:
        high_group = indicator_data >= indicator_data.quantile(0.8)
        low_group = indicator_data <= indicator_data.quantile(0.2)
        
        high_returns = future_returns['30d'][high_group].mean()
        low_returns = future_returns['30d'][low_group].mean()
        discrimination = high_returns - low_returns
    except:
        discrimination = 0
    
    # 计算因子稳定性 - 滚动窗口IC的标准差
    try:
        rolling_ic = []
        window = 60
        for i in range(window, len(indicator_data)):
            window_data = indicator_data.iloc[i-window:i]
            window_returns = future_returns['7d'].iloc[i-window:i]
            if len(window_data.dropna()) > 20:
                ic = stats.spearmanr(window_data.dropna(), 
                                    window_returns.reindex(window_data.index).dropna())[0]
                rolling_ic.append(ic)
        
        stability = 1 / (np.std(rolling_ic) + 0.01) if rolling_ic else 0
    except:
        stability = 0
    
    return {
        'ic_scores': ic_scores,
        'monotonicity': monotonicity_score,
        'discrimination': discrimination,
        'stability': stability,
        'quality_score': (abs(ic_scores.get('rank_ic_30d', 0)) + 
                         monotonicity_score + 
                         abs(discrimination) * 10 + 
                         stability * 0.1) / 4
    }


def calculate_monotonicity(quantiles: pd.Series, returns: pd.Series) -> float:
    """计算因子单调性得分"""
    try:
        group_returns = []
        for q in range(10):
            mask = quantiles == q
            if mask.sum() > 0:
                group_returns.append(returns[mask].mean())
        
        # 计算单调性分数（斯皮尔曼相关系数）
        if len(group_returns) == 10:
            monotonicity = stats.spearmanr(range(10), group_returns)[0]
            return abs(monotonicity)
    except:
        pass
    
    return 0


# 示例：如何集成到主分析类
def integrate_improved_analysis(analyzer_class):
    """
    将改进的分析方法集成到GlassnodeAdvancedAnalyzer类
    
    Usage:
        analyzer.analyze_threshold_impact = analyze_threshold_impact_improved
    """
    analyzer_class.analyze_threshold_impact_improved = analyze_threshold_impact_improved
    analyzer_class.calculate_factor_quality = calculate_factor_quality
    return analyzer_class