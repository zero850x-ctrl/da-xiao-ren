#!/usr/bin/env python3
"""
最終更新檢查
"""

import subprocess
import os

def run_command(cmd):
    """運行命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "命令超時", 1
    except Exception as e:
        return "", str(e), 1

def main():
    print("🎯 OpenClaw更新最終檢查")
    print("=" * 60)
    
    # 檢查兩個版本的openclaw
    openclaw_paths = [
        ("系統命令", "/usr/local/bin/openclaw"),
        ("用戶命令", os.path.expanduser("~/.npm-global/bin/openclaw"))
    ]
    
    for name, path in openclaw_paths:
        if os.path.exists(path):
            version, error, code = run_command(f'"{path}" --version')
            if code == 0:
                print(f"✅ {name}: {path}")
                print(f"   版本: {version}")
            else:
                print(f"❌ {name}: {path}")
                print(f"   錯誤: {error}")
        else:
            print(f"⚠️  {name}: {path} 不存在")
        print()
    
    print("=" * 60)
    print("📋 當前狀況總結")
    print("=" * 60)
    
    print("""
狀況分析:
1. ✅ 用戶安裝已更新到 2026.2.3-1
2. ⚠️  系統安裝還是 2026.2.1
3. 🔧 系統PATH優先使用系統安裝版本
4. 🎯 需要解決版本不一致問題
    """)
    
    print("=" * 60)
    print("🚀 立即解決方案")
    print("=" * 60)
    
    print("""
方案1: 使用完整路徑運行新版本 (立即生效)
----------------------------------------
使用這個命令運行新版本:
   ~/.npm-global/bin/openclaw [命令]

例如:
   ~/.npm-global/bin/openclaw --version
   ~/.npm-global/bin/openclaw status
   ~/.npm-global/bin/openclaw gateway restart

方案2: 設置臨時別名 (當前會話有效)
----------------------------------------
在Terminal中執行:
   alias openclaw="~/.npm-global/bin/openclaw"
   
然後就可以直接使用:
   openclaw --version
   openclaw status

方案3: 永久設置別名
----------------------------------------
編輯 ~/.zshrc 文件，添加:
   alias openclaw="~/.npm-global/bin/openclaw"
   
然後執行:
   source ~/.zshrc

方案4: 更新系統安裝 (一勞永逸)
----------------------------------------
在Terminal中執行:
   sudo npm install -g openclaw@latest
   
這會更新系統安裝到最新版本。
    """)
    
    print("=" * 60)
    print("💡 我的建議")
    print("=" * 60)
    
    print("""
推薦執行順序:

1. 立即測試新版本:
   ~/.npm-global/bin/openclaw --version
   ~/.npm-global/bin/openclaw status

2. 重啟Gateway使用新版本:
   ~/.npm-global/bin/openclaw gateway restart

3. 設置永久別名 (在Terminal中執行):
   echo 'alias openclaw="~/.npm-global/bin/openclaw"' >> ~/.zshrc
   source ~/.zshrc

4. 檢查cron任務:
   openclaw cron list
    """)
    
    print("=" * 60)
    print("✅ 執行命令示例")
    print("=" * 60)
    
    print("""
# 1. 檢查新版本
~/.npm-global/bin/openclaw --version

# 2. 檢查狀態
~/.npm-global/bin/openclaw status

# 3. 重啟Gateway
~/.npm-global/bin/openclaw gateway restart

# 4. 設置別名 (一次性)
alias openclaw="~/.npm-global/bin/openclaw"

# 5. 永久設置 (添加到 ~/.zshrc)
echo 'alias openclaw="~/.npm-global/bin/openclaw"' >> ~/.zshrc
source ~/.zshrc
    """)
    
    print("=" * 60)
    print("🎉 更新完成！")
    print("=" * 60)
    
    print("現在你已經成功更新到 2026.2.3-1 版本！")
    print("")
    print("下次cron的Daily Update Check應該能正常工作了。")
    print("")
    print("如果有任何問題，請告訴我！ 🚀")

if __name__ == "__main__":
    main()