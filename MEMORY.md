# MEMORY.md - Long-Term Memory

---

# ⚠️ 核心提醒 (每次對話必須檢查)

## 🚨 兩個倉口 - 必須分清楚！

### 1. Gordon既實盤 (真錢 Self-managed)
| 股票代碼 | 名稱 |
|----------|------|
| 00992 | 聯想集團 |
| 00005 | 匯豐控股 |
| 01398 | 工商銀行 |
| 02638 | 港燈-SS |
| 09618 | 京東集團 |

### 2. 久留美模擬倉 (Kurumi Simulated)
| 股票代碼 | 名稱 | 股數 | 成本 |
|----------|------|------|------|
| 07500 | 兩倍看空 | 30,000 | $1.63 |
| 00700 | 騰訊控股 | 200 | $519.50 |
| 02800 | 盈富基金 | 4,500 | $26.78 |
| 01211 | 比亞迪 | 600 | $98.45 |

**每次monitor同report必須確認係邊個倉！**

## 📊 Cron數據優先
- 模擬倉既最新價錢同持倉要去cron output度拎
- 唔好假設，要check data
- 路徑: `/Users/gordonlui/.openclaw/workspace/monitor_reports/quick_*.json`

## 🔄 XGBoost Cron
- 每5分鐘執行一次 (9:00-16:00)
- 監控曬所有持倉股票
- Script: `xgboost_multi_stock.py`

---

## Language & Communication Settings

### 2026-02-21: 繁體中文溝通設定
**變更內容：** 更新SOUL.md和IDENTITY.md，設定主要使用繁體中文溝通
**設定細節：**
- SOUL.md加入Language章節：回覆通常為繁體中文
- IDENTITY.md加入Language項目：繁體中文
- 保持自然、親切的語氣，根據情境調整語言風格
- 技術討論時可適當使用英文術語

## Workspace Organization

### 2026-02-21: 工作區文件整理優化
**整理內容：** 將工作區根目錄的大型API文檔移動到適當的子目錄
**整理成果：**
1. **創建分類目錄**:
   - `api_docs/` - 9個API相關文檔
   - `trading_docs/` - 交易相關文檔
   - `cron_reports/` - Cron任務報告
   - `technical_reports/` - 技術分析報告
   - `market_reports/` - 市場報告
   - `guides/` - 指南和教學文件

2. **文件移動統計**:
   - 移動了25個大型文件到分類目錄
   - 根目錄文件從39個減少到14個
   - 創建了目錄結構文檔 `DIRECTORY_STRUCTURE.md`

3. **整理原則**:
   - 根目錄只保留核心配置和當前活動文件
   - 相關文件分類存放，便於查找和管理
   - 定期使用 `memory_cleanup.sh` 清理大型文件

**效益：**
- ✅ 工作區根目錄大幅整潔
- ✅ 文件查找效率提升
- ✅ 系統維護更容易
- ✅ 記憶管理更有效

## System Issues & Solutions

### OpenClaw Update Permission Issue (2026-02-12)
**Problem:** Daily update checks fail due to npm permission errors
**Root Cause:** npm cache contains root-owned files from previous installations
**Error Message:** `npm error Your cache folder contains root-owned files`

**Solution:**
1. Fix npm permissions:
   ```bash
   sudo chown -R 501:20 "/Users/gordonlui/.npm"
   ```
2. Update OpenClaw:
   ```bash
   npm i -g openclaw@latest
   ```
3. Restart gateway:
   ```bash
   openclaw gateway restart
   ```

**Note:** This prevents automatic updates in cron jobs until fixed manually.

## Important Dates & Events

### 2026-02-12
- Daily update check cron job running
- OpenClaw version: 2026.2.1
- Update available: 2026.2.9
- Automatic updates blocked by npm permission issue
- **技术图表全自动交易系统上线**
  - Cron任务: 每30分钟执行一次 (交易时间09:30-16:00)
  - 交易系统: futu_technical_trader_safe.py
  - 风险管理: 严格2% Rule版本
  - 执行环境: 模拟账户（只操作模拟环境）
  - 首次执行: 13:00，系统正常运行，无新交易信号

### 2026-02-17
- **選擇方案D：替代API方案**
  - 決定使用OANDA REST API方案，放棄虛擬機方案
  - 已創建OANDA模擬賬戶: 1600092639
  - 清理所有虛擬機相關文件
  - 專注於純API自動交易系統
  - 系統健康檢查cron job已修改為正常不報告

