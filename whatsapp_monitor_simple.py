#!/usr/bin/env python3
"""
简化的WhatsApp连接监控脚本
只检查状态，不发送测试消息
"""

import subprocess
import json
import time
import sys

def run_command(cmd):
    """运行shell命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)

def check_whatsapp_status():
    """检查WhatsApp状态"""
    print("检查WhatsApp状态...")
    
    # 方法1: 使用openclaw status
    returncode, stdout, stderr = run_command("openclaw status")
    
    if returncode != 0:
        print(f"检查状态失败: {stderr}")
        return False
    
    # 检查输出中是否有WhatsApp信息
    if "WhatsApp" in stdout and "OK" in stdout:
        print("✅ WhatsApp状态显示为OK")
        return True
    else:
        print("❌ WhatsApp状态不正常或未找到")
        return False

def relink_whatsapp():
    """重新连接WhatsApp"""
    print("尝试重新连接WhatsApp...")
    
    # 1. 先登出
    print("登出WhatsApp...")
    run_command("openclaw channels logout --channel whatsapp")
    time.sleep(2)
    
    # 2. 生成新的QR码
    print("生成新的QR码...")
    returncode, stdout, stderr = run_command("openclaw channels login --channel whatsapp --account default")
    
    if returncode == 0:
        print("✅ QR码已生成")
        # 提取QR码信息
        if "Scan this QR" in stdout:
            qr_start = stdout.find("Scan this QR")
            print("\n" + "="*60)
            print("请用手机WhatsApp扫描以下QR码:")
            print("打开WhatsApp → 设置 → 已连接的设备 → 连接设备")
            print("="*60 + "\n")
            print(stdout[qr_start:min(qr_start+1000, len(stdout))])
        return True
    else:
        print(f"❌ 生成QR码失败: {stderr}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print(f"WhatsApp连接监控 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查WhatsApp状态
    whatsapp_ok = check_whatsapp_status()
    
    if whatsapp_ok:
        print("✅ WhatsApp连接正常")
        return 0
    else:
        print("❌ WhatsApp连接有问题，尝试重新连接...")
        if relink_whatsapp():
            print("✅ WhatsApp重新连接流程已启动")
            return 2  # 需要用户扫描QR码
        else:
            print("❌ WhatsApp重新连接失败")
            return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)