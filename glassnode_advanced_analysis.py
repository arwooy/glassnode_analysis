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
        
        # 提取IC值
        pearson_ic_values = []
        rank_ic_values = []
        for r in multi_horizon_results.values():
            pearson_ic_values.append(abs(r.get('pearson_ic', r.get('correlation', 0))))
            rank_ic_values.append(abs(r.get('rank_ic', r.get('pearson_ic', r.get('correlation', 0)))))
        
        # 找最优值
        optimal_ig_idx = np.argmax(ig_values)
        optimal_mi_idx = np.argmax(mi_values)
        optimal_pearson_ic_idx = np.argmax(pearson_ic_values)
        optimal_rank_ic_idx = np.argmax(rank_ic_values)
        
        return {
            'optimal_horizon_ig': horizons[optimal_ig_idx],
            'max_ig': ig_values[optimal_ig_idx],
            'optimal_horizon_mi': horizons[optimal_mi_idx],
            'max_mi': mi_values[optimal_mi_idx],
            'optimal_horizon_pearson_ic': horizons[optimal_pearson_ic_idx],
            'max_pearson_ic': pearson_ic_values[optimal_pearson_ic_idx],
            'optimal_horizon_rank_ic': horizons[optimal_rank_ic_idx],
            'max_rank_ic': rank_ic_values[optimal_rank_ic_idx],
            'all_horizons': horizons,
            'all_ig': ig_values,
            'all_rank_ic': rank_ic_values,
            'all_pearson_ic': pearson_ic_values
        }
    
    def analyze_threshold_impact(self, 
                                indicator_data: pd.Series,
                                price_data: pd.Series,
                                percentiles: List[float] = None,
                                benchmark_returns: pd.DataFrame = None,
                                market_regime: pd.Series = None,
                                full_regime_benchmarks: Dict = None) -> Dict:
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
            percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
        
        results = {}
        
        # 检测相关性方向：计算指标与未来收益的相关性
        future_returns = price_data.pct_change(periods=7).shift(-7)  # 7天后的收益
        correlation = indicator_data.corr(future_returns)
        is_positive_correlation = correlation > 0
        
        for pct in percentiles:
            try:
                # 计算阈值
                threshold = np.percentile(indicator_data.dropna(), pct)
                
                # 根据相关性方向设置持有条件
                if is_positive_correlation:
                    # 正相关：高于阈值时持有
                    mask = indicator_data >= threshold
                else:
                    # 负相关：低于阈值时持有（例如恐慌指数等）
                    mask = indicator_data <= threshold
                
                if mask.sum() < 50:
                    continue
                
                # 构建策略信号
                strategy_signal = mask.astype(int)  # 1=持有, 0=空仓
                
                # 计算策略收益
                strategy_returns = self._calculate_strategy_returns(
                    price_data, 
                    strategy_signal,
                    indicator_data.index
                )
                
                # 计算性能指标（包含超额收益和信息比率）
                performance = self._calculate_performance_metrics(
                    strategy_returns,
                    benchmark_returns,
                    strategy_signal
                )
                
                # 分离不同市场状态下的表现
                regime_performance = self._calculate_regime_performance(
                    strategy_returns,
                    benchmark_returns,
                    market_regime,
                    full_regime_benchmarks
                )
                
                # 计算综合评分
                comprehensive_score = self._calculate_comprehensive_score(
                    performance, regime_performance
                )
                
                results[pct] = {
                    'threshold': threshold,
                    'sample_size': mask.sum(),
                    'sample_ratio': mask.sum() / len(indicator_data),
                    'correlation_type': 'positive' if is_positive_correlation else 'negative',
                    'correlation_value': correlation,
                    
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
                    
                    # 市场状态下的表现
                    'regime_performance': regime_performance,
                    
                    # 综合评分
                    'comprehensive_scores': comprehensive_score
                }
                
            except Exception as e:
                print(f"Error analyzing percentile {pct}: {e}")
                continue
        
        return results
    
    def _calculate_benchmark_returns(self, price_data: pd.Series) -> pd.DataFrame:
        """计算基准（买入持有）收益"""
        returns = price_data.pct_change().fillna(0)
        cumulative_returns = (1 + returns).cumprod()
        
        return pd.DataFrame({
            'daily': returns,
            'cumulative': cumulative_returns
        })
    
    def _calculate_full_regime_benchmarks(self, benchmark_returns: pd.DataFrame, 
                                          market_regime: pd.Series) -> Dict:
        """计算统一的市场状态基准收益（所有指标共享）"""
        full_regime_benchmarks = {}
        
        # 确保索引对齐
        common_index = benchmark_returns.index.intersection(market_regime.index)
        benchmark_aligned = benchmark_returns.loc[common_index]
        regime_aligned = market_regime.loc[common_index]
        
        print("\n  统一市场状态基准收益:")
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
                
                full_regime_benchmarks[regime_name] = {
                    'total_days': mask.sum(),
                    'benchmark_return': regime_benchmark_returns.mean() * 252 if len(regime_benchmark_returns) > 0 else 0,
                    'benchmark_cumulative': (1 + regime_benchmark_returns).prod() - 1 if len(regime_benchmark_returns) > 0 else 0,
                    'benchmark_volatility': regime_benchmark_returns.std() * np.sqrt(252) if len(regime_benchmark_returns) > 1 else 0,
                    'benchmark_max_drawdown': max_drawdown
                }
                
                # 打印基准信息
                print(f"    {regime_name:8s}: {full_regime_benchmarks[regime_name]['total_days']:4d}天, "
                      f"年化收益: {full_regime_benchmarks[regime_name]['benchmark_return']:6.1f}%, "
                      f"累计收益: {full_regime_benchmarks[regime_name]['benchmark_cumulative']*100:6.1f}%, "
                      f"最大回撤: {full_regime_benchmarks[regime_name]['benchmark_max_drawdown']*100:6.1f}%")
        
        return full_regime_benchmarks
    
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
                                   index_align: pd.Index) -> Dict:
        """计算策略收益"""
        # 对齐数据
        aligned_price = price_data.reindex(index_align).fillna(method='ffill')
        aligned_signal = signal.reindex(index_align).fillna(0)
        
        # 计算日收益率
        daily_returns = aligned_price.pct_change().fillna(0)
        
        # 策略收益 = 信号 * 日收益率 (shift(1)避免前瞻偏差)
        strategy_returns = aligned_signal.shift(1) * daily_returns
        
        # 累积收益
        cumulative_returns = (1 + strategy_returns).cumprod()
        
        # 年化收益和波动率
        annual_return = strategy_returns.mean() * 252
        volatility = strategy_returns.std() * np.sqrt(252)
        
        return {
            'daily': strategy_returns,
            'cumulative': cumulative_returns,
            'annual_return': annual_return,
            'volatility': volatility
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
        excess_return = excess_returns.mean() * 252  # 年化
        
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
                                     full_regime_benchmarks: Dict = None) -> Dict:
        """计算不同市场状态下的表现"""
        if not strategy_returns or 'daily' not in strategy_returns:
            return {}
        
        #计算策略表现（处理缺失值后）
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
                
                # 策略收益计算
                strategy_return = strategy_regime.mean() * 252 if len(strategy_regime) > 0 else 0
                
                # 计算策略的最大回撤
                strategy_cumulative = (1 + strategy_regime).cumprod()
                strategy_running_max = strategy_cumulative.expanding().max()
                strategy_drawdown = (strategy_cumulative - strategy_running_max) / strategy_running_max
                strategy_max_drawdown = strategy_drawdown.min() if len(strategy_drawdown) > 0 else 0
                
                regime_performance[regime_name] = {
                    'days': unified_benchmark['total_days'],  # 使用完整数据的天数
                    'strategy_return': strategy_return,
                    'benchmark_return': unified_benchmark['benchmark_return'],  # 统一的基准
                    'benchmark_max_drawdown': unified_benchmark['benchmark_max_drawdown'],  # 基准的最大回撤
                    'excess_return': strategy_return - unified_benchmark['benchmark_return'],
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
    
    
    def run_comprehensive_analysis(self, asset: str = 'BTC', end_date: datetime = None, only_cache: bool = False):
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
        self.analyze_key_indicators(price_data, only_cache=only_cache)
        
        # 生成报告
        self.generate_advanced_report()
    
    def analyze_key_indicators(self, price_data: pd.Series, only_cache: bool = False):
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
        
        self.indicator_analysis_results = {}
        
        # 预先计算基准收益和市场状态（只需计算一次）
        print("\n  计算基准收益和市场状态...")
        benchmark_returns = self._calculate_benchmark_returns(price_data)
        market_regime = self._identify_market_regime(price_data)
        
        # 计算统一的市场状态基准收益（所有指标共享）
        full_regime_benchmarks = self._calculate_full_regime_benchmarks(benchmark_returns, market_regime)
        
        # 可视化市场状态
        self._plot_market_regime(price_data, market_regime)
        
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
            
            # 3. 阈值影响分析（传入预计算的基准收益、市场状态和统一基准）
            threshold_impact = self.analyze_threshold_impact(
                indicator_data, price_data,
                benchmark_returns=benchmark_returns,
                market_regime=market_regime,
                full_regime_benchmarks=full_regime_benchmarks
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
                
            # 打印相关性信息
            if threshold_impact:
                first_result = next(iter(threshold_impact.values()))
                corr_type = first_result.get('correlation_type', 'unknown')
                corr_value = first_result.get('correlation_value', 0)
                print(f"  相关性: {corr_type} ({corr_value:.3f})")
            
            
    
    
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
                    <th>最优窗口(Rank IC)</th>
                    <th>最大Rank IC</th>
                    <th>最优窗口(Pearson IC)</th>
                    <th>最大Pearson IC</th>
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
                    <td>{opt.get('optimal_horizon_rank_ic', opt.get('optimal_horizon_corr', 'N/A'))}天</td>
                    <td>{opt.get('max_rank_ic', opt.get('max_correlation', 0)):.4f}</td>
                    <td>{opt.get('optimal_horizon_pearson_ic', opt.get('optimal_horizon_corr', 'N/A'))}天</td>
                    <td>{opt.get('max_pearson_ic', opt.get('max_correlation', 0)):.4f}</td>
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
        
        # 添加改进的最优阈值表（包含相对性能和市场状态）
        html += """
            <h3>各指标最优阈值分析（改进版）</h3>
            <table>
                <tr>
                    <th rowspan="2">指标</th>
                    <th rowspan="2">相关性</th>
                    <th rowspan="2">最优阈值</th>
                    <th colspan="5">绝对性能</th>
                    <th colspan="4">相对性能</th>
                    <th colspan="3">交易统计</th>
                    <th colspan="3">市场状态表现</th>
                    <th rowspan="2">综合评分</th>
                </tr>
                <tr>
                    <!-- 绝对性能 -->
                    <th>年化收益</th>
                    <th>波动率</th>
                    <th>夏普</th>
                    <th>最大回撤</th>
                    <th>样本占比</th>
                    <!-- 相对性能 -->
                    <th>超额收益</th>
                    <th>信息比率</th>
                    <th>Alpha</th>
                    <th>跟踪误差</th>
                    <!-- 交易统计 -->
                    <th>胜率</th>
                    <th>盈亏比</th>
                    <th>期望值</th>
                    <!-- 市场状态 -->
                    <th>牛市超额</th>
                    <th>熊市超额</th>
                    <th>震荡超额</th>
                </tr>
"""
        
        for indicator, results in self.indicator_analysis_results.items():
            if 'threshold_impact' in results and results['threshold_impact']:
                # 找最优阈值（基于信息比率而非夏普比率）
                best_pct = None
                best_ir = -999
                best_data = None
                
                for pct, data in results['threshold_impact'].items():
                    # 优先使用信息比率
                    ir = data.get('relative_performance', {}).get('information_ratio', -999)
                    if ir > best_ir:
                        best_ir = ir
                        best_pct = pct
                        best_data = data
                
                # 如果没有相对性能数据，回退到旧版本
                if best_data is None:
                    for pct, data in results['threshold_impact'].items():
                        if 'returns' in data and '7d' in data['returns']:
                            sharpe = data['returns']['7d']['sharpe']
                            if sharpe > best_sharpe:
                                best_sharpe = sharpe
                                best_pct = pct
                                best_data = data
                
                if best_pct and best_data:
                    # 提取各项数据
                    abs_perf = best_data.get('absolute_performance', {})
                    rel_perf = best_data.get('relative_performance', {})
                    regime_perf = best_data.get('regime_performance', {})
                    scores = best_data.get('comprehensive_scores', {})
                    
                    # 获取市场状态超额收益
                    bull_excess = regime_perf.get('bull', {}).get('excess_return', 0) * 100 if regime_perf else 0
                    bear_excess = regime_perf.get('bear', {}).get('excess_return', 0) * 100 if regime_perf else 0
                    sideways_excess = regime_perf.get('sideways', {}).get('excess_return', 0) * 100 if regime_perf else 0
                    
                    # 根据综合评分设置行的背景色
                    overall_score = scores.get('overall', 0)
                    row_class = ""
                    if overall_score > 70:
                        row_class = "style='background-color: #d4edda;'"  # 绿色
                    elif overall_score > 40:
                        row_class = "style='background-color: #fff3cd;'"  # 黄色
                    else:
                        row_class = "style='background-color: #f8d7da;'"  # 红色
                    
                    # 获取相关性信息
                    corr_type = best_data.get('correlation_type', 'positive')
                    corr_value = best_data.get('correlation_value', 0)
                    corr_color = 'green' if corr_type == 'positive' else 'red'
                    
                    html += f"""
                <tr {row_class}>
                    <td><strong>{indicator}</strong></td>
                    <td style="color: {corr_color}">
                        {corr_type[:3].upper()}<br>
                        <small>({corr_value:.2f})</small>
                    </td>
                    <td class="highlight">{best_pct}%</td>
                    <!-- 绝对性能 -->
                    <td>{abs_perf.get('annual_return', 0)*100:.1f}%</td>
                    <td>{abs_perf.get('volatility', 0)*100:.1f}%</td>
                    <td>{abs_perf.get('sharpe', 0):.2f}</td>
                    <td>{abs_perf.get('max_drawdown', 0)*100:.1f}%</td>
                    <td>{best_data.get('sample_ratio', 0)*100:.1f}%</td>
                    <!-- 相对性能 -->
                    <td style="color: {'green' if rel_perf.get('excess_return', 0) > 0 else 'red'}">
                        {rel_perf.get('excess_return', 0)*100:.1f}%
                    </td>
                    <td style="color: {'green' if rel_perf.get('information_ratio', 0) > 0 else 'red'}">
                        {rel_perf.get('information_ratio', 0):.2f}
                    </td>
                    <td>{rel_perf.get('alpha', 0)*100:.1f}%</td>
                    <td>{rel_perf.get('tracking_error', 0)*100:.1f}%</td>
                    <!-- 交易统计 -->
                    <td style="color: {'green' if rel_perf.get('win_rate', 0) > 0.5 else 'orange' if rel_perf.get('win_rate', 0) > 0.4 else 'red'}">
                        {rel_perf.get('win_rate', 0)*100:.1f}%
                    </td>
                    <td style="color: {'green' if rel_perf.get('profit_loss_ratio', 0) > 1.5 else 'orange' if rel_perf.get('profit_loss_ratio', 0) > 1 else 'red'}">
                        {rel_perf.get('profit_loss_ratio', 0):.2f}
                    </td>
                    <td style="color: {'green' if rel_perf.get('expectancy', 0) > 0 else 'red'}">
                        {rel_perf.get('expectancy', 0):.1f}%
                    </td>
                    <!-- 市场状态 -->
                    <td style="color: {'green' if bull_excess > 0 else 'red'}">{bull_excess:.1f}%</td>
                    <td style="color: {'green' if bear_excess > 0 else 'red'}">{bear_excess:.1f}%</td>
                    <td style="color: {'green' if sideways_excess > 0 else 'red'}">{sideways_excess:.1f}%</td>
                    <!-- 综合评分 -->
                    <td style="font-weight: bold; color: {'green' if overall_score > 60 else 'orange' if overall_score > 30 else 'red'}">
                        {overall_score:.1f}
                    </td>
                </tr>
"""
        
        html += """
            </table>
            
            <h4>指标说明</h4>
            <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p><strong>改进版分析的关键优势：</strong></p>
                <ul style="line-height: 1.8;">
                    <li><strong>相关性类型</strong>：
                        <ul>
                            <li>POS（正相关）：指标值越高，未来收益越好，高于阈值时持有</li>
                            <li>NEG（负相关）：指标值越低，未来收益越好，低于阈值时持有（如恐慌指数）</li>
                        </ul>
                    </li>
                    <li><strong>超额收益</strong>：策略收益 - 买入持有收益，剔除市场整体影响，真实反映策略价值</li>
                    <li><strong>信息比率 (IR)</strong>：超额收益 / 跟踪误差，衡量每单位风险获得的超额收益
                        <ul>
                            <li>IR > 1.0: 优秀策略</li>
                            <li>IR > 0.5: 良好策略</li>
                            <li>IR > 0: 有价值</li>
                            <li>IR < 0: 跑输基准</li>
                        </ul>
                    </li>
                    <li><strong>Alpha</strong>：风险调整后的超额收益，代表策略的纯alpha贡献</li>
                    <li><strong>跟踪误差</strong>：超额收益的标准差，反映策略偏离基准的稳定性</li>
                    <li><strong>胜率</strong>：盈利天数占总交易天数的比例
                        <ul>
                            <li>> 50%: 赢多输少</li>
                            <li>> 45%: 可接受（配合高盈亏比）</li>
                            <li>< 40%: 需要优化</li>
                        </ul>
                    </li>
                    <li><strong>盈亏比</strong>：平均盈利 / 平均亏损，衡量风险回报比
                        <ul>
                            <li>> 2.0: 优秀的风险回报</li>
                            <li>> 1.5: 良好</li>
                            <li>> 1.0: 基本合格</li>
                            <li>< 1.0: 风险大于回报</li>
                        </ul>
                    </li>
                    <li><strong>期望值</strong>：每次交易的数学期望收益，综合考虑胜率和盈亏比
                        <ul>
                            <li>期望值 = 胜率 × 平均盈利 - (1-胜率) × 平均亏损</li>
                            <li>> 0: 长期盈利策略</li>
                            <li>< 0: 长期亏损策略</li>
                        </ul>
                    </li>
                    <li><strong>市场状态超额</strong>：在牛市、熊市、震荡市分别的超额表现，评估策略的市场适应性</li>
                    <li><strong>综合评分</strong>：结合性能指标(50%)、市场适应性(50%)的综合评估</li>
                </ul>
                <p style="margin-top: 10px; color: #666;">
                    <em>注：表格中绿色背景表示综合评分>70分，黄色表示40-70分，红色表示<40分</em>
                </p>
            </div>
        </div>
"""
        
        # 指标组合分析
        html += """
        <div class="section">
            <h2>指标组合分析（2元组合）</h2>
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
            # 保存改进版的阈值分析数据
            if 'threshold_impact' in data:
                # 保存完整的阈值分析数据
                threshold_analysis = data['threshold_impact']
            else:
                threshold_analysis = {}
            
            results['indicators'][indicator] = {
                'optimal_horizon': data.get('optimal', {}),
                'multi_horizon_ig': {
                    str(k): v['information_gain'] 
                    for k, v in data.get('multi_horizon', {}).items()
                },
                'best_threshold': self._find_best_threshold(data.get('threshold_impact', {})),
                # 添加完整的阈值分析数据供Dashboard使用
                'threshold_analysis': threshold_analysis
            }
        
        # 组合结果
        if hasattr(self, 'combo_2_results'):
            results['combinations_2'] = self._format_combo_results(self.combo_2_results)
        
        with open('glassnode_advanced_results.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    def _find_best_threshold(self, threshold_data: Dict) -> Dict:
        """找出最佳阈值（改进版：优先使用信息比率）"""
        if not threshold_data:
            return {}
        
        best = None
        best_score = -999
        
        for pct, data in threshold_data.items():
            # 优先使用信息比率
            if 'relative_performance' in data:
                score = data['relative_performance'].get('information_ratio', -999)
                metric_type = 'information_ratio'
            # 其次使用综合评分
            elif 'comprehensive_scores' in data:
                score = data['comprehensive_scores'].get('overall', -999)
                metric_type = 'comprehensive_score'
            # 最后使用夏普比率（兼容旧版）
            elif '7d' in data.get('returns', {}):
                score = data['returns']['7d']['sharpe']
                metric_type = 'sharpe'
            else:
                continue
            
            if score > best_score:
                best_score = score
                
                # 根据数据格式构建返回结果
                if 'relative_performance' in data:
                    # 新版数据格式
                    best = {
                        'percentile': pct,
                        'sharpe': data.get('absolute_performance', {}).get('sharpe', 0),
                        'information_ratio': data['relative_performance'].get('information_ratio', 0),
                        'excess_return': data['relative_performance'].get('excess_return', 0),
                        'alpha': data['relative_performance'].get('alpha', 0),
                        'comprehensive_score': data.get('comprehensive_scores', {}).get('overall', 0),
                        'sample_ratio': data.get('sample_ratio', 0),
                        'metric_type': metric_type
                    }
                else:
                    # 旧版数据格式
                    best = {
                        'percentile': pct,
                        'sharpe': score if metric_type == 'sharpe' else 0,
                        'return_7d': data.get('returns', {}).get('7d', {}).get('mean', 0),
                        'sample_ratio': data.get('sample_ratio', 0),
                        'metric_type': metric_type
                    }
        
        return best if best else {}
    
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
    parser.add_argument('--asset', type=str, default='BTC', 
                       help='要分析的资产代码 (BTC, ETH, LTC, 等)')
    parser.add_argument('--api-key', type=str, default="myapi_sk_b3fa36048ea022be1c21e626742d4dec",
                       help='Glassnode API密钥')
    parser.add_argument('--end-date', type=str, default='2025-09-18',
                       help='分析结束日期 (格式: YYYY-MM-DD)，默认为2025-09-18 16:00')
    parser.add_argument('--only-cache', type=str, default='True',
                       choices=['True', 'False', 'true', 'false'],
                       help='只使用缓存数据，不发起网络请求 (True/False，默认False)')
    
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
    analyzer.run_comprehensive_analysis(asset=args.asset, end_date=end_date, only_cache=only_cache)


if __name__ == "__main__":
    main()