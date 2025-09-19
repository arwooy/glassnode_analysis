#!/usr/bin/env python3
"""
重命名缓存文件，将时间戳格式转换为日期格式
从: addresses_accumulation_balance_BTC_1474329600_1758067200_24h.pkl
到: addresses_accumulation_balance_BTC_20160920_20250918_24h.pkl
"""

import os
import re
from datetime import datetime
import shutil

def timestamp_to_date(timestamp):
    """将时间戳转换为YYYYMMDD格式"""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%Y%m%d')
    except:
        return timestamp

def rename_cache_files(cache_dir='glassnode_cache'):
    """批量重命名缓存文件"""
    
    if not os.path.exists(cache_dir):
        print(f"目录 {cache_dir} 不存在")
        return
    
    # 获取所有pkl文件
    pkl_files = [f for f in os.listdir(cache_dir) if f.endswith('.pkl')]
    
    print(f"找到 {len(pkl_files)} 个pkl文件")
    
    # 正则表达式匹配文件名格式
    # 格式: category_metric_asset_starttime_endtime_interval.pkl
    pattern = r'^(.+?)_(.+?)_(BTC|ETH|LTC|[A-Z]+)_(\d{10})_(\d{10})_(.+)\.pkl$'
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filename in pkl_files:
        match = re.match(pattern, filename)
        
        if match:
            category = match.group(1)
            metric = match.group(2)
            asset = match.group(3)
            start_timestamp = match.group(4)
            end_timestamp = match.group(5)
            interval = match.group(6)
            
            # 检查是否已经是日期格式（8位数字）
            if len(start_timestamp) == 8 and len(end_timestamp) == 8:
                print(f"跳过（已是日期格式）: {filename}")
                skipped_count += 1
                continue
            
            # 转换时间戳为日期
            start_date = timestamp_to_date(start_timestamp)
            end_date = timestamp_to_date(end_timestamp)
            
            # 构建新文件名
            new_filename = f"{category}_{metric}_{asset}_{start_date}_{end_date}_{interval}.pkl"
            
            # 完整路径
            old_path = os.path.join(cache_dir, filename)
            new_path = os.path.join(cache_dir, new_filename)
            
            # 如果新文件名已存在，跳过
            if os.path.exists(new_path):
                print(f"目标文件已存在，跳过: {new_filename}")
                skipped_count += 1
                continue
            
            # 重命名文件
            try:
                os.rename(old_path, new_path)
                print(f"✓ 重命名: {filename}")
                print(f"      -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"✗ 重命名失败: {filename}")
                print(f"  错误: {e}")
                error_count += 1
        else:
            # 尝试其他可能的格式
            # 可能是已经重命名过的文件，或者其他格式
            if re.match(r'^.+?_.+?_[A-Z]+_\d{8}_\d{8}_.+\.pkl$', filename):
                print(f"跳过（已是正确格式）: {filename}")
                skipped_count += 1
            else:
                print(f"⚠ 无法识别的文件格式: {filename}")
                error_count += 1
    
    print("\n" + "="*60)
    print("重命名完成")
    print("="*60)
    print(f"✓ 成功重命名: {renamed_count} 个文件")
    print(f"→ 跳过: {skipped_count} 个文件")
    print(f"✗ 错误: {error_count} 个文件")
    
    return renamed_count, skipped_count, error_count

def backup_cache_dir(cache_dir='glassnode_cache', backup_dir='glassnode_cache_backup'):
    """备份缓存目录（可选）"""
    if os.path.exists(cache_dir):
        print(f"备份缓存目录到 {backup_dir}...")
        if os.path.exists(backup_dir):
            print(f"备份目录已存在: {backup_dir}")
            response = input("是否覆盖? (y/n): ")
            if response.lower() != 'y':
                return False
            shutil.rmtree(backup_dir)
        
        shutil.copytree(cache_dir, backup_dir)
        print("✓ 备份完成")
        return True
    return False

def show_examples(cache_dir='glassnode_cache', num_examples=5):
    """显示一些文件名示例"""
    pkl_files = [f for f in os.listdir(cache_dir) if f.endswith('.pkl')]
    
    print("\n文件名示例:")
    print("-" * 60)
    
    # 显示时间戳格式的文件
    timestamp_files = []
    date_files = []
    
    pattern_timestamp = r'^(.+?)_(.+?)_(BTC|ETH|LTC|[A-Z]+)_(\d{10})_(\d{10})_(.+)\.pkl$'
    pattern_date = r'^(.+?)_(.+?)_(BTC|ETH|LTC|[A-Z]+)_(\d{8})_(\d{8})_(.+)\.pkl$'
    
    for filename in pkl_files[:20]:  # 检查前20个文件
        if re.match(pattern_timestamp, filename):
            timestamp_files.append(filename)
        elif re.match(pattern_date, filename):
            date_files.append(filename)
    
    if timestamp_files:
        print("\n需要重命名的文件（时间戳格式）:")
        for f in timestamp_files[:num_examples]:
            print(f"  {f}")
    
    if date_files:
        print("\n已是正确格式的文件（日期格式）:")
        for f in date_files[:num_examples]:
            print(f"  {f}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='重命名Glassnode缓存文件')
    parser.add_argument('--dir', type=str, default='glassnode_cache',
                       help='缓存目录路径')
    parser.add_argument('--backup', action='store_true',
                       help='重命名前先备份')
    parser.add_argument('--dry-run', action='store_true',
                       help='只显示将要重命名的文件，不实际执行')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Glassnode缓存文件重命名工具")
    print("="*60)
    
    # 检查目录
    if not os.path.exists(args.dir):
        print(f"错误：目录 {args.dir} 不存在")
        return
    
    # 显示示例
    show_examples(args.dir)
    
    if args.dry_run:
        print("\n[DRY RUN 模式 - 不会实际重命名文件]")
    
    # 备份（如果需要）
    if args.backup and not args.dry_run:
        print("\n执行备份...")
        if not backup_cache_dir(args.dir):
            print("备份取消，退出程序")
            return
    
    # 确认
    if not args.dry_run:
        print("\n准备重命名文件")
        response = input("确认继续? (y/n): ")
        if response.lower() != 'y':
            print("操作取消")
            return
    
    # 执行重命名
    print("\n开始重命名...")
    if args.dry_run:
        print("（DRY RUN - 仅显示）")
    
    renamed, skipped, errors = rename_cache_files(args.dir)
    
    # 如果有错误，提示用户
    if errors > 0:
        print("\n⚠ 注意：有一些文件无法处理，请手动检查")

if __name__ == "__main__":
    main()