#!/usr/bin/env python3
"""测试加载 glassnode_endpoints_detailed.json"""

import json
from glassnode_advanced_analysis import GlassnodeAdvancedAnalyzer

def test_detailed_config():
    """测试详细配置加载"""
    print("="*60)
    print("测试 glassnode_endpoints_detailed.json 加载")
    print("="*60)
    
    # 创建分析器
    api_key = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    analyzer = GlassnodeAdvancedAnalyzer(api_key)
    
    # 显示一些端点的详细信息
    print("\n显示部分端点的详细信息:")
    print("-"*60)
    
    for category_name, category_data in list(analyzer.categories.items())[:3]:  # 前3个类别
        print(f"\n类别: {category_name}")
        endpoints = category_data.get('endpoints', [])
        
        for endpoint in endpoints[:2]:  # 每个类别显示2个端点
            print(f"\n  Metric: {endpoint['metric']}")
            print(f"  Path: {endpoint['path']}")
            print(f"  Summary: {endpoint.get('summary', 'N/A')[:100]}")
            
            description = endpoint.get('description', '')
            if description:
                # 截取前200个字符
                desc_preview = description[:200] + "..." if len(description) > 200 else description
                # 清理换行符
                desc_preview = desc_preview.replace('\n', ' ').replace('\r', '')
                print(f"  Description: {desc_preview}")
            else:
                print(f"  Description: N/A")
    
    print("\n" + "="*60)
    print("✓ 详细配置加载成功！")
    print(f"  包含描述信息的端点可以提供更好的文档和理解")
    print("="*60)

if __name__ == "__main__":
    test_detailed_config()