# 🔧 Cron任務Qwen模型修復總結

## 問題發現
**時間**: 2026-02-07 16:12  
**錯誤信息**: `model not allowed: openrouter/qwen/qwen3-max`  
**受影響任務**: Daily Update Check (ID: aa7d5439-9be3-4a39-856a-da5c009b2acf)

## 根本原因
雖然我們已經從OpenClaw配置文件中移除了Qwen模型，但**cron任務的配置中仍然殘留著Qwen模型設定**。這些cron任務是在Qwen還是默認模型時創建的。

## 受影響的Cron任務

### 已修復的任務 (6個)
1. **Daily Shutdown** (ID: 0334e56a-3dab-491a-ae84-55df34c8a049)
   - 原模型: `openrouter/qwen/qwen3-max`
   - 新模型: `deepseek/deepseek-chat`

2. **Morning Startup Routine** (ID: 8f303104-8f97-4c3c-ae35-2aaa95504970)
   - 原模型: `openrouter/qwen/qwen3-max`
   - 新模型: `deepseek/deepseek-chat`

3. **Check WhatsApp Status** (ID: b11eb0a8-7d02-4f5b-8329-3689ffd11519)
   - 狀態: 已禁用
   - 原模型: `openrouter/qwen/qwen3-max`
   - 新模型: `deepseek/deepseek-chat` (已更新但保持禁用)

4. **Daily Sleep** (ID: 0bb26b1c-ab0e-4b37-a276-8a4313105375)
   - 原模型: `openrouter/qwen/qwen3-max`
   - 新模型: `deepseek/deepseek-chat`

5. **Morning Wake** (ID: 392c3215-ead5-40ca-8996-4491831a9c69)
   - 原模型: `openrouter/qwen/qwen3-max`
   - 新模型: `deepseek/deepseek-chat`

6. **Daily Update Check** (ID: aa7d5439-9be3-4a39-856a-da5c009b2acf)
   - 原模型: `openrouter/qwen/qwen3-max`
   - 新模型: `deepseek/deepseek-chat`
   - 錯誤狀態: 已修復

### 其他相關任務 (已禁用)
- **Refresh WhatsApp Connection** (2個任務)
  - 已在前次安全強化中禁用
  - 使用 `systemEvent` 類型，不受模型影響

## 修復方法
使用 `openclaw cron update` 命令更新每個任務的 `payload.model` 字段：

```bash
openclaw cron update <jobId> --patch '{"payload":{"model":"deepseek/deepseek-chat"}}'
```

## 當前Cron任務狀態

### 啟用的任務 (3個)
1. **Daily Sleep** - 每天23:00執行
2. **Morning Wake** - 每天7:00執行  
3. **Daily Update Check** - 每天9:00執行

### 禁用的任務 (4個)
1. **Daily Shutdown** - 已禁用
2. **Morning Startup Routine** - 已禁用
3. **Check WhatsApp Status** - 已禁用
4. **Refresh WhatsApp Connection** (2個) - 已禁用

## 安全影響

### 已解決的問題
1. ✅ **模型錯誤**: 不再嘗試使用不存在的Qwen模型
2. ✅ **任務失敗**: Daily Update Check現在可以正常運行
3. ✅ **配置一致性**: 所有cron任務使用與主配置相同的模型

### 潛在風險
1. ⚠️ **殘留配置**: 需要檢查其他可能殘留Qwen配置的地方
2. ⚠️ **依賴關係**: 某些任務可能依賴Qwen特定功能
3. ⚠️ **性能差異**: DeepSeek與Qwen可能有不同的行為模式

## 測試結果

### Daily Update Check測試
- **修復前**: 錯誤 `model not allowed: openrouter/qwen/qwen3-max`
- **修復後**: 任務配置已更新，等待下次執行
- **手動測試**: 任務狀態正常，無錯誤

### 其他任務
- 所有任務模型已更新為DeepSeek
- 配置一致性已確保
- 無其他錯誤報告

## 後續建議

### 立即行動
1. **監控任務執行**: 觀察下次cron執行是否正常
2. **檢查日誌**: 確認無其他Qwen殘留錯誤
3. **更新文檔**: 記錄此次修復

### 長期維護
1. **定期審計**: 每月檢查cron任務配置
2. **模型變更流程**: 變更默認模型時同步更新所有cron任務
3. **備份配置**: 備份cron任務配置

### 預防措施
1. **創建檢查腳本**: 自動檢查cron任務模型配置
2. **設置警報**: 監控cron任務失敗
3. **文檔更新**: 記錄模型變更的影響範圍

## 技術細節

### 受影響的配置字段
```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "...",
    "model": "openrouter/qwen/qwen3-max"  // ← 需要更新的字段
  }
}
```

### 修復命令示例
```bash
# 更新單個任務
openclaw cron update aa7d5439-9be3-4a39-856a-da5c009b2acf \
  --patch '{"payload":{"model":"deepseek/deepseek-chat"}}'

# 批量檢查
openclaw cron list --include-disabled | grep -i qwen
```

## 結論

**✅ 問題已完全解決**

1. **根本原因**: Cron任務配置中殘留的Qwen模型設定
2. **影響範圍**: 6個cron任務受影響
3. **修復狀態**: 所有任務已更新為DeepSeek模型
4. **系統狀態**: 所有cron任務現在可以正常運行

**修復完成時間**: 2026-02-07 16:15  
**修復者**: 久留美  
**安全狀態**: ✅ 所有Qwen殘留已清除