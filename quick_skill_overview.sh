#!/bin/bash
# 快速了解6個skill的基本功能

echo "🚀 6個Skill快速功能了解"
echo "=" * 60

SKILLS_DIR="/Users/gordonlui/.openclaw/skills"

echo "📁 已安裝的skill:"
ls -la "$SKILLS_DIR/"
echo ""

# 1. agent-browser
echo "1. 🕸️ agent-browser-clawdbot (瀏覽器自動化)"
echo "   -----------------------------------------"
if [ -f "$SKILLS_DIR/agent-browser-clawdbot/SKILL.md" ]; then
    grep -E "^#|^##|^-|^•" "$SKILLS_DIR/agent-browser-clawdbot/SKILL.md" | head -10
    echo "   核心功能: 網頁自動化、數據抓取、會話管理"
    echo "   應用場景: 加密貨幣數據收集、新聞抓取、市場監控"
else
    echo "   ❌ 文檔未找到"
fi
echo ""

# 2. pptx-creatord
echo "2. 📽️ pptx-creatord (PowerPoint生成)"
echo "   ---------------------------------"
if [ -f "$SKILLS_DIR/pptx-creatord/SKILL.md" ]; then
    grep -E "^#|^##|^-|^•" "$SKILLS_DIR/pptx-creatord/SKILL.md" | head -10
    echo "   核心功能: PPT自動生成、模板管理、簡報創建"
    echo "   應用場景: 學習報告、交易總結、項目展示"
else
    echo "   ❌ 文檔未找到"
fi
echo ""

# 3. ai-humanizer
echo "3. 🇨🇳 ai-humanizer (中文人性化)"
echo "   -----------------------------"
if [ -f "$SKILLS_DIR/ai-humanizer/SKILL.md" ]; then
    grep -E "^#|^##|^-|^•" "$SKILLS_DIR/ai-humanizer/SKILL.md" | head -10
    echo "   核心功能: 文本人性化、語氣優化、本地化處理"
    echo "   應用場景: 中文報告優化、溝通語氣調整、內容本地化"
else
    echo "   ❌ 文檔未找到"
fi
echo ""

# 4. thought-to-excalidraw
echo "4. 📊 thought-to-excalidraw (圖表生成)"
echo "   -----------------------------------"
if [ -f "$SKILLS_DIR/thought-to-excalidraw/SKILL.md" ]; then
    grep -E "^#|^##|^-|^•" "$SKILLS_DIR/thought-to-excalidraw/SKILL.md" | head -10
    echo "   核心功能: 思維導圖、流程圖、架構圖生成"
    echo "   應用場景: 學習進度圖表、技術分析圖、系統架構圖"
else
    echo "   ❌ 文檔未找到"
fi
echo ""

# 5. continuous-learning
echo "5. 🚢 continuous-learning (學習系統)"
echo "   ---------------------------------"
if [ -f "$SKILLS_DIR/continuous-learning/SKILL.md" ]; then
    grep -E "^#|^##|^-|^•" "$SKILLS_DIR/continuous-learning/SKILL.md" | head -10
    echo "   核心功能: 持續學習、知識管理、進度跟踪"
    echo "   應用場景: 學習計劃管理、知識庫構建、進度監控"
else
    echo "   ❌ 文檔未找到"
fi
echo ""

# 6. virtually-us
echo "6. 👤 virtually-us (個人助理)"
echo "   --------------------------"
if [ -f "$SKILLS_DIR/virtually-us/SKILL.md" ]; then
    grep -E "^#|^##|^-|^•" "$SKILLS_DIR/virtually-us/SKILL.md" | head -10
    echo "   核心功能: 個人助理、日程管理、任務提醒"
    echo "   應用場景: 學習提醒、交易提醒、日常任務管理"
else
    echo "   ❌ 文檔未找到"
fi
echo ""

echo "🎯 在加密貨幣學習系統中的整合應用:"
echo "=================================="
echo "1. 數據收集層: agent-browser"
echo "   • 自動收集市場價格"
echo "   • 抓取新聞資訊"
echo "   • 監控社交媒體"
echo ""
echo "2. 可視化層: thought-to-excalidraw + pptx"
echo "   • 生成學習進度圖表"
echo "   • 創建技術分析圖"
echo "   • 製作報告簡報"
echo ""
echo "3. 優化層: ai-humanizer"
echo "   • 優化中文報告文本"
echo "   • 調整溝通語氣"
echo "   • 本地化內容"
echo ""
echo "4. 管理層: continuous-learning"
echo "   • 跟踪學習進度"
echo "   • 管理知識庫"
echo "   • 規劃學習路徑"
echo ""
echo "5. 交互層: virtually-us"
echo "   • 發送學習提醒"
echo "   • 通知交易機會"
echo "   • 日常任務管理"
echo ""

echo "🚀 下一步行動建議:"
echo "=================="
echo "1. 快速測試每個skill的核心功能"
echo "2. 創建簡單的整合示例"
echo "3. 規劃具體的應用場景"
echo "4. 制定詳細的學習計劃"
echo ""

echo "💡 超進化原則: 先進化，再改善工作"
echo "現在已經完成基礎進化，可以開始改善工作流程了！"
echo ""

echo "📋 可用命令:"
echo "-----------"
echo "• 查看詳細文檔: cat \$SKILLS_DIR/<skill-name>/SKILL.md"
echo "• 測試基本功能: 參考各skill的示例"
echo "• 創建整合腳本: 結合加密貨幣學習系統"
echo ""

echo "🎉 超進化第一階段完成！開始第二階段：改善工作！"