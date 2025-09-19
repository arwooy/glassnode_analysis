#!/usr/bin/env python3
"""
跟踪误差（Tracking Error）解释和示例
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def explain_tracking_error():
    """用具体例子解释跟踪误差"""
    
    # 创建示例数据
    np.random.seed(42)
    days = 100
    dates = pd.date_range('2024-01-01', periods=days)
    
    # 基准收益（比如买入持有BTC）
    benchmark_returns = np.random.normal(0.002, 0.02, days)  # 日均0.2%，波动2%
    
    # 三种不同的策略
    # 策略1：稳定跑赢（低跟踪误差）
    strategy1_returns = benchmark_returns + np.random.normal(0.001, 0.005, days)
    
    # 策略2：不稳定跑赢（高跟踪误差）
    strategy2_returns = benchmark_returns + np.random.normal(0.001, 0.03, days)
    
    # 策略3：稳定跑输（低跟踪误差）
    strategy3_returns = benchmark_returns + np.random.normal(-0.0005, 0.005, days)
    
    # 计算超额收益
    excess1 = strategy1_returns - benchmark_returns
    excess2 = strategy2_returns - benchmark_returns
    excess3 = strategy3_returns - benchmark_returns
    
    # 计算跟踪误差（年化）
    tracking_error1 = np.std(excess1) * np.sqrt(252)
    tracking_error2 = np.std(excess2) * np.sqrt(252)
    tracking_error3 = np.std(excess3) * np.sqrt(252)
    
    # 计算信息比率
    avg_excess1 = np.mean(excess1) * 252  # 年化超额收益
    avg_excess2 = np.mean(excess2) * 252
    avg_excess3 = np.mean(excess3) * 252
    
    ir1 = avg_excess1 / tracking_error1
    ir2 = avg_excess2 / tracking_error2
    ir3 = avg_excess3 / tracking_error3
    
    print("=" * 60)
    print("跟踪误差（Tracking Error）解释")
    print("=" * 60)
    
    print("\n【什么是跟踪误差？】")
    print("跟踪误差 = 超额收益的标准差")
    print("它衡量策略偏离基准的稳定性")
    print("- 低跟踪误差 = 稳定地跟随或超越基准")
    print("- 高跟踪误差 = 时好时坏，不稳定")
    
    print("\n" + "=" * 60)
    print("三种策略对比")
    print("=" * 60)
    
    print("\n策略1：稳定跑赢（好）")
    print(f"  年化超额收益: {avg_excess1*100:.2f}%")
    print(f"  跟踪误差: {tracking_error1*100:.2f}%")
    print(f"  信息比率: {ir1:.2f}")
    print("  评价: ★★★★★ 优秀！稳定跑赢")
    
    print("\n策略2：不稳定跑赢（一般）")
    print(f"  年化超额收益: {avg_excess2*100:.2f}%")
    print(f"  跟踪误差: {tracking_error2*100:.2f}%")
    print(f"  信息比率: {ir2:.2f}")
    print("  评价: ★★★ 跑赢但不稳定")
    
    print("\n策略3：稳定跑输（差）")
    print(f"  年化超额收益: {avg_excess3*100:.2f}%")
    print(f"  跟踪误差: {tracking_error3*100:.2f}%")
    print(f"  信息比率: {ir3:.2f}")
    print("  评价: ★ 稳定但跑输")
    
    print("\n" + "=" * 60)
    print("信息比率的意义")
    print("=" * 60)
    print("\n信息比率 = 超额收益 / 跟踪误差")
    print("\n解读：")
    print("  IR > 1.0  : 优秀策略")
    print("  IR > 0.5  : 良好策略")
    print("  IR > 0    : 有价值")
    print("  IR < 0    : 跑输基准")
    
    print("\n为什么信息比率比夏普比率更好？")
    print("- 夏普比率看绝对收益的风险调整")
    print("- 信息比率看超额收益的风险调整")
    print("- 在牛市中，夏普比率可能都很高")
    print("- 但信息比率能区分谁真正创造了Alpha")
    
    # 可视化
    plot_tracking_error_visualization(
        dates, benchmark_returns, 
        strategy1_returns, strategy2_returns, strategy3_returns,
        tracking_error1, tracking_error2, tracking_error3
    )
    
    return {
        'strategy1': {'excess': avg_excess1, 'te': tracking_error1, 'ir': ir1},
        'strategy2': {'excess': avg_excess2, 'te': tracking_error2, 'ir': ir2},
        'strategy3': {'excess': avg_excess3, 'te': tracking_error3, 'ir': ir3}
    }


def plot_tracking_error_visualization(dates, benchmark, s1, s2, s3, te1, te2, te3):
    """可视化跟踪误差"""
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    
    # 累积收益对比
    cum_bench = (1 + benchmark).cumprod()
    cum_s1 = (1 + s1).cumprod()
    cum_s2 = (1 + s2).cumprod()
    cum_s3 = (1 + s3).cumprod()
    
    # 策略1
    ax = axes[0, 0]
    ax.plot(dates, cum_bench, label='基准', color='black', linewidth=2)
    ax.plot(dates, cum_s1, label='策略1', color='green', alpha=0.7)
    ax.set_title(f'策略1：稳定跑赢 (TE={te1*100:.1f}%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    excess1 = s1 - benchmark
    ax.plot(dates, excess1 * 100, color='green', alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.fill_between(dates, 0, excess1 * 100, color='green', alpha=0.3)
    ax.set_title('策略1 日超额收益（稳定）')
    ax.set_ylabel('超额收益 (%)')
    ax.grid(True, alpha=0.3)
    
    # 策略2
    ax = axes[1, 0]
    ax.plot(dates, cum_bench, label='基准', color='black', linewidth=2)
    ax.plot(dates, cum_s2, label='策略2', color='orange', alpha=0.7)
    ax.set_title(f'策略2：不稳定跑赢 (TE={te2*100:.1f}%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    excess2 = s2 - benchmark
    ax.plot(dates, excess2 * 100, color='orange', alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.fill_between(dates, 0, excess2 * 100, color='orange', alpha=0.3)
    ax.set_title('策略2 日超额收益（波动大）')
    ax.set_ylabel('超额收益 (%)')
    ax.grid(True, alpha=0.3)
    
    # 策略3
    ax = axes[2, 0]
    ax.plot(dates, cum_bench, label='基准', color='black', linewidth=2)
    ax.plot(dates, cum_s3, label='策略3', color='red', alpha=0.7)
    ax.set_title(f'策略3：稳定跑输 (TE={te3*100:.1f}%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    ax = axes[2, 1]
    excess3 = s3 - benchmark
    ax.plot(dates, excess3 * 100, color='red', alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.fill_between(dates, 0, excess3 * 100, color='red', alpha=0.3)
    ax.set_title('策略3 日超额收益（稳定但为负）')
    ax.set_ylabel('超额收益 (%)')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('跟踪误差（Tracking Error）可视化对比', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('tracking_error_visualization.png', dpi=100, bbox_inches='tight')
    plt.show()
    

def practical_example():
    """实际例子：计算真实的跟踪误差"""
    print("\n" + "=" * 60)
    print("实际例子：计算跟踪误差")
    print("=" * 60)
    
    # 模拟真实数据
    dates = pd.date_range('2023-01-01', '2023-12-31')
    
    # 基准（BTC买入持有）日收益
    btc_returns = np.array([0.02, -0.03, 0.01, 0.04, -0.02, 0.03, -0.01, 0.02, 0.00, -0.01])
    
    # 策略收益
    strategy_returns = np.array([0.03, -0.02, 0.02, 0.05, -0.03, 0.04, 0.00, 0.01, 0.01, -0.02])
    
    # 计算超额收益
    excess_returns = strategy_returns - btc_returns
    
    print("\n日收益数据（前10天）：")
    print("-" * 40)
    print("日期  | BTC收益 | 策略收益 | 超额收益")
    print("-" * 40)
    
    for i in range(10):
        print(f"Day {i+1:2} | {btc_returns[i]:7.2%} | {strategy_returns[i]:8.2%} | {excess_returns[i]:8.2%}")
    
    # 计算指标
    avg_excess = np.mean(excess_returns)
    tracking_error_daily = np.std(excess_returns)
    tracking_error_annual = tracking_error_daily * np.sqrt(252)
    
    avg_excess_annual = avg_excess * 252
    information_ratio = avg_excess_annual / tracking_error_annual
    
    print("\n计算结果：")
    print("-" * 40)
    print(f"平均日超额收益: {avg_excess:.4%}")
    print(f"超额收益标准差（日）: {tracking_error_daily:.4%}")
    print(f"跟踪误差（年化）: {tracking_error_annual:.2%}")
    print(f"年化超额收益: {avg_excess_annual:.2%}")
    print(f"信息比率: {information_ratio:.2f}")
    
    print("\n解释：")
    if tracking_error_annual < 0.05:
        print("✓ 低跟踪误差（<5%）：策略非常稳定地跟随基准")
    elif tracking_error_annual < 0.15:
        print("✓ 中等跟踪误差（5-15%）：策略有一定偏离但可控")
    else:
        print("⚠ 高跟踪误差（>15%）：策略偏离基准较大，风险较高")
    
    if information_ratio > 0.5:
        print("✓ 良好的信息比率（>0.5）：风险调整后的超额收益不错")
    elif information_ratio > 0:
        print("→ 正信息比率：有一定价值但可以改进")
    else:
        print("✗ 负信息比率：跑输基准")


if __name__ == "__main__":
    # 运行解释
    results = explain_tracking_error()
    
    # 实际例子
    practical_example()
    
    print("\n" + "=" * 60)
    print("关键要点")
    print("=" * 60)
    print("\n1. 跟踪误差 = 超额收益的波动性")
    print("2. 低跟踪误差 = 稳定（好事，如果超额收益为正）")
    print("3. 信息比率 = 每单位跟踪误差获得的超额收益")
    print("4. IR > 0.5 被认为是好策略")
    print("5. IR > 1.0 是优秀策略（很难达到）")