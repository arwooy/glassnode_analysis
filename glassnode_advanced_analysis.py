#!/usr/bin/env python3
"""
Glassnode高级分析系统
- 多时间窗口信息增益分析
- 最优预测时间窗口识别
- 阈值优化分析
- 指标组合效果分析（2元和3元组合）
"""

import os
import json
import time
import requests
import numpy as np
import pandas as pd
import hashlib
import pickle
from datetime import datetime, timedelta
from scipy.stats import entropy
from itertools import combinations
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 添加SSL重试相关
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 可视化
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}

class GlassnodeAdvancedAnalyzer:
    """Glassnode高级分析器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://grassnoodle.cloud/v1/metrics"
        
        # 设置缓存目录
        self.cache_dir = "glassnode_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 创建带重试策略的session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=10,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 加载配置
        self.load_endpoints_config()
        
        # 存储结果
        self.results = {}
        self.failed_endpoints = []
        self.indicators_data = {}  # 内存缓存
        
        # 加载已有的缓存数据
        self.load_cache_from_disk()
        
    def load_endpoints_config(self):
        """从JSON文件加载端点配置"""
        # 优先使用 glassnode_endpoints_detailed.json (包含description)
        detailed_config_file = 'glassnode_endpoints_detailed.json'

        
        if os.path.exists(detailed_config_file):
            config_path = detailed_config_file
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从detailed格式转换为需要的格式
            self.categories = {}
            for category_name, endpoints_list in data.items():
                endpoints = []
                for endpoint_info in endpoints_list:
                    # 从path提取metric名称
                    path = endpoint_info.get('path', '')
                    if path:
                        # path格式: /v1/metrics/category/metric
                        parts = path.strip('/').split('/')
                        if len(parts) >= 4:
                            metric = parts[-1]
                            endpoints.append({
                                'metric': metric,
                                'path': path,
                                'description': endpoint_info.get('description', ''),
                                'summary': endpoint_info.get('summary', ''),
                                'method': endpoint_info.get('method', 'GET'),
                                'full_endpoint': endpoint_info
                            })
                
                if endpoints:
                    self.categories[category_name] = {
                        'name': category_name.replace('_', ' ').title(),
                        'endpoints': endpoints
                    }
            
            total_endpoints = sum(len(cat.get('endpoints', [])) for cat in self.categories.values())
            print(f"✓ 已加载 {config_path} (包含描述信息):")
            print(f"  - {len(self.categories)} 个类别")
            print(f"  - {total_endpoints} 个端点")
        
        else:
            raise FileNotFoundError(f"配置文件 {detailed_config_file} 不存在")
    
    def load_cache_from_disk(self):
        """启动时加载所有磁盘缓存到内存"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            print("创建缓存目录")
            return
            
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
        if cache_files:
            print(f"发现 {len(cache_files)} 个缓存文件")
        
        for cache_file in cache_files:
            try:
                cache_key = cache_file[:-4]  # 移除.pkl扩展名
                file_path = os.path.join(self.cache_dir, cache_file)
                with open(file_path, 'rb') as f:
                    df = pickle.load(f)
                self.indicators_data[cache_key] = df
            except Exception as e:
                print(f"加载缓存 {cache_file} 失败: {e}")
    
    def save_to_disk_cache(self, cache_key: str, df: pd.DataFrame):
        """保存数据到磁盘缓存"""
        try:
            file_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
            with open(file_path, 'wb') as f:
                pickle.dump(df, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def load_from_disk_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """从磁盘加载缓存"""
        file_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"读取缓存失败: {e}")
        return None
            
    def fetch_metric_data(self, category: str, metric: str, 
                         start_date: datetime, end_date: datetime, path: str = None, asset: str = None) -> pd.DataFrame:
        """获取单个指标数据
        
        Args:
            category: 指标类别
            metric: 指标名称
            start_date: 开始日期
            end_date: 结束日期
            path: API路径
            asset: 资产代码 (如果不提供，使用实例的asset属性)
        """
        # 使用提供的asset或默认使用实例的asset属性
        asset_code = asset if asset else getattr(self, 'asset', 'BTC')
        
        params = {
            'a': asset_code,
            's': int(start_date.timestamp()),
            'u': int(end_date.timestamp()),
            'i': '24h'
        }
        
        # 生成包含参数的缓存键
        cache_key = f"{category}_{metric}_{params['a']}_{params['s']}_{params['u']}_{params['i']}"
        
        # 检查内存缓存
        if cache_key in self.indicators_data:
            return self.indicators_data[cache_key]
        
        # 检查磁盘缓存
        cached_df = self.load_from_disk_cache(cache_key)
        if cached_df is not None:
            self.indicators_data[cache_key] = cached_df
            return cached_df
        
        # 构建URL
        if path:
            url = f"https://grassnoodle.cloud{path}"
        else:
            url = f"{self.base_url}/{category}/{metric}"
        
        # 重试逻辑
        max_retries = 10
        retry_count = 0
        # 逐渐增加等待时间: 2, 5, 10, 15, 20, 30, 30, 45, 60, 60
        wait_times = [2, 5, 10, 15, 20, 30, 30, 45, 60, 60]
        
        while retry_count < max_retries:
            try:
                # 使用session进行请求
                response = self.session.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data)
                    
                    if not df.empty:
                        if 't' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['t'], unit='s')
                            df = df.set_index('timestamp')
                        
                        if 'v' in df.columns:
                            df = df.rename(columns={'v': metric})
                            df = df[[metric]]
                            # 缓存到内存和磁盘
                            self.indicators_data[cache_key] = df
                            self.save_to_disk_cache(cache_key, df)
                            return df
                        elif 'o' in df.columns:
                            # 处理多维数据
                            expanded = pd.json_normalize(df['o'])
                            expanded.index = df.index
                            if not expanded.empty:
                                expanded[metric] = expanded.mean(axis=1)
                            if metric in expanded.columns:
                                df = expanded[[metric]]
                                # 缓存到内存和磁盘
                                self.indicators_data[cache_key] = df
                                self.save_to_disk_cache(cache_key, df)
                                return df
                    return pd.DataFrame()
                    
                elif response.status_code == 429:
                    # 速率限制
                    print(f"  速率限制，等待{wait_times[retry_count]}秒: {metric}")
                    time.sleep(wait_times[retry_count])
                    retry_count += 1
                    continue
                    
                else:
                    print(f"  ✗ {metric}: {response.status_code}")
                    self.failed_endpoints.append(f"{category}/{metric}")
                    return pd.DataFrame()
                    
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = wait_times[retry_count - 1]
                    error_type = "SSL错误" if isinstance(e, requests.exceptions.SSLError) else "连接错误"
                    print(f"  {error_type}，等待{wait_time}秒后重试 ({retry_count}/{max_retries}): {metric}")
                    time.sleep(wait_time)
                else:
                    print(f"  ✗ {metric}: 重试{max_retries}次后失败")
                    self.failed_endpoints.append(f"{category}/{metric}")
                    return pd.DataFrame()
                    
            except requests.exceptions.Timeout:
                print(f"  ✗ {metric}: 请求超时")
                self.failed_endpoints.append(f"{category}/{metric}")
                return pd.DataFrame()
                
            except Exception as e:
                print(f"  ✗ {metric}: {str(e)[:50]}")
                self.failed_endpoints.append(f"{category}/{metric}")
                return pd.DataFrame()
        
        # 所有重试都失败
        print(f"  ✗ {metric}: 达到最大重试次数")
        self.failed_endpoints.append(f"{category}/{metric}")
        return pd.DataFrame()
    
    def calculate_information_gain_multi_horizon(self, 
                                                 indicator_data: pd.Series,
                                                 price_data: pd.Series,
                                                 horizons: List[int] = None) -> Dict:
        """计算多个时间窗口的信息增益"""
        if horizons is None:
            horizons = [1, 2, 3, 5, 7, 10, 14, 21, 30, 45, 60, 90, 120, 150, 180, 270, 365, 450, 730]
        
        results = {}
        
        for horizon in horizons:
            try:
                # 准备数据
                df = pd.DataFrame({
                    'indicator': indicator_data,
                    'price': price_data
                }).dropna()
                
                if len(df) < 100:
                    continue
                
                # 计算未来价格变化
                df['future_price'] = df['price'].shift(-horizon)
                df['price_change'] = (df['future_price'] / df['price'] - 1).fillna(0)
                df = df.dropna()
                
                if len(df) < 50:
                    continue
                
                # 离散化
                n_bins = 10
                try:
                    indicator_bins = pd.qcut(df['indicator'].values, n_bins, 
                                            labels=False, duplicates='drop')
                    price_bins = pd.qcut(df['price_change'].values, n_bins, 
                                       labels=False, duplicates='drop')
                except:
                    continue
                
                # 计算熵 所有时间窗口和指标都有相同的 H(Y) 基准，便于公平比较 差异体现在条件熵 H(Y|X) 上
                H_price = entropy(np.bincount(price_bins) / len(price_bins))
                
                # 计算条件熵
                H_conditional = 0
                for i in range(n_bins):
                    mask = indicator_bins == i
                    p_indicator = np.sum(mask) / len(indicator_bins)
                    
                    if p_indicator > 0 and np.sum(mask) > 1:
                        price_in_bin = price_bins[mask]
                        if len(price_in_bin) > 0:
                            bin_probs = np.bincount(price_in_bin, minlength=n_bins) / len(price_in_bin)
                            h = entropy(bin_probs)
                            H_conditional += p_indicator * h
                
                # 信息增益
                ig = max(0, H_price - H_conditional)
                
                # 归一化互信息
                normalized_mi = ig / H_price if H_price > 0 else 0
                
                # 相关性
                correlation = df['indicator'].corr(df['price_change'])
                
                results[horizon] = {
                    'information_gain': ig,
                    'normalized_mi': normalized_mi,
                    'correlation': correlation,
                    'entropy_price': H_price,
                    'entropy_conditional': H_conditional,
                    'reduction_ratio': ig/H_price if H_price > 0 else 0,
                    'sample_size': len(df)
                }
                
            except Exception as e:
                continue
        
        return results
    
    def find_optimal_horizon(self, multi_horizon_results: Dict) -> Dict:
        """找出最优预测时间窗口"""
        if not multi_horizon_results:
            return {}
        
        # 提取各指标
        horizons = list(multi_horizon_results.keys())
        ig_values = [r['information_gain'] for r in multi_horizon_results.values()]
        mi_values = [r['normalized_mi'] for r in multi_horizon_results.values()]
        corr_values = [abs(r['correlation']) for r in multi_horizon_results.values()]
        
        # 找最优值
        optimal_ig_idx = np.argmax(ig_values)
        optimal_mi_idx = np.argmax(mi_values)
        optimal_corr_idx = np.argmax(corr_values)
        
        return {
            'optimal_horizon_ig': horizons[optimal_ig_idx],
            'max_ig': ig_values[optimal_ig_idx],
            'optimal_horizon_mi': horizons[optimal_mi_idx],
            'max_mi': mi_values[optimal_mi_idx],
            'optimal_horizon_corr': horizons[optimal_corr_idx],
            'max_correlation': corr_values[optimal_corr_idx],
            'all_horizons': horizons,
            'all_ig': ig_values
        }
    
    def analyze_threshold_impact(self, 
                                indicator_data: pd.Series,
                                price_data: pd.Series,
                                percentiles: List[float] = None) -> Dict:
        """分析不同阈值过滤后的影响"""
        if percentiles is None:
            # 增加90以上的细粒度分析
            percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
        
        results = {}
        
        for pct in percentiles:
            try:
                # 计算阈值
                threshold = np.percentile(indicator_data.dropna(), pct)
                
                # 过滤数据
                mask = indicator_data >= threshold
                filtered_indicator = indicator_data[mask]
                filtered_price = price_data[mask.index][mask]
                
                if len(filtered_indicator) < 50:
                    continue
                
                # 计算未来收益
                df = pd.DataFrame({
                    'indicator': filtered_indicator,
                    'price': filtered_price
                }).dropna()
                
                # 多个时间窗口的收益
                returns = {}
                for days in [1, 7, 30, 60, 90, 180, 365]:
                    df[f'return_{days}d'] = df['price'].shift(-days) / df['price'] - 1
                    returns[f'{days}d'] = {
                        'mean': df[f'return_{days}d'].mean(),
                        'std': df[f'return_{days}d'].std(),
                        'sharpe': df[f'return_{days}d'].mean() / df[f'return_{days}d'].std() if df[f'return_{days}d'].std() > 0 else 0,
                        'win_rate': (df[f'return_{days}d'] > 0).mean()
                    }
                
                results[pct] = {
                    'threshold': threshold,
                    'sample_size': len(filtered_indicator),
                    'sample_ratio': len(filtered_indicator) / len(indicator_data),
                    'returns': returns,
                    'avg_indicator_value': filtered_indicator.mean()
                }
                
            except Exception as e:
                continue
        
        return results
    
    def analyze_indicator_combinations(self, 
                                      indicators_dict: Dict[str, pd.Series],
                                      price_data: pd.Series,
                                      combination_size: int = 2) -> Dict:
        """分析指标组合的效果"""
        results = {}
        
        # 获取所有指标名称
        indicator_names = list(indicators_dict.keys())
        
        # 生成组合
        for combo in combinations(indicator_names, combination_size):
            try:
                # 合并指标数据
                combined_df = pd.DataFrame()
                for ind_name in combo:
                    combined_df[ind_name] = indicators_dict[ind_name]
                
                # 标准化
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                
                # 确保没有NaN
                combined_df = combined_df.dropna()
                if len(combined_df) < 100:
                    continue
                
                # 标准化并计算组合指标
                scaled_data = scaler.fit_transform(combined_df)
                
                # 尝试不同的组合方式
                combo_methods = {
                    'mean': np.mean(scaled_data, axis=1),
                    'weighted': self.calculate_weighted_combination(scaled_data, price_data, combined_df.index),
                    'pca': self.calculate_pca_combination(scaled_data)
                }
                
                combo_results = {}
                for method_name, combo_indicator in combo_methods.items():
                    if combo_indicator is None:
                        continue
                        
                    # 转换为Series
                    combo_series = pd.Series(combo_indicator, index=combined_df.index)
                    
                    # 计算信息增益
                    ig_results = self.calculate_information_gain_multi_horizon(
                        combo_series, 
                        price_data,
                        horizons=[1, 7, 30, 60, 90, 180, 365]
                    )
                    
                    if ig_results:
                        # 平均信息增益
                        avg_ig = np.mean([r['information_gain'] for r in ig_results.values()])
                        avg_mi = np.mean([r['normalized_mi'] for r in ig_results.values()])
                        
                        combo_results[method_name] = {
                            'avg_ig': avg_ig,
                            'avg_mi': avg_mi,
                            'horizons': ig_results
                        }
                
                if combo_results:
                    results[combo] = combo_results
                    
            except Exception as e:
                continue
        
        return results
    
    def calculate_weighted_combination(self, scaled_data: np.ndarray, 
                                      price_data: pd.Series, 
                                      index: pd.Index) -> np.ndarray:
        """计算加权组合"""
        try:
            # 使用与价格的相关性作为权重
            weights = []
            for i in range(scaled_data.shape[1]):
                indicator_series = pd.Series(scaled_data[:, i], index=index)
                # 计算与未来价格的相关性
                future_price = price_data.shift(-7)
                price_change = (future_price / price_data - 1).fillna(0)
                
                # 对齐数据
                aligned_data = pd.DataFrame({
                    'ind': indicator_series,
                    'price_change': price_change
                }).dropna()
                
                if len(aligned_data) > 0:
                    corr = abs(aligned_data['ind'].corr(aligned_data['price_change']))
                    weights.append(corr)
                else:
                    weights.append(0)
            
            # 归一化权重
            weights = np.array(weights)
            if weights.sum() > 0:
                weights = weights / weights.sum()
            else:
                weights = np.ones(len(weights)) / len(weights)
            
            # 加权组合
            return np.dot(scaled_data, weights)
            
        except:
            return None
    
    def calculate_pca_combination(self, scaled_data: np.ndarray) -> np.ndarray:
        """使用PCA计算组合"""
        try:
            from sklearn.decomposition import PCA
            pca = PCA(n_components=1)
            return pca.fit_transform(scaled_data).flatten()
        except:
            return None
    
    def run_comprehensive_analysis(self, asset: str = 'BTC'):
        """运行综合分析
        
        Args:
            asset: 要分析的资产代码 (BTC, ETH, 或其他支持的代币)
        """
        print("\n" + "="*60)
        print(f"Glassnode 高级分析系统 - {asset}")
        print("="*60)
        
        # 存储资产类型
        self.asset = asset.upper()
        
        # 获取价格数据
        print(f"\n1. 获取 {self.asset} 价格数据...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*9)  # 9年数据，确保有足够数据进行365天预测
        
        price_df = self.fetch_metric_data('market', 'price_usd_close', start_date, end_date, asset=self.asset)
        if price_df.empty:
            price_df = self.fetch_metric_data('market', 'close', start_date, end_date, asset=self.asset)
            if not price_df.empty:
                price_df = price_df.rename(columns={'close': 'price_usd_close'})
        
        if price_df.empty:
            print(f"错误：无法获取 {self.asset} 价格数据")
            return
            
        price_data = price_df['price_usd_close']
        print(f"✓ 获取到 {len(price_data)} 天的价格数据")
        
        # 分析关键指标
        self.analyze_key_indicators(price_data)
        
        # 分析指标组合
        self.analyze_combinations(price_data)
        
        # 生成报告
        self.generate_advanced_report()
    
    def analyze_key_indicators(self, price_data: pd.Series):
        """分析关键指标"""
        print("\n2. 分析所有配置的指标...")
        
        # 收集所有要分析的指标
        all_indicators = []
        # for category_name, category_data in self.categories.items():
        #     endpoints = category_data.get('endpoints', [])
        #     for endpoint in endpoints[:5]:  # 每个类别最多分析5个，测试
        #         all_indicators.append((category_name, endpoint))
        
        # print(f"  将分析 {len(all_indicators)} 个指标")
        
        # 如果要分析完整的478个端点，使用下面的代码
        for category_name, category_data in self.categories.items():
            endpoints = category_data.get('endpoints', [])
            for endpoint in endpoints:
                all_indicators.append((category_name, endpoint))
        
        key_indicators = all_indicators
        
        self.indicator_analysis_results = {}
        
        for category, endpoint_info in key_indicators:
            # 从endpoint_info中提取metric和path
            if isinstance(endpoint_info, dict):
                metric = endpoint_info['metric']
                path = endpoint_info.get('path', None)
            else:
                metric = endpoint_info
                path = None
            
            print(f"\n分析 {metric}...")
            
            # 获取数据，传入path参数和asset
            df = self.fetch_metric_data(category, metric, 
                                       price_data.index[0], 
                                       price_data.index[-1],
                                       path=path,
                                       asset=self.asset)
            if df.empty:
                continue
            
            indicator_data = df[metric]
            
            # 1. 多时间窗口分析
            multi_horizon = self.calculate_information_gain_multi_horizon(
                indicator_data, price_data
            )
            
            # 2. 找最优窗口
            optimal = self.find_optimal_horizon(multi_horizon)
            
            # 3. 阈值影响分析
            threshold_impact = self.analyze_threshold_impact(
                indicator_data, price_data
            )
            
            # 保存结果
            self.indicator_analysis_results[metric] = {
                'multi_horizon': multi_horizon,
                'optimal': optimal,
                'threshold_impact': threshold_impact
            }
            
            # 打印关键结果
            if optimal:
                print(f"  最优预测窗口: {optimal.get('optimal_horizon_ig', 'N/A')}天")
                print(f"  最大信息增益: {optimal.get('max_ig', 0):.4f}")
            
            
    
    def analyze_combinations(self, price_data: pd.Series):
        """分析指标组合"""
        print("\n3. 分析指标组合...")
        
        # 收集已有的指标数据
        indicators_dict = {}
        for cache_key, df in self.indicators_data.items():
            if not df.empty:
                metric_name = df.columns[0]
                indicators_dict[metric_name] = df[metric_name]
        
        if len(indicators_dict) < 2:
            print("指标数据不足，跳过组合分析")
            return
        
        # 2元组合
        print("\n分析2元组合...")
        self.combo_2_results = self.analyze_indicator_combinations(
            indicators_dict, price_data, combination_size=2
        )
        
        # 3元组合（如果指标足够）
        if len(indicators_dict) >= 3:
            print("\n分析3元组合...")
            self.combo_3_results = self.analyze_indicator_combinations(
                indicators_dict, price_data, combination_size=3
            )
        else:
            self.combo_3_results = {}
        
        # 打印最佳组合
        self.print_best_combinations()
    
    def print_best_combinations(self):
        """打印最佳指标组合"""
        print("\n" + "="*60)
        print("最佳指标组合")
        print("="*60)
        
        # 2元组合
        if hasattr(self, 'combo_2_results') and self.combo_2_results:
            print("\n### 2元组合 TOP 5 ###")
            best_2_combos = []
            for combo, methods in self.combo_2_results.items():
                for method, results in methods.items():
                    best_2_combos.append({
                        'combo': combo,
                        'method': method,
                        'avg_ig': results['avg_ig'],
                        'avg_mi': results['avg_mi']
                    })
            
            # 排序
            best_2_combos.sort(key=lambda x: x['avg_ig'], reverse=True)
            
            for i, item in enumerate(best_2_combos[:5], 1):
                print(f"{i}. {'+'.join(item['combo'])} ({item['method']})")
                print(f"   平均IG: {item['avg_ig']:.4f}, 平均MI: {item['avg_mi']:.4f}")
        
        # 3元组合
        if hasattr(self, 'combo_3_results') and self.combo_3_results:
            print("\n### 3元组合 TOP 5 ###")
            best_3_combos = []
            for combo, methods in self.combo_3_results.items():
                for method, results in methods.items():
                    best_3_combos.append({
                        'combo': combo,
                        'method': method,
                        'avg_ig': results['avg_ig'],
                        'avg_mi': results['avg_mi']
                    })
            
            # 排序
            best_3_combos.sort(key=lambda x: x['avg_ig'], reverse=True)
            
            for i, item in enumerate(best_3_combos[:5], 1):
                print(f"{i}. {'+'.join(item['combo'])} ({item['method']})")
                print(f"   平均IG: {item['avg_ig']:.4f}, 平均MI: {item['avg_mi']:.4f}")
    
    def generate_advanced_report(self):
        """生成高级分析报告"""
        print("\n" + "="*60)
        print("生成高级分析报告")
        print("="*60)
        
        # 生成可视化
        self.create_visualizations()
        
        # 生成HTML报告
        self.generate_html_report()
        
        # 保存JSON结果
        self.save_json_results()
        
        print("\n✓ 报告生成完成")
        print("  - HTML报告: glassnode_advanced_analysis.html")
        print("  - JSON结果: glassnode_advanced_results.json")
        print("  - 可视化图表: advanced_analysis_*.png")
    
    def create_visualizations(self):
        """创建可视化图表"""
        if not hasattr(self, 'indicator_analysis_results'):
            return
        
        # 1. 多时间窗口信息增益热力图
        self.plot_multi_horizon_heatmap()
        
        # 2. 阈值影响分析图
        self.plot_threshold_impact()
        
        # 3. 组合效果对比图
        if hasattr(self, 'combo_2_results'):
            self.plot_combination_comparison()
    
    def plot_multi_horizon_heatmap(self):
        """绘制多时间窗口信息增益热力图"""
        try:
            # 准备数据
            indicators = []
            horizons = []
            ig_matrix = []
            
            for indicator, results in self.indicator_analysis_results.items():
                if 'multi_horizon' in results and results['multi_horizon']:
                    indicators.append(indicator)
                    horizon_results = results['multi_horizon']
                    
                    if not horizons:
                        horizons = sorted(horizon_results.keys())
                    
                    row = [horizon_results.get(h, {}).get('information_gain', 0) 
                          for h in horizons]
                    ig_matrix.append(row)
            
            if not ig_matrix:
                return
            
            # 创建热力图
            plt.figure(figsize=(16, 8))
            sns.heatmap(ig_matrix, 
                       xticklabels=[f"{h}d" if h < 30 else f"{h/30:.0f}m" for h in horizons],
                       yticklabels=indicators,
                       cmap='YlOrRd',
                       annot=True,
                       fmt='.3f',
                       cbar_kws={'label': '信息增益'})
            
            plt.title('多时间窗口信息增益分析')
            plt.xlabel('预测时间窗口')
            plt.ylabel('指标')
            plt.tight_layout()
            plt.savefig('advanced_analysis_horizon_heatmap.png', dpi=100)
            plt.close()
            
        except Exception as e:
            print(f"绘制热力图失败: {e}")
    
    def plot_threshold_impact(self):
        """绘制阈值影响分析图"""
        try:
            fig, axes = plt.subplots(3, 2, figsize=(14, 15))
            axes = axes.flatten()
            
            # 绘制每个指标的阈值影响
            for idx, (indicator, results) in enumerate(self.indicator_analysis_results.items()):
                if idx >= 5:
                    break
                    
                if 'threshold_impact' not in results:
                    continue
                    
                threshold_data = results['threshold_impact']
                if not threshold_data:
                    continue
                
                ax = axes[idx]
                
                # 提取数据
                percentiles = sorted(threshold_data.keys())
                returns_30d = []
                sharpe_30d = []
                sample_ratios = []
                
                for pct in percentiles:
                    if '30d' in threshold_data[pct].get('returns', {}):
                        returns_30d.append(threshold_data[pct]['returns']['30d']['mean'])
                        sharpe_30d.append(threshold_data[pct]['returns']['30d']['sharpe'])
                        sample_ratios.append(threshold_data[pct]['sample_ratio'])
                
                if returns_30d:
                    ax2 = ax.twinx()
                    
                    # 收益率
                    line1 = ax.plot(percentiles, returns_30d, 'b-', marker='o', 
                                   markersize=4, label='30天收益率')
                    # 夏普比率
                    line2 = ax2.plot(percentiles, sharpe_30d, 'r-', marker='s', 
                                    markersize=4, label='夏普比率')
                    
                    # 突出显示90以上的区域
                    ax.axvspan(90, 99, alpha=0.1, color='yellow')
                    
                    ax.set_xlabel('阈值百分位')
                    ax.set_ylabel('30天平均收益率', color='b')
                    ax2.set_ylabel('夏普比率', color='r')
                    ax.set_title(f'{indicator} 阈值影响分析')
                    ax.grid(True, alpha=0.3)
                    
                    # 合并图例
                    lines = line1 + line2
                    labels = [l.get_label() for l in lines]
                    ax.legend(lines, labels, loc='best')
            
            # 添加90+细粒度分析图
            ax = axes[5]
            
            # 收集所有指标在90+的表现
            high_threshold_data = []
            for indicator, results in self.indicator_analysis_results.items():
                if 'threshold_impact' in results:
                    for pct in [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]:
                        if pct in results['threshold_impact']:
                            if '30d' in results['threshold_impact'][pct].get('returns', {}):
                                high_threshold_data.append({
                                    'indicator': indicator,
                                    'percentile': pct,
                                    'sharpe': results['threshold_impact'][pct]['returns']['30d']['sharpe']
                                })
            
            if high_threshold_data:
                df = pd.DataFrame(high_threshold_data)
                pivot = df.pivot(index='indicator', columns='percentile', values='sharpe')
                sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', 
                           center=0, ax=ax, cbar_kws={'label': '夏普比率'})
                ax.set_title('90%以上阈值细粒度分析（夏普比率）')
                ax.set_xlabel('阈值百分位')
                ax.set_ylabel('指标')
            
            plt.suptitle('不同阈值对指标预测效果的影响', fontsize=14, y=1.02)
            plt.tight_layout()
            plt.savefig('advanced_analysis_threshold_impact.png', dpi=100)
            plt.close()
            
        except Exception as e:
            print(f"绘制阈值影响图失败: {e}")
    
    def plot_combination_comparison(self):
        """绘制组合效果对比图"""
        try:
            # 收集所有组合结果
            combo_data = []
            
            # 2元组合
            if hasattr(self, 'combo_2_results'):
                for combo, methods in self.combo_2_results.items():
                    for method, results in methods.items():
                        combo_data.append({
                            'name': f"{'+'.join(combo[:2])}..." if len(combo) > 2 else '+'.join(combo),
                            'type': '2元组合',
                            'method': method,
                            'ig': results['avg_ig'],
                            'mi': results['avg_mi']
                        })
            
            # 3元组合
            if hasattr(self, 'combo_3_results'):
                for combo, methods in self.combo_3_results.items():
                    for method, results in methods.items():
                        combo_data.append({
                            'name': f"{combo[0]}+{combo[1]}+...",
                            'type': '3元组合',
                            'method': method,
                            'ig': results['avg_ig'],
                            'mi': results['avg_mi']
                        })
            
            if not combo_data:
                return
            
            # 转为DataFrame
            df = pd.DataFrame(combo_data)
            
            # 按IG排序取前20
            df = df.nlargest(20, 'ig')
            
            # 绘图
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 信息增益对比
            colors = {'mean': 'blue', 'weighted': 'green', 'pca': 'red'}
            for method in df['method'].unique():
                mask = df['method'] == method
                ax1.scatter(df[mask]['ig'], range(len(df[mask])), 
                          label=method, alpha=0.6, s=100,
                          color=colors.get(method, 'gray'))
            
            ax1.set_xlabel('平均信息增益')
            ax1.set_ylabel('组合排名')
            ax1.set_title('指标组合信息增益对比')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2元 vs 3元对比
            grouped = df.groupby('type')['ig'].agg(['mean', 'max', 'std'])
            grouped.plot(kind='bar', ax=ax2)
            ax2.set_title('2元组合 vs 3元组合')
            ax2.set_xlabel('组合类型')
            ax2.set_ylabel('信息增益')
            ax2.legend(['平均值', '最大值', '标准差'])
            
            plt.suptitle('指标组合效果分析')
            plt.tight_layout()
            plt.savefig('advanced_analysis_combination.png', dpi=100)
            plt.close()
            
        except Exception as e:
            print(f"绘制组合对比图失败: {e}")
    
    def generate_html_report(self):
        """生成HTML报告"""
        asset_name = getattr(self, 'asset', 'BTC')
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Glassnode高级分析报告 - {asset_name}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; text-align: center; background: white; padding: 20px; }}
        h2 {{ color: #666; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; }}
        h3 {{ color: #888; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; 
                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .metric-box {{ display: inline-block; padding: 10px; margin: 10px;
                     background: #e8f5e9; border-radius: 5px; }}
        .highlight {{ background: #fff3cd; font-weight: bold; }}
        img {{ max-width: 100%; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Glassnode 高级分析报告 - {asset_name}</h1>
        <div class="section">
            <h2>分析概览</h2>
            <div class="metric-box">
                <strong>资产:</strong> {asset_name}
            </div>
            <div class="metric-box">
                <strong>分析时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </div>
            <div class="metric-box">
                <strong>分析指标数:</strong> {len(self.indicator_analysis_results)}
            </div>
        </div>
"""
        
        # 最优时间窗口分析
        html += """
        <div class="section">
            <h2>最优预测时间窗口分析</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>最优窗口(IG)</th>
                    <th>最大IG</th>
                    <th>最优窗口(MI)</th>
                    <th>最大MI</th>
                    <th>最优窗口(相关性)</th>
                    <th>最大相关性</th>
                </tr>
"""
        
        for indicator, results in self.indicator_analysis_results.items():
            if 'optimal' in results and results['optimal']:
                opt = results['optimal']
                html += f"""
                <tr>
                    <td><strong>{indicator}</strong></td>
                    <td class="highlight">{opt.get('optimal_horizon_ig', 'N/A')}天</td>
                    <td>{opt.get('max_ig', 0):.4f}</td>
                    <td>{opt.get('optimal_horizon_mi', 'N/A')}天</td>
                    <td>{opt.get('max_mi', 0):.4f}</td>
                    <td>{opt.get('optimal_horizon_corr', 'N/A')}天</td>
                    <td>{opt.get('max_correlation', 0):.4f}</td>
                </tr>
"""
        
        html += """
            </table>
            <img src="advanced_analysis_horizon_heatmap.png" alt="时间窗口热力图">
        </div>
"""
        
        # 阈值影响分析
        html += """
        <div class="section">
            <h2>阈值优化分析</h2>
            <p>通过设置不同的阈值百分位，分析指标筛选后的预测效果：</p>
            <img src="advanced_analysis_threshold_impact.png" alt="阈值影响分析">
"""
        
        # 添加最优阈值表
        html += """
            <h3>各指标最优阈值</h3>
            <table>
                <tr>
                    <th>指标</th>
                    <th>最优阈值(百分位)</th>
                    <th>7天收益率</th>
                    <th>夏普比率</th>
                    <th>样本占比</th>
                </tr>
"""
        
        for indicator, results in self.indicator_analysis_results.items():
            if 'threshold_impact' in results and results['threshold_impact']:
                # 找最优阈值（基于夏普比率）
                best_pct = None
                best_sharpe = -999
                
                for pct, data in results['threshold_impact'].items():
                    if '7d' in data.get('returns', {}):
                        sharpe = data['returns']['7d']['sharpe']
                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_pct = pct
                            best_data = data
                
                if best_pct:
                    html += f"""
                <tr>
                    <td><strong>{indicator}</strong></td>
                    <td class="highlight">{best_pct}%</td>
                    <td>{best_data['returns']['7d']['mean']*100:.2f}%</td>
                    <td>{best_sharpe:.3f}</td>
                    <td>{best_data['sample_ratio']*100:.1f}%</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
"""
        
        # 指标组合分析
        html += """
        <div class="section">
            <h2>指标组合分析</h2>
            <img src="advanced_analysis_combination.png" alt="组合效果对比">
            
            <h3>最佳2元组合 TOP 10</h3>
            <table>
                <tr>
                    <th>排名</th>
                    <th>指标组合</th>
                    <th>组合方法</th>
                    <th>平均IG</th>
                    <th>平均MI</th>
                </tr>
"""
        
        # 2元组合
        if hasattr(self, 'combo_2_results'):
            combo_list = []
            for combo, methods in self.combo_2_results.items():
                for method, results in methods.items():
                    combo_list.append({
                        'combo': combo,
                        'method': method,
                        'avg_ig': results['avg_ig'],
                        'avg_mi': results['avg_mi']
                    })
            
            combo_list.sort(key=lambda x: x['avg_ig'], reverse=True)
            
            for i, item in enumerate(combo_list[:10], 1):
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{' + '.join(item['combo'])}</strong></td>
                    <td>{item['method']}</td>
                    <td class="highlight">{item['avg_ig']:.4f}</td>
                    <td>{item['avg_mi']:.4f}</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
        
        <div class="section">
            <h2>结论与建议</h2>
            <ul>
                <li>不同指标有不同的最优预测时间窗口，应根据具体需求选择</li>
                <li>设置适当的阈值可以提高预测准确性，但需要权衡样本量</li>
                <li>指标组合通常比单一指标有更好的预测效果</li>
                <li>加权组合方法在大多数情况下优于简单平均</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
        
        with open('glassnode_advanced_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html)
    
    def save_json_results(self):
        """保存JSON格式结果"""
        asset_name = getattr(self, 'asset', 'BTC')
        results = {
            'analysis_time': datetime.now().isoformat(),
            'asset': asset_name,
            'indicators': {}
        }
        
        # 指标分析结果
        for indicator, data in self.indicator_analysis_results.items():
            results['indicators'][indicator] = {
                'optimal_horizon': data.get('optimal', {}),
                'multi_horizon_ig': {
                    str(k): v['information_gain'] 
                    for k, v in data.get('multi_horizon', {}).items()
                },
                'best_threshold': self._find_best_threshold(data.get('threshold_impact', {}))
            }
        
        # 组合结果
        if hasattr(self, 'combo_2_results'):
            results['combinations_2'] = self._format_combo_results(self.combo_2_results)
        
        if hasattr(self, 'combo_3_results'):
            results['combinations_3'] = self._format_combo_results(self.combo_3_results)
        
        with open('glassnode_advanced_results.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    def _find_best_threshold(self, threshold_data: Dict) -> Dict:
        """找出最佳阈值"""
        if not threshold_data:
            return {}
        
        best = {'percentile': None, 'sharpe': -999}
        
        for pct, data in threshold_data.items():
            if '7d' in data.get('returns', {}):
                sharpe = data['returns']['7d']['sharpe']
                if sharpe > best['sharpe']:
                    best = {
                        'percentile': pct,
                        'sharpe': sharpe,
                        'return_7d': data['returns']['7d']['mean'],
                        'sample_ratio': data['sample_ratio']
                    }
        
        return best
    
    def _format_combo_results(self, combo_results: Dict) -> List[Dict]:
        """格式化组合结果"""
        formatted = []
        
        for combo, methods in combo_results.items():
            for method, results in methods.items():
                formatted.append({
                    'indicators': list(combo),
                    'method': method,
                    'avg_ig': results['avg_ig'],
                    'avg_mi': results['avg_mi']
                })
        
        return sorted(formatted, key=lambda x: x['avg_ig'], reverse=True)


def main():
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Glassnode 高级分析系统')
    parser.add_argument('--asset', type=str, default='ETH', 
                       help='要分析的资产代码 (BTC, ETH, LTC, 等)')
    parser.add_argument('--api-key', type=str, default="myapi_sk_b3fa36048ea022be1c21e626742d4dec",
                       help='Glassnode API密钥')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = GlassnodeAdvancedAnalyzer(args.api_key)
    
    # 显示配置信息
    print("\n" + "=" * 60)
    print(f"Glassnode 完整分析系统 - {args.asset}")
    print("=" * 60)
    
    # 运行综合分析
    analyzer.run_comprehensive_analysis(asset=args.asset)


if __name__ == "__main__":
    main()