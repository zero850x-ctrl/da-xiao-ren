#!/bin/bash

echo "🔍 檢查OpenClaw版本狀態..."
echo "========================================"

# 檢查當前版本
echo "1. 當前運行版本:"
openclaw --version
echo ""

# 檢查系統安裝版本
echo "2. 系統安裝版本 (/usr/local/lib/node_modules/openclaw/):"
if [ -f "/usr/local/lib/node_modules/openclaw/package.json" ]; then
    cat /usr/local/lib/node_modules/openclaw/package.json | grep '"version"' | head -1
else
    echo "   ❌ 系統安裝不存在"
fi
echo ""

# 檢查用戶安裝版本
echo "3. 用戶安裝版本 (~/.npm-global/lib/node_modules/openclaw/):"
if [ -f "$HOME/.npm-global/lib/node_modules/openclaw/package.json" ]; then
    cat "$HOME/.npm-global/lib/node_modules/openclaw/package.json" | grep '"version"' | head -1
else
    echo "   ❌ 用戶安裝不存在"
fi
echo ""

# 檢查npm最新版本
echo "4. npm最新可用版本:"
npm view openclaw version
echo ""

# 檢查更新狀態
echo "5. OpenClaw狀態檢查:"
openclaw status | grep -A2 "Update"
echo ""

echo "========================================"
echo "📋 版本不一致問題分析"
echo "========================================"

echo "問題:"
echo "1. 系統安裝 (v2026.2.1) 和用戶安裝 (v2026.2.3-1) 版本不一致"
echo "2. Gateway服務使用系統安裝版本"
echo "3. 需要更新系統安裝以獲得最新功能"
echo ""

echo "解決方案:"
echo "1. 需要管理員權限更新系統安裝"
echo "2. 命令: sudo npm install -g openclaw@latest"
echo "3. 或者: 使用系統包管理器更新"
echo ""

echo "⚠️  注意: 更新需要輸入管理員密碼"
echo "========================================"
echo ""

# 詢問是否要更新
read -p "是否要嘗試更新系統安裝? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在更新系統安裝..."
    echo "請輸入管理員密碼:"
    sudo npm install -g openclaw@latest
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 更新成功!"
        echo ""
        echo "重啟Gateway服務..."
        openclaw gateway restart
        sleep 3
        echo ""
        echo "檢查新版本:"
        openclaw --version
        echo ""
        echo "🎉 更新完成!"
    else
        echo ""
        echo "❌ 更新失敗，請手動執行:"
        echo "   sudo npm install -g openclaw@latest"
    fi
else
    echo ""
    echo "ℹ️  跳過更新，當前版本繼續使用"
    echo "如需更新請手動執行:"
    echo "   sudo npm install -g openclaw@latest"
fi

echo ""
echo "========================================"
echo "更新腳本完成"