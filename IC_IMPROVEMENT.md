# IC (Information Coefficient) 改进说明

## 当前实现

在 `calculate_information_gain_multi_horizon` 方法中，`correlation` 实际上就是 IC：

```python
# 第343行
correlation = df['indicator'].corr(df['price_change'])
```

这计算的是：**指标值与未来收益率的相关性 = IC**

## IC 的两种类型

### 1. Pearson IC（当前使用）
- **公式**: `pearson_ic = corr(indicator, future_return)`
- **特点**: 
  - 衡量线性相关性
  - 对异常值敏感
  - 假设正态分布

### 2. Rank IC（推荐使用）
- **公式**: `rank_ic = spearman_corr(indicator, future_return)`
- **特点**:
  - 衡量单调相关性
  - 对异常值稳健
  - 不假设特定分布
  - 业界标准

## 建议的改进

```python
def calculate_information_gain_multi_horizon(self, ...):
    # ... 现有代码 ...
    
    # 计算两种IC
    pearson_ic = df['indicator'].corr(df['price_change'])  # Pearson IC
    
    from scipy import stats
    rank_ic, _ = stats.spearmanr(df['indicator'], df['price_change'])  # Rank IC
    
    results[horizon] = {
        'information_gain': ig,
        'normalized_mi': normalized_mi,
        'correlation': pearson_ic,  # 保持向后兼容
        'pearson_ic': pearson_ic,   # 明确命名
        'rank_ic': rank_ic,         # 添加Rank IC
        'ic': rank_ic,               # 默认使用Rank IC作为IC
        # ... 其他字段
    }
```

## 为什么 Rank IC 更好？

### 示例对比

假设有以下数据：

| 指标值 | 未来收益 |
|--------|----------|
| 100    | 5%       |
| 200    | 8%       |
| 300    | 10%      |
| 1000   | 11%      | ← 异常值

- **Pearson IC**: 可能被1000这个异常值拉低
- **Rank IC**: 只看排序关系，更稳健

### 实际应用

```python
# 因子评估标准
if abs(rank_ic) > 0.05:
    print("有效因子")
elif abs(rank_ic) > 0.03:
    print("弱因子")
else:
    print("无效因子")
```

## IC 的时间衰减

IC 通常随预测时间增长而衰减：

```
时间窗口  | 典型 IC 值
---------|----------
1天      | 0.05-0.10
7天      | 0.03-0.08
30天     | 0.02-0.05
90天     | 0.01-0.03
```

## 总结

1. **当前代码中的 `correlation` 确实是 IC**
2. **建议添加 Rank IC** 作为补充
3. **在报告中明确标注** 是 Pearson IC 还是 Rank IC
4. **优先使用 Rank IC** 进行因子质量评估