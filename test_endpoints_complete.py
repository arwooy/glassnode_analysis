#!/usr/bin/env python3
"""测试从glassnode_endpoints_complete.json加载端点"""

import json
from datetime import datetime, timedelta
from glassnode_advanced_analysis import GlassnodeAdvancedAnalyzer

def test_endpoints_loading():
    """测试端点加载"""
    print("="*60)
    print("测试端点加载")
    print("="*60)
    
    # 创建分析器
    api_key = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    analyzer = GlassnodeAdvancedAnalyzer(api_key)
    
    # 显示加载的类别和端点
    print("\n加载的类别:")
    for category_name, category_data in analyzer.categories.items():
        endpoints = category_data.get('endpoints', [])
        print(f"  {category_name}: {len(endpoints)} 个端点")
        
        # 显示前3个端点的详细信息
        for i, endpoint in enumerate(endpoints[:3]):
            if isinstance(endpoint, dict):
                metric = endpoint.get('metric', 'unknown')
                path = endpoint.get('path', 'no path')
                print(f"    - {metric}: {path}")
    
    # 测试获取一个带path的指标
    print("\n测试获取指标数据...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # 从addresses类别获取第一个指标
    if 'addresses' in analyzer.categories:
        endpoints = analyzer.categories['addresses']['endpoints']
        if endpoints and isinstance(endpoints[0], dict):
            first_endpoint = endpoints[0]
            metric = first_endpoint['metric']
            path = first_endpoint.get('path')
            
            print(f"\n获取 addresses/{metric}")
            print(f"  使用path: {path}")
            
            df = analyzer.fetch_metric_data('addresses', metric, start_date, end_date, path=path)
            
            if not df.empty:
                print(f"  ✓ 成功获取 {len(df)} 条数据")
            else:
                print("  ✗ 无法获取数据")
    
    print("\n✓ 测试完成")

if __name__ == "__main__":
    test_endpoints_loading()