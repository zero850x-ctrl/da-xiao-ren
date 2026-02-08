#!/bin/bash

# ========================================
# OpenClaw Mac Mini 快速安裝腳本
# 版本: 1.0
# 創建日期: 2026-02-07
# ========================================

set -e  # 遇到錯誤時停止

echo "🚀 OpenClaw Mac Mini 快速安裝腳本"
echo "========================================"
echo "這個腳本將自動安裝和配置OpenClaw"
echo "預設使用DeepSeek API"
echo ""

# 檢查是否為macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ 錯誤: 這個腳本只適用於macOS"
    exit 1
fi

# 檢查是否為全新安裝
read -p "這是全新的Mac mini安裝嗎? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  注意: 這個腳本設計用於全新安裝"
    echo "如果系統已有相關軟件，可能會衝突"
    read -p "繼續嗎? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安裝取消"
        exit 0
    fi
fi

# 獲取必要信息
echo ""
echo "📝 請提供以下信息:"
echo "----------------------------------------"

read -p "1. DeepSeek API Key: " DEEPSEEK_API_KEY
read -p "2. 你的手機號碼 (格式: +85212345678): " PHONE_NUMBER
read -p "3. 你的名字 (用於配置): " USER_NAME
read -p "4. 你的郵箱 (可選，用於通知): " USER_EMAIL

echo ""
echo "🔧 開始安裝..."
echo "========================================"

# ========================================
# 第一步：安裝基礎工具
# ========================================
echo "📦 第一步：安裝基礎工具..."
echo "----------------------------------------"

# 檢查並安裝Homebrew
if ! command -v brew &> /dev/null; then
    echo "安裝Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 設置環境變量
    if [[ "$(uname -m)" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew 已安裝"
fi

# 安裝Node.js
if ! command -v node &> /dev/null; then
    echo "安裝Node.js..."
    brew install node
else
    echo "✅ Node.js 已安裝"
fi

# 安裝Git
if ! command -v git &> /dev/null; then
    echo "安裝Git..."
    brew install git
else
    echo "✅ Git 已安裝"
fi

# ========================================
# 第二步：配置npm
# ========================================
echo ""
echo "⚙️  第二步：配置npm..."
echo "----------------------------------------"

# 創建用戶全局目錄
mkdir -p ~/.npm-global

# 配置npm使用用戶目錄
npm config set prefix ~/.npm-global

# 添加到PATH
if ! grep -q "\.npm-global/bin" ~/.zshrc; then
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
fi

# 立即生效
export PATH="$HOME/.npm-global/bin:$PATH"

echo "✅ npm配置完成"

# ========================================
# 第三步：安裝OpenClaw
# ========================================
echo ""
echo "🚀 第三步：安裝OpenClaw..."
echo "----------------------------------------"

# 安裝OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "安裝OpenClaw..."
    npm install -g openclaw@latest
else
    echo "✅ OpenClaw 已安裝"
    echo "更新到最新版本..."
    npm install -g openclaw@latest
fi

# 驗證安裝
OPENCLAW_VERSION=$(openclaw --version 2>/dev/null || echo "未安裝")
echo "OpenClaw版本: $OPENCLAW_VERSION"

# ========================================
# 第四步：創建配置文件
# ========================================
echo ""
echo "📁 第四步：創建配置文件..."
echo "----------------------------------------"

# 創建OpenClaw目錄
mkdir -p ~/.openclaw
mkdir -p ~/.openclaw/workspace
mkdir -p ~/.openclaw/workspace/memory
mkdir -p ~/.openclaw/credentials
mkdir -p ~/.openclaw/logs

# 生成安全Token
SECURE_TOKEN=$(openssl rand -base64 32)

# 創建主配置文件
cat > ~/.openclaw/openclaw.json << EOF
{
  "gateway": {
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "$SECURE_TOKEN"
    }
  },
  "models": {
    "providers": {
      "deepseek": {
        "kind": "openai",
        "baseURL": "https://api.deepseek.com",
        "defaultModel": "deepseek-chat",
        "apiKey": "$DEEPSEEK_API_KEY"
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "provider": "deepseek",
        "id": "deepseek-chat"
      },
      "fallbacks": [
        {
          "provider": "deepseek",
          "id": "deepseek-coder"
        }
      ]
    }
  },
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",
      "groupPolicy": "allowlist",
      "allowFrom": ["$PHONE_NUMBER"],
      "selfChatMode": true,
      "mediaMaxMb": 50
    }
  },
  "tools": {
    "exec": {
      "security": "allowlist",
      "ask": "always"
    },
    "web": {
      "search": {
        "provider": "brave"
      }
    }
  },
  "plugins": {
    "entries": {
      "whatsapp": {
        "enabled": true
      },
      "memory-core": {
        "enabled": true
      }
    }
  }
}
EOF

