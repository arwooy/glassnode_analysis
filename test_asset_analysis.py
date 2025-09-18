#!/usr/bin/env python3
"""测试不同资产的分析功能"""

import sys
from datetime import datetime, timedelta
from glassnode_advanced_analysis import GlassnodeAdvancedAnalyzer

def test_asset_analysis(asset='BTC'):
    """测试指定资产的分析"""
    print("=" * 60)
    print(f"测试 {asset} 分析功能")
    print("=" * 60)
    
    # API密钥
    api_key = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    
    # 创建分析器
    analyzer = GlassnodeAdvancedAnalyzer(api_key)
    
    # 设置asset属性
    analyzer.asset = asset
    
    # 测试获取价格数据
    print(f"\n获取 {asset} 价格数据...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    price_df = analyzer.fetch_metric_data('market', 'price_usd_close', start_date, end_date, asset=asset)
    
    if price_df.empty:
        price_df = analyzer.fetch_metric_data('market', 'close', start_date, end_date, asset=asset)
        if not price_df.empty:
            price_df = price_df.rename(columns={'close': 'price_usd_close'})
    
    if not price_df.empty:
        price_col = price_df.columns[0]
        print(f"✓ 成功获取 {len(price_df)} 天的价格数据")
        print(f"  最新价格: ${price_df[price_col].iloc[-1]:,.2f}")
        print(f"  日期范围: {price_df.index[0]} 到 {price_df.index[-1]}")
    else:
        print(f"✗ 无法获取 {asset} 价格数据")
        print("  注意：某些资产可能需要更高的API权限")
    
    # 测试获取其他指标
    print(f"\n测试获取 {asset} 的其他指标...")
    
    # 尝试获取活跃地址数
    active_df = analyzer.fetch_metric_data('addresses', 'active_count', start_date, end_date, asset=asset)
    
    if not active_df.empty:
        print(f"✓ 活跃地址数据: {len(active_df)} 天")
        active_col = active_df.columns[0]
        print(f"  最新值: {active_df[active_col].iloc[-1]:,.0f}")
    else:
        print(f"  活跃地址数据不可用")
    
    print(f"\n✓ {asset} 分析功能测试完成")

def main():
    """主函数"""
    # 获取命令行参数
    if len(sys.argv) > 1:
        asset = sys.argv[1].upper()
    else:
        asset = 'BTC'
    
    # 测试资产分析
    test_asset_analysis(asset)
    
    print("\n" + "=" * 60)
    print("使用示例:")
    print("  python test_asset_analysis.py BTC")
    print("  python test_asset_analysis.py ETH")
    print("  python test_asset_analysis.py LTC")
    print("\n运行完整分析:")
    print("  python glassnode_advanced_analysis.py --asset BTC")
    print("  python glassnode_advanced_analysis.py --asset ETH")
    print("=" * 60)

if __name__ == "__main__":
    main()