#!/usr/bin/env python3
"""
添加黃金交易cron任務到OpenClaw
"""

import subprocess
import json
import sys

def add_cron_job(job_name, job_config):
    """添加cron任務"""
    print(f"🔧 添加任務: {job_name}")
    
    # 將配置轉為JSON字符串
    job_json = json.dumps(job_config)
    
    # 構建命令
    cmd = ['openclaw', 'cron', 'add', '--job', job_json]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 任務添加成功: {job_name}")
            print(f"   輸出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 任務添加失敗: {job_name}")
            print(f"   錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 執行命令失敗: {e}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("🏆 添加黃金交易cron任務")
    print("=" * 60)
    
    # 加載配置
    config_path = '/Users/gordonlui/.openclaw/workspace/cron_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 加載配置失敗: {e}")
        return
    
    # 添加任務
    success_count = 0
    
    # 每小時交易任務
    if add_cron_job("hourly_trade", config['hourly_trade']):
        success_count += 1
    
    # 每日報告任務
    if add_cron_job("daily_report", config['daily_report']):
        success_count += 1
    
    # 每周優化任務
    if add_cron_job("weekly_optimization", config['weekly_optimization']):
        success_count += 1
    
    print(f"
📊 結果: {success_count}/3 個任務添加成功")
    
    if success_count == 3:
        print("✅ 所有cron任務設置完成")
        print("
📋 任務安排:")
        print("   1. 每小時交易檢查: 整點執行")
        print("   2. 每日報告: 16:30 (收盤後)")
        print("   3. 每周優化: 周一09:00")
    else:
        print("⚠️  部分任務添加失敗，請手動檢查")

if __name__ == "__main__":
    main()