echo "✅ 配置文件創建完成"

# ========================================
# 第五步：設置文件權限
# ========================================
echo ""
echo "🔒 第五步：設置安全權限..."
echo "----------------------------------------"

# 設置文件權限
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.openclaw/credentials
chmod 700 ~/.openclaw

echo "✅ 文件權限設置完成"

# ========================================
# 第六步：創建用戶文檔
# ========================================
echo ""
echo "👤 第六步：創建用戶文檔..."
echo "----------------------------------------"

# 創建USER.md
cat > ~/.openclaw/workspace/USER.md << EOF
# USER.md - 關於用戶

## 基本信息
- **姓名**: $USER_NAME
- **郵箱**: ${USER_EMAIL:-未提供}
- **手機**: $PHONE_NUMBER
- **時區**: Asia/Hong_Kong
- **設備**: Mac mini

## 偏好設置
- **默認AI模型**: DeepSeek
- **通訊渠道**: WhatsApp
- **安全級別**: 高

## 注意事項
- 定期備份配置文件
- 監控API使用量
- 定期更新軟件
EOF

# 創建SOUL.md
cat > ~/.openclaw/workspace/SOUL.md << EOF
# SOUL.md - AI助手個性設定

## 基本設定
- **名稱**: 久留美 (Kurumi)
- **角色**: 專業AI助手
- **語言**: 中文為主，英文為輔
- **風格**: 專業、友好、高效

## 行為準則
1. 優先使用DeepSeek模型
2. 重視安全性和隱私
3. 提供準確有用的信息
4. 保持專業但友好的態度

## 特殊能力
- 技術問題解決
- 代碼編寫和調試
- 系統管理和配置
- 安全審計和建議
EOF

# 創建AGENTS.md
cat > ~/.openclaw/workspace/AGENTS.md << EOF
# AGENTS.md - 代理配置

## 默認代理
- **主代理**: 使用DeepSeek Chat模型
- **編程代理**: 使用DeepSeek Coder模型
- **備用代理**: DeepSeek Coder (備用)

## 通道配置
- **WhatsApp**: 已啟用，白名單模式
- **安全策略**: 只允許指定號碼

## 工具配置
- **命令執行**: 需要確認
- **網絡搜索**: Brave搜索
- **文件訪問**: 受限訪問
EOF

echo "✅ 用戶文檔創建完成"

# ========================================
# 第七步：安裝和啟動服務
# ========================================
echo ""
echo "⚡ 第七步：安裝和啟動服務..."
echo "----------------------------------------"

# 安裝Gateway服務
echo "安裝Gateway服務..."
openclaw gateway install

# 啟動服務
echo "啟動Gateway服務..."
openclaw gateway start

# 等待服務啟動
sleep 3

# 檢查服務狀態
echo "檢查服務狀態..."
openclaw gateway status

echo "✅ 服務安裝完成"

# ========================================
# 第八步：初始測試
# ========================================
echo ""
echo "🧪 第八步：初始測試..."
echo "----------------------------------------"

