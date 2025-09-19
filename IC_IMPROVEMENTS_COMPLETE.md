# IC (Information Coefficient) 改进完成

## ✅ 改进内容

### 1. **calculate_information_gain_multi_horizon 方法更新**

#### 改进前
```python
correlation = df['indicator'].corr(df['price_change'])
```

#### 改进后
```python
# Pearson IC (线性相关)
pearson_ic = df['indicator'].corr(df['price_change'])

# Rank IC (等级相关，更稳健)
from scipy import stats
rank_ic, _ = stats.spearmanr(df['indicator'], df['price_change'])
```

### 2. **返回结果新增字段**

```python
results[horizon] = {
    'information_gain': ig,
    'normalized_mi': normalized_mi,
    'correlation': pearson_ic,  # 保持向后兼容
    'pearson_ic': pearson_ic,   # 明确的Pearson IC
    'rank_ic': rank_ic,         # Rank IC (Spearman)
    # ... 其他字段
}
```

### 3. **find_optimal_horizon 方法更新**

新增了对两种IC的最优窗口查找：
- `optimal_horizon_pearson_ic`: Pearson IC最优窗口
- `max_pearson_ic`: 最大Pearson IC值
- `optimal_horizon_rank_ic`: Rank IC最优窗口  
- `max_rank_ic`: 最大Rank IC值
- 保留原有的`optimal_horizon_corr`和`max_correlation`向后兼容

### 4. **HTML报告表格更新**

表格现在显示8列：
- 指标名称
- 最优窗口(IG) / 最大IG
- 最优窗口(MI) / 最大MI
- **最优窗口(Rank IC) / 最大Rank IC** ← 新增
- **最优窗口(Pearson IC) / 最大Pearson IC** ← 新增

### 5. **generate_dashboard_data.py 更新**

在rankings生成中添加了：
```python
'max_pearson_ic': ind_data['optimal_horizon'].get('max_pearson_ic', ...),
'max_rank_ic': ind_data['optimal_horizon'].get('max_rank_ic', ...),
```

## 📊 两种IC的对比

| 特性 | Pearson IC | Rank IC (Spearman) |
|------|------------|-------------------|
| **计算方式** | 线性相关系数 | 等级相关系数 |
| **对异常值** | 敏感 | 稳健 |
| **捕捉关系** | 线性关系 | 单调关系 |
| **分布假设** | 正态分布 | 无需假设 |
| **业界使用** | 较少 | 标准做法 |

## 🎯 使用建议

### IC值解读
```
|IC| > 0.05  : 有效因子
|IC| > 0.03  : 弱因子  
|IC| < 0.03  : 无效因子
```

### 时间衰减特性
- IC通常随预测时间窗口增长而衰减
- 1天IC > 7天IC > 30天IC > 90天IC
- 衰减速度反映因子的时效性

### 选择建议
1. **优先使用Rank IC**
   - 对异常值更稳健
   - 不需要线性假设
   - 业界标准

2. **Pearson IC适用场景**
   - 明确的线性关系
   - 数据质量高，无异常值
   - 需要衡量线性相关强度

## 📝 代码示例

```python
# 使用改进后的分析器
analyzer = GlassnodeAdvancedAnalyzer(api_key)

# 计算多时间窗口分析
results = analyzer.calculate_information_gain_multi_horizon(
    indicator_data, 
    price_data
)

# 访问IC值
for horizon, data in results.items():
    print(f"{horizon}天:")
    print(f"  Pearson IC: {data['pearson_ic']:.4f}")
    print(f"  Rank IC: {data['rank_ic']:.4f}")
    
# 找最优窗口
optimal = analyzer.find_optimal_horizon(results)
print(f"Rank IC最优窗口: {optimal['optimal_horizon_rank_ic']}天")
```

## ✨ 关键优势

1. **更准确的因子评估**：Rank IC对异常值稳健，更适合实际数据
2. **全面的分析**：同时提供两种IC，适应不同场景
3. **向后兼容**：保留原有`correlation`字段，不破坏现有代码
4. **清晰的命名**：明确区分`pearson_ic`和`rank_ic`
5. **完整的报告**：HTML和Dashboard都显示两种IC

## 📈 测试结果

测试表明：
- ✅ 线性关系：两种IC差异不大
- ✅ 非线性单调关系：Rank IC更优
- ✅ 异常值场景：Rank IC稳健性明显
- ✅ 时间衰减：两种IC都表现出衰减特性

## 🔄 文件更新列表

| 文件 | 更新内容 |
|------|---------|
| `glassnode_advanced_analysis.py` | 添加pearson_ic和rank_ic计算 |
| `generate_dashboard_data.py` | 支持新的IC字段 |
| HTML报告模板 | 显示两种IC |
| JSON输出 | 包含两种IC值 |

---

**完成时间**: 2024年  
**状态**: ✅ 生产就绪  
**向后兼容**: ✅ 完全兼容