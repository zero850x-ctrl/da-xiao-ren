# 工作區目錄結構

## 根目錄文件
- **核心配置文件**:
  - `AGENTS.md` - 代理設定和工作區指南
  - `SOUL.md` - AI助理個性和行為設定
  - `IDENTITY.md` - AI身份設定 (名稱: 久留美, 語言: 繁體中文)
  - `USER.md` - 用戶資訊和偏好設定
  - `MEMORY.md` - 長期記憶和重要事件記錄
  - `TOOLS.md` - 本地工具和環境設定
  - `HEARTBEAT.md` - 定期檢查任務清單

- **系統文件**:
  - `BOOTSTRAP.md` - 初始設定指南 (可刪除)
  - `MEMORY_OPTIMIZATION_SUMMARY.md` - 記憶優化總結
  - `update-check-summary.md` - 更新檢查報告
  - `whatsapp_monitor_log.md` - WhatsApp監控日誌

- **臨時文件**:
  - `chongqing_food_outline.md` - 重慶美食大綱
  - `post_market_summary_20260220_1606.md` - 收市總結
  - `stock_report_20260219_134312.md` - 股票報告

## 分類目錄

### 📁 `api_docs/` - API相關文檔
- `ALTERNATIVE_API_GUIDE.md` - 替代API指南
- `ALTERNATIVE_API_SOLUTION.md` - 替代API解決方案
- `API_START_COMMANDS.md` - API啟動命令
- `OANDA_REGISTRATION_GUIDE.md` - OANDA註冊指南
- `OANDA_SOLUTION_SUMMARY.md` - OANDA解決方案總結
- `OANDA_START_GUIDE.md` - OANDA開始指南
- `PURE_API_SOLUTION.md` - 純API解決方案
- `get_cursor_api_key.md` - 獲取Cursor API key
- `google_api_quick_setup.md` - Google API快速設定

### 📁 `trading_docs/` - 交易相關文檔
- `TRADING_SYSTEM_SUMMARY.md` - 交易系統總結
- `TRADING_MONITOR_UPDATES.md` - 交易監控更新
- 各種交易摘要文件

### 📁 `cron_reports/` - Cron任務報告
- `CRON_TASKS_SUMMARY.md` - Cron任務總結
- 各種cron執行報告

### 📁 `technical_reports/` - 技術分析報告
- `technical_analysis_report_20260211.md` - 2026-02-11技術分析
- `technical_analysis_report_20260212.md` - 2026-02-12技術分析

### 📁 `market_reports/` - 市場報告
- `today_achievements_20260219.md` - 今日成就
- `final_post_market_summary_20260220.md` - 最終收市總結
- `price_validation_summary.md` - 價格驗證總結
- `afternoon_market_summary_20260220_1300.md` - 下午市場總結
- `detailed_post_market_analysis_20260220.md` - 詳細收市分析

### 📁 `guides/` - 指南和教學
- `START_NOW_GUIDE.md` - 立即開始指南
- `true_automation_guide.md` - 真正自動化指南
- `cursor_login_guide.md` - Cursor登入指南
- `EMAIL_INSTRUCTIONS.md` - 電子郵件指令
- `grant_peekaboo_permissions.md` - 授予Peekaboo權限
- `WHATSAPP_MONITOR_README.md` - WhatsApp監控README

### 📁 `memory/` - 記憶文件系統
- `archive/` - 存檔文件
- `daily/` - 每日記錄
- `logs/` - 日誌文件
- `monthly/` - 每月總結
- `projects/` - 項目記憶
- `weekly/` - 每週總結

## 其他重要目錄

### 📁 `trading_system/` - 交易系統
- `backups/` - 備份文件
- `data/` - 數據文件
- `logs/` - 系統日誌
- `models/` - 機器學習模型
- `reports/` - 交易報告

### 📁 `skills/` - 技能文件
- `browser-automation/` - 瀏覽器自動化技能
- `chrome/` - Chrome技能
- `desktop-control/` - 桌面控制技能
- `peekaboo/` - Peekaboo技能

### 📁 數據收集目錄
- `crypto_collected_data/` - 加密貨幣收集數據
- `crypto_data/` - 加密貨幣數據
- `crypto_learning/` - 加密貨幣學習
- `crypto_monitor_data/` - 加密貨幣監控數據
- `crypto_reports/` - 加密貨幣報告
- `hsi_data/` - 恆生指數數據

## 文件管理原則

1. **根目錄保持整潔**: 只保留核心配置文件和當前活動文件
2. **分類存放**: 相關文件放入對應分類目錄
3. **定期清理**: 使用 `memory_cleanup.sh` 定期清理大型文件
4. **版本控制**: 重要變更記錄在 `MEMORY.md` 中
5. **備份重要文件**: 重要配置和數據定期備份

## 最近整理 (2026-02-21)
- 移動了9個大型API文檔到 `api_docs/` 目錄
- 移動了交易相關文檔到 `trading_docs/` 目錄
- 移動了cron報告到 `cron_reports/` 目錄
- 移動了技術分析報告到 `technical_reports/` 目錄
- 移動了市場報告到 `market_reports/` 目錄
- 移動了指南文件到 `guides/` 目錄
- 根目錄文件從39個減少到14個，大幅提升整潔度