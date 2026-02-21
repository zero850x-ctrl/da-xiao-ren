#!/usr/bin/env python3
"""
WhatsApp连接监控脚本
检查WhatsApp连接状态，如果断开则尝试重新连接
"""

import subprocess
import json
import time
import os
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

def check_openclaw_status():
    """检查OpenClaw状态"""
    print("检查OpenClaw状态...")
    returncode, stdout, stderr = run_command("openclaw status --json")
    
    if returncode != 0:
        print(f"检查OpenClaw状态失败: {stderr}")
        return False, None
    
    try:
        status_data = json.loads(stdout)
        return True, status_data
    except json.JSONDecodeError:
        print("解析OpenClaw状态JSON失败")
        return False, None

def check_whatsapp_connection(status_data):
    """检查WhatsApp连接状态"""
    if not status_data or "channels" not in status_data:
        print("状态数据中没有channels信息")
        return False
    
    for channel in status_data.get("channels", []):
        if channel.get("channel") == "WhatsApp":
            state = channel.get("state", "").upper()
            detail = channel.get("detail", "")
            print(f"WhatsApp状态: {state}, 详情: {detail}")
            
            # 检查是否连接
            if state == "OK" and "linked" in detail.lower():
                print("WhatsApp显示为已连接")
                return True
            else:
                print("WhatsApp显示为未连接或连接有问题")
                return False
    
    print("未找到WhatsApp通道信息")
    return False

def test_whatsapp_message():
    """测试发送WhatsApp消息"""
    print("测试发送WhatsApp消息...")
    test_message = "WhatsApp连接测试消息。如果收到此消息，连接正常。"
    
    # 尝试发送测试消息到自己的号码
    cmd = f'openclaw message send --channel whatsapp --to "+85298104938" --message "{test_message}"'
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        print("测试消息发送成功，WhatsApp连接正常")
        return True
    else:
        print(f"测试消息发送失败: {stderr}")
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
        print("QR码已生成，请用手机WhatsApp扫描连接")
        # 提取QR码信息
        if "Scan this QR" in stdout:
            qr_start = stdout.find("Scan this QR")
            print(stdout[qr_start:qr_start+500])  # 打印部分QR码信息
        return True
    else:
        print(f"生成QR码失败: {stderr}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print(f"WhatsApp连接监控 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查OpenClaw状态
    success, status_data = check_openclaw_status()
    if not success:
        print("无法获取OpenClaw状态，退出")
        return 1
    
    # 检查WhatsApp连接状态
    whatsapp_connected = check_whatsapp_connection(status_data)
    
    if whatsapp_connected:
        # 如果状态显示已连接，测试发送消息
        if test_whatsapp_message():
            print("✅ WhatsApp连接正常")
            return 0
        else:
            print("⚠️ 状态显示已连接但发送消息失败，尝试重新连接")
            whatsapp_connected = False
    
    if not whatsapp_connected:
        print("❌ WhatsApp连接断开，尝试重新连接...")
        if relink_whatsapp():
            print("✅ WhatsApp重新连接流程已启动，请扫描QR码")
            return 2  # 需要用户扫描QR码
        else:
            print("❌ WhatsApp重新连接失败")
            return 3
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)