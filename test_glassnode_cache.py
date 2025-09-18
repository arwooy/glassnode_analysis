#!/usr/bin/env python3
"""测试Glassnode缓存功能"""

import os
import sys
from datetime import datetime, timedelta

# 导入分析器
from glassnode_advanced_analysis import GlassnodeAdvancedAnalyzer

def test_cache_functionality():
    """测试缓存功能"""
    print("="*60)
    print("测试 Glassnode 缓存功能")
    print("="*60)
    
    # API密钥
    api_key = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    
    # 创建分析器
    analyzer = GlassnodeAdvancedAnalyzer(api_key)
    
    # 测试获取少量数据
    print("\n测试获取数据（应该会缓存）...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 获取价格数据
    print("获取价格数据...")
    price_df = analyzer.fetch_metric_data('market', 'price_usd_close', start_date, end_date)
    
    if price_df.empty:
        print("尝试使用close作为指标名...")
        price_df = analyzer.fetch_metric_data('market', 'close', start_date, end_date)
    
    if not price_df.empty:
        print(f"✓ 成功获取 {len(price_df)} 条价格数据")
        print(f"  日期范围: {price_df.index[0]} 到 {price_df.index[-1]}")
    else:
        print("✗ 无法获取价格数据")
    
    # 检查缓存目录
    if os.path.exists(analyzer.cache_dir):
        cache_files = [f for f in os.listdir(analyzer.cache_dir) if f.endswith('.pkl')]
        print(f"\n缓存目录中有 {len(cache_files)} 个文件")
        for f in cache_files[:5]:  # 显示前5个
            print(f"  - {f}")
    
    # 测试从缓存加载
    print("\n创建新的分析器实例（应该从缓存加载）...")
    analyzer2 = GlassnodeAdvancedAnalyzer(api_key)
    
    # 再次获取相同数据（应该从缓存返回）
    print("\n再次获取相同数据（应该从缓存返回）...")
    price_df2 = analyzer2.fetch_metric_data('market', 'price_usd_close', start_date, end_date)
    
    if not price_df2.empty:
        print(f"✓ 从缓存获取了 {len(price_df2)} 条数据")
    
    print("\n✓ 缓存功能测试完成")

if __name__ == "__main__":
    test_cache_functionality()