#!/bin/bash
# agent-browser測試腳本

echo "🧪 agent-browser測試腳本"
echo "=" * 50

# 設置PATH
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

echo "1. 檢查agent-browser安裝..."
if command -v agent-browser &> /dev/null; then
    echo "✅ agent-browser已安裝"
    agent-browser --version
else
    echo "❌ agent-browser未找到，使用完整路徑"
    AGENT_BROWSER="/Users/gordonlui/.npm-global/bin/agent-browser"
    if [ -f "$AGENT_BROWSER" ]; then
        echo "✅ 找到agent-browser: $AGENT_BROWSER"
        $AGENT_BROWSER --version
    else
        echo "❌ agent-browser未安裝"
        exit 1
    fi
fi

echo ""
echo "2. 檢查瀏覽器依賴..."
if agent-browser install --check 2>/dev/null | grep -q "installed"; then
    echo "✅ 瀏覽器依賴已安裝"
else
    echo "⚠️  瀏覽器依賴未安裝或正在安裝中"
    echo "   運行: agent-browser install"
fi

echo ""
echo "3. 簡單功能測試..."
echo "創建測試腳本..."

# 創建測試Python腳本
TEST_SCRIPT="/Users/gordonlui/.openclaw/workspace/test_crypto_scraper.py"

cat > "$TEST_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
agent-browser加密貨幣數據收集測試
"""

import subprocess
import json
import os
import time

def run_agent_browser_command(cmd_args):
    """運行agent-browser命令"""
    agent_browser_path = "/Users/gordonlui/.npm-global/bin/agent-browser"
    
    if not os.path.exists(agent_browser_path):
        print(f"❌ agent-browser未找到: {agent_browser_path}")
        return None
    
    cmd = [agent_browser_path] + cmd_args
    print(f"執行: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 命令執行成功")
            return result.stdout
        else:
            print(f"❌ 命令執行失敗: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ 命令超時")
        return None
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return None

def test_basic_navigation():
    """測試基本導航"""
    print("\n🧪 測試1: 基本導航")
    print("-" * 40)
    
    # 打開測試頁面
    output = run_agent_browser_command(["open", "https://httpbin.org/html"])
    
    if output:
        print("✅ 頁面打開成功")
        
        # 獲取頁面快照
        snapshot = run_agent_browser_command(["snapshot", "-i", "--json"])
        
        if snapshot:
            try:
                data = json.loads(snapshot)
                if data.get("success"):
                    print("✅ 頁面快照成功")
                    refs = data.get("data", {}).get("refs", {})
                    print(f"找到 {len(refs)} 個可交互元素")
                    
                    # 顯示前幾個元素
                    for i, (ref, info) in enumerate(list(refs.items())[:3]):
                        print(f"  {ref}: {info.get('role', 'N/A')} - {info.get('name', 'N/A')}")
                    
                    return True
                else:
                    print("❌ 快照失敗")
            except json.JSONDecodeError:
                print("❌ JSON解析失敗")
    
    return False

def test_crypto_data_collection():
    """測試加密貨幣數據收集"""
    print("\n🧪 測試2: 加密貨幣數據收集模擬")
    print("-" * 40)
    
    # 注意: 實際測試需要處理反爬蟲機制
    # 這裡創建一個模擬測試
    
    print("📊 模擬加密貨幣數據收集工作流:")
    print("1. 打開交易所網站")
    print("2. 獲取頁面結構")
    print("3. 定位價格元素")
    print("4. 提取價格數據")
    print("5. 保存到文件")
    
    # 創建模擬數據收集腳本
    script_content = '''
# agent-browser加密貨幣數據收集示例
# 實際使用時需要調整選擇器和等待邏輯

# 1. 打開幣安網站
agent-browser open https://www.binance.com

# 2. 等待頁面加載
agent-browser wait --load networkidle

# 3. 獲取頁面快照
agent-browser snapshot -i --json > snapshot.json

# 4. 分析快照，找到價格元素（需要人工或AI分析）
# 通常價格元素有特定的class或data屬性

# 5. 提取價格數據
# agent-browser get text @e123 --json

# 6. 保存數據
# 將提取的數據保存到CSV或數據庫
'''
    
    script_file = "/Users/gordonlui/.openclaw/workspace/crypto_data_collector.sh"
    with open(script_file, "w") as f:
        f.write(script_content)
    
    print(f"✅ 創建數據收集腳本: {script_file}")
    print("💡 注意: 實際網站可能有反爬蟲機制，需要謹慎測試")
    
    return True

def create_learning_examples():
    """創建學習示例"""
    print("\n📚 創建學習示例")
    print("-" * 40)
    
    examples = {
        "basic_navigation.sh": """#!/bin/bash
# 基本導航示例
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

echo "1. 打開網頁"
agent-browser open https://example.com

echo "2. 獲取頁面快照"
agent-browser snapshot -i --json > snapshot.json

echo "3. 查看頁面標題"
agent-browser get title --json

echo "✅ 基本導航完成"
""",
        
        "element_interaction.sh": """#!/bin/bash
