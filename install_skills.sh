#!/bin/bash
# 安裝和學習OpenClaw skill

echo "🚀 OpenClaw Skill安裝程序"
echo "=" * 50

# 創建skill目錄
SKILLS_DIR="/Users/gordonlui/.openclaw/skills"
mkdir -p "$SKILLS_DIR"

echo "📁 Skill目錄: $SKILLS_DIR"
echo ""

# 顯示可安裝的skill
echo "🎯 可安裝的Skill列表:"
echo "1. agent-browser-clawdbot (瀏覽器自動化)"
echo "2. pptx-creatord (PowerPoint生成)"
echo "3. ai-humanizer (文本人性化)"
echo "4. thought-to-excalidraw (圖表生成)"
echo "5. continuous-learning (持續學習)"
echo "6. virtually-us (個人助理)"
echo ""

# 安裝函數
install_skill() {
    local skill_name=$1
    local display_name=$2
    
    echo "📦 安裝 $display_name ($skill_name)..."
    
    # 檢查是否已安裝
    if [ -d "$SKILLS_DIR/$skill_name" ]; then
        echo "✅ $display_name 已安裝"
        return 0
    fi
    
    # 安裝skill
    echo "正在從clawhub安裝..."
    npx clawhub install "$skill_name" --dir "$SKILLS_DIR" 2>&1 | tail -20
    
    if [ $? -eq 0 ] && [ -d "$SKILLS_DIR/$skill_name" ]; then
        echo "✅ $display_name 安裝成功"
        
        # 檢查SKILL.md文件
        if [ -f "$SKILLS_DIR/$skill_name/SKILL.md" ]; then
            echo "📖 找到文檔: $SKILLS_DIR/$skill_name/SKILL.md"
        fi
        
        return 0
    else
        echo "❌ $display_name 安裝失敗"
        return 1
    fi
}

# 學習函數
learn_skill() {
    local skill_name=$1
    local display_name=$2
    
    echo ""
    echo "🧠 學習 $display_name..."
    echo "-" * 40
    
    SKILL_FILE="$SKILLS_DIR/$skill_name/SKILL.md"
    
    if [ -f "$SKILL_FILE" ]; then
        # 顯示skill基本信息
        echo "📋 Skill信息:"
        head -20 "$SKILL_FILE" | grep -E "^#|^##|^###|^-|^•"
        
        # 創建學習筆記
        NOTE_FILE="/Users/gordonlui/.openclaw/workspace/learn_${skill_name}.md"
        {
            echo "# 📚 學習筆記: $display_name"
            echo "安裝時間: $(date)"
            echo ""
            echo "## 📋 基本信息"
            echo "- Skill名稱: $skill_name"
            echo "- 顯示名稱: $display_name"
            echo "- 安裝路徑: $SKILLS_DIR/$skill_name"
            echo ""
            echo "## 🎯 主要功能"
            # 從SKILL.md提取功能描述
            grep -A 5 -i "功能\|feature\|purpose" "$SKILL_FILE" | head -10
            echo ""
            echo "## 🚀 使用方法"
            # 從SKILL.md提取使用方法
            grep -A 5 -i "使用\|usage\|example" "$SKILL_FILE" | head -10
            echo ""
            echo "## 💡 應用場景"
            echo "1. 加密貨幣學習系統"
            echo "2. 數據收集和分析"
            echo "3. 報告生成"
            echo "4. 自動化任務"
            echo ""
            echo "## 🔧 整合計劃"
            echo "- [ ] 了解基本功能"
            echo "- [ ] 測試示例"
            echo "- [ ] 整合到現有系統"
            echo "- [ ] 優化工作流程"
        } > "$NOTE_FILE"
        
        echo "✅ 學習筆記已創建: $NOTE_FILE"
        
    else
        echo "❌ 找不到SKILL.md文件"
        echo "嘗試查看目錄內容:"
        ls -la "$SKILLS_DIR/$skill_name/" 2>/dev/null | head -10
    fi
}

# 主菜單
echo "請選擇操作:"
echo "1. 安裝所有skill"
echo "2. 安裝agent-browser (優先)"
echo "3. 安裝pptx相關"
echo "4. 安裝ai-humanizer"
echo "5. 查看已安裝skill"
echo "6. 學習已安裝skill"
echo ""

read -p "請輸入選擇 (1-6): " choice

case $choice in
    1)
        echo "🔄 安裝所有skill..."
        install_skill "agent-browser-clawdbot" "Agent Browser"
        install_skill "pptx-creatord" "PowerPoint Creator"
        install_skill "ai-humanizer" "AI Humanizer"
        install_skill "thought-to-excalidraw" "Diagram Generator"
        install_skill "continuous-learning" "Continuous Learning"
        install_skill "virtually-us" "Personal Assistant"
        ;;
    2)
        echo "🔄 安裝agent-browser..."
        install_skill "agent-browser-clawdbot" "Agent Browser"
        learn_skill "agent-browser-clawdbot" "Agent Browser"
        ;;
    3)
        echo "🔄 安裝pptx相關..."
        install_skill "pptx-creatord" "PowerPoint Creator"
        learn_skill "pptx-creatord" "PowerPoint Creator"
        ;;
    4)
        echo "🔄 安裝ai-humanizer..."
        install_skill "ai-humanizer" "AI Humanizer"
        learn_skill "ai-humanizer" "AI Humanizer"
        ;;
    5)
        echo "📁 已安裝的skill:"
        ls -la "$SKILLS_DIR/" 2>/dev/null || echo "❌ 沒有安裝任何skill"
        ;;
    6)
        echo "🧠 學習已安裝skill..."
        for skill_dir in "$SKILLS_DIR"/*; do
            if [ -d "$skill_dir" ]; then
                skill_name=$(basename "$skill_dir")
                echo "學習 $skill_name..."
                learn_skill "$skill_name" "$skill_name"
            fi
        done
        ;;
    *)
        echo "❌ 無效選擇"
        ;;
esac

# 總結
echo ""
echo "🎉 Skill安裝/學習完成"
echo ""
echo "📋 下一步:"
echo "1. 閱讀學習筆記"
echo "2. 測試skill功能"
echo "3. 整合到加密貨幣學習系統"
echo "4. 實踐應用"
echo ""
echo "💡 提示:"
echo "• 每個skill都有SKILL.md文檔"
echo "• 可以隨時重新運行此腳本"
echo "• 需要幫助請WhatsApp"
echo ""
echo "🚀 開始你的skill學習之旅！"