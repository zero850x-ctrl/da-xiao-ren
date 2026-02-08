# 📧 OpenClaw 郵件功能使用指南

## 已完成設置

✅ **郵件功能已成功配置並可正常使用**

### 配置詳情
- **郵件帳號**: zero850x@gmail.com
- **應用程式密碼**: hebr wwxy syqo xwbq
- **配置位置**: `~/.config/himalaya/config.toml`
- **狀態**: IMAP接收正常，SMTP發送正常

## 可用工具

### 1. Himalaya CLI (基本郵件管理)
```bash
# 查看郵件文件夾
himalaya folder list

# 查看收件箱（最近郵件）
himalaya envelope list --page-size 10

# 閱讀特定郵件
himalaya message read <郵件ID>

# 查看帳號配置
himalaya account list
```

### 2. OpenClaw郵件工具 (email_tool.py)
```bash
# 發送郵件
python3 email_tool.py send --to "收件人@example.com" --subject "郵件主題" --body "郵件內容"

# 檢查收件箱（最近5封）
python3 email_tool.py inbox

# 閱讀特定郵件
python3 email_tool.py read <郵件ID>

# 列出文件夾
python3 email_tool.py folders

# 顯示幫助
python3 email_tool.py help
```

### 3. Shell腳本發送工具 (send_email.sh)
```bash
# 發送郵件
./send_email.sh "收件人@example.com" "郵件主題" "郵件內容"
```

## 從OpenClaw內部使用

### 發送郵件示例
```python
# 在OpenClaw會話中直接執行
import subprocess

# 發送郵件
result = subprocess.run([
    "python3", "/Users/gordonlui/.openclaw/workspace/email_tool.py",
    "send",
    "--to", "recipient@example.com",
    "--subject", "來自OpenClaw的郵件",
    "--body", "這是一封通過OpenClaw發送的測試郵件。"
], capture_output=True, text=True)

print(result.stdout)
```

### 檢查郵件示例
```python
# 檢查收件箱
import subprocess

result = subprocess.run([
    "python3", "/Users/gordonlui/.openclaw/workspace/email_tool.py",
    "inbox"
], capture_output=True, text=True)

print(result.stdout)
```

## 常見用例

### 1. 發送通知郵件
```bash
python3 email_tool.py send --to "yourself@gmail.com" --subject "任務完成通知" --body "OpenClaw已成功完成任務。"
```

### 2. 定期檢查新郵件
可以設置cron任務定期檢查：
```bash
# 每天上午9點檢查
0 9 * * * cd /Users/gordonlui/.openclaw/workspace && python3 email_tool.py inbox >> email_check.log
```

### 3. 郵件轉發
可以編寫腳本將重要郵件轉發到其他帳號。

## 故障排除

### 問題1: 認證失敗
- 檢查應用程式密碼是否正確
- 確認Gmail帳號已啟用兩步驟驗證
- 重新生成應用程式密碼

### 問題2: 無法發送郵件
- 檢查網絡連接
- 確認SMTP設置正確（smtp.gmail.com:587）
- 嘗試使用Python腳本發送

### 問題3: 無法接收郵件
- 檢查IMAP設置（imap.gmail.com:993）
- 確認Himalaya配置正確
- 檢查防火牆設置

## 安全提示

1. **保護應用程式密碼**：不要將密碼硬編碼在公開腳本中
2. **使用環境變量**：建議將密碼存儲在環境變量中
3. **定期更換密碼**：定期更新應用程式密碼
4. **審查訪問權限**：定期檢查Google帳號的應用程式訪問權限

## 擴展功能建議

1. **郵件模板**：創建常用郵件模板
2. **附件支持**：添加附件發送功能
3. **郵件過濾**：根據規則過濾和處理郵件
4. **自動回覆**：設置自動回覆規則
5. **郵件歸檔**：自動歸檔舊郵件

## 聯繫支持

如有問題，請聯繫OpenClaw助理或檢查日誌文件：
- Himalaya日誌：設置`RUST_LOG=debug`環境變量
- SMTP日誌：查看Python腳本輸出
- 配置檢查：`himalaya account list`

---

**最後更新**: 2026-02-07  
**狀態**: ✅ 所有功能正常運行