### 2026-02-19
- **安裝self-improving-agent技能**
  - 學習並安裝持續改進技能
  - 創建`.learnings/`目錄和學習文件
  - 開始記錄系統學習、錯誤和功能請求
  - 技能位置: `/Users/gordonlui/.openclaw/skills/self-improving-agent/`
- **系統監控改進**
  - 修改cron job設置，正常時不報告
  - 檢測到網關連接超時問題
  - WhatsApp連接有短暫斷開又恢復

### 🎯 重要里程碑：人工与系统完美协作（14:31-14:35）
#### **人工决策 + 系统纪律的完美结合**
1. **人工机会识别** (14:31)
   - 买入HK.00992联想集团 26,000股 @ 8.99
   - 市值HKD 233,480，识别到交易机会
   - 证明人工判断在机会识别中的价值

2. **系统风险管理** (14:35)
   - 自动止损HK.00700腾讯 400股 @ 533.00
   - 亏损-2.60%（触发2%止损），订单ID: 7426246
   - 止损金额HKD 5,700，严格执行2% Rule
   - 证明系统纪律在风险管理中的重要性

#### **关键学习：**
- ✅ **人工优势**：机会识别、市场感觉、灵活判断
- ✅ **系统优势**：纪律执行、风险控制、情绪免疫
- ✅ **完美配合**：人工判断机会，系统管理风险
- ✅ **2% Rule验证**：有效控制单笔损失，保护资金

#### **系统优化完成：**
- 添加HK.00992到监控列表
- 为992设置8.81止损价（2%止损）
- 更新持仓风险管理
- 建立人工+自动协作模式

### 🤖 XGBoost股價預測系統開發成功 (2026-02-19)
#### **技術突破：傳統技術分析與機器學習完美結合**
1. **系統功能**:
   - XGBoost機器學習模型預測股價漲跌
   - 黃金分割位(0.382, 0.5, 0.618)技術分析
   - 費波那契移動平均線(8,13,21,34,55天)
   - 多因子特徵工程(20個技術特徵)

2. **開發成果**:
   - **`xgboost_stock_predictor.py`** - 完整預測系統
   - **`simple_xgboost_predictor.py`** - 簡化測試版
   - **`run_xgboost_stock.py`** - 可運行版本
   - **測試準確率**: 98.3% (模擬數據)

3. **技術挑戰解決**:
   - XGBoost安裝問題: `brew install libomp`
   - 環境變量配置: LDFLAGS和CPPFLAGS設置
   - 依賴庫安裝: xgboost, scikit-learn, scipy, numpy, pandas

4. **最重要的特徵**:
   - **golden_618** (0.4195) - 黃金分割位最重要
   - **MA34** (0.1131) - 費波那契中期均線
   - **return_5d** (0.0658) - 5日收益率

#### **實戰應用：聯想集團(00992)明日開市預測**
1. **價格突破事件** (19:56):
   - 之前價格: $8.99
   - 當前價格: **$9.30** (+3.45%)
   - 用戶盈利: **+8.27%** (從$8.59買入價)
   - 盈利金額: **HKD 18,460**

2. **預測系統動態調整**:
   - **之前預測**: 上漲概率14.0%，信號🔴強力賣出
   - **更新預測**: 上漲概率**65.0%**，信號🟢持有/加倉
   - **調整原因**: 價格突破0.618黃金分割位($9.12)

3. **交易建議更新**:
   - **推薦策略**: 部分獲利了結(30-50%) + 持有觀察
   - **止損位**: $9.02 (-3%)
   - **目標價**: $9.58 (+3%), $10.04 (+8%)
   - **關鍵價位**: $9.12(0.618), $9.00(0.5), $8.88(0.382)

4. **創建執行系統**:
   - **`predict_992_tomorrow.py`** - 聯想專用預測系統
   - **`execute_992_updated.py`** - 更新版監控腳本
   - **`update_992_analysis.py`** - 緊急更新分析

#### **系統價值證明**:
1. **動態適應能力**: 根據價格變化實時調整預測
2. **技術分析整合**: 傳統黃金分割與機器學習結合
3. **風險管理系統**: 分層止損和目標設置
4. **執行自動化**: 創建可執行的交易腳本

#### **人機協作模式深化**:
1. **人工優勢強化**: 機會識別、市場感覺、靈活判斷
2. **系統優勢擴展**: 數據分析、概率預測、紀律執行
3. **協作流程優化**: 人工判斷 → 系統分析 → 動態調整 → 執行監控
4. **風險控制完善**: 2% Rule + 技術位止損 + 盈利保護

