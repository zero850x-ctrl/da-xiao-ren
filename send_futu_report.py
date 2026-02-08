#!/usr/bin/env python3
"""
發送富途API研究報告郵件
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from datetime import datetime

# 配置
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = 'hebr wwxy syqo xwbq'
TO_EMAIL = 'zero850x@gmail.com'

def send_futu_report():
    """發送富途API研究報告"""
    try:
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = f"OpenClaw助理 <{USERNAME}>"
        msg['To'] = TO_EMAIL
        msg['Subject'] = "富途Open API研究完成報告"
        
        # 郵件正文
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""已完成富途（FUTU）Open API的深入研究，以下是主要成果：

📊 研究概述
- 完成富途Open API文檔分析
- 創建完整使用指南和測試工具
- 了解如何獲取9618.HK（京東健康）股票數據

📁 創建文件
1. FUTU_API_GUIDE.md - 完整使用指南（8118字）
   - API架構說明
   - 安裝步驟
   - 代碼示例
   - 常見問題解決

2. test_futu_api.py - 測試腳本
   - 檢查API安裝
   - 測試OpenD連接
   - 獲取股票數據示例

🔧 API核心功能
- 實時行情數據
- 歷史K線數據
- 交易執行接口
- 賬戶管理功能
- 支持港股、美股、A股等多市場

📝 使用流程
1. 安裝OpenD網關程序
2. 獲取富途API權限
3. 安裝Python SDK：pip install futu-api
4. 開發應用程序

💻 示例代碼（獲取9618.HK價格）
```python
import futu as ft

# 連接行情服務器
quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)

# 獲取京東健康數據
ret, data = quote_ctx.get_market_snapshot(['HK.9618'])

if ret == ft.RET_OK:
    stock_name = data.iloc[0]['stock_name']
    last_price = data.iloc[0]['last_price']
    print(f'{{stock_name}}最新價: HKD {{last_price}}')
    
quote_ctx.close()
```

🚀 下一步行動
1. 下載並安裝OpenD網關
2. 在富途牛牛APP中啟用API權限
3. 運行測試腳本驗證連接
4. 開發具體的股票查詢應用

📋 注意事項
- 需要富途交易賬戶
- 首次使用需在APP中啟用API
- 建議先在模擬環境測試
- 保護好API訪問憑證

所有相關文件已保存在工作空間中，可以隨時查閱和使用。

發送時間：{current_time}
發送者：OpenClaw助理"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 發送郵件
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
        
        print("✅ 富途API研究報告郵件發送成功！")
        return True
        
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        return False

if __name__ == "__main__":
    send_futu_report()