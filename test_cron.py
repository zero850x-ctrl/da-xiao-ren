#!/usr/bin/env python3
"""
簡單測試腳本 - 驗證cron執行
"""
import datetime

print(f"🚀 Cron測試執行 - {datetime.datetime.now()}")
print("==========================================")
print("監控股票:")
print("1. 00992 聯想集團")
print("2. 00700 騰訊")
print("3. 09988 阿里")
print("4. 02800 盈富")
print("5. HSI 恆生指數")
print("==========================================")
print("✅ Cron任務執行成功!")
print(f"下次執行時間: {datetime.datetime.now() + datetime.timedelta(minutes=10)}")