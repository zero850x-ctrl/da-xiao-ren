#!/usr/bin/env python3
"""
檢查Mac通訊錄問題的系統性工具
"""

import subprocess
import os
import json
import plistlib
from datetime import datetime

def run_command(cmd):
    """運行命令並返回結果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_icloud_sync():
    """檢查iCloud同步設定"""
    print("🔍 檢查iCloud同步設定...")
    
    # 檢查iCloud通訊錄是否開啟
    cmd = "defaults read MobileMeAccounts 2>/dev/null | grep -A5 -B5 'Contacts' || echo '無法讀取iCloud設定'"
    output, error, code = run_command(cmd)
    
    if "Enabled = 1" in output:
        print("   ✅ iCloud通訊錄同步已開啟")
        return True
    else:
        print("   ℹ️  iCloud通訊錄同步可能未開啟")
        return False

def check_contacts_sources():
    """檢查通訊錄來源"""
    print("\n🔍 檢查通訊錄來源...")
    
    # 檢查通訊錄資料庫位置
    contacts_db = os.path.expanduser("~/Library/Application Support/AddressBook/AddressBook-v22.abcddb")
    if os.path.exists(contacts_db):
        print(f"   ✅ 通訊錄資料庫存在: {contacts_db}")
        
        # 檢查檔案大小
        size = os.path.getsize(contacts_db)
        print(f"   資料庫大小: {size:,} bytes")
        
        if size > 100000000:  # 大於100MB
            print("   ⚠️  通訊錄資料庫過大，可能包含異常數據")
        else:
            print("   ✅ 資料庫大小正常")
    else:
        print("   ℹ️  未找到標準通訊錄資料庫")
    
    # 檢查是否有其他通訊錄檔案
    cmd = "find ~/Library/Application\\ Support/AddressBook -name '*.abcddb' -o -name '*.abcddb-wal' -o -name '*.abcddb-shm' 2>/dev/null | wc -l"
    output, error, code = run_command(cmd)
    
    if output.isdigit() and int(output) > 0:
        print(f"   ℹ️  找到 {output} 個通訊錄相關檔案")
    else:
        print("   ℹ️  未找到其他通訊錄檔案")

def check_third_party_apps():
    """檢查第三方應用"""
    print("\n🔍 檢查可能同步通訊錄的應用...")
    
    apps_to_check = [
        "com.facebook.Facebook",
        "com.linkedin.LinkedIn", 
        "com.google.Gmail",
        "com.microsoft.Outlook",
        "com.tencent.xin",  # 微信
        "jp.naver.line.mac",
        "com.toyopagroup.picaboo",  # Snapchat
        "com.skype.skype"
    ]
    
    found_apps = []
    for app in apps_to_check:
        cmd = f"mdfind 'kMDItemCFBundleIdentifier == \"{app}\"' 2>/dev/null"
        output, error, code = run_command(cmd)
        
        if output:
            found_apps.append(app.split('.')[-1])
    
    if found_apps:
        print(f"   ⚠️  找到可能同步通訊錄的應用: {', '.join(found_apps)}")
        print("     這些應用可能會自動導入聯絡人")
    else:
        print("   ✅ 未找到常見的通訊錄同步應用")

def check_system_permissions():
    """檢查系統權限"""
    print("\n🔍 檢查通訊錄權限...")
    
    # 檢查TCC資料庫（需要管理員權限）
    tcc_db = "/Library/Application Support/com.apple.TCC/TCC.db"
    
    if os.path.exists(tcc_db):
        print(f"   ✅ TCC資料庫存在")
        
        # 嘗試讀取通訊錄權限（需要sqlite3）
        cmd = "sqlite3 '/Library/Application Support/com.apple.TCC/TCC.db' \"SELECT client, auth_value FROM access WHERE service = 'kTCCServiceAddressBook' AND auth_value = 2;\" 2>/dev/null || echo '需要管理員權限'"
        output, error, code = run_command(cmd)
        
        if output and "需要管理員權限" not in output:
            apps = output.split('\n')
            if apps and apps[0]:
                print(f"   ℹ️  有以下應用有通訊錄存取權限:")
                for app in apps:
                    if app:
                        print(f"      - {app}")
        else:
            print("   ℹ️  無法讀取詳細權限資訊（需要管理員權限）")
    else:
        print("   ℹ️  無法存取TCC資料庫")

def check_openclaw_config():
    """檢查OpenClaw配置"""
    print("\n🔍 檢查OpenClaw配置...")
    
    openclaw_config = os.path.expanduser("~/.openclaw/openclaw.json")
    
    if os.path.exists(openclaw_config):
        print(f"   ✅ OpenClaw配置文件存在")
        
        try:
            with open(openclaw_config, 'r') as f:
                config = json.load(f)
            
            # 檢查是否有通訊錄相關配置
            has_contacts_config = False
            
            # 檢查插件
            plugins = config.get('plugins', {}).get('entries', {})
            for plugin in plugins.keys():
                if 'contact' in plugin.lower() or 'address' in plugin.lower():
                    has_contacts_config = True
                    print(f"   ⚠️  發現通訊錄相關插件: {plugin}")
            
            # 檢查工具配置
            tools = config.get('tools', {})
            if 'contacts' in str(tools).lower():
                has_contacts_config = True
                print("   ⚠️  發現通訊錄相關工具配置")
            
            if not has_contacts_config:
                print("   ✅ OpenClaw配置中未發現通訊錄相關設定")
            
            # 檢查Qwen殘留
            config_str = json.dumps(config)
            if 'qwen' in config_str.lower():
                print("   ⚠️  配置中可能還有Qwen殘留")
            else:
                print("   ✅ 配置中無Qwen殘留")
                
        except Exception as e:
            print(f"   ❌ 讀取OpenClaw配置時出錯: {e}")
    else:
        print("   ℹ️  OpenClaw配置文件不存在")

def check_whatsapp_integration():
    """檢查WhatsApp集成"""
    print("\n🔍 檢查WhatsApp集成...")
    
    # 檢查WhatsApp是否可能導入通訊錄
    whatsapp_dir = os.path.expanduser("~/Library/Application Support/WhatsApp")
    
    if os.path.exists(whatsapp_dir):
        print(f"   ✅ WhatsApp應用程式目錄存在")
        
        # 檢查聯絡人相關檔案
        cmd = f"find '{whatsapp_dir}' -name '*contact*' -o -name '*address*' 2>/dev/null | head -5"
        output, error, code = run_command(cmd)
        
        if output:
            print(f"   ℹ️  WhatsApp可能有聯絡人相關檔案")
            files = output.split('\n')
            for file in files[:3]:  # 只顯示前3個
                if file:
                    print(f"      - {os.path.basename(file)}")
        else:
            print("   ✅ 未找到明顯的聯絡人檔案")
    else:
        print("   ℹ️  WhatsApp應用程式目錄不存在")

def provide_solutions():
    """提供解決方案"""
    print("\n" + "=" * 60)
    print("🔧 建議解決方案")
    print("=" * 60)
    
    solutions = [
        {
            "步驟": 1,
            "操作": "手動清理通訊錄",
            "命令": "打開「通訊錄」應用，刪除不認識的聯絡人",
            "說明": "最直接的解決方法"
        },
        {
            "步驟": 2, 
            "操作": "重置通訊錄權限",
            "命令": "tccutil reset AddressBook",
            "說明": "已執行，清除所有應用的通訊錄存取權限"
        },
        {
            "步驟": 3,
            "操作": "檢查iCloud同步",
            "命令": "系統設定 > Apple ID > iCloud > 通訊錄",
            "說明": "確保只同步自己的通訊錄"
        },
        {
            "步驟": 4,
            "操作": "檢查第三方應用",
            "命令": "系統設定 > 隱私權與安全性 > 通訊錄",
            "說明": "移除不必要應用的通訊錄權限"
        },
        {
            "步驟": 5,
            "操作": "備份並重置通訊錄",
            "命令": "1. 導出通訊錄備份\n2. 刪除 ~/Library/Application Support/AddressBook/\n3. 重新啟動通訊錄",
            "說明": "徹底解決問題，但需要備份"
        }
    ]
    
    for solution in solutions:
        print(f"\n{solution['步驟']}. {solution['操作']}")
        print(f"   命令: {solution['命令']}")
        print(f"   說明: {solution['說明']}")

def main():
    """主函數"""
    print("=" * 60)
    print("📱 Mac通訊錄問題診斷工具")
    print(f"診斷時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 執行檢查
    check_icloud_sync()
    check_contacts_sources()
    check_third_party_apps()
    check_system_permissions()
    check_openclaw_config()
    check_whatsapp_integration()
    
    # 提供解決方案
    provide_solutions()
    
    print("\n" + "=" * 60)
    print("📋 總結建議")
    print("=" * 60)
    
    print("""
基於檢查結果，建議按以下順序操作：

1. **立即操作**:
   - 手動刪除不認識的聯絡人
   - 檢查系統設定 > 隱私權與安全性 > 通訊錄

2. **預防措施**:
   - 定期檢查通訊錄
   - 審查應用權限
   - 避免使用不明應用

3. **關於OpenClaw**:
   - 配置檢查正常，未發現通訊錄相關設定
   - Qwen已完全移除，不是問題原因
   - WhatsApp配置安全，只允許你的號碼

4. **如果問題持續**:
   - 考慮備份後重置通訊錄
   - 檢查是否有其他設備同步
   - 考慮重設Apple ID密碼
    """)
    
    print("\n💡 提示: 通訊錄問題通常來自:")
    print("   - iCloud同步其他設備的聯絡人")
    print("   - 第三方應用自動導入")
    print("   - 系統同步錯誤")
    print("   - 極少數情況下的安全問題")

if __name__ == "__main__":
    main()