# 元素交互示例
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

echo "1. 打開測試表單頁面"
agent-browser open https://httpbin.org/forms/post

echo "2. 等待頁面加載"
agent-browser wait --load networkidle

echo "3. 獲取快照找到表單元素"
agent-browser snapshot -i --json > form_snapshot.json

echo "💡 查看form_snapshot.json找到元素引用"
echo "然後可以使用:"
echo "  agent-browser fill @e1 'John Doe'"
echo "  agent-browser click @e2"
""",
        
        "crypto_price_check.sh": """#!/bin/bash
# 加密貨幣價格檢查示例（概念）
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

echo "📈 加密貨幣價格檢查工作流"
echo ""
echo "步驟1: 分析目標網站結構"
echo "  agent-browser open https://www.coingecko.com"
echo "  agent-browser snapshot -i --json > coingecko_snapshot.json"
echo ""
echo "步驟2: 識別價格元素"
echo "  分析JSON文件，找到價格相關的元素引用"
echo ""
echo "步驟3: 創建數據提取腳本"
echo "  agent-browser get text @price_element --json"
echo ""
echo "步驟4: 設置定時任務"
echo "  使用cron定期運行數據收集"
echo ""
echo "⚠️  注意: 尊重網站服務條款，避免過度請求"
"""
    }
    
    for filename, content in examples.items():
        filepath = f"/Users/gordonlui/.openclaw/workspace/{filename}"
        with open(filepath, "w") as f:
            f.write(content)
        os.chmod(filepath, 0o755)
        print(f"✅ 創建示例: {filename}")
    
    return True

def main():
    print("🚀 agent-browser學習和測試")
    print("=" * 50)
    
    # 測試基本功能
    test_basic_navigation()
    
    # 創建加密貨幣數據收集示例
    test_crypto_data_collection()
    
    # 創建學習示例
    create_learning_examples()
    
    print("\n" + "=" * 50)
    print("🎉 agent-browser測試完成")
    print("=" * 50)
    
    print("\n📁 創建的文件:")
    print("• test_crypto_scraper.py - 測試腳本")
    print("• crypto_data_collector.sh - 數據收集腳本")
    print("• basic_navigation.sh - 基本導航示例")
    print("• element_interaction.sh - 元素交互示例")
    print("• crypto_price_check.sh - 加密貨幣價格檢查示例")
    
    print("\n🚀 下一步:")
    print("1. 完成瀏覽器依賴安裝")
    print("2. 運行測試腳本")
    print("3. 學習agent-browser命令")
    print("4. 創建實際的數據收集工作流")
    
    print("\n💡 提示:")
    print("• 查看SKILL.md獲取完整文檔")
    print("• 從簡單網站開始測試")
    print("• 逐步增加複雜度")
    print("• 注意網站服務條款")

if __name__ == "__main__":
    main()
EOF

chmod +x "$TEST_SCRIPT"

echo "✅ 創建測試腳本: $TEST_SCRIPT"

echo ""
echo "4. 創建PATH設置腳本..."
PATH_SCRIPT="/Users/gordonlui/.openclaw/workspace/setup_agent_browser_path.sh"

cat > "$PATH_SCRIPT" << 'EOF'
#!/bin/bash
# 設置agent-browser PATH

echo "🔧 設置agent-browser環境變量"

# 添加到當前shell的PATH
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

# 添加到bashrc/zshrc（可選）
SHELL_RC="$HOME/.zshrc"
if [ -f "$SHELL_RC" ]; then
    if ! grep -q "agent-browser" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# agent-browser PATH" >> "$SHELL_RC"
        echo 'export PATH="/Users/gordonlui/.npm-global/bin:$PATH"' >> "$SHELL_RC"
        echo "✅ 已添加到 $SHELL_RC"
    else
        echo "✅ PATH已存在於 $SHELL_RC"
    fi
fi

echo ""
echo "📋 當前設置:"
echo "PATH包含: $PATH"
echo ""
echo "🧪 測試命令:"
if command -v agent-browser &> /dev/null; then
    echo "✅ agent-browser可訪問"
    agent-browser --version
else
    echo "❌ agent-browser不可訪問"
    echo "嘗試使用完整路徑: /Users/gordonlui/.npm-global/bin/agent-browser"
fi

echo ""
echo "💡 使用方法:"
echo "source $0  # 設置當前shell"
echo "./setup_agent_browser_path.sh  # 查看狀態"
EOF

chmod +x "$PATH_SCRIPT"

echo "✅ 創建PATH設置腳本: $PATH_SCRIPT"

echo ""
echo "🎉 測試準備完成"
echo ""
echo "🚀 可用命令:"
echo "1. 運行測試: python3 $TEST_SCRIPT"
echo "2. 設置PATH: source $PATH_SCRIPT"
echo "3. 查看文檔: cat /Users/gordonlui/.openclaw/skills/agent-browser-clawdbot/SKILL.md"
echo ""
echo "⏰ 等待瀏覽器依賴安裝完成後即可開始測試！"