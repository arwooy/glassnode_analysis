#!/usr/bin/env python3
"""
测试信息增益计算中的做空收益修复
"""

import numpy as np
import pandas as pd

def test_ig_short_calculation():
    """测试信息增益计算中的做空收益处理"""
    
    # 创建测试数据
    dates = pd.date_range('2023-01-01', periods=100)
    
    # 价格序列：总体下跌趋势
    prices = pd.Series(100 * (1 - np.linspace(0, 0.5, 100) + 0.1 * np.random.randn(100)), index=dates)
    prices[prices < 20] = 20  # 设置最低价格
    
    print("="*60)
    print("测试信息增益计算中的做空收益")
    print("="*60)
    
    print(f"\n初始价格: {prices.iloc[0]:.2f}")
    print(f"最终价格: {prices.iloc[-1]:.2f}")
    print(f"价格变化: {(prices.iloc[-1]/prices.iloc[0] - 1)*100:.1f}%")
    
    # 测试不同时间窗口
    horizons = [1, 5, 10, 30]
    
    for horizon in horizons:
        print(f"\n--- {horizon}天预测窗口 ---")
        
        # 方法1：旧的做空计算（简单负收益）
        future_returns_old = prices.shift(-horizon).pct_change(horizon)
        short_returns_old = -future_returns_old
        
        # 方法2：新的做空计算（价格比率倒数）
        future_prices = prices.shift(-horizon)
        price_ratio = future_prices / prices
        short_returns_new = (1 / price_ratio - 1).fillna(0)
        
        # 比较结果
        valid_idx = ~(future_returns_old.isna() | short_returns_new.isna())
        
        if valid_idx.sum() > 0:
            # 计算平均收益
            avg_long = future_returns_old[valid_idx].mean() * 100
            avg_short_old = short_returns_old[valid_idx].mean() * 100
            avg_short_new = short_returns_new[valid_idx].mean() * 100
            
            # 计算正收益比例（这会影响信息增益）
            positive_ratio_long = (future_returns_old[valid_idx] > 0).mean() * 100
            positive_ratio_short_old = (short_returns_old[valid_idx] > 0).mean() * 100
            positive_ratio_short_new = (short_returns_new[valid_idx] > 0).mean() * 100
            
            print(f"  做多平均收益: {avg_long:.2f}%")
            print(f"  做空平均收益（旧方法）: {avg_short_old:.2f}%")
            print(f"  做空平均收益（新方法）: {avg_short_new:.2f}%")
            print(f"  ")
            print(f"  正收益天数比例:")
            print(f"    做多: {positive_ratio_long:.1f}%")
            print(f"    做空（旧方法）: {positive_ratio_short_old:.1f}%")
            print(f"    做空（新方法）: {positive_ratio_short_new:.1f}%")
            
            # 信息增益相关：熵的计算
            def calc_entropy(returns):
                """计算收益二分类的熵"""
                p_positive = (returns > 0).mean()
                p_negative = 1 - p_positive
                if p_positive == 0 or p_negative == 0:
                    return 0
                return -p_positive * np.log2(p_positive) - p_negative * np.log2(p_negative)
            
            h_long = calc_entropy(future_returns_old[valid_idx])
            h_short_old = calc_entropy(short_returns_old[valid_idx])
            h_short_new = calc_entropy(short_returns_new[valid_idx])
            
            print(f"  ")
            print(f"  收益分布熵值（越接近1越平衡）:")
            print(f"    做多: {h_long:.3f}")
            print(f"    做空（旧方法）: {h_short_old:.3f}")
            print(f"    做空（新方法）: {h_short_new:.3f}")
    
    # 展示具体例子
    print("\n" + "="*60)
    print("具体例子：价格从100跌到50")
    print("="*60)
    
    # 做多收益
    long_return = (50/100 - 1) * 100
    
    # 做空收益（旧方法）
    short_return_old = -long_return
    
    # 做空收益（新方法）
    short_return_new = (1/(50/100) - 1) * 100
    
    print(f"做多收益: {long_return:.1f}%")
    print(f"做空收益（旧方法）: {short_return_old:.1f}%")
    print(f"做空收益（新方法）: {short_return_new:.1f}%")
    print("\n新方法正确反映了做空的非线性收益特性")

if __name__ == "__main__":
    test_ig_short_calculation()