# 🚀 OpenClaw Mac Mini 安裝指南 (2026版)

## 📋 文件信息
- **適用對象**: 全新Mac mini用戶
- **操作系統**: macOS Sonoma 14.0+ 或更新版本
- **預設模型**: DeepSeek (深度求索)
- **安全標準**: 基於Leo Laboratory 2026安全指南
- **創建日期**: 2026年2月7日
- **創建者**: 久留美 (專業AI助手)

---

## 🎯 安裝前準備

### 1. 系統要求
- ✅ macOS 14.0 (Sonoma) 或更新版本
- ✅ 至少8GB RAM (建議16GB)
- ✅ 至少20GB可用存儲空間
- ✅ 穩定的網絡連接

### 2. 必要賬號
- [ ] **DeepSeek API Key**: [申請地址](https://platform.deepseek.com/api_keys)
- [ ] **GitHub賬號** (可選，用於更新)
- [ ] **Apple ID** (用於App Store下載)

### 3. 工具準備
需要安裝以下工具：
1. Homebrew (macOS包管理器)
2. Node.js 20.x 或更新版本
3. Git (版本控制)

---

## 🔧 第一步：基礎環境設置

### 1.1 安裝Homebrew
打開 **Terminal.app** (按 `Cmd + Space`，輸入 "Terminal")，執行：

```bash
# 安裝Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 設置環境變量 (根據提示執行)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# 驗證安裝
brew --version
```

### 1.2 安裝Node.js和Git
```bash
# 安裝Node.js (LTS版本)
brew install node

# 安裝Git
brew install git

# 驗證安裝
node --version  # 應該顯示 v20.x 或更高
git --version
npm --version
```

### 1.3 配置npm全局安裝目錄
```bash
# 創建用戶全局目錄
mkdir -p ~/.npm-global

# 配置npm使用用戶目錄
npm config set prefix ~/.npm-global

# 添加到PATH
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 驗證配置
npm config get prefix
```

---

## 🚀 第二步：安裝OpenClaw

### 2.1 安裝OpenClaw
```bash
# 安裝最新版OpenClaw
npm install -g openclaw@latest

# 驗證安裝
openclaw --version
```

### 2.2 初始化OpenClaw
```bash
# 創建工作目錄
mkdir -p ~/.openclaw/workspace

# 初始化配置
openclaw doctor
```

### 2.3 獲取DeepSeek API Key
1. 訪問 [DeepSeek平台](https://platform.deepseek.com/api_keys)
2. 登錄或註冊賬號
3. 創建新的API Key
4. 複製API Key並保存到安全的地方

---

## 🔐 第三步：配置OpenClaw

### 3.1 創建配置文件
```bash
# 創建基礎配置
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  "gateway": {
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "your-secure-token-here"
    }
  },
  "models": {
    "providers": {
      "deepseek": {
        "kind": "openai",
        "baseURL": "https://api.deepseek.com",
        "defaultModel": "deepseek-chat",
        "apiKey": "YOUR_DEEPSEEK_API_KEY_HERE"
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
      "allowFrom": ["YOUR_PHONE_NUMBER"],
      "selfChatMode": true
    }
  },
  "tools": {
    "exec": {
      "security": "allowlist",
      "ask": "always"
    },
    "web": {
      "search": {
        "provider": "brave",
        "braveApiKey": "YOUR_BRAVE_API_KEY_OPTIONAL"
      }
    }
  }
}
EOF
```

### 3.2 替換配置中的占位符
用文本編輯器打開配置文件：
```bash
nano ~/.openclaw/openclaw.json
```

替換以下內容：
1. `YOUR_DEEPSEEK_API_KEY_HERE` → 你的DeepSeek API Key
2. `YOUR_PHONE_NUMBER` → 你的WhatsApp號碼 (格式: +85212345678)
3. `your-secure-token-here` → 生成安全token (見下一節)

### 3.3 生成安全Token
```bash
# 生成隨機安全Token
openssl rand -base64 32
```

複製生成的Token，替換配置文件中的 `your-secure-token-here`。

---

## 🛡️ 第四步：安全配置 (基於2026安全指南)

### 4.1 文件權限設置
```bash
# 設置配置文件權限
chmod 600 ~/.openclaw/openclaw.json

# 設置憑證目錄權限
mkdir -p ~/.openclaw/credentials
chmod 700 ~/.openclaw/credentials
```

### 4.2 安全審計
```bash
# 運行安全審計
openclaw security audit

# 詳細審計
openclaw security audit --deep
```

### 4.3 啟用Gateway服務
```bash
# 安裝並啟動Gateway服務
openclaw gateway install
openclaw gateway start

# 檢查服務狀態
openclaw gateway status
```

---

## 📱 第五步：配置WhatsApp通道

### 5.1 安裝WhatsApp插件
```bash
# WhatsApp插件通常已包含在默認安裝中
# 檢查插件狀態
openclaw status
```

### 5.2 鏈接WhatsApp賬號
```bash
# 啟動WhatsApp鏈接
openclaw whatsapp login

# 按照提示掃描QR碼
# 使用手機WhatsApp掃描
```

### 5.3 驗證連接
```bash
# 檢查通道狀態
openclaw status

# 應該顯示 WhatsApp: ON 和 OK狀態
```

---

## 🔧 第六步：高級配置 (可選)

### 6.1 配置Brave搜索 (可選)
1. 訪問 [Brave Search API](https://brave.com/search/api/)
2. 申請API Key
3. 替換配置文件中的 `YOUR_BRAVE_API_KEY_OPTIONAL`

### 6.2 設置定時任務
```bash
# 創建每日更新檢查
openclaw cron add --name "Daily Update Check" \
  --schedule "0 9 * * *" \
  --timezone "Asia/Hong_Kong" \
  --message "Check for OpenClaw updates and install if available" \
  --model "deepseek/deepseek-chat"

# 查看cron任務
openclaw cron list
```

### 6.3 配置電子郵件 (可選)
```bash
# 安裝Himalaya郵件客戶端
brew install himalaya

# 配置Gmail
mkdir -p ~/.config/himalaya
cat > ~/.config/himalaya/config.toml << 'EOF'
[default]
name = "Your Name"
email = "your-email@gmail.com"

[settings]
default-page-size = 50

[accounts.gmail]
email = "your-email@gmail.com"
display-name = "Your Name"

[accounts.gmail.imap]
host = "imap.gmail.com"
port = 993
login = "your-email@gmail.com"
password = "your-app-specific-password"
tls = true

[accounts.gmail.smtp]
host = "smtp.gmail.com"
port = 587
login = "your-email@gmail.com"
password = "your-app-specific-password"
tls = true
EOF
```

---

## 🧪 第七步：測試與驗證

### 7.1 基本功能測試
```bash
# 測試版本
openclaw --version

# 測試狀態
openclaw status

# 測試Gateway
openclaw gateway status

# 測試健康狀態
openclaw doctor
```

### 7.2 模型測試
```bash
# 測試DeepSeek連接
openclaw --model deepseek/deepseek-chat "Hello, test connection"

# 測試代碼模型
openclaw --model deepseek/deepseek-coder "Write a simple Python function"
```

### 7.3 WhatsApp測試
1. 向你的WhatsApp號碼發送消息
2. OpenClaw應該會自動回復
3. 測試群組聊天 (如果配置了)

---

## 📊 第八步：監控與維護

### 8.1 日常檢查命令
```bash
# 檢查系統狀態
openclaw status

# 檢查安全狀態
openclaw security audit

# 檢查更新
openclaw update

# 查看日誌
openclaw logs --follow
```

### 8.2 定期維護任務
```bash
# 每周安全審計 (可添加到cron)
openclaw security audit --deep

# 每月備份配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d)

# 清理舊日誌
find ~/.openclaw/logs -name "*.log" -mtime +30 -delete
```

### 8.3 故障排除
```bash
# 如果遇到問題
openclaw doctor --verbose

# 重啟服務
openclaw gateway restart

# 查看詳細日誌
openclaw logs --tail 100
```

---

## 🚨 常見問題解決

### Q1: 安裝失敗 "Permission denied"
```bash
# 修復權限
sudo chown -R $(whoami):staff ~/.npm-global
sudo chown -R $(whoami):staff ~/.openclaw
```

### Q2: WhatsApp無法連接
```bash
# 重新鏈接
openclaw whatsapp login --force

# 檢查配置
openclaw status
```

### Q3: DeepSeek API錯誤
1. 檢查API Key是否正確
2. 確認賬號有足夠額度
3. 檢查網絡連接

### Q4: Gateway無法啟動
```bash
# 重新安裝服務
openclaw gateway uninstall
openclaw gateway install
openclaw gateway start
```

---

## 📁 文件結構參考

```
~/.openclaw/
├── openclaw.json          # 主配置文件
├── openclaw.json.backup   # 配置備份
├── credentials/           # 憑證存儲
├── logs/                  # 日誌文件
│   ├── gateway.log
│   └── session.log
├── workspace/            # 工作目錄
│   ├── memory/          # 記憶文件
│   │   ├── 2026-02-07.md
│   │   └── MEMORY.md
│   ├── AGENTS.md        # 代理配置
│   ├── SOUL.md          # 個性配置
│   └── USER.md          # 用戶信息
└── agents/              # 代理文件
    └── main/
        └── agent/
            └── auth-profiles.json
```

---

## 🔗 有用資源

### 官方資源
- **OpenClaw文檔**: https://docs.openclaw.ai
- **GitHub倉庫**: https://github.com/openclaw/openclaw
- **社區討論**: https://discord.com/invite/clawd

### API提供商
- **DeepSeek API**: https://platform.deepseek.com
- **Brave Search API**: https://brave.com/search/api
- **Anthropic Claude**: https://console.anthropic.com

### 安全資源
- **Leo Laboratory安全指南**: https://leo-laboratory.com/internet-resource/openclaw-security-guide-2026/
- **OpenClaw安全文檔**: https://docs.openclaw.ai/security

---

## 📧 支持與聯繫

### 遇到問題時
1. 首先運行 `openclaw doctor`
2. 檢查日誌 `openclaw logs --tail 50`
3. 查看官方文檔
4. 在社區尋求幫助

### 緊急聯繫
- 重啟服務: `openclaw gateway restart`
- 重置配置: 恢復備份文件
- 完全重裝: 刪除 `~/.openclaw` 重新開始

---

## 🎉 安裝完成！

恭喜！你已經成功在Mac mini上安裝並配置了OpenClaw。系統現在具備：

### ✅ 核心功能
- 最新版OpenClaw (2026.2.3-1+)
- DeepSeek AI模型集成
- WhatsApp通訊通道
- 安全Gateway服務

### ✅ 安全特性
- 基於2026安全指南配置
- 文件權限保護
- 命令執行限制
- 訪問控制白名單

### ✅ 維護工具
- 自動更新檢查
- 安全審計腳本
- 日誌監控
- 配置備份

### 🚀 開始使用
1. 通過WhatsApp與你的AI助手對話
2. 嘗試各種命令和任務
3. 根據需要調整配置
4. 享受智能助理帶來的便利！

---

**文檔版本**: 1.0  
**最後更新**: 2026-02-07  
**適用系統**: macOS 14.0+  
**預設模型**: DeepSeek  
**安全標準**: Leo Laboratory 2026指南  

**祝使用愉快！** 🎯

---
*本指南由久留美創建，基於實際安裝經驗和安全最佳實踐。*