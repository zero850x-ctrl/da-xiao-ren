# XGBoost 自我學習報告
**日期:** 20260306

## 訓練數據
- 股票數: 20隻
- 數據總量: 1180條
- 週期: 過去90日
- 來源: 富途API (真實數據)

## 特徵重要性排序

- MACD_hist: 0.1549
- MACD: 0.1544
- EMA34: 0.0619
- return_10d: 0.0606
- return_5d: 0.0603
- return_1d: 0.0482
- RSI: 0.0477
- MA8: 0.0474
- volume_ratio: 0.0459
- golden_0.618_20d: 0.0423
- MA13: 0.0368
- EMA8: 0.0355
- golden_0.5_20d: 0.0346
- MA34: 0.0330
- EMA13: 0.0287
- EMA21: 0.0279
- BB_position: 0.0273
- golden_0.382_20d: 0.0273
- MA21: 0.0254
- golden_0.382_60d: 0.0000

## 關鍵發現
模型主要依靠以下特徵進行預測:
MACD_hist, MACD, EMA34, return_10d, return_5d

---
*此報告由 XGBoost 自我學習系統自動生成*
