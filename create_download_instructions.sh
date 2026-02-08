#!/bin/bash

echo "📥 OpenClaw安裝文件下載指南"
echo "========================================"
echo ""
echo "由於郵件附件限制，這裡提供多種獲取文件的方法："
echo ""

echo "方法1: 直接從我的系統複製"
echo "----------------------------------------"
echo "文件位置在我的Mac上："
echo "1. 安裝指南: /Users/gordonlui/.openclaw/workspace/OpenClaw_Mac_Mini_Installation_Guide.md"
echo "2. 安裝腳本: /Users/gordonlui/.openclaw/workspace/openclaw_quick_install.sh"
echo ""

echo "方法2: 使用scp命令複製（如果網絡相通）"
echo "----------------------------------------"
echo "在你的朋友電腦上執行："
echo "scp gordonlui@你的IP:/Users/gordonlui/.openclaw/workspace/openclaw_quick_install.sh ."
echo "scp gordonlui@你的IP:/Users/gordonlui/.openclaw/workspace/OpenClaw_Mac_Mini_Installation_Guide.md ."
echo ""

echo "方法3: 從郵件內容創建文件"
echo "----------------------------------------"
echo "步驟："
echo "1. 打開郵件，複製腳本內容"
echo "2. 在Terminal中執行："
echo "   cat > openclaw_quick_install.sh << 'EOF'"
echo "   [在此處粘貼內容]"
echo "   EOF"
echo "3. 給予執行權限："
echo "   chmod +x openclaw_quick_install.sh"
echo "4. 同樣方法創建指南文件"
echo ""

echo "方法4: 使用curl下載（如果我有HTTP服務）"
echo "----------------------------------------"
echo "# 臨時啟動HTTP服務（在我的電腦上）"
echo "cd /Users/gordonlui/.openclaw/workspace"
echo "python3 -m http.server 8000"
echo ""
echo "# 在你的朋友電腦上下載"
echo "curl http://你的IP:8000/openclaw_quick_install.sh -o openclaw_quick_install.sh"
echo "curl http://你的IP:8000/OpenClaw_Mac_Mini_Installation_Guide.md -o OpenClaw_Mac_Mini_Installation_Guide.md"
echo ""

echo "方法5: 通過雲存儲分享"
echo "----------------------------------------"
echo "1. 將文件上傳到Google Drive、Dropbox等"
echo "2. 分享下載鏈接"
echo "3. 你的朋友從鏈接下載"
echo ""

echo "🎯 推薦方法：方法3（從郵件內容創建）"
echo "========================================"
echo ""
echo "快速創建腳本的命令："
echo "----------------------------------------"
cat << 'EOF'
cat > openclaw_quick_install.sh << 'SCRIPT_EOF'
#!/bin/bash

set -e

echo "🚀 OpenClaw Mac Mini 快速安裝腳本"
echo "========================================"
# ... [腳本內容]
SCRIPT_EOF

chmod +x openclaw_quick_install.sh
EOF
echo ""
echo "然後運行： ./openclaw_quick_install.sh"
echo ""
echo "========================================"
echo "✅ 選擇最適合的方法即可！"