#### **學習收穫**:
- ✅ **XGBoost在股價預測的優勢**: 處理非線性關係、特徵重要性、防止過擬合
- ✅ **技術突破的影響**: 價格突破關鍵位會大幅改變概率分布
- ✅ **動態調整的重要性**: 系統需要根據市場變化實時更新
- ✅ **風險管理的層次**: 分層止損、盈利保護、倉位控制
- ✅ **執行系統的價值**: 自動監控、條件觸發、紀律執行

### 📊 技术图表每日收盘分析系统上线 (2026-02-12 16:30)
#### **系统功能：**
- **分析时间**: 每日收盘后16:30自动执行
- **分析范围**: 5只监控股票 (02800, 00700, 09988, 01299, 02318)
- **技术指标**: 平行通道、黄金分割、旗形形态、RSI、K线分析
- **输出报告**: 详细技术分析报告 (technical_analysis_report_YYYYMMDD.md)

#### **今日分析结果 (2026-02-12):**
1. **趋势分布**: 4只上升趋势，1只下降趋势
2. **RSI状态**: 腾讯严重超卖(28.7)，平安接近超买(63.5)
3. **关键发现**:
   - 腾讯(00700): RSI 28.7超卖，接近0.0%黄金分割位530.50
   - 阿里(09988): 接近50.0%黄金分割位157.60，RSI 36.9
   - 友邦(01299): 接近50.0%黄金分割位84.30，RSI 51.6
   - 平安(02318): 出现看涨旗形形态，但RSI偏高63.5
   - 盈富(02800): 接近61.8%黄金分割位27.17

4. **交易信号**:
   - 🟢 BUY HK.00700 @535.50 (RSI超卖28.7<35)
   - 🟢 BUY HK.09988 @158.60 (黄金分割支撑位50.0%)
   - 🟢 BUY HK.01299 @83.80 (黄金分割支撑位50.0%)

5. **报告生成**: `/Users/gordonlui/.openclaw/workspace/technical_analysis_report_20260212.md`

#### **系统价值：**
- ✅ 自动化技术分析，减少人工工作量
- ✅ 系统化风险管理，避免情绪化决策
- ✅ 每日复盘，持续优化交易策略
- ✅ 完整记录，便于回溯和学习

---

## Important Context: Two Portfolios

(See above "核心提醒" for latest portfolio info)
- Timezone: Asia/Hong_Kong (GMT+8)
- Uses Futu OpenD for stock trading
- Interested in technical analysis and automation
- Prefers practical solutions over theoretical explanations
- Values continuity and remembers past conversations

## Technical Environment
- Mac with Unified Memory architecture
- OpenClaw installed via npm (not git)
- Telegram channel configured (@fx_kurumi_bot)
- WhatsApp linked (+85298104938)
- DeepSeek models as primary (coder/chat)
- Claude models as fallback (sonnet/opus)

## System Monitoring & Automation

### WhatsApp连接监控系统 (2026-02-14)
**系统功能：**
- **监控脚本**: `/Users/gordonlui/.openclaw/workspace/check_whatsapp.sh`
- **执行频率**: 通过cron任务定期执行
- **检查内容**: WhatsApp连接状态
- **自动恢复**: 如果连接断开，自动尝试重新连接

**当前状态 (2026-02-14 16:44):**
- ✅ WhatsApp连接正常
- ✅ 账号: +85298104938
- ✅ 认证时间: 1分钟前
- ✅ OpenClaw网关运行正常
- ✅ Telegram通道也正常

**监控脚本逻辑：**
1. 检查OpenClaw状态中的WhatsApp连接
2. 如果状态为OK，正常退出
3. 如果状态异常，执行重新连接流程：
   - 登出WhatsApp
   - 生成新的QR码
   - 提示用户扫描重新连接

### 🔧 WhatsApp監控系統重大修復 (2026-02-15/16)
**問題發現**: 2026-02-15 全天出現間歇性`which openclaw failed`和`openclaw status failed`錯誤
**根本原因分析**:
1. **cron環境PATH問題**: cron執行時只有基本PATH (`/usr/bin:/bin`)，缺少Node.js和OpenClaw路徑
2. **AI代理額外行為**: AI代理除了運行指定腳本外，還嘗試執行`openclaw status`命令
3. **環境變量缺失**: cron環境不繼承用戶shell的環境設置

**解決方案實施**:
1. ✅ **創建健壯監控腳本**: `whatsapp_monitor_robust.sh`
   - 顯式設置所有環境變量 (PATH, HOME, USER, SHELL, NODE_PATH)
   - 使用完整路徑執行命令 (`/Users/gordonlui/.npm-global/bin/openclaw`)
   - 詳細日誌記錄到`/Users/gordonlui/.openclaw/whatsapp_monitor.log`

