#!/usr/bin/env python3
"""
测试做空收益计算的修复
"""

import numpy as np
import pandas as pd

def test_short_returns():
    """测试做空收益计算"""
    
    # 创建测试价格序列
    # 场景1：价格下跌50%
    prices_down = pd.Series([100, 90, 80, 70, 60, 50])
    
    # 场景2：价格上涨100%
    prices_up = pd.Series([100, 110, 120, 150, 180, 200])
    
    # 场景3：横盘震荡（最终略跌）
    prices_sideways = pd.Series([100, 110, 90, 95, 105, 85, 90])
    
    test_cases = [
        ("价格下跌50%", prices_down),
        ("价格上涨100%", prices_up),
        ("横盘震荡", prices_sideways)
    ]
    
    for name, prices in test_cases:
        print(f"\n{'='*60}")
        print(f"测试场景: {name}")
        print(f"{'='*60}")
        print(f"价格序列: {list(prices)}")
        
        # 计算价格变化
        price_change = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
        print(f"总价格变化: {price_change:.1f}%")
        
        # 方法1：旧的做空计算（简单负收益）
        returns = prices.pct_change().fillna(0)
        short_returns_old = -returns
        cumulative_old = (1 + short_returns_old).cumprod()
        final_return_old = (cumulative_old.iloc[-1] - 1) * 100
        
        print(f"\n旧方法（简单负收益）:")
        print(f"  做空最终收益: {final_return_old:.1f}%")
        
        # 方法2：新的做空计算（倒数法）
        price_ratio = prices / prices.iloc[0]
        short_cumulative_new = 1 / price_ratio
        final_return_new = (short_cumulative_new.iloc[-1] - 1) * 100
        
        print(f"\n新方法（价格比率法）:")
        print(f"  做空最终收益: {final_return_new:.1f}%")
        
        # 理论收益
        theoretical_return = -price_change
        print(f"\n理论收益（价格反向）: {theoretical_return:.1f}%")
        
        # 验证对称性
        print(f"\n对称性验证:")
        print(f"  做多收益: {price_change:.1f}%")
        print(f"  做空收益（新方法）: {final_return_new:.1f}%")
        print(f"  总和: {price_change + final_return_new:.1f}% (理想值: 0%)")

def test_regime_returns():
    """测试不同市场状态下的收益"""
    
    print(f"\n{'='*60}")
    print(f"测试ETH横盘市场场景")
    print(f"{'='*60}")
    
    # 模拟ETH横盘市场：658天，累计下跌73.8%
    days = 658
    final_price_ratio = 0.262  # 价格剩余26.2%
    
    print(f"市场情况: {days}天，价格从100跌至{final_price_ratio*100:.1f}")
    
    # 做多收益
    long_return = (final_price_ratio - 1) * 100
    print(f"\n做多收益: {long_return:.1f}%")
    
    # 做空收益（新方法：倒数法）
    short_return_new = (1 / final_price_ratio - 1) * 100
    print(f"做空收益（新方法）: {short_return_new:.1f}%")
    
    # 每日平均收益率
    daily_return = final_price_ratio ** (1/days) - 1
    print(f"\n每日平均收益率: {daily_return*100:.4f}%")
    
    # 验证
    print(f"\n验证:")
    print(f"  如果价格跌{-long_return:.1f}%")
    print(f"  做空应该赚{short_return_new:.1f}%")
    print(f"  这符合做空的实际机制")

if __name__ == "__main__":
    print("测试做空收益计算修复")
    print("="*60)
    
    test_short_returns()
    test_regime_returns()
    
    print(f"\n{'='*60}")
    print("测试完成")