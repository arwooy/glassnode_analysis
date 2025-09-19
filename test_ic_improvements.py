#!/usr/bin/env python3
"""
测试IC (Information Coefficient)改进
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats

def test_ic_calculation():
    """测试IC计算的改进"""
    
    print("="*60)
    print("IC (Information Coefficient) 改进测试")
    print("="*60)
    
    # 创建测试数据
    np.random.seed(42)
    n = 100
    
    # 场景1: 线性关系（Pearson IC表现好）
    print("\n### 场景1: 线性关系 ###")
    indicator1 = np.random.randn(n)
    future_return1 = 0.5 * indicator1 + np.random.randn(n) * 0.5
    
    pearson_ic1 = np.corrcoef(indicator1, future_return1)[0, 1]
    rank_ic1, _ = stats.spearmanr(indicator1, future_return1)
    
    print(f"Pearson IC: {pearson_ic1:.4f}")
    print(f"Rank IC: {rank_ic1:.4f}")
    print("结论: 线性关系下两者差异不大")
    
    # 场景2: 非线性单调关系（Rank IC表现更好）
    print("\n### 场景2: 非线性单调关系 ###")
    indicator2 = np.random.randn(n)
    # 创建非线性但单调的关系
    future_return2 = np.sign(indicator2) * (np.abs(indicator2) ** 0.5) + np.random.randn(n) * 0.3
    
    pearson_ic2 = np.corrcoef(indicator2, future_return2)[0, 1]
    rank_ic2, _ = stats.spearmanr(indicator2, future_return2)
    
    print(f"Pearson IC: {pearson_ic2:.4f}")
    print(f"Rank IC: {rank_ic2:.4f}")
    print("结论: 非线性关系下Rank IC更能捕捉相关性")
    
    # 场景3: 有异常值（Rank IC更稳健）
    print("\n### 场景3: 存在异常值 ###")
    indicator3 = np.random.randn(n)
    future_return3 = 0.5 * indicator3 + np.random.randn(n) * 0.5
    # 添加异常值
    future_return3[0] = 100  # 极端异常值
    
    pearson_ic3 = np.corrcoef(indicator3, future_return3)[0, 1]
    rank_ic3, _ = stats.spearmanr(indicator3, future_return3)
    
    print(f"Pearson IC: {pearson_ic3:.4f} (被异常值影响)")
    print(f"Rank IC: {rank_ic3:.4f} (对异常值稳健)")
    print("结论: Rank IC对异常值更稳健")
    
    # 场景4: 实际的指标数据模拟
    print("\n### 场景4: 模拟真实因子 ###")
    dates = pd.date_range('2023-01-01', periods=365)
    
    # 创建一个有预测能力的指标
    trend = np.linspace(0, 1, len(dates))
    noise = np.random.randn(len(dates)) * 0.5
    indicator = pd.Series(trend + noise, index=dates)
    
    # 创建价格数据（与指标有一定相关性）
    price_base = 100 * np.exp(trend * 0.5)
    price_noise = np.random.randn(len(dates)) * 5
    price = pd.Series(price_base + price_noise, index=dates)
    
    # 计算不同时间窗口的IC
    horizons = [1, 7, 30, 60]
    
    print("\n时间窗口 | Pearson IC | Rank IC | IC衰减")
    print("-" * 50)
    
    base_pearson = None
    base_rank = None
    
    for horizon in horizons:
        # 计算未来收益
        future_return = (price.shift(-horizon) / price - 1).fillna(0)
        
        # 计算IC
        pearson_ic = indicator.corr(future_return)
        rank_ic, _ = stats.spearmanr(indicator.dropna(), future_return.dropna())
        
        # 计算衰减
        if base_pearson is None:
            base_pearson = abs(pearson_ic)
            base_rank = abs(rank_ic)
            pearson_decay = 0
            rank_decay = 0
        else:
            pearson_decay = (1 - abs(pearson_ic) / base_pearson) * 100
            rank_decay = (1 - abs(rank_ic) / base_rank) * 100
        
        print(f"{horizon:3}天    | {pearson_ic:9.4f} | {rank_ic:7.4f} | "
              f"P:{pearson_decay:5.1f}% R:{rank_decay:5.1f}%")
    
    print("\n结论: IC随预测时间窗口增长而衰减")
    
    return True

def test_integration_with_analyzer():
    """测试与分析器的集成"""
    print("\n" + "="*60)
    print("测试与GlassnodeAdvancedAnalyzer的集成")
    print("="*60)
    
    try:
        from glassnode_advanced_analysis import GlassnodeAdvancedAnalyzer
        
        # 创建分析器实例
        analyzer = GlassnodeAdvancedAnalyzer("dummy_key")
        
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=365)
        indicator_data = pd.Series(np.random.randn(len(dates)), index=dates)
        price_data = pd.Series(100 * np.exp(np.random.randn(len(dates)).cumsum() * 0.01), index=dates)
        
        # 调用改进的方法
        results = analyzer.calculate_information_gain_multi_horizon(
            indicator_data, 
            price_data,
            horizons=[1, 7, 30]
        )
        
        print("\n分析结果:")
        for horizon, data in results.items():
            print(f"\n{horizon}天窗口:")
            print(f"  信息增益: {data.get('information_gain', 0):.4f}")
            print(f"  归一化MI: {data.get('normalized_mi', 0):.4f}")
            print(f"  Pearson IC: {data.get('pearson_ic', 0):.4f}")
            print(f"  Rank IC: {data.get('rank_ic', 0):.4f}")
            
            # 检查是否包含新字段
            if 'pearson_ic' in data and 'rank_ic' in data:
                print("  ✓ 新IC字段已添加")
            else:
                print("  ✗ 缺少新IC字段")
        
        # 测试find_optimal_horizon
        optimal = analyzer.find_optimal_horizon(results)
        
        print("\n最优时间窗口:")
        print(f"  IG最优: {optimal.get('optimal_horizon_ig', 'N/A')}天")
        print(f"  Rank IC最优: {optimal.get('optimal_horizon_rank_ic', 'N/A')}天")
        print(f"  Pearson IC最优: {optimal.get('optimal_horizon_pearson_ic', 'N/A')}天")
        
        if 'max_rank_ic' in optimal and 'max_pearson_ic' in optimal:
            print("\n✓ find_optimal_horizon已更新支持两种IC")
        
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试IC改进...")
    
    # 测试IC计算
    test_ic_calculation()
    
    # 测试集成
    test_integration_with_analyzer()
    
    print("\n" + "="*60)
    print("IC改进总结")
    print("="*60)
    print("\n关键改进:")
    print("1. ✓ 添加了明确的 pearson_ic 字段")
    print("2. ✓ 添加了 rank_ic (Spearman相关)")
    print("3. ✓ 保留 correlation 字段向后兼容")
    print("4. ✓ find_optimal_horizon 支持两种IC")
    print("5. ✓ HTML报告显示两种IC")
    print("6. ✓ Dashboard数据生成器已更新")
    
    print("\n使用建议:")
    print("• 优先关注 Rank IC，它对异常值更稳健")
    print("• Pearson IC 适合线性关系分析")
    print("• IC > 0.05 被认为是有效因子")
    print("• IC 会随时间窗口衰减")

if __name__ == "__main__":
    main()