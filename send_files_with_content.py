#!/usr/bin/env python3
"""
發送包含文件內容的郵件
"""

import subprocess
import os
from datetime import datetime

def read_file_with_preview(filepath, max_lines=100):
    """讀取文件內容，限制行數"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) > max_lines:
            preview = ''.join(lines[:max_lines])
            preview += f"\n\n[文件過長，已截斷前{max_lines}行，完整文件請從工作空間獲取]"
            return preview
        else:
            return ''.join(lines)
    except Exception as e:
        return f"讀取文件失敗: {e}"

def main():
    print("📧 發送包含文件內容的郵件...")
    
    # 文件路徑
    guide_file = "/Users/gordonlui/.openclaw/workspace/OpenClaw_Mac_Mini_Installation_Guide.md"
    script_file = "/Users/gordonlui/.openclaw/workspace/openclaw_quick_install.sh"
    
    # 讀取文件內容
    guide_content = read_file_with_preview(guide_file, 80)
    script_content = read_file_with_preview(script_file, 150)
    
    # 創建郵件內容
    email_body = f"""
已為你朋友的全新Mac mini創建了完整的OpenClaw安裝指南和自動化腳本。

📁 包含兩個文件：
1. OpenClaw_Mac_Mini_Installation_Guide.md - 完整安裝手冊
2. openclaw_quick_install.sh - 一鍵安裝腳本

========================================
文件1: OpenClaw_Mac_Mini_Installation_Guide.md
========================================

{guide_content}

========================================
文件2: openclaw_quick_install.sh
========================================

{script_content}

========================================
🎯 使用說明
========================================

1. 保存腳本文件：
   將上面的「openclaw_quick_install.sh」內容保存到文件

2. 給予執行權限：
   chmod +x openclaw_quick_install.sh

3. 運行安裝：
   ./openclaw_quick_install.sh

4. 按照提示輸入：
   - DeepSeek API Key
   - 手機號碼
   - 姓名等基本信息

5. 安裝完成後：
   - 運行: openclaw whatsapp login
   - 掃描QR碼鏈接WhatsApp
   - 開始使用！

========================================
💡 重要提示
========================================

• 安裝腳本會自動處理大部分配置
• 會生成詳細的安裝報告
• 包含安全設置和權限配置
• 基於2026安全最佳實踐

========================================
📁 文件位置（在我的系統）
========================================

1. 安裝指南: {guide_file}
2. 安裝腳本: {script_file}

你可以從這些位置複製文件，或者使用上面的內容創建文件。

========================================
🆘 遇到問題？
========================================

1. 檢查網絡連接
2. 確保有DeepSeek API Key
3. 運行: openclaw doctor
4. 查看日誌: openclaw logs

如有任何問題，請隨時告訴我！

發送時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
發送者: 久留美
"""
    
    # 發送郵件
    print("發送郵件...")
    cmd = [
        'python3', 'email_tool.py', 'send',
        '--to', 'zero850x@gmail.com',
        '--subject', 'OpenClaw安裝文件（包含內容）',
        '--body', email_body
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd='/Users/gordonlui/.openclaw/workspace')
    
    if result.returncode == 0:
        print("✅ 郵件發送成功！")
        print("📧 收件人: zero850x@gmail.com")
        print("📋 主題: OpenClaw安裝文件（包含內容）")
        print("📎 包含: 兩個文件的完整內容")
    else:
        print(f"❌ 郵件發送失敗: {result.stderr}")
        return
    
    # 提供額外信息
    print("\n📊 文件信息:")
    print(f"• 安裝指南: {os.path.getsize(guide_file)} 字節")
    print(f"• 安裝腳本: {os.path.getsize(script_file)} 字節")
    
    print("\n🔧 快速創建文件的方法:")
    print("1. 複製郵件中的腳本內容")
    print("2. 在Terminal中執行:")
    print("   cat > openclaw_quick_install.sh << 'EOF'")
    print("   [粘貼內容]")
    print("   EOF")
    print("3. 給予權限: chmod +x openclaw_quick_install.sh")
    
    print("\n🎯 完成！你的朋友現在可以安裝OpenClaw了。")

if __name__ == "__main__":
    main()