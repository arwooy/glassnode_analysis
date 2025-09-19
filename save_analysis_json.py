#!/usr/bin/env python3
"""
独立的保存分析结果到JSON的函数
"""

import json
from datetime import datetime
import pandas as pd
import numpy as np


def convert_to_serializable(obj):
    """递归转换对象为可序列化格式"""
    if isinstance(obj, dict):
        return {str(k): convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, pd.Series):
        # 将 Series 转换为字典，索引转为字符串
        return {str(k): convert_to_serializable(v) for k, v in obj.to_dict().items()}
    elif isinstance(obj, pd.DataFrame):
        # 将 DataFrame 转换为字典
        return obj.to_dict(orient='index')
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


def save_analysis_results_to_json(asset: str, analysis_results: dict, output_filename: str = None):
    """
    保存分析结果到JSON文件
    
    Args:
        asset: 资产名称 (如 'BTC', 'ETH')
        analysis_results: 分析结果字典，应包含 'market' 和 'indicators' 两个主要键
        output_filename: 输出文件名（可选），如果不提供则自动生成
    
    Returns:
        str: 保存的文件名
    """
    # 生成文件名（包含资产和时间戳）
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"indicator_analysis_results_{asset}_{timestamp}.json"
    
    # 获取指标数据用于元数据统计
    indicators_data = analysis_results.get('indicators', {})
    
    # 准备要保存的数据
    results_to_save = {
        'metadata': {
            'asset': asset,
            'analysis_time': datetime.now().isoformat(),
            'total_indicators': len(indicators_data),
            'indicators_list': list(indicators_data.keys())
        },
        'market': convert_to_serializable(analysis_results.get('market', {})),
        'indicators': convert_to_serializable(indicators_data)
    }
    
    try:
        # 保存到 JSON 文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(results_to_save, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n✓ 完整分析结果已保存到: {output_filename}")
        
        # 打印摘要信息
        print(f"  - 资产: {asset}")
        print(f"  - 分析指标数: {len(indicators_data)}")
        
        # 统计各策略的最优表现
        best_long_indicators = []
        best_short_indicators = []
        
        for indicator, data in indicators_data.items():
            if 'threshold_impact' in data and data['threshold_impact']:
                # 找出该指标的最佳多头和空头策略
                for pct, pct_data in data['threshold_impact'].items():
                    strategies = pct_data.get('strategies', {})
                    
                    if 'long' in strategies:
                        ir = strategies['long']['relative_performance'].get('information_ratio', -999)
                        if ir > 0.5:  # IR > 0.5 认为是好策略
                            best_long_indicators.append((indicator, pct, ir))
                    
                    if 'short' in strategies:
                        ir = strategies['short']['relative_performance'].get('information_ratio', -999)
                        if ir > 0.5:
                            best_short_indicators.append((indicator, pct, ir))
        
        # 排序并打印前5个
        best_long_indicators.sort(key=lambda x: x[2], reverse=True)
        best_short_indicators.sort(key=lambda x: x[2], reverse=True)
        
        if best_long_indicators:
            print("\n  Top 5 多头策略指标:")
            for i, (indicator, pct, ir) in enumerate(best_long_indicators[:5], 1):
                print(f"    {i}. {indicator} (阈值{pct}%, IR={ir:.3f})")
        
        if best_short_indicators:
            print("\n  Top 5 空头策略指标:")
            for i, (indicator, pct, ir) in enumerate(best_short_indicators[:5], 1):
                print(f"    {i}. {indicator} (阈值{pct}%, IR={ir:.3f})")
        
        # 打印市场基准信息（如果存在）
        market_data = analysis_results.get('market', {})
        if 'benchmark_metrics' in market_data:
            print("\n  市场基准指标:")
            for strategy_type in ['long', 'short']:
                if strategy_type in market_data['benchmark_metrics']:
                    metrics = market_data['benchmark_metrics'][strategy_type]
                    print(f"    {strategy_type.upper()}:")
                    print(f"      年化收益: {metrics.get('annual_return', 0)*100:.2f}%")
                    print(f"      夏普比率: {metrics.get('sharpe_ratio', 0):.3f}")
                    print(f"      最大回撤: {metrics.get('max_drawdown', 0)*100:.2f}%")
        
        # 计算文件大小
        import os
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename) / (1024 * 1024)  # 转换为 MB
            print(f"\n  文件大小: {file_size:.2f} MB")
        
        return output_filename
        
    except Exception as e:
        print(f"\n✗ 保存分析结果失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_analysis_results_from_json(filename: str):
    """
    从JSON文件加载分析结果
    
    Args:
        filename: JSON文件名
    
    Returns:
        dict: 分析结果字典
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ 成功加载分析结果: {filename}")
        
        # 打印基本信息
        metadata = data.get('metadata', {})
        print(f"  - 资产: {metadata.get('asset', 'N/A')}")
        print(f"  - 分析时间: {metadata.get('analysis_time', 'N/A')}")
        print(f"  - 指标数量: {metadata.get('total_indicators', 0)}")
        
        return data
        
    except Exception as e:
        print(f"✗ 加载分析结果失败: {e}")
        return None

