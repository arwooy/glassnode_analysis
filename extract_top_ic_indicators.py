import json
import pandas as pd

# 读取JSON文件
with open('indicator_analysis_results_ETH_20250919_162431.json', 'r') as f:
    data = json.load(f)

# 提取indicators部分
indicators = data.get('indicators', {})

# 创建列表存储所有指标的IC信息
ic_results = []

for indicator_name, indicator_data in indicators.items():
    if 'optimal' in indicator_data:
        optimal_data = indicator_data['optimal']
        
        # 提取Pearson IC和Rank IC
        pearson_ic = optimal_data.get('max_pearson_ic', 0)
        rank_ic = optimal_data.get('max_rank_ic', 0)
        optimal_horizon_pearson = optimal_data.get('optimal_horizon_pearson_ic', 0)
        optimal_horizon_rank = optimal_data.get('optimal_horizon_rank_ic', 0)
        max_ig = optimal_data.get('max_ig', 0)
        max_mi = optimal_data.get('max_mi', 0)
        
        ic_results.append({
            'indicator': indicator_name,
            'max_rank_ic': rank_ic,
            'optimal_horizon_rank': optimal_horizon_rank,
            'max_pearson_ic': pearson_ic,
            'optimal_horizon_pearson': optimal_horizon_pearson,
            'max_ig': max_ig,
            'max_mi': max_mi
        })

# 转换为DataFrame
df = pd.DataFrame(ic_results)

# 按Rank IC排序，取前20
top20_by_rank_ic = df.nlargest(20, 'max_rank_ic')

print("=" * 80)
print("Top 20 指标 - 按 Rank IC (秩相关信息系数) 排序")
print("=" * 80)
print()

for i, (idx, row) in enumerate(top20_by_rank_ic.iterrows(), 1):
    print(f"排名 {i}:")
    print(f"  指标名称: {row['indicator']}")
    print(f"  最大 Rank IC: {row['max_rank_ic']:.6f}")
    print(f"  最优预测周期 (天): {row['optimal_horizon_rank']}")
    print(f"  最大 Pearson IC: {row['max_pearson_ic']:.6f}")
    print(f"  最优Pearson周期 (天): {row['optimal_horizon_pearson']}")
    print(f"  最大信息增益 (IG): {row['max_ig']:.6f}")
    print(f"  最大互信息 (MI): {row['max_mi']:.6f}")
    print("-" * 40)

# 保存结果到CSV
top20_by_rank_ic.to_csv('top20_rank_ic_indicators.csv', index=False)
print("\n结果已保存到: top20_rank_ic_indicators.csv")

# 另外按Pearson IC排序
print("\n" + "=" * 80)
print("Top 20 指标 - 按 Pearson IC (线性相关信息系数) 排序")
print("=" * 80)
print()

top20_by_pearson_ic = df.nlargest(20, 'max_pearson_ic')
for i, (idx, row) in enumerate(top20_by_pearson_ic.iterrows(), 1):
    print(f"排名 {i}:")
    print(f"  指标名称: {row['indicator']}")
    print(f"  最大 Pearson IC: {row['max_pearson_ic']:.6f}")
    print(f"  最优预测周期 (天): {row['optimal_horizon_pearson']}")
    print(f"  最大 Rank IC: {row['max_rank_ic']:.6f}")
    print("-" * 40)

# 保存Pearson IC结果
top20_by_pearson_ic.to_csv('top20_pearson_ic_indicators.csv', index=False)

# 按信息增益排序
print("\n" + "=" * 80)
print("Top 20 指标 - 按信息增益 (Information Gain) 排序")
print("=" * 80)
print()

top20_by_ig = df.nlargest(20, 'max_ig')
for i, (idx, row) in enumerate(top20_by_ig.iterrows(), 1):
    print(f"排名 {i}:")
    print(f"  指标名称: {row['indicator']}")
    print(f"  最大信息增益 (IG): {row['max_ig']:.6f}")
    print(f"  最大互信息 (MI): {row['max_mi']:.6f}")
    print(f"  最大 Rank IC: {row['max_rank_ic']:.6f}")
    print(f"  最大 Pearson IC: {row['max_pearson_ic']:.6f}")
    print("-" * 40)

# 保存信息增益结果
top20_by_ig.to_csv('top20_information_gain_indicators.csv', index=False)
print("\n结果已保存到: top20_information_gain_indicators.csv")

# 按互信息排序
print("\n" + "=" * 80)
print("Top 20 指标 - 按互信息 (Mutual Information) 排序")
print("=" * 80)
print()

top20_by_mi = df.nlargest(20, 'max_mi')
for i, (idx, row) in enumerate(top20_by_mi.iterrows(), 1):
    print(f"排名 {i}:")
    print(f"  指标名称: {row['indicator']}")
    print(f"  最大互信息 (MI): {row['max_mi']:.6f}")
    print(f"  最大信息增益 (IG): {row['max_ig']:.6f}")
    print(f"  最大 Rank IC: {row['max_rank_ic']:.6f}")
    print("-" * 40)

# 保存互信息结果
top20_by_mi.to_csv('top20_mutual_information_indicators.csv', index=False)

# 统计信息
print("\n" + "=" * 80)
print("统计摘要")
print("=" * 80)
print(f"总指标数量: {len(df)}")
print(f"Rank IC 范围: [{df['max_rank_ic'].min():.6f}, {df['max_rank_ic'].max():.6f}]")
print(f"Pearson IC 范围: [{df['max_pearson_ic'].min():.6f}, {df['max_pearson_ic'].max():.6f}]")
print(f"信息增益范围: [{df['max_ig'].min():.6f}, {df['max_ig'].max():.6f}]")
print(f"互信息范围: [{df['max_mi'].min():.6f}, {df['max_mi'].max():.6f}]")
print(f"平均 Rank IC: {df['max_rank_ic'].mean():.6f}")
print(f"平均 Pearson IC: {df['max_pearson_ic'].mean():.6f}")
print(f"平均信息增益: {df['max_ig'].mean():.6f}")
print(f"平均互信息: {df['max_mi'].mean():.6f}")