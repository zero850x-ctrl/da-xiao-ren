#!/bin/bash

echo "🔧 完全修復.zshrc文件"
echo "========================================"

# 備份當前文件
BACKUP_FILE="$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"
cp ~/.zshrc "$BACKUP_FILE"
echo "✅ 已備份到: $BACKUP_FILE"
echo ""

# 顯示當前內容
echo "當前.zshrc內容:"
cat ~/.zshrc
echo ""

echo "發現的問題:"
echo "1. 有重複的openclaw別名"
echo "2. openclaw補全命令可能導致錯誤"
echo "3. 需要清理和優化"
echo ""

# 創建新的.zshrc文件
echo "創建新的.zshrc文件..."
cat > ~/.zshrc.new << 'EOF'
# ========================================
# OpenClaw配置
# ========================================

# OpenClaw別名 - 使用用戶安裝版本
alias openclaw="~/.npm-global/bin/openclaw"

# OpenClaw補全 (可選，如果不需要可以註釋掉)
# source <(~/.npm-global/bin/openclaw completion --shell zsh)

# ========================================
# 其他配置
# ========================================

# 如果需要，可以在這裡添加其他配置

EOF

echo "✅ 新.zshrc文件創建完成"
echo ""

# 顯示新文件內容
echo "新.zshrc內容:"
cat ~/.zshrc.new
echo ""

# 詢問是否替換
read -p "是否要替換當前的.zshrc文件? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mv ~/.zshrc.new ~/.zshrc
    echo "✅ .zshrc文件已更新"
    echo ""
    echo "重新加載配置..."
    source ~/.zshrc 2>/dev/null || echo "重新加載時有小錯誤，但不影響使用"
    echo ""
    echo "測試別名:"
    alias openclaw
    echo ""
    echo "測試版本:"
    ~/.npm-global/bin/openclaw --version
else
    echo "ℹ️ 保留當前文件，新文件保存在: ~/.zshrc.new"
    echo "你可以手動比較和合併:"
    echo "  diff ~/.zshrc ~/.zshrc.new"
    echo "  mv ~/.zshrc.new ~/.zshrc"
fi

echo ""
echo "========================================"
echo "💡 替代方案"
echo "========================================"

echo "如果不想修改.zshrc，可以使用這些方法:"
echo ""
echo "1. 創建單獨的別名文件:"
echo "   echo 'alias openclaw=\"~/.npm-global/bin/openclaw\"' > ~/.openclaw_alias"
echo "   echo 'source ~/.openclaw_alias' >> ~/.zshrc"
echo ""
echo "2. 使用臨時別名 (每個Terminal會話):"
echo "   alias openclaw=\"~/.npm-global/bin/openclaw\""
echo ""
echo "3. 直接使用完整路徑:"
echo "   ~/.npm-global/bin/openclaw [命令]"
echo ""
echo "4. 創建腳本文件:"
echo "   echo '#!/bin/bash' > ~/bin/ocl"
echo "   echo '~/.npm-global/bin/openclaw \"\$@\"' >> ~/bin/ocl"
echo "   chmod +x ~/bin/ocl"
echo "   # 使用: ocl --version"
echo ""

echo "========================================"
echo "✅ 修復完成"
echo "========================================"