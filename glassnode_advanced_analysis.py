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
from typing import Dict, List, Tuple, Optional
from multiprocessing import Pool, cpu_count
import traceback

# 导入独立的保存函数
from save_analysis_json import save_analysis_results_to_json
import warnings
from scipy import stats
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

def process_single_indicator_worker(args):
    """独立的处理函数，用于多进程池调用，在每个进程中创建新的分析器"""
    try:
        # 解包参数
        api_key, cache_dir, categories, asset, category, endpoint_info, price_data, market_regime, \
        full_regime_benchmarks, benchmark_returns_long, \
        benchmark_returns_short, only_cache = args
        
        # 在每个进程中创建一个新的分析器实例
        analyzer = GlassnodeAdvancedAnalyzer(api_key)
        analyzer.cache_dir = cache_dir
        analyzer.categories = categories  # 传递categories配置
        analyzer.asset = asset
        
        # 从endpoint_info中提取metric和path
        if isinstance(endpoint_info, dict):
            metric = endpoint_info['metric']
            path = endpoint_info.get('path', None)
        else:
            metric = endpoint_info
            path = None
        
        print(f"[进程 {os.getpid()}] 分析 {metric}...")
        
        # 获取数据
        df = analyzer.fetch_metric_data(category, metric, 
                                   price_data.index[0], 
                                   price_data.index[-1],
                                   path=path,
                                   asset=asset,
                                   only_cache=only_cache)
        if df.empty:
            return None
        
        indicator_data = df[metric]
        
        # 1. 多时间窗口分析
        multi_horizon = analyzer.calculate_information_gain_multi_horizon(
            indicator_data, price_data
        )
        
        # 2. 找最优窗口
        optimal = analyzer.find_optimal_horizon(multi_horizon)
        
        # 3. 阈值影响分析
        threshold_impact = analyzer.analyze_threshold_impact(
            indicator_data, price_data,
            market_regime=market_regime,
            full_regime_benchmarks=full_regime_benchmarks,
            benchmark_long=benchmark_returns_long,
            benchmark_short=benchmark_returns_short
        )
        
        # 返回结果
        result_dict = {
            'multi_horizon': multi_horizon,
            'optimal': optimal,
            'threshold_impact': threshold_impact
        }
        
        return (metric, result_dict)
        
    except Exception as e:
        metric_name = 'unknown'
        if 'metric' in locals():
            metric_name = metric
        print(f"[进程 {os.getpid()}] 处理 {metric_name} 时出错: {str(e)}")
        traceback.print_exc()
        return None

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
                         start_date: datetime, end_date: datetime, path: str = None, 
                         asset: str = None, only_cache: bool = False) -> pd.DataFrame:
        """获取单个指标数据
        
        Args:
            category: 指标类别
            metric: 指标名称
            start_date: 开始日期
            end_date: 结束日期
            path: API路径
            asset: 资产代码 (如果不提供，使用实例的asset属性)
            only_cache: 如果为True，只从缓存读取，不发起网络请求
        """
        # 使用提供的asset或默认使用实例的asset属性
        asset_code = asset if asset else getattr(self, 'asset', 'BTC')
        
        params = {
            'a': asset_code,
            's': int(start_date.timestamp()),
            'u': int(end_date.timestamp()),
            'i': '24h'
        }
        
        # 生成更易读的缓存键 (格式: category_metric_BTC_20230101_20250918_24h)
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        cache_key = f"{category}_{metric}_{asset_code}_{start_date_str}_{end_date_str}_{params['i']}"
        
        # 检查内存缓存
        if cache_key in self.indicators_data:
            return self.indicators_data[cache_key]
        
        # 检查磁盘缓存
        cached_df = self.load_from_disk_cache(cache_key)
        if cached_df is not None:
            self.indicators_data[cache_key] = cached_df
            return cached_df
        
        # 如果只使用缓存模式，缓存不存在时直接返回空DataFrame
        if only_cache:
            return pd.DataFrame()
        
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
                
                # IC (Information Coefficient) - 两种计算方式
                # Pearson IC (线性相关)
                pearson_ic = df['indicator'].corr(df['price_change'])
                
                # Rank IC (等级相关，更稳健)
                rank_ic, _ = stats.spearmanr(df['indicator'], df['price_change'])
                
                results[horizon] = {
                    'information_gain': ig,
                    'normalized_mi': normalized_mi,
                    'pearson_ic': pearson_ic,   # 明确的Pearson IC
                    'rank_ic': rank_ic,         # Rank IC (Spearman)
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
        
        # 提取IC值（保存原始值和绝对值）
        pearson_ic_values = []
        rank_ic_values = []
        pearson_ic_abs_values = []
        rank_ic_abs_values = []
        for r in multi_horizon_results.values():
            pearson = r.get('pearson_ic', r.get('correlation', 0))
            rank = r.get('rank_ic', r.get('pearson_ic', r.get('correlation', 0)))
            pearson_ic_values.append(pearson)
            rank_ic_values.append(rank)
            pearson_ic_abs_values.append(abs(pearson))
            rank_ic_abs_values.append(abs(rank))
        
        # 找最优值（基于绝对值）
        optimal_ig_idx = np.argmax(ig_values)
        optimal_mi_idx = np.argmax(mi_values)
        optimal_pearson_ic_idx = np.argmax(pearson_ic_abs_values)
        optimal_rank_ic_idx = np.argmax(rank_ic_abs_values)
        
        return {
            'optimal_horizon_ig': horizons[optimal_ig_idx],
            'max_ig': ig_values[optimal_ig_idx],
            'optimal_horizon_mi': horizons[optimal_mi_idx],
            'max_mi': mi_values[optimal_mi_idx],
            'optimal_horizon_pearson_ic': horizons[optimal_pearson_ic_idx],
            'max_pearson_ic': pearson_ic_values[optimal_pearson_ic_idx],  # 返回原始值，保留符号
            'optimal_horizon_rank_ic': horizons[optimal_rank_ic_idx],
            'max_rank_ic': rank_ic_values[optimal_rank_ic_idx],  # 返回原始值，保留符号
            'all_horizons': horizons,
            # 'all_ig': ig_values,
            # 'all_rank_ic': rank_ic_values,
            # 'all_pearson_ic': pearson_ic_values
        }
    
    def analyze_threshold_impact(self, 
                                indicator_data: pd.Series,
                                price_data: pd.Series,
                                percentiles: List[float] = None,
                                market_regime: pd.Series = None,
                                full_regime_benchmarks: Dict = None,
                                benchmark_long: pd.DataFrame = None,
                                benchmark_short: pd.DataFrame = None) -> Dict:
        """
        分析不同阈值过滤后的影响 - 改进版
        
        主要改进：
        1. 自动检测指标与收益的相关性方向（正相关/负相关）
        2. 与基准（买入持有）对比，计算超额收益
        3. 计算信息比率（Information Ratio）
        4. 市场状态分离（牛市/熊市/震荡市）
        """
        if percentiles is None:
            # 增加90以上的细粒度分析
            percentiles = [1,2,3,4,5,6,7,8,9,10, 20, 30, 40, 50, 60, 70, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
        
        results = {}
        
        # 检测相关性方向：计算指标与未来收益的相关性
        future_returns = price_data.pct_change(periods=7).shift(-7)  # 7天后的收益
        correlation = indicator_data.corr(future_returns)
        is_positive_correlation = correlation > 0
        
        for pct in percentiles:
            try:
                # 计算阈值
                threshold = np.percentile(indicator_data.dropna(), pct)
                
                # 根据相关性方向设置持有条件和策略类型
                # 计算反向阈值（用于空头策略）
                reverse_threshold = np.percentile(indicator_data.dropna(), 100 - pct)
                
                if is_positive_correlation:
                    # 正相关：指标高 -> 价格涨
                    long_mask = indicator_data >= threshold  # 高于阈值时做多
                    short_mask = indicator_data <= reverse_threshold  # 低于反向阈值时做空
                else:
                    # 负相关：指标高 -> 价格跌（如恐慌指数）
                    long_mask = indicator_data <= threshold  # 低于阈值时做多（逆向思维）
                    short_mask = indicator_data >= reverse_threshold  # 高于反向阈值时做空
                
                # 存储该阈值下两种策略的结果
                pct_results = {}
                
                # 测试两种策略：多头和空头
                for strategy_type in ['long', 'short']:
                    if strategy_type == 'long':
                        mask = long_mask
                        position_signal = mask.astype(int)  # 1=做多, 0=空仓
                    else:
                        mask = short_mask
                        position_signal = mask.astype(int) * -1  # -1=做空, 0=空仓
                    
                    if abs(mask.sum()) < 50:
                        continue
                    
                    # 计算策略收益
                    strategy_returns = self._calculate_strategy_returns(
                        price_data, 
                        position_signal,
                        indicator_data.index,
                        strategy_type=strategy_type
                    )
                    
                    # 使用预先计算的基准收益
                    strategy_benchmark = benchmark_long if strategy_type == 'long' else benchmark_short
                    
                    # 计算性能指标（包含超额收益和信息比率）
                    performance = self._calculate_performance_metrics(
                        strategy_returns,
                        strategy_benchmark,
                        position_signal
                    )
                    
                    # 计算信号的信息增益
                    # 信号分类：1=有信号，0=无信号
                    signal_binary = (position_signal != 0).astype(int)
                    
                    # 计算不同周期的信息增益
                    signal_ig_results = {}
                    for horizon in [1, 5, 10, 20, 30, 60, 120, 360, 720]:
                        try:
                            # 计算未来收益
                            if strategy_type == 'short':
                                # 做空策略：使用价格比率的倒数
                                # 价格从P1变到P2，做空收益 = 1/price_ratio - 1
                                future_prices = price_data.shift(-horizon)
                                price_ratio = future_prices / price_data
                                # 做空收益 = 1/price_ratio - 1
                                future_returns = (1 / price_ratio - 1).fillna(0)
                            else:
                                # 做多策略：正常的价格变化收益
                                future_returns = price_data.shift(-horizon).pct_change(horizon)
                            
                            # 将未来收益分为正负两类
                            returns_binary = (future_returns > 0).astype(int)
                            
                            # 对齐数据
                            valid_data = pd.DataFrame({
                                'signal': signal_binary,
                                'returns': returns_binary
                            }).dropna()
                            
                            if len(valid_data) > 50:
                                # 计算信息增益
                                # H(Y) - 未来收益的熵
                                p_positive = (valid_data['returns'] == 1).mean()
                                p_negative = 1 - p_positive
                                H_returns = -p_positive * np.log2(p_positive + 1e-10) - p_negative * np.log2(p_negative + 1e-10)
                                
                                # H(Y|X) - 给定信号的条件熵
                                H_conditional = 0
                                for signal_val in [0, 1]:
                                    mask = valid_data['signal'] == signal_val
                                    p_signal = mask.mean()
                                    
                                    if p_signal > 0 and mask.sum() > 10:
                                        subset = valid_data[mask]
                                        p_pos_given_signal = (subset['returns'] == 1).mean()
                                        p_neg_given_signal = 1 - p_pos_given_signal
                                        
                                        if p_pos_given_signal > 0 and p_neg_given_signal > 0:
                                            h_given = -p_pos_given_signal * np.log2(p_pos_given_signal) - p_neg_given_signal * np.log2(p_neg_given_signal)
                                            H_conditional += p_signal * h_given
                                
                                # 信息增益
                                ig = H_returns - H_conditional
                                
                                # 计算信号准确率
                                signal_mask = valid_data['signal'] == 1
                                if signal_mask.sum() > 0:
                                    accuracy = (valid_data[signal_mask]['returns'] == 1).mean()
                                else:
                                    accuracy = 0
                                
                                signal_ig_results[f'{horizon}d'] = {
                                    'information_gain': ig,
                                    'strategy_type': strategy_type,
                                    'correlation': correlation,
                                    'signal_accuracy': accuracy,
                                    'signal_count': signal_mask.sum(),
                                    'total_days': len(valid_data)
                                }
                        except Exception as e:
                            continue
                    
                    # 找出最优的时间窗口
                    best_horizon = None
                    best_ig = 0
                    best_accuracy = 0
                    best_signal_count = 0
                    best_total_days = 0
                    
                    for horizon_key, horizon_data in signal_ig_results.items():
                        ig = horizon_data.get('information_gain', 0)
                        if ig > best_ig:
                            best_ig = ig
                            best_horizon = horizon_key
                            best_accuracy = horizon_data.get('signal_accuracy', 0)
                            best_strategy_type = horizon_data.get('strategy_type', '')
                            best_signal_count = horizon_data.get('signal_count', 0)
                            best_total_days = horizon_data.get('total_days', 0)
                    
                    if not signal_ig_results:
                        signal_ig_results = {}
                    
                    # 分离不同市场状态下的表现（使用对应策略类型的基准）
                    regime_performance = self._calculate_regime_performance(
                        strategy_returns,
                        strategy_benchmark,
                        market_regime,
                        full_regime_benchmarks[strategy_type],  # 使用对应策略类型的基准
                        strategy_type=strategy_type
                    )
                    
                    # 计算综合评分
                    comprehensive_score = self._calculate_comprehensive_score(
                        performance, regime_performance
                    )
                    
                    # 存储该策略的结果
                    pct_results[strategy_type] = {
                        'strategy_type': strategy_type,  # 明确标记策略类型
                        'sample_size': abs(mask.sum()),
                        'sample_ratio': abs(mask.sum()) / len(indicator_data),
                        
                        # 绝对性能
                        'absolute_performance': {
                            'total_return': strategy_returns['cumulative'].iloc[-1] - 1 if len(strategy_returns['cumulative']) > 0 else 0,
                            'annual_return': strategy_returns['annual_return'],
                            'volatility': strategy_returns['volatility'],
                            'sharpe': performance['sharpe'],
                            'max_drawdown': performance['max_drawdown']
                        },
                        
                        # 相对性能（vs 基准）
                        'relative_performance': {
                            'excess_return': performance['excess_return'],
                            'information_ratio': performance['information_ratio'],
                            'alpha': performance['alpha'],
                            'beta': performance['beta'],
                            'tracking_error': performance['tracking_error'],
                            'win_rate_vs_benchmark': performance['win_rate_vs_benchmark']
                        },
                        
                        # 信号信息增益分析
                        'signal_ig_analysis': signal_ig_results,
                        
                        # 最优预测窗口
                        'optimal_horizon': {
                            'horizon': best_horizon,
                            'information_gain': best_ig,
                            'signal_accuracy': best_accuracy,
                            'strategy_type': best_strategy_type,
                            'signal_count': best_signal_count,
                            'total_days': best_total_days
                        } if best_horizon else None,
                        
                        # 市场状态下的表现
                        'regime_performance': regime_performance,
                        
                        # 综合评分
                        'comprehensive_scores': comprehensive_score
                    }
                
                # 如果有有效的策略结果，存储
                if pct_results:
                    results[pct] = {
                        'threshold': threshold,
                        'correlation_type': 'positive' if is_positive_correlation else 'negative',
                        'correlation_value': correlation,
                        'strategies': pct_results  # 包含long和short两种策略的结果
                    }
                
            except Exception as e:
                print(f"Error analyzing percentile {pct}: {e}")
                continue
        
        return results
    
    def _calculate_benchmark_returns(self, price_data: pd.Series, strategy_type: str = 'long') -> pd.DataFrame:
        """计算基准收益
        
        Args:
            price_data: 价格数据
            strategy_type: 'long' 为买入持有，'short' 为做空持有
        """
        import numpy as np
        
        if strategy_type == 'short':
            # 做空收益的正确计算方法
            # 如果价格从P1变到P2，做空收益 = (P1 - P2) / P1 = 1 - P2/P1
            # 但考虑到复利，我们使用倒数关系：
            # 做空收益 = 1/price_ratio - 1
            # 这确保了正确的对称性：价格跌50%（ratio=0.5），做空赚100%（1/0.5-1=1）
            
            # 计算价格比率（相对于初始价格）
            price_ratio = price_data / price_data.iloc[0]
            
            # 做空的累计收益：使用倒数关系
            # 如果价格变为原来的r倍，做空收益是1/r - 1
            # 例如：价格跌到0.5倍，做空收益 = 1/0.5 - 1 = 1 (100%)
            short_cumulative = 1 / price_ratio
            
            # 计算每日收益（从累计收益推导）
            benchmark_returns = short_cumulative.pct_change().fillna(0)
            cumulative_returns = short_cumulative
        else:
            # 多头基准：买入持有的收益
            returns = price_data.pct_change().fillna(0)
            benchmark_returns = returns
            cumulative_returns = (1 + benchmark_returns).cumprod()
        
        return pd.DataFrame({
            'daily': benchmark_returns,
            'cumulative': cumulative_returns,
            'strategy_type': strategy_type
        })
    
    def _calculate_full_regime_benchmarks(self, benchmark_returns: pd.DataFrame, 
                                          market_regime: pd.Series) -> Dict:
        """计算统一的市场状态基准收益（所有指标共享）"""
        full_regime_benchmarks = {}
        
        # 确保索引对齐
        common_index = benchmark_returns.index.intersection(market_regime.index)
        benchmark_aligned = benchmark_returns.loc[common_index]
        regime_aligned = market_regime.loc[common_index]
        
        # 获取策略类型
        strategy_type = benchmark_returns.get('strategy_type', 'long').iloc[0] if 'strategy_type' in benchmark_returns.columns else 'long'
        
        print(f"\n  统一市场状态基准收益 ({strategy_type.upper()}):")
        for regime_value, regime_name in [(1, 'bull'), (-1, 'bear'), (0, 'sideways')]:
            mask = regime_aligned == regime_value
            
            if mask.sum() > 0:
                # 使用完整的benchmark数据计算该市场状态的基准收益
                regime_benchmark_returns = benchmark_aligned.loc[mask, 'daily']
                
                # 计算最大回撤
                cumulative_returns = (1 + regime_benchmark_returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
                
                # 计算累计收益率
                cumulative_return = (1 + regime_benchmark_returns).prod() - 1 if len(regime_benchmark_returns) > 0 else 0
                
                # 计算年化收益率（使用几何平均）
                total_days = mask.sum()
                if total_days > 0 and cumulative_return > -1:
                    years = total_days / 365.25
                    # 使用复利公式计算年化收益率
                    annual_return = (1 + cumulative_return) ** (1/years) - 1 if years > 0 else 0
                else:
                    annual_return = 0
                
                # 计算年化波动率和夏普比率
                annual_volatility = regime_benchmark_returns.std() * np.sqrt(252) if len(regime_benchmark_returns) > 1 else 0
                sharpe = (annual_return - 0.02) / annual_volatility if annual_volatility > 0 else 0
                
                full_regime_benchmarks[regime_name] = {
                    'total_days': total_days,
                    'benchmark_annual_return': annual_return,
                    'benchmark_cumulative': cumulative_return,
                    'benchmark_annual_volatility': annual_volatility,
                    'benchmark_max_drawdown': max_drawdown,
                    'benchmark_sharpe': sharpe
                }
                
                # 打印基准信息
                print(f"    {regime_name:8s}: {full_regime_benchmarks[regime_name]['total_days']:4d}天, "
                      f"年化收益: {full_regime_benchmarks[regime_name]['benchmark_annual_return']:6.1f}%, "
                      f"累计收益: {full_regime_benchmarks[regime_name]['benchmark_cumulative']*100:6.1f}%, "
                      f"最大回撤: {full_regime_benchmarks[regime_name]['benchmark_max_drawdown']*100:6.1f}%")
        
        return full_regime_benchmarks
    
    def _calculate_market_metrics(self, 
                                 benchmark_returns_long: pd.DataFrame,
                                 benchmark_returns_short: pd.DataFrame,
                                 price_data: pd.Series) -> Dict:
        """
        计算市场基准的详细指标
        """
        market_metrics = {}
        
        for strategy_type, benchmark_returns in [('long', benchmark_returns_long), 
                                                 ('short', benchmark_returns_short)]:
            
            # 获取每日收益
            daily_returns = benchmark_returns['daily']
            
            # 计算累计收益
            cumulative_returns = (1 + daily_returns).cumprod()
            total_return = cumulative_returns.iloc[-1] - 1 if len(cumulative_returns) > 0 else 0
            
            # 年化收益
            n_days = len(daily_returns)
            annual_return = ((1 + total_return) ** (252 / n_days) - 1) if n_days > 0 else 0
            
            # 波动率（年化）
            volatility = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 1 else 0
            
            # 夏普比率
            risk_free_rate = 0.02  # 假设无风险利率为2%
            sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            # 最大回撤
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
            
            # 最大回撤持续时间
            drawdown_periods = []
            in_drawdown = False
            start_idx = 0
            
            for i in range(len(drawdown)):
                if drawdown.iloc[i] < 0 and not in_drawdown:
                    in_drawdown = True
                    start_idx = i
                elif drawdown.iloc[i] >= 0 and in_drawdown:
                    in_drawdown = False
                    drawdown_periods.append(i - start_idx)
            
            max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
            
            # 胜率（正收益天数比例）
            win_rate = (daily_returns > 0).mean() if len(daily_returns) > 0 else 0
            
            # 盈亏比
            winning_returns = daily_returns[daily_returns > 0]
            losing_returns = daily_returns[daily_returns < 0]
            avg_win = winning_returns.mean() if len(winning_returns) > 0 else 0
            avg_loss = abs(losing_returns.mean()) if len(losing_returns) > 0 else 1
            profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
            
            market_metrics[strategy_type] = {
                'total_return': total_return,
                'annual_return': annual_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'max_drawdown_duration': max_drawdown_duration,
                'win_rate': win_rate,
                'profit_loss_ratio': profit_loss_ratio,
                'total_days': n_days,
                'start_date': daily_returns.index[0].strftime('%Y-%m-%d') if len(daily_returns) > 0 else None,
                'end_date': daily_returns.index[-1].strftime('%Y-%m-%d') if len(daily_returns) > 0 else None
            }
            
            # 打印关键指标
            print(f"\n  市场基准指标 ({strategy_type.upper()}):")
            print(f"    年化收益: {annual_return*100:.2f}%")
            print(f"    波动率: {volatility*100:.2f}%")
            print(f"    夏普比率: {sharpe_ratio:.3f}")
            print(f"    最大回撤: {max_drawdown*100:.2f}%")
            print(f"    胜率: {win_rate*100:.1f}%")
        
        return market_metrics
    
    def _identify_market_regime(self, price_data: pd.Series, window: int = 50) -> pd.Series:
        """
        识别市场状态 - 基于实际价格走势
        Returns: pd.Series with 1=牛市, -1=熊市, 0=震荡
        """
        import pandas as pd
        import numpy as np
        
        # 计算不同周期的收益率
        returns_90d = (price_data / price_data.shift(90) - 1).fillna(0) * 100  # 90天收益率
        returns_180d = (price_data / price_data.shift(180) - 1).fillna(0) * 100  # 180天收益率
        returns_360d = (price_data / price_data.shift(360) - 1).fillna(0) * 100  # 360天收益率
        
        # 计算滚动最高价和最低价
        rolling_high = price_data.rolling(window=252, min_periods=50).max()
        rolling_low = price_data.rolling(window=252, min_periods=50).min()
        
        # 价格位置（0-100%，0是年度最低，100是年度最高）
        price_position = ((price_data - rolling_low) / (rolling_high - rolling_low) * 100).fillna(50)
        
        # 计算趋势得分（综合多个因素）
        trend_score = pd.Series(index=price_data.index, data=0.0)
        
        # 1. 中期趋势（90天收益率，权重30%）
        trend_score += np.where(returns_90d > 10, 0.3, 
                                np.where(returns_90d < -10, -0.3, returns_90d / 100 * 3))
        
        # 2. 长期趋势（180天收益率，权重40%）
        trend_score += np.where(returns_180d > 20, 0.4,
                                np.where(returns_180d < -20, -0.4, returns_180d / 100 * 2))
        
        # 3. 价格位置（权重30%）
        trend_score += (price_position - 50) / 100 * 0.3
        
        # 平滑处理
        smoothed_score = trend_score.rolling(window=30, center=True, min_periods=1).mean()
        
        # 初始化市场状态
        regime = pd.Series(index=price_data.index, data=0)
        
        # 根据综合得分判定市场状态
        # 牛市：得分为正且价格在中位以上
        regime[(smoothed_score > 0.2) & (price_position > 40)] = 1
        
        # 熊市：得分为负且价格在中位以下
        regime[(smoothed_score < -0.2) & (price_position < 60)] = -1
        
        # 震荡市：其他情况
        regime[((smoothed_score >= -0.2) & (smoothed_score <= 0.2)) | 
               ((price_position >= 40) & (price_position <= 60))] = 0
        
        # 填充NaN值
        regime = regime.fillna(0)
        
        # 使用较长的窗口进行最终平滑（减少碎片化）
        regime_smooth = regime.rolling(window=45, min_periods=1, center=True).apply(
            lambda x: 1 if x.mean() > 0.3 else (-1 if x.mean() < -0.3 else 0)
        )
        
        # 后处理：将短期趋势转为震荡市
        # 第一步：确保最小持续时间（至少45天）
        min_duration = 45
        result = regime_smooth.copy()
        
        # 第二步：识别所有片段
        segments = []
        current_state = result.iloc[0] if len(result) > 0 else 0
        segment_start = 0
        
        for i in range(1, len(result)):
            if result.iloc[i] != current_state:
                segments.append({
                    'start': segment_start,
                    'end': i - 1,
                    'state': current_state,
                    'duration': i - segment_start
                })
                current_state = result.iloc[i]
                segment_start = i
        
        # 添加最后一个片段
        if len(result) > 0:
            segments.append({
                'start': segment_start,
                'end': len(result) - 1,
                'state': current_state,
                'duration': len(result) - segment_start
            })
        
        # 第三步：将短期牛市或熊市改为震荡市
        for segment in segments:
            # 如果是牛市或熊市，且持续时间小于最小值，改为震荡市
            if segment['state'] != 0 and segment['duration'] < min_duration:
                result.iloc[segment['start']:segment['end']+1] = 0
        
        # 第四步：合并相邻的震荡市片段
        final_result = result.copy()
        i = 0
        while i < len(final_result) - 1:
            if final_result.iloc[i] == 0:
                # 找到震荡市的结束位置
                j = i
                while j < len(final_result) and final_result.iloc[j] == 0:
                    j += 1
                # 整个震荡市期间保持为0
                final_result.iloc[i:j] = 0
                i = j
            else:
                i += 1
        
        # 打印市场状态统计
        bull_days = (final_result == 1).sum()
        bear_days = (final_result == -1).sum()
        sideways_days = (final_result == 0).sum()
        total_days = len(final_result)
        
        print(f"\n  市场状态分布（最小持续{min_duration}天）:")
        print(f"    牛市: {bull_days}天 ({bull_days/total_days*100:.1f}%)")
        print(f"    熊市: {bear_days}天 ({bear_days/total_days*100:.1f}%)")
        print(f"    震荡市: {sideways_days}天 ({sideways_days/total_days*100:.1f}%)")
        
        return final_result
    
    def _plot_market_regime(self, price_data: pd.Series, market_regime: pd.Series):
        """
        可视化市场状态
        """
        print("\n  生成市场状态可视化图表...")
        
        # 创建图表
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        
        # 1. 价格走势与市场状态
        ax1 = axes[0]
        
        # 绘制价格线（使用对数坐标）
        ax1.plot(price_data.index, price_data.values, 'k-', alpha=0.7, linewidth=0.8, label='价格')
        
        # 添加移动平均线
        ma_20 = price_data.rolling(window=20, min_periods=20).mean()
        ma_50 = price_data.rolling(window=50, min_periods=50).mean()
        ma_200 = price_data.rolling(window=200, min_periods=200).mean()
        
        ax1.plot(price_data.index, ma_20, 'b-', alpha=0.5, linewidth=0.5, label='MA20')
        ax1.plot(price_data.index, ma_50, 'g-', alpha=0.5, linewidth=0.5, label='MA50')
        ax1.plot(price_data.index, ma_200, 'r-', alpha=0.5, linewidth=0.5, label='MA200')
        
        ax1.set_yscale('log')
        
        # 用不同颜色填充背景表示市场状态
        bull_mask = market_regime == 1
        bear_mask = market_regime == -1
        sideways_mask = market_regime == 0
        
        # 使用fill_between来创建背景色块
        y_min, y_max = ax1.get_ylim()
        ax1.fill_between(price_data.index, y_min, y_max, where=bull_mask, 
                         alpha=0.2, color='green', label='牛市')
        ax1.fill_between(price_data.index, y_min, y_max, where=bear_mask, 
                         alpha=0.2, color='red', label='熊市')
        ax1.fill_between(price_data.index, y_min, y_max, where=sideways_mask, 
                         alpha=0.2, color='gray', label='震荡市')
        
        ax1.set_title(f'{getattr(self, "asset", "BTC")} 价格走势与市场状态', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格 (对数坐标)')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. 市场状态分布（时间序列）
        ax2 = axes[1]
        
        # 创建阶梯图显示市场状态
        ax2.plot(market_regime.index, market_regime.values, drawstyle='steps-post', linewidth=1)
        ax2.fill_between(market_regime.index, 0, market_regime.values, 
                         where=(market_regime > 0), color='green', alpha=0.3, step='post')
        ax2.fill_between(market_regime.index, 0, market_regime.values, 
                         where=(market_regime < 0), color='red', alpha=0.3, step='post')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        ax2.set_title('市场状态时间序列', fontsize=12)
        ax2.set_ylabel('市场状态')
        ax2.set_yticks([-1, 0, 1])
        ax2.set_yticklabels(['熊市', '震荡', '牛市'])
        ax2.grid(True, alpha=0.3)
        
        # 3. 价格表现分析
        ax3 = axes[2]
        
        # 计算实际收益率
        returns_90d = (price_data / price_data.shift(90) - 1).fillna(0) * 100
        returns_180d = (price_data / price_data.shift(180) - 1).fillna(0) * 100
        
        # 计算价格位置
        rolling_high = price_data.rolling(window=252, min_periods=50).max()
        rolling_low = price_data.rolling(window=252, min_periods=50).min()
        price_position = ((price_data - rolling_low) / (rolling_high - rolling_low) * 100).fillna(50)
        
        # 创建双Y轴
        ax3_twin = ax3.twinx()
        
        # 左轴：收益率
        line1 = ax3.plot(price_data.index, returns_90d, 'b-', linewidth=0.8, alpha=0.7, label='90天收益率')
        line2 = ax3.plot(price_data.index, returns_180d, 'g-', linewidth=1, label='180天收益率')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax3.axhline(y=20, color='green', linestyle='--', alpha=0.3)
        ax3.axhline(y=-20, color='red', linestyle='--', alpha=0.3)
        
        # 右轴：价格位置
        line3 = ax3_twin.plot(price_data.index, price_position, 'orange', linewidth=0.8, alpha=0.6, label='价格位置')
        ax3_twin.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
        
        ax3.set_title('价格表现分析（基于此判定市场状态）', fontsize=12)
        ax3.set_ylabel('收益率 (%)', color='blue')
        ax3_twin.set_ylabel('价格位置 (0=年低, 100=年高)', color='orange')
        ax3.set_ylim(-60, 60)
        ax3_twin.set_ylim(0, 100)
        
        # 合并图例
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper left', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. 市场状态统计
        ax4 = axes[3]
        
        # 计算各状态的天数和占比
        regime_counts = market_regime.value_counts()
        regime_pct = regime_counts / len(market_regime) * 100
        
        # 创建饼图
        colors = {'牛市': 'green', '熊市': 'red', '震荡市': 'gray'}
        labels = []
        sizes = []
        pie_colors = []
        
        for value, name, color in [(1, '牛市', 'green'), (-1, '熊市', 'red'), (0, '震荡市', 'gray')]:
            if value in regime_counts.index:
                count = regime_counts[value]
                pct = regime_pct[value]
                labels.append(f'{name}\n{count}天 ({pct:.1f}%)')
                sizes.append(count)
                pie_colors.append(color)
        
        wedges, texts, autotexts = ax4.pie(sizes, labels=labels, colors=pie_colors, 
                                           autopct='%1.1f%%', startangle=90)
        
        # 调整文字大小
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax4.set_title('市场状态分布统计', fontsize=12)
        
        # 添加统计信息文本
        stats_text = f"""
        数据范围: {price_data.index[0].strftime('%Y-%m-%d')} 至 {price_data.index[-1].strftime('%Y-%m-%d')}
        总天数: {len(market_regime)}
        最新状态: {'牛市' if market_regime.iloc[-1] == 1 else '熊市' if market_regime.iloc[-1] == -1 else '震荡市'}
        """
        
        fig.text(0.95, 0.02, stats_text.strip(), ha='right', va='bottom', 
                fontsize=9, color='gray', style='italic')
        
        plt.tight_layout()
        plt.savefig('market_regime_analysis.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        print(f"    ✓ 市场状态图表已保存: market_regime_analysis.png")
        
        # 打印统计信息
        print(f"\n  市场状态统计:")
        for value, name in [(1, '牛市'), (-1, '熊市'), (0, '震荡市')]:
            if value in regime_counts.index:
                count = regime_counts[value]
                pct = regime_pct[value]
                print(f"    {name}: {count}天 ({pct:.1f}%)")
    
    def _calculate_strategy_returns(self, price_data: pd.Series, signal: pd.Series, 
                                   index_align: pd.Index, strategy_type: str = 'long') -> Dict:
        """计算策略收益
        
        Args:
            price_data: 价格数据
            signal: 交易信号 (1=做多, -1=做空, 0=空仓)
            index_align: 用于对齐的索引
            strategy_type: 策略类型 ('long' 或 'short')
        """
        # 对齐数据
        aligned_price = price_data.reindex(index_align).fillna(method='ffill')
        aligned_signal = signal.reindex(index_align).fillna(0)
        
        # 计算日收益率
        daily_returns = aligned_price.pct_change().fillna(0)
        
        # 策略收益计算
        # shift(1)避免前瞻偏差（今天的信号明天生效）
        shifted_signal = aligned_signal.shift(1).fillna(0)
        
        # 分别处理多头和空头位置
        long_positions = (shifted_signal == 1)  # 多头信号
        short_positions = (shifted_signal == -1)  # 空头信号
        
        # 初始化策略收益序列
        strategy_returns = pd.Series(index=aligned_price.index, data=0.0)
        
        # 多头收益：正常的价格变化收益
        strategy_returns[long_positions] = daily_returns[long_positions]
        
        # 空头收益：需要特殊处理以确保对称性
        # 使用价格比率方法计算空头收益
        if short_positions.any():
            # 找出所有空头持仓期间
            short_periods = []
            in_short = False
            start_idx = None
            
            for i, is_short in enumerate(short_positions):
                if is_short and not in_short:
                    # 开始做空
                    start_idx = i
                    in_short = True
                elif not is_short and in_short:
                    # 结束做空
                    short_periods.append((start_idx, i))
                    in_short = False
            
            # 如果最后仍在做空
            if in_short:
                short_periods.append((start_idx, len(short_positions)))
            
            # 计算每个做空期间的收益
            for start, end in short_periods:
                if start < len(aligned_price) and end <= len(aligned_price):
                    # 获取做空期间的价格
                    period_prices = aligned_price.iloc[start:end]
                    if len(period_prices) > 0:
                        # 计算相对于期初的价格比率
                        price_ratio = period_prices / period_prices.iloc[0]
                        # 做空收益 = 1/price_ratio - 1
                        # 但为了保持日收益率格式，我们计算每日收益
                        short_returns = (1 / price_ratio).pct_change().fillna(0)
                        strategy_returns.iloc[start:end] = short_returns
        
        # 累积收益
        cumulative_returns = (1 + strategy_returns).cumprod()
        
        # 年化收益和波动率
        # 使用几何平均计算年化收益率
        cumulative_return = cumulative_returns.iloc[-1] - 1 if len(cumulative_returns) > 0 else 0
        n_days = len(strategy_returns)
        annual_return = ((1 + cumulative_return) ** (252 / n_days) - 1) if n_days > 0 and cumulative_return > -1 else 0
        volatility = strategy_returns.std() * np.sqrt(252)
        
        return {
            'daily': strategy_returns,
            'cumulative': cumulative_returns,
            'annual_return': annual_return,
            'volatility': volatility,
            'strategy_type': strategy_type
        }
    
    def _calculate_performance_metrics(self, strategy_returns: Dict, 
                                      benchmark_returns: pd.DataFrame,
                                      signal: pd.Series) -> Dict:
        """计算性能指标（包括超额收益和信息比率）"""
        if not strategy_returns or 'daily' not in strategy_returns:
            return self._empty_performance_metrics()
        
        strategy_daily = strategy_returns['daily']
        benchmark_daily = benchmark_returns['daily']
        
        # 对齐数据
        aligned_data = pd.DataFrame({
            'strategy': strategy_daily,
            'benchmark': benchmark_daily
        }).dropna()
        
        if len(aligned_data) < 30:
            return self._empty_performance_metrics()
        
        # Sharpe Ratio
        sharpe = (aligned_data['strategy'].mean() / aligned_data['strategy'].std() * np.sqrt(252)) if aligned_data['strategy'].std() > 0 else 0
        
        # 最大回撤
        cumulative = (1 + aligned_data['strategy']).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 超额收益
        excess_returns = aligned_data['strategy'] - aligned_data['benchmark']
        # 年化超额收益：使用几何平均
        excess_cumulative = (1 + excess_returns).prod() - 1 if len(excess_returns) > 0 else 0
        n_days = len(excess_returns)
        excess_return = ((1 + excess_cumulative) ** (252 / n_days) - 1) if n_days > 0 and excess_cumulative > -1 else excess_returns.mean() * 252
        
        # 跟踪误差
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        # Information Ratio
        information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
        
        # Alpha 和 Beta (使用线性回归)
        try:
            from scipy import stats
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                aligned_data['benchmark'], 
                aligned_data['strategy']
            )
            beta = slope
            alpha = intercept * 252  # 年化
        except:
            # beta = 1
            # alpha = 0
            raise
                 
        # 相对于基准的胜率
        win_rate_vs_benchmark = (excess_returns > 0).mean()
        
        # 计算策略的胜率和盈亏比
        winning_days = aligned_data['strategy'] > 0
        losing_days = aligned_data['strategy'] < 0
        
        # 胜率：盈利天数 / 总交易天数
        win_rate = winning_days.sum() / (winning_days.sum() + losing_days.sum()) if (winning_days.sum() + losing_days.sum()) > 0 else 0
        
        # 平均盈利和平均亏损
        avg_win = aligned_data.loc[winning_days, 'strategy'].mean() if winning_days.sum() > 0 else 0
        avg_loss = abs(aligned_data.loc[losing_days, 'strategy'].mean()) if losing_days.sum() > 0 else 0
        
        # 盈亏比：平均盈利 / 平均亏损
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else float('inf') if avg_win > 0 else 0
        
        # 期望值（数学期望）
        expectancy = win_rate * avg_win - (1 - win_rate) * avg_loss if (winning_days.sum() + losing_days.sum()) > 0 else 0
        
        return {
            'sharpe': sharpe,
            'max_drawdown': max_drawdown,
            'excess_return': excess_return,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'alpha': alpha,
            'beta': beta,
            'win_rate_vs_benchmark': win_rate_vs_benchmark,
            'win_rate': win_rate,  # 策略胜率
            'profit_loss_ratio': profit_loss_ratio,  # 盈亏比
            'avg_win': avg_win * 252,  # 年化平均盈利
            'avg_loss': avg_loss * 252,  # 年化平均亏损
            'expectancy': expectancy * 252  # 年化期望值
        }
    
    def _empty_performance_metrics(self) -> Dict:
        """返回空的性能指标"""
        return {
            'sharpe': 0,
            'max_drawdown': 0,
            'excess_return': 0,
            'tracking_error': 0,
            'information_ratio': 0,
            'alpha': 0,
            'beta': 0,
            'win_rate_vs_benchmark': 0,
            'win_rate': 0,
            'profit_loss_ratio': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'expectancy': 0
        }
    
    def _calculate_regime_performance(self, strategy_returns: Dict,
                                     benchmark_returns: pd.DataFrame,
                                     market_regime: pd.Series,
                                     full_regime_benchmarks: Dict = None,
                                     strategy_type: str = 'long') -> Dict:
        """计算不同市场状态下的表现
        
        Args:
            strategy_returns: 策略收益
            benchmark_returns: 基准收益（根据策略类型已经调整过）
            market_regime: 市场状态
            full_regime_benchmarks: 统一的市场基准（可选）
            strategy_type: 策略类型 ('long' 或 'short')
        """
        if not strategy_returns or 'daily' not in strategy_returns:
            return {}
        
        # 计算策略表现（处理缺失值后）
        aligned_data = pd.DataFrame({
            'strategy': strategy_returns['daily'],
            'benchmark': benchmark_returns['daily'],
            'regime': market_regime
        }).dropna()
        
        if len(aligned_data) == 0:
            return {}
        
        # 第三步：组合结果 - 使用统一的基准收益
        regime_performance = {}
        
        for regime_value, regime_name in [(1, 'bull'), (-1, 'bear'), (0, 'sideways')]:
            mask = aligned_data['regime'] == regime_value
            
            if mask.sum() > 0 and regime_name in full_regime_benchmarks:
                strategy_regime = aligned_data.loc[mask, 'strategy']
                # 仍需要这个用于计算win_rate
                benchmark_regime = aligned_data.loc[mask, 'benchmark']
                
                # 使用统一的基准收益
                unified_benchmark = full_regime_benchmarks[regime_name]
                
                # 策略收益计算（使用几何平均）
                strategy_cumulative_return = (1 + strategy_regime).prod() - 1 if len(strategy_regime) > 0 else 0
                regime_days = len(strategy_regime)
                strategy_return = ((1 + strategy_cumulative_return) ** (252 / regime_days) - 1) if regime_days > 0 and strategy_cumulative_return > -1 else 0
                
                # 计算策略的最大回撤
                strategy_cumulative = (1 + strategy_regime).cumprod()
                strategy_running_max = strategy_cumulative.expanding().max()
                strategy_drawdown = (strategy_cumulative - strategy_running_max) / strategy_running_max
                strategy_max_drawdown = strategy_drawdown.min() if len(strategy_drawdown) > 0 else 0
                
                regime_performance[regime_name] = {
                    'days': unified_benchmark['total_days'],  # 使用完整数据的天数
                    'strategy_type': strategy_type,  # 策略类型
                    'strategy_return': strategy_return,
                    'benchmark_return': unified_benchmark.get('benchmark_annual_return'),  # 统一的基准（兼容旧字段名）
                    'benchmark_max_drawdown': unified_benchmark['benchmark_max_drawdown'],  # 基准的最大回撤
                    'excess_return': strategy_return - unified_benchmark.get('benchmark_annual_return'),
                    'excess_return_win_rate': (strategy_regime > benchmark_regime).mean() if len(strategy_regime) > 0 else 0,
                    'sharpe': (strategy_regime.mean() / strategy_regime.std() * np.sqrt(252)) if strategy_regime.std() > 0 else 0,
                    'strategy_max_drawdown': strategy_max_drawdown  # 策略的最大回撤
                }
        
        return regime_performance
    
    
    def _calculate_comprehensive_score(self, performance: Dict, 
                                      regime_performance: Dict) -> Dict:
        """计算各市场状态下的综合评分"""
        scores = {}
        
        # 整体评分
        overall_score = 0
        
        # 性能评分 (50%权重) - 原来40%，移除因子质量后调整
        perf_score = (
            max(0, performance['information_ratio']) * 20 +  # IR最重要
            max(0, performance['sharpe']) * 10 +
            max(0, performance['win_rate'] - 0.4) * 20 +  # 胜率（40%以上开始计分）
            max(0, performance['profit_loss_ratio'] - 1) * 10 +  # 盈亏比（1以上开始计分）
            (1 - abs(performance['max_drawdown'])) * 10
        )
        overall_score += perf_score * 0.5
        
        # 市场适应性评分 (50%权重) - 原来30%，调整为50%
        regime_score = 0
        for regime_name, regime_data in regime_performance.items():
            if regime_data['days'] > 0:
                # 每个市场状态的得分
                state_score = (
                    max(0, regime_data['excess_return'] / 10) * 5 +  # 超额收益
                    regime_data['excess_return_win_rate'] * 3 +  # 胜率
                    max(0, regime_data['sharpe']) * 2  # 夏普比率
                )
                
                scores[f'{regime_name}_score'] = min(100, state_score * 10)
                
                # 根据天数加权
                weight = regime_data['days'] / sum([r['days'] for r in regime_performance.values()])
                regime_score += state_score * weight
        
        overall_score += regime_score * 0.5
        
        scores['overall'] = min(100, overall_score)
        scores['performance_component'] = min(100, perf_score)
        scores['regime_component'] = min(100, regime_score * 10)
        
        return scores
    
    
    def run_comprehensive_analysis(self, asset: str = 'BTC', end_date: datetime = None, only_cache: bool = False, num_workers: int = 12):
        """运行综合分析
        
        Args:
            asset: 要分析的资产代码 (BTC, ETH, 或其他支持的代币)
            end_date: 分析的结束日期，默认为2025年9月18日
            only_cache: 如果为True，只使用缓存数据，不发起网络请求
        """
        print("\n" + "="*60)
        print(f"Glassnode 高级分析系统 - {asset}")
        print("="*60)
        
        # 存储资产类型
        self.asset = asset.upper()
        
        # 获取价格数据
        print(f"\n1. 获取 {self.asset} 价格数据...")

        
        start_date = end_date - timedelta(days=365*9)  # 9年数据，确保有足够数据进行365天预测
        
        print(f"   数据时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
        
        price_df = self.fetch_metric_data('market', 'price_usd_close', start_date, end_date, 
                                         asset=self.asset, only_cache=only_cache)
        if price_df.empty:
            price_df = self.fetch_metric_data('market', 'close', start_date, end_date, 
                                             asset=self.asset, only_cache=only_cache)
            if not price_df.empty:
                price_df = price_df.rename(columns={'close': 'price_usd_close'})
        
        if price_df.empty:
            print(f"错误：无法获取 {self.asset} 价格数据")
            return
            
        price_data = price_df['price_usd_close']
        print(f"✓ 获取到 {len(price_data)} 天的价格数据")
        
        # 分析关键指标
        self.analyze_key_indicators(price_data, only_cache=only_cache, num_workers=num_workers)
        
        # 保存完整的分析结果到 JSON
        save_analysis_results_to_json(self.asset, self.analysis_results)
        
    
    def _process_single_indicator(self, args):
        """处理单个指标的方法（用于多进程）"""
        try:
            category, endpoint_info, price_data, market_regime, \
            full_regime_benchmarks, benchmark_returns_long, \
            benchmark_returns_short, asset, only_cache = args
            
            # 从endpoint_info中提取metric和path
            if isinstance(endpoint_info, dict):
                metric = endpoint_info['metric']
                path = endpoint_info.get('path', None)
            else:
                metric = endpoint_info
                path = None
            
            print(f"[进程 {os.getpid()}] 分析 {metric}...")
            
            # 获取数据
            df = self.fetch_metric_data(category, metric, 
                                       price_data.index[0], 
                                       price_data.index[-1],
                                       path=path,
                                       asset=asset,
                                       only_cache=only_cache)
            if df.empty:
                return None
            
            indicator_data = df[metric]
            
            # 1. 多时间窗口分析
            multi_horizon = self.calculate_information_gain_multi_horizon(
                indicator_data, price_data
            )
            
            # 2. 找最优窗口
            optimal = self.find_optimal_horizon(multi_horizon)
            
            # 3. 阈值影响分析
            threshold_impact = self.analyze_threshold_impact(
                indicator_data, price_data,
                market_regime=market_regime,
                full_regime_benchmarks=full_regime_benchmarks,
                benchmark_long=benchmark_returns_long,
                benchmark_short=benchmark_returns_short
            )
            
            # 返回结果
            result_dict = {
                'multi_horizon': multi_horizon,
                'optimal': optimal,
                'threshold_impact': threshold_impact
            }
            
            return (metric, result_dict)
            
        except Exception as e:
            print(f"[进程 {os.getpid()}] 处理 {metric if 'metric' in locals() else 'unknown'} 时出错: {str(e)}")
            traceback.print_exc()
            return None
    
    def analyze_key_indicators(self, price_data: pd.Series, only_cache: bool = False, num_workers: int = 12):
        """分析关键指标
        
        Args:
            price_data: 价格数据
            only_cache: 如果为True，只使用缓存数据
        """
        print("\n2. 分析所有配置的指标...")
        if only_cache:
            print("  (仅使用缓存模式)")
        
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
        
        # 初始化分析结果的两个主要类别
        self.analysis_results = {
            'market': {},  # 市场基准相关
            'indicators': {}  # 指标分析结果
        }
        self.indicator_analysis_results = {}  # 保留以向后兼容
        
        # 预先计算基准收益和市场状态（只需计算一次）
        print("\n  计算基准收益和市场状态...")
        benchmark_returns_long = self._calculate_benchmark_returns(price_data, 'long')
        benchmark_returns_short = self._calculate_benchmark_returns(price_data, 'short')
        market_regime = self._identify_market_regime(price_data)
        
        # 计算统一的市场状态基准收益（多头和空头分别计算）
        full_regime_benchmarks = {
            'long': self._calculate_full_regime_benchmarks(benchmark_returns_long, market_regime),
            'short': self._calculate_full_regime_benchmarks(benchmark_returns_short, market_regime)
        }
        
        # 计算市场基准的详细指标
        market_metrics = self._calculate_market_metrics(
            benchmark_returns_long, 
            benchmark_returns_short,
            price_data
        )
        
        # 存储市场相关数据到 analysis_results
        self.analysis_results['market'] = {
            'benchmark_metrics': market_metrics,
            'market_regime': market_regime.to_dict() if hasattr(market_regime, 'to_dict') else market_regime,
            'full_regime_benchmarks': full_regime_benchmarks
        }
        
        # 可视化市场状态
        self._plot_market_regime(price_data, market_regime)
        
        # 准备并行处理的参数
        process_args = []
        for category, endpoint_info in key_indicators:
            # 准备完整的参数包，包括配置信息
            args = (
                self.api_key,
                self.cache_dir,
                self.categories,  # 传递categories配置
                self.asset,
                category, 
                endpoint_info, 
                price_data, 
                market_regime, 
                full_regime_benchmarks, 
                benchmark_returns_long, 
                benchmark_returns_short, 
                only_cache
            )
            process_args.append(args)
        
        # 使用多进程并行处理指标
        print(f"\n使用 {num_workers} 个进程并行处理 {len(process_args)} 个指标...")
        
        # 使用多进程池
        with Pool(processes=num_workers) as pool:
            results = pool.map(process_single_indicator_worker, process_args)
        
        # 收集结果
        for result in results:
            if result is not None:
                metric_name, result_dict = result
                self.results[metric_name] = result_dict
        self.analysis_results['indicators'] = self.results
        print(f"\n成功分析了 {len(self.results)} 个指标")
        
        # 原来的串行处理代码已经被多进程替代，注释掉
        '''
        for category, endpoint_info in key_indicators:
            # 从endpoint_info中提取metric和path
            if isinstance(endpoint_info, dict):
                metric = endpoint_info['metric']
                path = endpoint_info.get('path', None)
            else:
                metric = endpoint_info
                path = None
            
            print(f"\n分析 {metric}...")
            
            # 获取数据，传入path参数、asset和only_cache
            df = self.fetch_metric_data(category, metric, 
                                       price_data.index[0], 
                                       price_data.index[-1],
                                       path=path,
                                       asset=self.asset,
                                       only_cache=only_cache)
            if df.empty:
                continue
            
            indicator_data = df[metric]
            
            # 1. 多时间窗口分析
            multi_horizon = self.calculate_information_gain_multi_horizon(
                indicator_data, price_data
            )
            
            # 2. 找最优窗口
            optimal = self.find_optimal_horizon(multi_horizon)
            
            # 3. 阈值影响分析（传入市场状态和统一基准）
            threshold_impact = self.analyze_threshold_impact(
                indicator_data, price_data,
                market_regime=market_regime,
                full_regime_benchmarks=full_regime_benchmarks,
                benchmark_long=benchmark_returns_long,
                benchmark_short=benchmark_returns_short
            )
            
            # 保存结果到两个地方
            result_dict = {
                'multi_horizon': multi_horizon,
                'optimal': optimal,
                'threshold_impact': threshold_impact
            }
            
            # 保存到新结构
            self.analysis_results['indicators'][metric] = result_dict
            
            # 保留旧结构以向后兼容
            self.indicator_analysis_results[metric] = result_dict
            
            # 打印关键结果
            if optimal:
                print(f"  最优预测窗口: {optimal.get('optimal_horizon_ig', 'N/A')}天")
                print(f"  最大信息增益: {optimal.get('max_ig', 0):.4f}")
                
            # 打印相关性和策略信息
            if threshold_impact:
                first_result = next(iter(threshold_impact.values()))
                corr_type = first_result.get('correlation_type', 'unknown')
                corr_value = first_result.get('correlation_value', 0)
                print(f"  相关性: {corr_type} ({corr_value:.3f})")
                
                # 找出最佳的多头和空头策略
                best_long_ir = -999
                best_short_ir = -999
                best_long_pct = None
                best_short_pct = None
                best_long_ig = -999
                best_short_ig = -999
                best_long_accuracy = 0
                best_short_accuracy = 0
                best_long_horizon = None
                best_short_horizon = None
                
                for pct, pct_data in threshold_impact.items():
                    strategies = pct_data.get('strategies', {})
                    
                    # 检查多头策略
                    if 'long' in strategies:
                        ir = strategies['long']['relative_performance'].get('information_ratio', -999)
                        if ir > best_long_ir:
                            best_long_ir = ir
                            best_long_pct = pct
                        
                        # 检查最优时间窗口的信息增益
                        optimal = strategies['long'].get('optimal_horizon')
                        if optimal:
                            ig = optimal.get('information_gain', 0)
                            accuracy = optimal.get('signal_accuracy', 0)
                            horizon = optimal.get('horizon', 'N/A')
                            if ig > best_long_ig:
                                best_long_ig = ig
                                best_long_accuracy = accuracy
                                best_long_horizon = horizon
                    
                    # 检查空头策略
                    if 'short' in strategies:
                        ir = strategies['short']['relative_performance'].get('information_ratio', -999)
                        if ir > best_short_ir:
                            best_short_ir = ir
                            best_short_pct = pct
                        
                        # 检查最优时间窗口的信息增益
                        optimal = strategies['short'].get('optimal_horizon')
                        if optimal:
                            ig = optimal.get('information_gain', 0)
                            accuracy = optimal.get('signal_accuracy', 0)
                            horizon = optimal.get('horizon', 'N/A')
                            if ig > best_short_ig:
                                best_short_ig = ig
                                best_short_accuracy = accuracy
                                best_short_horizon = horizon
                
                # 打印最佳策略
                if best_long_pct is not None:
                    print(f"  最佳多头策略: 阈值{best_long_pct}%, IR={best_long_ir:.3f}")
                    if best_long_horizon:
                        print(f"    最优预测窗口: {best_long_horizon}, IG={best_long_ig:.4f}, 准确率={best_long_accuracy:.1%}")
                        
                if best_short_pct is not None:
                    print(f"  最佳空头策略: 阈值{best_short_pct}%, IR={best_short_ir:.3f}")
                    if best_short_horizon:
                        print(f"    最优预测窗口: {best_short_horizon}, IG={best_short_ig:.4f}, 准确率={best_short_accuracy:.1%}")
        '''


def main():
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Glassnode 高级分析系统')
    parser.add_argument('--asset', type=str, default='BTC', 
                       help='要分析的资产代码 (BTC, ETH, LTC, 等)')
    parser.add_argument('--api-key', type=str, default="myapi_sk_b3fa36048ea022be1c21e626742d4dec",
                       help='Glassnode API密钥')
    parser.add_argument('--end-date', type=str, default='2025-09-18',
                       help='分析结束日期 (格式: YYYY-MM-DD)，默认为2025-09-18 16:00')
    parser.add_argument('--only-cache', type=str, default='True',
                       choices=['True', 'False', 'true', 'false'],
                       help='只使用缓存数据，不发起网络请求 (True/False，默认False)')
    parser.add_argument('--num-workers', type=int, default=12,
                       help='并行处理的进程数 (默认12)')
    
    args = parser.parse_args()
    
    # 解析日期
    end_date = None
    if args.end_date:
        try:
            # 解析日期并设置时间为16:00
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=16, minute=0, second=0)
        except ValueError:
            print(f"警告：无效的日期格式 '{args.end_date}'，使用默认值")
    
    # 解析only_cache参数（将字符串转为布尔值）
    only_cache = args.only_cache.lower() == 'true'
    
    # 创建分析器
    analyzer = GlassnodeAdvancedAnalyzer(args.api_key)
    
    # 显示配置信息
    print("\n" + "=" * 60)
    print(f"Glassnode 完整分析系统 - {args.asset}")
    print("=" * 60)
    if only_cache:
        print("模式: 仅使用缓存（不发起网络请求）")
    
    # 运行综合分析
    analyzer.run_comprehensive_analysis(asset=args.asset, end_date=end_date, only_cache=only_cache, num_workers=args.num_workers)


if __name__ == "__main__":
    main()