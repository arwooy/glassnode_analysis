#!/usr/bin/env python3
"""
检查IC符号一致性
"""
import json
import numpy as np

# 读取数据
with open('indicator_analysis_results_ETH_20250919_162431.json', 'r') as f:
    data = json.load(f)

# 统计符号一致性
total = 0
same_sign = 0
diff_sign = 0
examples = []

if 'indicators' in data:
    for indicator_name, indicator_data in data['indicators'].items():
        if 'optimal' in indicator_data:
            optimal = indicator_data['optimal']
            pearson_ic = optimal.get('max_pearson_ic', 0)
            rank_ic = optimal.get('max_rank_ic', 0)
            
            if pearson_ic is not None and rank_ic is not None and pearson_ic != 0 and rank_ic != 0:
                total += 1
                if pearson_ic * rank_ic > 0:  # 同号
                    same_sign += 1
                else:  # 异号
                    diff_sign += 1
                    if len(examples) < 10:
                        examples.append({
                            'indicator': indicator_name,
                            'pearson_ic': pearson_ic,
                            'rank_ic': rank_ic,
                            'pearson_horizon': optimal.get('optimal_horizon_pearson_ic'),
                            'rank_horizon': optimal.get('optimal_horizon_rank_ic')
                        })

print(f'统计结果:')
print(f'总指标数: {total}')
print(f'符号相同: {same_sign} ({same_sign/total*100:.1f}%)')
print(f'符号不同: {diff_sign} ({diff_sign/total*100:.1f}%)')

print(f'\n符号不同的例子:')
for i, ex in enumerate(examples, 1):
    print(f'{i}. {ex["indicator"][:40]:<40} | Pearson: {ex["pearson_ic"]:+.4f} ({ex["pearson_horizon"]}d) | Rank: {ex["rank_ic"]:+.4f} ({ex["rank_horizon"]}d)')

# 检查某个具体指标的所有时间窗口
print("\n\n检查一个指标的所有时间窗口:")
example_indicator = examples[0]['indicator'] if examples else list(data['indicators'].keys())[0]
if example_indicator in data['indicators']:
    if 'multi_horizon' in data['indicators'][example_indicator]:
        multi_horizon = data['indicators'][example_indicator]['multi_horizon']
        print(f"指标: {example_indicator}")
        print("时间窗口 | Pearson IC | Rank IC")
        print("-" * 40)
        for horizon, horizon_data in sorted(multi_horizon.items(), key=lambda x: int(x[0].replace('d', ''))):
            p_ic = horizon_data.get('pearson_ic', 0)
            r_ic = horizon_data.get('rank_ic', 0)
            print(f"{horizon:>5} | {p_ic:+.4f} | {r_ic:+.4f}")