# 測試版本
echo "1. 測試OpenClaw版本:"
openclaw --version

# 測試狀態
echo ""
echo "2. 測試系統狀態:"
openclaw status --brief

# 測試安全
echo ""
echo "3. 快速安全檢查:"
openclaw security audit | head -20

echo "✅ 初始測試完成"

# ========================================
# 第九步：創建安裝報告
# ========================================
echo ""
echo "📄 第九步：創建安裝報告..."
echo "----------------------------------------"

# 創建安裝報告
INSTALL_REPORT="$HOME/OpenClaw_Install_Report_$(date +%Y%m%d_%H%M%S).txt"

cat > "$INSTALL_REPORT" << EOF
# OpenClaw 安裝報告
## 安裝時間: $(date)
## 安裝設備: Mac mini
## 安裝用戶: $USER_NAME

## 安裝摘要
✅ 基礎工具安裝完成
✅ OpenClaw 安裝完成 (版本: $OPENCLAW_VERSION)
✅ 配置文件創建完成
✅ 安全權限設置完成
✅ Gateway服務安裝並啟動

## 配置信息
- DeepSeek API: 已配置
- WhatsApp號碼: $PHONE_NUMBER
- Gateway Token: $SECURE_TOKEN
- 服務端口: 18789

## 重要文件位置
- 配置文件: ~/.openclaw/openclaw.json
- 工作目錄: ~/.openclaw/workspace/
- 日誌文件: ~/.openclaw/logs/
- 憑證目錄: ~/.openclaw/credentials/

## 下一步操作
1. 鏈接WhatsApp: openclaw whatsapp login
2. 測試AI對話: 通過WhatsApp發送消息
3. 配置Brave搜索: 可選
4. 設置定時任務: 可選

## 安全提示
1. 備份你的配置文件
2. 保管好Gateway Token
3. 定期運行安全審計
4. 監控API使用量

## 支持資源
- 官方文檔: https://docs.openclaw.ai
- 社區討論: https://discord.com/invite/clawd
- 問題反饋: GitHub Issues

安裝完成時間: $(date)
EOF

echo "✅ 安裝報告創建完成: $INSTALL_REPORT"

# ========================================
# 安裝完成
# ========================================
echo ""
echo "🎉 安裝完成！"
echo "========================================"
echo ""
echo "✅ OpenClaw 已成功安裝到你的Mac mini！"
echo ""
echo "📋 下一步操作:"
echo "1. 鏈接WhatsApp賬號:"
echo "   運行: openclaw whatsapp login"
echo "   然後用手機WhatsApp掃描QR碼"
echo ""
echo "2. 測試安裝:"
echo "   運行: openclaw status"
echo "   運行: openclaw doctor"
echo ""
echo "3. 開始使用:"
echo "   通過WhatsApp發送消息給你的AI助手"
echo ""
echo "4. 查看詳細指南:"
echo "   查看安裝目錄中的詳細文檔"
echo ""
echo "🔧 常用命令:"
echo "   openclaw status      # 查看狀態"
echo "   openclaw logs        # 查看日誌"
echo "   openclaw update      # 檢查更新"
echo "   openclaw gateway restart  # 重啟服務"
echo ""
echo "📁 重要文件:"
echo "   配置文件: ~/.openclaw/openclaw.json"
echo "   安裝報告: $INSTALL_REPORT"
echo ""
echo "🛡️  安全提示:"
echo "   • 保管好你的API Key和Token"
echo "   • 定期備份配置文件"
echo "   • 運行安全審計: openclaw security audit"
echo ""
echo "========================================"
echo "🚀 開始你的OpenClaw之旅吧！"
echo "========================================"

# 重新加載zsh配置
echo ""
echo "重新加載shell配置..."
source ~/.zshrc 2>/dev/null || true

echo ""
echo "安裝腳本完成！"