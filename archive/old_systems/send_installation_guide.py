#!/usr/bin/env python3
"""
發送OpenClaw安裝指南郵件
"""

import subprocess
import os
from datetime import datetime

def read_file_content(filepath):
    """讀取文件內容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"讀取文件失敗: {e}"

def main():
    print("📧 準備發送OpenClaw安裝指南...")
    
    # 讀取文件內容
    guide_file = "/Users/gordonlui/.openclaw/workspace/OpenClaw_Mac_Mini_Installation_Guide.md"
    script_file = "/Users/gordonlui/.openclaw/workspace/openclaw_quick_install.sh"
    
    guide_content = read_file_content(guide_file)
    script_content = read_file_content(script_file)
    
    # 創建簡潔的郵件內容
    email_body = f"""
已為你朋友的全新Mac mini創建了完整的OpenClaw安裝指南和自動化腳本。

🎯 核心內容：
1. 📖 完整安裝手冊 - 詳細步驟說明
2. ⚡ 一鍵安裝腳本 - 自動化安裝程序

🚀 主要特點：
• 專為全新Mac mini優化
• 預設使用DeepSeek API
• 基於2026安全最佳實踐
• 包含完整的配置示例
• 自動化安裝和測試

🔧 安裝前準備：
1. DeepSeek API Key: https://platform.deepseek.com/api_keys
2. 手機號碼 (WhatsApp鏈接用)
3. 穩定的網絡連接

📋 快速開始：
1. 下載安裝腳本
2. 運行: chmod +x openclaw_quick_install.sh
3. 運行: ./openclaw_quick_install.sh
4. 按照提示輸入信息

🛡️ 內置安全：
• Gateway安全綁定
• Token認證保護  
• 文件權限強化
• 訪問控制白名單

📁 文件已準備好，可以通過以下方式獲取：
1. 從工作空間目錄複製
2. 或讓我通過其他方式發送

💡 提示：
• 安裝腳本會自動處理大部分配置
• 會生成詳細的安裝報告
• 包含故障排除指南

如有任何問題，請隨時告訴我！

發送時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
發送者: 久留美
"""
    
    # 發送郵件
    print("發送郵件...")
    cmd = [
        'python3', 'email_tool.py', 'send',
        '--to', 'zero850x@gmail.com',
        '--subject', 'OpenClaw Mac Mini 安裝指南與腳本',
        '--body', email_body
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd='/Users/gordonlui/.openclaw/workspace')
    
    if result.returncode == 0:
        print("✅ 郵件發送成功！")
        print("郵件已發送到: zero850x@gmail.com")
        print("主題: OpenClaw Mac Mini 安裝指南與腳本")
    else:
        print(f"❌ 郵件發送失敗: {result.stderr}")
    
    # 提供文件位置信息
    print("\n📁 文件位置:")
    print(f"1. 安裝指南: {guide_file}")
    print(f"2. 安裝腳本: {script_file}")
    
    print("\n📋 文件摘要:")
    print(f"• 安裝指南: {len(guide_content)} 字符")
    print(f"• 安裝腳本: {len(script_content)} 字符")
    
    print("\n🎯 下一步:")
    print("1. 將文件分享給你的朋友")
    print("2. 讓他們按照指南操作")
    print("3. 如有問題隨時問我")

if __name__ == "__main__":
    main()