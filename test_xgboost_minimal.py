#!/usr/bin/env python3
"""
最小化XGBoost測試 - 確認環境正常
"""

import sys
print("Python版本:", sys.version)

try:
    import numpy as np
    print("✅ numpy版本:", np.__version__)
except ImportError:
    print("❌ numpy未安裝")

try:
    import pandas as pd
    print("✅ pandas版本:", pd.__version__)
except ImportError:
    print("❌ pandas未安裝")

try:
    import xgboost as xgb
    print("✅ xgboost版本:", xgb.__version__)
    
    # 簡單測試XGBoost
    X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    y = np.array([0, 1, 0, 1])
    
    model = xgb.XGBClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    predictions = model.predict(X)
    accuracy = (predictions == y).mean()
    print(f"✅ XGBoost簡單測試準確率: {accuracy:.2f}")
    
except Exception as e:
    print(f"❌ xgboost錯誤: {e}")

try:
    from sklearn.model_selection import train_test_split
    print("✅ scikit-learn可用")
except ImportError:
    print("❌ scikit-learn未安裝")

print("\n🎯 環境檢查完成!")