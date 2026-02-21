# ERRORS.md

記錄命令失敗、異常和錯誤。

## [ERR-20260219-001] cron_gateway_connection

**Logged**: 2026-02-19T12:17:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Cron作業在連接網關時出現60秒超時

### Error
```
Cron作業執行超時，狀態: "cron: job execution timed out"
WhatsApp連接檢查任務超時 (1844秒)
```

### Context
- 早上7:05 WhatsApp連接檢查任務執行超時
- 網關連接出現60秒超時
- 檢測到網關服務PATH缺少必要目錄
- 可能存在多個網關實例

### Suggested Fix
1. 運行 `openclaw doctor --repair` 修復服務配置
2. 檢查並清理可能的重複網關服務
3. 重啟OpenClaw網關服務確保穩定連接

### Metadata
- Reproducible: yes
- Related Files: /Users/gordonlui/.openclaw/workspace/check_whatsapp.sh
- See Also: 

---

## [ERR-20260219-002] browser_control_service

**Logged**: 2026-02-19T12:16:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
瀏覽器控制服務出現間歇性連接問題

### Error
```
There seems to be an intermittent issue with the browser control service for tab management operations.
```

### Context
- 早上啟動程序執行時遇到瀏覽器控制服務連接問題
- 瀏覽器成功啟動 (PID: 3132)
- 所有啟動頁面成功打開 (Google, Gmail, Calendar)
- 服務間歇性不穩定，但核心功能正常

### Suggested Fix
1. 檢查瀏覽器控制服務狀態
2. 重啟瀏覽器控制服務
3. 增加重試機制和錯誤處理

### Metadata
- Reproducible: intermittent
- Related Files: 
- See Also: 

---

## [ERR-20260219-003] xgboost_installation

**Logged**: 2026-02-19T19:32:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: development

### Summary
XGBoost安裝時出現libxgboost.dylib加載錯誤

### Error
```
XGBoostError: XGBoost Library (libxgboost.dylib) could not be loaded.
Likely causes:
  * OpenMP runtime is not installed (vcomp140.dll or libgomp-1.dll for Windows, libomp.dylib for macOS, libgomp.so for Linux)
  * You are running 32-bit Python on a 64-bit OS
```

### Context
- 在macOS上安裝XGBoost 2.1.4時出現
- 系統缺少OpenMP運行時庫
- 影響XGBoost股價預測系統開發

### Solution Applied
1. 安裝OpenMP運行時: `brew install libomp`
2. 設置環境變量:
   ```bash
   export LDFLAGS="-L/opt/homebrew/opt/libomp/lib"
   export CPPFLAGS="-I/opt/homebrew/opt/libomp/include"
   ```
3. 重新安裝XGBoost: `pip install xgboost==2.1.4`
4. 驗證安裝: `python3 -c "import xgboost; print(xgboost.__version__)"`

### Root Cause
macOS系統默認不包含OpenMP運行時庫，而XGBoost需要它來進行並行計算。

### Prevention
1. 在安裝XGBoost前先檢查OpenMP庫
2. 為macOS用戶提供完整的安裝指南
3. 在requirements文件中添加註釋說明

### Metadata
- Reproducible: yes (on fresh macOS installations)
- Related Files: 
  - /Users/gordonlui/.openclaw/workspace/xgboost_stock_predictor.py
  - /Users/gordonlui/.openclaw/workspace/requirements_mt5.txt
- See Also: [LRN-20260219-003]

---

## [ERR-20260219-004] futu_api_stock_format

**Logged**: 2026-02-19T13:44:00+08:00
**Priority**: medium
**Status**: pending
**Area**: api_integration

### Summary
富途API無法識別股票代碼格式

### Error
```
Unknown stock 0005
```

### Context
- 嘗試使用富途API獲取股票數據
- 股票代碼: 0005 (匯豐控股)
- API連接成功，但無法識別股票代碼
- 推測原因: 股票代碼格式不正確

### Suggested Fix
1. 嘗試正確的股票代碼格式: "00005.HK", "01398.HK", "02638.HK"
2. 檢查富途API文檔確認正確格式
3. 測試其他活躍股票如"00700.HK" (騰訊)
4. 創建模擬數據系統作為備用方案

### Root Cause
富途API可能需要完整的股票代碼格式，包括市場後綴(.HK)和正確的位數(5位)。

### Prevention
1. 創建股票代碼格式驗證函數
2. 為不同市場(港股、A股、美股)提供格式轉換
3. 在API調用前先驗證股票代碼格式

### Metadata
- Reproducible: yes
- Related Files: 
  - /Users/gordonlui/.openclaw/workspace/get_real_time_data.py
  - /Users/gordonlui/.openclaw/workspace/get_precise_data.py
- See Also: 

---

## [ERR-20260219-005] script_execution_error

**Logged**: 2026-02-19T19:53:00+08:00
**Priority**: low
**Status**: resolved
**Area**: development

### Summary
Python腳本執行時變量未定義錯誤

### Error
```
NameError: name 'stock_code' is not defined
File "/Users/gordonlui/.openclaw/workspace/predict_992_tomorrow.py", line 717
```

### Context
- 在創建聯想集團執行腳本時出現
- 字符串格式化中使用了未定義的變量
- 腳本生成邏輯中的變量作用域問題

### Solution Applied
1. 修復變量引用: 將`{stock_code}`改為`HK.00992`
2. 重新運行腳本驗證修復
3. 創建簡化版本避免複雜的字符串格式化

### Root Cause
在動態生成Python代碼時，變量作用域管理不當，導致模板變量未正確替換。

### Prevention
1. 使用更安全的字符串格式化方法
2. 在生成代碼前驗證所有變量都已定義
3. 創建代碼生成模板系統
4. 增加代碼語法檢查

### Metadata
- Reproducible: yes (in specific script generation scenarios)
- Related Files: 
  - /Users/gordonlui/.openclaw/workspace/predict_992_tomorrow.py
  - /Users/gordonlui/.openclaw/workspace/quick_992_predict.py
- See Also: [LRN-20260219-003]