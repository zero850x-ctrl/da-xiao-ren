#!/usr/bin/env python3
"""
簡單的OpenClaw更新檢查和解決方案
"""

import subprocess
import json
import os

def run_command(cmd):
    """運行命令並返回結果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("🔍 OpenClaw更新狀態檢查")
    print("=" * 50)
    
    # 檢查當前版本
    print("1. 當前運行版本:")
    version, error, code = run_command("openclaw --version")
    if code == 0:
        print(f"   ✅ {version}")
    else:
        print(f"   ❌ 無法獲取版本: {error}")
    
    # 檢查狀態
    print("\n2. 更新狀態:")
    status, error, code = run_command("openclaw status")
    if code == 0:
        # 提取更新信息
        lines = status.split('\n')
        for line in lines:
            if "Update" in line or "update" in line.lower():
                print(f"   {line.strip()}")
    else:
        print(f"   ❌ 無法獲取狀態: {error}")
    
    # 檢查npm最新版本
    print("\n3. 最新可用版本:")
    latest, error, code = run_command("npm view openclaw version")
    if code == 0:
        print(f"   📦 npm最新版本: {latest}")
    else:
        print(f"   ❌ 無法獲取最新版本: {error}")
    
    print("\n" + "=" * 50)
    print("📋 問題總結")
    print("=" * 50)
    
    print("""
當前狀況:
1. 系統安裝版本: 2026.2.1 (需要更新)
2. 用戶安裝版本: 2026.2.3-1 (已更新但權限有問題)
3. 最新版本: 2026.2.3-1 (可用)

主要問題:
• 用戶安裝目錄權限為root，無法更新
• 系統安裝需要管理員權限更新
• 兩個安裝版本不一致
    """)
    
    print("=" * 50)
    print("🎯 推薦解決方案")
    print("=" * 50)
    
    print("""
方案A: 修復權限並更新 (需要終端操作)
----------------------------------------
1. 打開 Terminal.app
2. 執行以下命令:

   # 修復npm緩存權限
   sudo chown -R $(whoami):staff ~/.npm
   
   # 修復OpenClaw安裝權限  
   sudo chown -R $(whoami):staff ~/.npm-global/lib/node_modules/openclaw
   
   # 更新OpenClaw
   npm install -g openclaw@latest
   
   # 檢查版本
   openclaw --version
   
   # 重啟Gateway
   openclaw gateway restart

方案B: 只更新系統安裝 (最簡單)
----------------------------------------
1. 打開 Terminal.app
2. 執行:

   sudo npm install -g openclaw@latest
   openclaw gateway restart

方案C: 使用OpenClaw內置更新 (如果可用)
----------------------------------------
1. 在OpenClaw對話中輸入:
   /update
   
   或者
   
   openclaw update --force

方案D: 手動下載安裝
----------------------------------------
1. 卸載當前安裝:
   sudo npm uninstall -g openclaw
   
2. 重新安裝:
   sudo npm install -g openclaw@latest
   
3. 重啟服務:
   openclaw gateway restart
    """)
    
    print("=" * 50)
    print("💡 我的建議")
    print("=" * 50)
    
    print("""
推薦使用「方案B: 只更新系統安裝」:

1. 它最簡單直接
2. 只需要一個命令
3. 解決版本不一致問題
4. Gateway服務使用系統安裝版本

執行步驟:
1. 點擊Mac屏幕右上角的「聚焦搜索」(Cmd+Space)
2. 輸入「Terminal」打開終端
3. 複製粘貼這個命令:
   
   sudo npm install -g openclaw@latest && openclaw gateway restart
   
4. 輸入你的Mac登錄密碼
5. 等待完成

完成後檢查:
• openclaw --version 應該顯示 2026.2.3-1
• openclaw status 應該顯示已是最新版本
• cron任務應該能正常檢測更新
    """)
    
    print("=" * 50)
    print("⚠️  注意事項")
    print("=" * 50)
    
    print("""
1. 更新需要管理員權限 (需要輸入密碼)
2. 更新期間Gateway會短暫重啟
3. 所有連接會自動恢復
4. 配置和數據不會受影響
5. 更新後建議運行: openclaw doctor
    """)
    
    # 提供快速檢查命令
    print("\n" + "=" * 50)
    print("🔧 快速檢查命令")
    print("=" * 50)
    
    print("""
更新後可以使用這些命令檢查:

# 檢查版本
openclaw --version

# 檢查狀態
openclaw status

# 檢查Gateway
openclaw gateway status

# 運行健康檢查
openclaw doctor

# 檢查cron任務
openclaw cron list
    """)
    
    print("\n" + "=" * 50)
    print("✅ 準備好更新了嗎？")
    print("=" * 50)
    
    print("請打開Terminal.app並執行:")
    print("\n   sudo npm install -g openclaw@latest && openclaw gateway restart")
    print("\n然後告訴我結果！ 🚀")

if __name__ == "__main__":
    main()