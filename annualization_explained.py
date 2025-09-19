#!/usr/bin/env python3
"""
解释为什么要年化，以及√252的数学原理
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def explain_annualization():
    """解释年化的必要性"""
    
    print("=" * 60)
    print("为什么要年化？")
    print("=" * 60)
    
    # 创建示例数据
    np.random.seed(42)
    
    # 生成日收益数据（252个交易日）
    daily_returns = np.random.normal(0.0005, 0.02, 252)  # 日均0.05%，标准差2%
    
    # 计算不同时间窗口的统计量
    results = {}
    
    # 1. 日度统计
    daily_mean = np.mean(daily_returns)
    daily_std = np.std(daily_returns)
    results['daily'] = {'mean': daily_mean, 'std': daily_std}
    
    # 2. 周度统计（从日数据聚合）
    weekly_returns = []
    for i in range(0, 252, 5):  # 每5天为一周
        week_return = np.prod(1 + daily_returns[i:i+5]) - 1
        weekly_returns.append(week_return)
    weekly_mean = np.mean(weekly_returns)
    weekly_std = np.std(weekly_returns)
    results['weekly'] = {'mean': weekly_mean, 'std': weekly_std}
    
    # 3. 月度统计（从日数据聚合）
    monthly_returns = []
    for i in range(0, 252, 21):  # 每21天为一月
        month_return = np.prod(1 + daily_returns[i:i+21]) - 1
        monthly_returns.append(month_return)
    monthly_mean = np.mean(monthly_returns)
    monthly_std = np.std(monthly_returns)
    results['monthly'] = {'mean': monthly_mean, 'std': monthly_std}
    
    print("\n【问题：不同频率的数据如何比较？】")
    print("-" * 40)
    print("频率   | 平均收益  | 标准差")
    print("-" * 40)
    print(f"日度   | {results['daily']['mean']*100:6.3f}% | {results['daily']['std']*100:6.3f}%")
    print(f"周度   | {results['weekly']['mean']*100:6.3f}% | {results['weekly']['std']*100:6.3f}%")
    print(f"月度   | {results['monthly']['mean']*100:6.3f}% | {results['monthly']['std']*100:6.3f}%")
    print("\n❓ 哪个策略风险更大？无法直接比较！")
    
    print("\n" + "=" * 60)
    print("年化后的比较")
    print("=" * 60)
    
    # 年化计算
    annualized = {}
    
    # 日度年化
    annualized['daily'] = {
        'mean': results['daily']['mean'] * 252,
        'std': results['daily']['std'] * np.sqrt(252)
    }
    
    # 周度年化
    annualized['weekly'] = {
        'mean': results['weekly']['mean'] * 52,
        'std': results['weekly']['std'] * np.sqrt(52)
    }
    
    # 月度年化
    annualized['monthly'] = {
        'mean': results['monthly']['mean'] * 12,
        'std': results['monthly']['std'] * np.sqrt(12)
    }
    
    print("\n【年化后的统一标准】")
    print("-" * 40)
    print("频率   | 年化收益  | 年化波动率 | 夏普比率")
    print("-" * 40)
    
    for freq in ['daily', 'weekly', 'monthly']:
        sharpe = annualized[freq]['mean'] / annualized[freq]['std']
        print(f"{freq:7} | {annualized[freq]['mean']*100:7.2f}% | {annualized[freq]['std']*100:8.2f}% | {sharpe:8.3f}")
    
    print("\n✓ 现在可以公平比较了！")
    
    return annualized


def explain_sqrt_rule():
    """解释平方根规则"""
    
    print("\n" + "=" * 60)
    print("为什么是 √252？")
    print("=" * 60)
    
    print("\n【数学原理：方差的可加性】")
    print("-" * 40)
    
    # 模拟验证
    np.random.seed(42)
    daily_std = 0.02  # 2%日波动
    
    # 生成1000次模拟
    simulations = 1000
    
    # 不同时间长度的实际标准差
    actual_stds = {}
    theoretical_stds = {}
    
    for days in [1, 5, 21, 63, 126, 252]:
        # 模拟n天的总收益
        total_returns = []
        for _ in range(simulations):
            daily_returns = np.random.normal(0, daily_std, days)
            # 简单相加（对数收益可加）
            total_return = np.sum(daily_returns)
            total_returns.append(total_return)
        
        # 实际标准差
        actual_stds[days] = np.std(total_returns)
        # 理论标准差
        theoretical_stds[days] = daily_std * np.sqrt(days)
    
    print("\n验证: σ(n天) = σ(1天) × √n")
    print("-" * 50)
    print("天数 | 实际std | 理论std (σ×√n) | 误差")
    print("-" * 50)
    
    for days in [1, 5, 21, 63, 126, 252]:
        actual = actual_stds[days]
        theoretical = theoretical_stds[days]
        error = abs(actual - theoretical) / theoretical * 100
        print(f"{days:4} | {actual*100:7.3f}% | {theoretical*100:7.3f}% | {error:5.2f}%")
    
    print("\n✓ 实际值与理论值（σ×√n）非常接近！")
    
    print("\n【关键假设】")
    print("1. 收益独立同分布（IID）")
    print("2. 无自相关")
    print("3. 波动率恒定")
    
    return actual_stds, theoretical_stds


def practical_example():
    """实际例子：不同年化方式的影响"""
    
    print("\n" + "=" * 60)
    print("实际例子：年化的影响")
    print("=" * 60)
    
    # 一个策略的日跟踪误差
    daily_tracking_error = 0.01  # 1%
    
    print(f"\n日跟踪误差: {daily_tracking_error*100:.2f}%")
    print("-" * 40)
    
    # 不同市场的年化
    markets = {
        '美股(252天)': 252,
        '加密货币(365天)': 365,
        'A股(244天)': 244,
        '期货(250天)': 250
    }
    
    print("\n不同市场的年化跟踪误差：")
    for market, days in markets.items():
        annual_te = daily_tracking_error * np.sqrt(days)
        print(f"{market:15} : {annual_te*100:5.2f}%")
    
    print("\n【为什么需要年化？】")
    print("1. 投资者习惯年度思考")
    print("   - '这个策略年收益10%' 比 '日收益0.04%' 更直观")
    
    print("\n2. 不同策略公平比较")
    print("   - 高频策略：每天交易")
    print("   - 低频策略：每月调仓")
    print("   - 年化后才能比较")
    
    print("\n3. 行业标准")
    print("   - 基金年报：年化收益、年化波动率")
    print("   - 风险管理：年化VaR")
    print("   - 业绩费：基于年化表现")
    
    # 示例：不年化的问题
    print("\n【不年化的问题】")
    print("-" * 40)
    
    # 两个策略
    strategy_A_daily_return = 0.04 / 100  # 日均0.04%
    strategy_A_daily_std = 1.0 / 100      # 日波动1%
    
    strategy_B_monthly_return = 0.8 / 100  # 月均0.8%
    strategy_B_monthly_std = 4.5 / 100     # 月波动4.5%
    
    print("\n不年化的比较（错误❌）：")
    print(f"策略A: 日收益{strategy_A_daily_return*100:.3f}%, 日波动{strategy_A_daily_std*100:.1f}%")
    print(f"策略B: 月收益{strategy_B_monthly_return*100:.3f}%, 月波动{strategy_B_monthly_std*100:.1f}%")
    print("看起来策略B更好？")
    
    print("\n年化后的比较（正确✓）：")
    A_annual_return = strategy_A_daily_return * 252
    A_annual_std = strategy_A_daily_std * np.sqrt(252)
    A_sharpe = A_annual_return / A_annual_std
    
    B_annual_return = strategy_B_monthly_return * 12
    B_annual_std = strategy_B_monthly_std * np.sqrt(12)
    B_sharpe = B_annual_return / B_annual_std
    
    print(f"策略A: 年化收益{A_annual_return*100:.1f}%, 年化波动{A_annual_std*100:.1f}%, 夏普{A_sharpe:.2f}")
    print(f"策略B: 年化收益{B_annual_return*100:.1f}%, 年化波动{B_annual_std*100:.1f}%, 夏普{B_sharpe:.2f}")
    print(f"实际上策略A更好！")


def visualize_annualization():
    """可视化年化效果"""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. 波动率随时间增长
    ax = axes[0, 0]
    days = np.arange(1, 253)
    daily_vol = 0.02
    annualized_vol = daily_vol * np.sqrt(days)
    
    ax.plot(days, annualized_vol * 100, 'b-', linewidth=2)
    ax.axhline(y=daily_vol*100, color='r', linestyle='--', label=f'日波动率={daily_vol*100:.1f}%')
    ax.axhline(y=daily_vol*np.sqrt(252)*100, color='g', linestyle='--', label=f'年化波动率={daily_vol*np.sqrt(252)*100:.1f}%')
    ax.set_xlabel('天数')
    ax.set_ylabel('累积波动率 (%)')
    ax.set_title('波动率的时间累积效应')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. 不同频率数据的年化
    ax = axes[0, 1]
    frequencies = ['日', '周', '月', '季', '年']
    periods = [252, 52, 12, 4, 1]
    raw_stds = [2, 4.5, 9, 18, 32]  # 原始标准差
    annualized_stds = [raw_stds[i] * np.sqrt(periods[i]) for i in range(len(periods))]
    
    x = np.arange(len(frequencies))
    width = 0.35
    
    ax.bar(x - width/2, raw_stds, width, label='原始波动率', color='skyblue')
    ax.bar(x + width/2, annualized_stds, width, label='年化波动率', color='orange')
    ax.set_xlabel('数据频率')
    ax.set_ylabel('波动率 (%)')
    ax.set_title('不同频率数据的年化对比')
    ax.set_xticks(x)
    ax.set_xticklabels(frequencies)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. 收益的时间累积
    ax = axes[1, 0]
    np.random.seed(42)
    daily_returns = np.random.normal(0.001, 0.02, 252)
    cumulative_returns = np.cumprod(1 + daily_returns)
    
    ax.plot(cumulative_returns, 'b-', linewidth=2)
    ax.axhline(y=1, color='k', linestyle='--', alpha=0.5)
    
    # 标注年化收益
    final_return = cumulative_returns[-1]
    annual_return = final_return - 1
    ax.text(200, final_return, f'年化: {annual_return*100:.1f}%', fontsize=10, color='red')
    
    ax.set_xlabel('交易日')
    ax.set_ylabel('累积收益')
    ax.set_title('日收益的年度累积')
    ax.grid(True, alpha=0.3)
    
    # 4. 夏普比率的频率影响
    ax = axes[1, 1]
    
    # 同一策略，不同采样频率
    true_annual_return = 0.10  # 10%
    true_annual_std = 0.15     # 15%
    true_sharpe = true_annual_return / true_annual_std
    
    frequencies = ['日', '周', '月', '季']
    periods = [252, 52, 12, 4]
    
    # 不同频率下的夏普比率（如果不年化）
    wrong_sharpes = [
        (true_annual_return / 252) / (true_annual_std / np.sqrt(252)),  # 日
        (true_annual_return / 52) / (true_annual_std / np.sqrt(52)),     # 周
        (true_annual_return / 12) / (true_annual_std / np.sqrt(12)),     # 月
        (true_annual_return / 4) / (true_annual_std / np.sqrt(4))        # 季
    ]
    
    # 正确的夏普比率（年化后都一样）
    correct_sharpes = [true_sharpe] * 4
    
    x = np.arange(len(frequencies))
    width = 0.35
    
    ax.bar(x - width/2, wrong_sharpes, width, label='未年化(错误)', color='red', alpha=0.7)
    ax.bar(x + width/2, correct_sharpes, width, label='年化后(正确)', color='green', alpha=0.7)
    ax.set_xlabel('数据频率')
    ax.set_ylabel('夏普比率')
    ax.set_title('年化对夏普比率计算的重要性')
    ax.set_xticks(x)
    ax.set_xticklabels(frequencies)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('年化的必要性可视化', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('annualization_visualization.png', dpi=100, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # 1. 解释为什么年化
    annualized_results = explain_annualization()
    
    # 2. 解释平方根规则
    actual, theoretical = explain_sqrt_rule()
    
    # 3. 实际例子
    practical_example()
    
    # 4. 可视化
    visualize_annualization()
    
    print("\n" + "=" * 60)
    print("总结：为什么要年化？")
    print("=" * 60)
    print("\n1. 📊 统一标准：不同频率数据可比")
    print("2. 📅 符合习惯：投资者按年度思考")
    print("3. 🏆 行业规范：基金业绩都是年化")
    print("4. ⚖️ 公平比较：高频/低频策略对比")
    print("5. 📈 风险评估：年化波动率更直观")