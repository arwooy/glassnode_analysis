#!/usr/bin/env python3
"""
测试多进程并行分析功能
"""

import sys
import time
import subprocess

def test_parallel_analysis():
    """测试并行分析功能"""
    
    # 测试不同的进程数
    worker_counts = [1, 4, 8, 12]
    
    for num_workers in worker_counts:
        print(f"\n{'='*60}")
        print(f"测试 {num_workers} 个进程并行处理")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # 运行分析脚本（只分析少量指标以快速测试）
        cmd = [
            sys.executable,
            "glassnode_advanced_analysis.py",
            "--asset", "BTC",
            "--only-cache", "True",
            "--num-workers", str(num_workers)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # 从输出中提取成功分析的指标数
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if '成功分析了' in line:
                        print(line.strip())
                        break
                
                elapsed_time = time.time() - start_time
                print(f"处理时间: {elapsed_time:.2f} 秒")
                
                # 检查是否有错误
                if result.stderr:
                    print(f"警告信息: {result.stderr[:200]}")
            else:
                print(f"错误: 进程返回码 {result.returncode}")
                print(f"错误信息: {result.stderr[:500]}")
                
        except subprocess.TimeoutExpired:
            print(f"超时: 处理超过300秒")
        except Exception as e:
            print(f"发生异常: {str(e)}")
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("开始测试多进程并行分析功能...")
    test_parallel_analysis()