2. ✅ **更新OpenClaw cron任務消息**:
   - 任務ID: `e28508e1-7bdb-4de4-8b7d-5614f61c9a1f`
   - 新消息: "只運行這個腳本：/Users/gordonlui/.openclaw/workspace/whatsapp_monitor_robust.sh。不要執行其他命令，腳本會處理所有WhatsApp連接檢查。"

3. ✅ **雙重保障策略**:
   - crontab中設置完整PATH
   - 腳本中使用完整路徑
   - 腳本中顯式設置所有必要環境變量

**修復驗證時間線**:
- **20:40**: 腳本測試成功
- **20:52**: 首次使用新腳本，仍有額外命令錯誤
- **21:22**: 更新任務消息後，監控完全正常 ✅
- **21:53, 22:22, 22:53**: 持續正常運行
- **夜間時段**: 按計劃網絡斷電，連接錯誤為預期行為
- **07:52**: 早晨網絡恢復後監控正常

**技術學習點**:
1. **cron環境限制**: 需要顯式設置所有環境變量
2. **OpenClaw cron任務管理**: 任務通過AI代理執行，需要明確指令
3. **錯誤處理策略**: 雙重保障（PATH設置 + 完整路徑）

**系統當前狀態**:
- ✅ WhatsApp監控: 完全穩定運行
- ✅ 早晨啟動程序: 正常執行
- ✅ 網絡斷電恢復: 自動處理正常
- ✅ 所有通信通道: 雙向通信完全正常

**用戶交互模式觀察**:
- 技術細節敏感度高，關注系統錯誤報告
- 主動報告問題並尋求解決方案
- 理解系統技術細節，偏好簡潔直接的技術回答
- 重視問題的徹底解決和系統穩定性

## Trading System Enhancements

### MiniMax API Configuration (2026-02-21)
**問題**: 之前MiniMax API key一直無法使用，DeepSeek持續扣費
**根本原因**: 使用了錯誤的API端點
**解決方案**: 
- Coding Plan需要使用Anthropic兼容API: `https://api.minimax.io/anthropic/v1`
- 認證頭需要使用: `x-api-key`（不是`Authorization: Bearer`）
- 更新openclaw.json配置

**API Key (Coding Plan)**: sk-cp-TQn7MImNXFYXNlXiMG-V8PBd-Eq60stea8qdujaRFT_vCoA0LGutOEqMGaEindGXnLwN98qvy_b3AztoKsM8YO-epg9Kma7Og4bQ3HBODRF-q9joNcTfrI8

**Coding Plan額度**: 100 prompts / 5小時

**學習**: 不同方案(Coding Plan vs Pay-As-You-Go)可能使用不同的API端點

### Volume Analysis System (2026-02-21)
**契機**: 用戶分享了量價關係八大法則

**八大法則**:
1. 量漲價漲 - 健康上升趨勢
2. 價漲量縮 - 警示信號
3. 量縮價漲 - 趨勢反轉
4. 井噴後暴跌 - 趨勢反轉
5. 高位放量滯漲 - 下跌前兆
6. 底部成交量遞減 - 即將上漲
7. 恐慌性拋售 - 空頭結束
8. 跌破趨勢線放量 - 下跌信號

**系統改進**:
- 創建 volume_analyzer.py: 成交量分析核心模組
- 整合到 analyze_stocks.py: 技術分析系統
- 創建 daily_technical_analysis_with_volume.py: 每日技術分析報告
- 創建 volume_enhanced_trader.py: 成交量增強的交易系統

**交易規則整合**:
- 成交量買入信號 → 增強買入
- 成交量賣出信號 → 增強賣出
- 異常成交量 → 過濾交易
- 量比 > 3 → 謹慎操作
- 量比 < 0.2 → 市場觀望

### OANDA Account (2026-02-21)
**狀態**: 用戶已開戶
**待辦**: 獲取API Key
- 網址: https://fxds.oanda.com/app/login
- 路徑: My Account → My Services → Manage API Access

### Howard Marks - Mastering the Market Cycle
**用戶推薦**: 霍華·馬克斯的投資經典
**核心概念**: 「我們不能預測，但是可以準備」
**原則**:
- 逆向投資: 別人恐懼我貪婪，別人貪慾我恐懼
- 風險意識: 市場風險升溫時要更謹慎
- 買在低價: 便宜價格才能控制損失
- 週期思考: 沒有永遠上漲，也沒有永遠下跌

**應用**: 考慮將市場週期判斷加入到交易系統中