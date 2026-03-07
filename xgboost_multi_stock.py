#!/usr/bin/env python3
"""
XGBoost多股票交易系統 - 完整版
監控: 聯想(00992), 騰訊(00700), 阿里(09988), 盈富(02800), 恆生指數(HSI), 兩倍看空(07500), 比亞迪(01211)
功能:
1. 富途API獲取真實股價
2. K線數據分析
3. 成交量八大法則分析
4. 自動交易信號生成
每5分鐘運行
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加項目路徑
sys.path.insert(0, '/Users/gordonlui/.openclaw/workspace')

# ML Model 相關
MODEL_PATH = Path('/Users/gordonlui/.openclaw/workspace/models/xgboost_model_real.pkl')
YFINANCE_MODEL_PATH = Path('/Users/gordonlui/.openclaw/workspace/models/yfinance_multi_model.json')
YFINANCE_ENHANCED_MODEL_PATH = Path('/Users/gordonlui/.openclaw/workspace/models/yfinance_enhanced_model.json')
MODEL_DIR = Path('/Users/gordonlui/.openclaw/workspace/models')

_model = None
_yfinance_model = None

def load_model():
    """載入訓練好的ML模型"""
    global _model
    if _model is None:
        try:
            import joblib
            if MODEL_PATH.exists():
                _model = joblib.load(MODEL_PATH)
                print(f"✅ ML模型已載入: {MODEL_PATH}")
            else:
                print(f"⚠️ 模型文件不存在: {MODEL_PATH}")
        except Exception as e:
            print(f"❌ 模型載入失敗: {e}")
    return _model

def ensemble_predict(code, kline_data):
    """Ensemble預測：用兩個模型並結合結果"""
    import pandas as pd
    
    # 檢查數據是否足夠
    if kline_data is None or (isinstance(kline_data, pd.DataFrame) and len(kline_data) < 20):
        print(f"  ⚠️ 數據不足，無法使用ML模型")
        return None
    
    # 模型1: 富途模型 (用富途數據訓練)
    model1 = load_model()
    result1 = None
    
    # 模型2: yfinance模型 (用Yahoo Finance數據訓練)
    model2 = load_yfinance_model()
    result2 = None
    
    predictions = []
    confidences = []
    sources = []
    
    # 如果有kline_data，嘗試用兩個模型預測
    if kline_data is not None and isinstance(kline_data, pd.DataFrame) and not kline_data.empty:
        try:
            features = create_prediction_features(
                kline_data['close'].astype(float),
                kline_data['high'].astype(float),
                kline_data['low'].astype(float),
                kline_data['volume'].astype(float)
            )
            feat_df = pd.DataFrame([features])
            
            # 嘗試模型1
            if model1:
                try:
                    feat_df1 = feat_df.copy()
                    if hasattr(model1, 'feature_names_in_'):
                        for col in model1.feature_names_in_:
                            if col not in feat_df1.columns:
                                feat_df1[col] = 0
                        feat_df1 = feat_df1[model1.feature_names_in_]
                    X1 = feat_df1.values.astype(float)
                    pred1 = int(model1.predict(X1)[0])
                    prob1 = model1.predict_proba(X1)[0]
                    predictions.append(pred1)
                    confidences.append(float(max(prob1)))
                    sources.append('Futu')
                except Exception as e:
                    print(f"  模型1預測失敗: {e}")
            
            # 嘗試模型2
            if model2:
                try:
                    feat_df2 = feat_df.copy()
                    if hasattr(model2, 'feature_names_in_'):
                        for col in model2.feature_names_in_:
                            if col not in feat_df2.columns:
                                feat_df2[col] = 0
                        feat_df2 = feat_df2[model2.feature_names_in_]
                    X2 = feat_df2.values.astype(float)
                    pred2 = int(model2.predict(X2)[0])
                    prob2 = model2.predict_proba(X2)[0]
                    predictions.append(pred2)
                    confidences.append(float(max(prob2)))
                    sources.append('yFinance')
                except Exception as e:
                    print(f"  模型2預測失敗: {e}")
        except Exception as e:
            print(f"  特徵創建失敗: {e}")
    
    # Ensemble: 平均兩個模型的預測
    if len(predictions) >= 2:
        # 兩個模型加權平均
        avg_pred = sum(predictions) / len(predictions)
        avg_conf = sum(confidences) / len(confidences)
        
        # 如果兩個模型意見一致，信心更高
        if predictions[0] == predictions[1]:
            avg_conf = min(0.95, avg_conf + 0.15)
        
        label_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
        
        # 四捨五入到最近的整數
        final_pred = round(avg_pred)
        final_pred = max(0, min(2, final_pred))  # clamp to 0-2
        
        return {
            'signal': label_map.get(final_pred, 'HOLD'),
            'confidence': avg_conf * 100,
            'sources': sources,
            'details': list(zip(predictions, confidences))
        }
    elif len(predictions) == 1:
        # 只有一個模型
        label_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
        return {
            'signal': label_map.get(predictions[0], 'HOLD'),
            'confidence': confidences[0] * 100,
            'sources': sources,
            'details': list(zip(predictions, confidences))
        }
    
    return None

def create_prediction_features(close, high, low, volume):
    """為預測創建特徵 (與訓練時相同)"""
    import pandas as pd
    import numpy as np
    
    features = {}
    
    # 價格數據轉換
    close = pd.Series(close) if not isinstance(close, pd.Series) else close
    high = pd.Series(high) if not isinstance(high, pd.Series) else high
    low = pd.Series(low) if not isinstance(low, pd.Series) else low
    volume = pd.Series(volume) if not isinstance(volume, pd.Series) else volume
    
    close = close.astype(float)
    high = high.astype(float)
    low = low.astype(float)
    volume = volume.astype(float)
    
    # 價格變化
    features['return_1d'] = close.pct_change(1).iloc[-1] if len(close) > 1 else 0
    features['return_5d'] = close.pct_change(5).iloc[-1] if len(close) > 5 else 0
    features['return_10d'] = close.pct_change(10).iloc[-1] if len(close) > 10 else 0
    
    # 黃金分割位
    for window in [20, 60]:
        rolling_high = high.rolling(window).max().iloc[-1] if len(high) >= window else high.max()
        rolling_low = low.rolling(window).min().iloc[-1] if len(low) >= window else low.min()
        for key in ['0.382', '0.5', '0.618']:
            golden_level = rolling_low + (rolling_high - rolling_low) * float(key)
            features[f'golden_{key}_{window}d'] = close.iloc[-1] / golden_level - 1 if golden_level else 0
    
    # 均線
    for window in [8, 13, 21, 34, 55]:
        ma = close.rolling(window).mean().iloc[-1] if len(close) >= window else close.mean()
        features[f'MA{window}'] = close.iloc[-1] / ma - 1 if ma else 0
    
    # EMA
    for span in [8, 13, 21, 34]:
        ema = close.ewm(span=span, adjust=False).mean().iloc[-1]
        features[f'EMA{span}'] = close.iloc[-1] / ema - 1 if ema else 0
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
    rs = gain / loss if loss != 0 else 1
    features['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
    macd = ema12 - ema26
    signal = macd  # 簡化
    features['MACD'] = macd
    features['MACD_hist'] = macd - signal
    
    # 布林線
    bb20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else close.mean()
    bb_std = close.rolling(20).std().iloc[-1] if len(close) >= 20 else close.std()
    bb_upper = bb20 + 2 * bb_std
    bb_lower = bb20 - 2 * bb_std
    bb_range = bb_upper - bb_lower
    features['BB_position'] = (close.iloc[-1] - bb_lower) / bb_range * 100 if bb_range != 0 else 50
    
    # 成交量
    avg_volume = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.mean()
    features['volume_ratio'] = float(volume.iloc[-1]) / float(avg_volume) if float(avg_volume) != 0 else 1
    
    # 確保所有值都是scalar
    for k, v in features.items():
        if hasattr(v, 'item'):  # numpy scalar
            features[k] = float(v)
        elif hasattr(v, '__len__') and not isinstance(v, str):
            features[k] = float(v[0]) if len(v) > 0 else 0
        else:
            features[k] = float(v) if v is not None else 0
    
    return features

def ml_predict(code):
    """使用ML模型預測"""
    model = load_model()
    if model is None:
        return None
    
    try:
        from futu import OpenQuoteContext, KLType
        
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        ret, data, _ = quote_ctx.request_history_kline(
            code,
            start=(datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
            end=datetime.now().strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            max_count=100
        )
        
        quote_ctx.close()
        
        if ret == 0 and data is not None and not data.empty:
            features = create_prediction_features(
                data['close'].astype(float),
                data['high'].astype(float),
                data['low'].astype(float),
                data['volume'].astype(float)
            )
            
            # 轉換為numpy array
            import pandas as pd
            feat_df = pd.DataFrame([features])
            
            # 確保特徵順序與訓練時相同
            feature_names = list(model.feature_names_in_) if hasattr(model, 'feature_names_in_') else list(feat_df.columns)
            for col in feature_names:
                if col not in feat_df.columns:
                    feat_df[col] = 0
            feat_df = feat_df[feature_names]
            
            # 轉換為numpy array避免問題
            X = feat_df.values.astype(float)
            
            # 預測
            try:
                pred = int(model.predict(X)[0])
                prob = model.predict_proba(X)[0]
                
                # 轉換標籤
                label_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
                signal = label_map.get(pred, 'HOLD')
                confidence = float(max(prob)) * 100
                
                return {
                    'signal': signal,
                    'confidence': confidence,
                    'proba': prob.tolist()
                }
            except Exception as pred_err:
                print(f"  預測錯誤: {pred_err}")
        
        return None
    except Exception as e:
        print(f"ML預測失敗: {e}")
        return None

def load_yfinance_model():
    """載入yfinance訓練的模型 (增強版優先)"""
    global _yfinance_model
    if _yfinance_model is None:
        try:
            from xgboost import XGBClassifier
            # 優先使用增強模型
            if YFINANCE_ENHANCED_MODEL_PATH.exists():
                _yfinance_model = XGBClassifier()
                _yfinance_model.load_model(str(YFINANCE_ENHANCED_MODEL_PATH))
                print(f"✅ yfinance增強模型已載入")
            elif YFINANCE_MODEL_PATH.exists():
                _yfinance_model = XGBClassifier()
                _yfinance_model.load_model(str(YFINANCE_MODEL_PATH))
                print(f"✅ yfinance模型已載入: {YFINANCE_MODEL_PATH}")
            else:
                print(f"⚠️ yfinance模型不存在")
        except Exception as e:
            print(f"❌ yfinance模型載入失敗: {e}")
    return _yfinance_model

def calculate_rr_ratio(code, current_price, kline_data, signal):
    """計算風險回報比率
    
    Returns:
        (rr_ratio, stop_loss, take_profit, recommendation)
        - rr_ratio: reward/risk ratio (>=2.0 先出擊)
        - stop_loss: 建議止損價
        - take_profit: 建議目標價
        - recommendation: 'TRADE' 或 'NO_TRADE'
    """
    import pandas as pd
    
    if kline_data is None or signal == 'HOLD':
        return 0, 0, 0, 'NO_TRADE'
    
    # 確保kline_data是DataFrame
    if isinstance(kline_data, pd.DataFrame) and not kline_data.empty:
        close_prices = kline_data['close'].astype(float)
    else:
        return 0, current_price * 0.97, current_price * 1.06, 'NO_TRADE'
    
    # 計算支撐/阻力位
    bb20 = close_prices.rolling(20).mean().iloc[-1]
    bb_std = close_prices.rolling(20).std().iloc[-1]
    bb_lower = bb20 - 2 * bb_std
    bb_upper = bb20 + 2 * bb_std
    
    # 計算止損 (用布林底或 ATR)
    atr = close_prices.diff().abs().rolling(14).mean().iloc[-1]
    stop_loss = min(bb_lower, current_price - atr * 2)
    
    # 計算目標價 (用布林頂 或 黃金分割)
    golden_618 = bb20 - 0.618 * (bb20 - bb_lower)
    take_profit = max(bb_upper, current_price + (current_price - stop_loss) * 2)  # 2:1
    
    # 計算 R/R ratio
    risk = current_price - stop_loss
    reward = take_profit - current_price
    
    if risk <= 0:
        return 0, stop_loss, take_profit, 'NO_TRADE'
    
    rr_ratio = reward / risk
    
    # 只有 R/R >= 2.0 先交易
    if rr_ratio >= 2.0:
        recommendation = 'TRADE'
    else:
        recommendation = 'NO_TRADE'
    
    return round(rr_ratio, 2), round(stop_loss, 2), round(take_profit, 2), recommendation

# 監控股票列表 (久留美模擬倉 + Gordon持倉 + 擴展監控)
STOCKS = {
    # 久留美持倉 (已更新 2026-02-24)
    # HK.00700: {'name': '騰訊控股', 'owner': '久留美'}, # 已止損
    # HK.00992: {'name': '聯想集團', 'owner': '久留美'}, # 尋日賣出
    'HK.03750': {'name': '寧德時代', 'owner': 'Monitor'},
    'HK.02800': {'name': '盈富基金', 'owner': '久留美'},
    'HK.07500': {'name': '兩倍看空', 'owner': '久留美'},
    'HK.01211': {'name': '比亞迪', 'owner': '久留美'},
    # Gordon持倉 (収息組合)
    'HK.09618': {'name': '京東集團', 'owner': 'Gordon'},
    'HK.00005': {'name': '匯豐控股', 'owner': 'Gordon'},
    'HK.01398': {'name': '工商銀行', 'owner': 'Gordon'},
    'HK.02638': {'name': '港燈', 'owner': 'Gordon'},
    # 恆生指數
    'HK.800000': {'name': '恆生指數', 'owner': '-'},
    # 擴展監控 (15隻)
    'HK.00857': {'name': '中國石油', 'owner': 'Monitor'},
    'HK.01024': {'name': '快手', 'owner': 'Monitor'},
    'HK.02331': {'name': '李寧', 'owner': 'Monitor'},
    'HK.02343': {'name': '太平洋航運', 'owner': 'Monitor'},  # 乾散貨船 (煤炭/鐵礦)
    'HK.00358': {'name': '江西銅業', 'owner': 'Monitor'},  # 銅 (變壓器材料)
    'HK.02318': {'name': '中國銀行', 'owner': 'Monitor'},
    'HK.01810': {'name': '小米集團', 'owner': 'Monitor'},
    'HK.09988': {'name': '阿里巴巴', 'owner': 'Monitor'},
}

def get_realtime_prices():
    """1. 富途API獲取真實股價"""
    try:
        from futu import OpenQuoteContext
        
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        results = {}
        for code in STOCKS.keys():
            ret, data = quote_ctx.get_market_snapshot([code])
            if ret == 0 and not data.empty:
                row = data.iloc[0]
                last_price = row.get('last_price', 0)
                prev_close = row.get('prev_close_price', last_price)
                
                if prev_close and prev_close > 0:
                    change_pct = ((last_price - prev_close) / prev_close) * 100
                else:
                    change_pct = 0
                
                results[code] = {
                    'price': last_price,
                    'prev_close': prev_close,
                    'change_pct': change_pct,
                    'volume': row.get('volume', 0),
                    'turnover': row.get('turnover', 0),
                }
        
        quote_ctx.close()
        return results
    except Exception as e:
        print(f"Error getting prices: {e}")
        return {}

def get_kline_data(code, days=30):
    """2. K線數據分析"""
    try:
        from futu import OpenQuoteContext, KLType
        
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 獲取日K線
        ret, data, page_req_key = quote_ctx.request_history_kline(
            code, 
            start=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end=datetime.now().strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            max_count=100
        )
        
        quote_ctx.close()
        
        if ret == 0 and data is not None and not data.empty:
            return data
        return None
    except Exception as e:
        print(f"Error getting kline: {e}")
        return None

def analyze_kline_technicals(kline_data):
    """技術分析 - 完整指標"""
    if kline_data is None or kline_data.empty:
        return {}
    
    try:
        close_prices = kline_data['close'].astype(float)
        high_prices = kline_data['high'].astype(float)
        low_prices = kline_data['low'].astype(float)
        
        # 轉為array
        close_arr = close_prices.values
        high_arr = high_prices.values
        low_arr = low_prices.values
        
        # === 基本均線 MA ===
        ma5 = float(close_prices.rolling(5).mean().iloc[-1])
        ma10 = float(close_prices.rolling(10).mean().iloc[-1])
        ma20 = float(close_prices.rolling(20).mean().iloc[-1])
        
        # === EMA 指數移動平均線 (8, 13, 34) ===
        ema8 = float(close_prices.ewm(span=8, adjust=False).mean().iloc[-1])
        ema13 = float(close_prices.ewm(span=13, adjust=False).mean().iloc[-1])
        ema34 = float(close_prices.ewm(span=34, adjust=False).mean().iloc[-1])
        
        # === RSI ===
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1])
        
        # === MACD ===
        ema12 = close_prices.ewm(span=12, adjust=False).mean()
        ema26 = close_prices.ewm(span=26, adjust=False).mean()
        macd_line = float(ema12.iloc[-1] - ema26.iloc[-1])
        signal_line = macd_line  # 簡化版用MACD線本身
        macd_hist = float(macd_line - signal_line)
        
        # === 布林線 Bollinger Bands (20, 2) ===
        bb20 = close_prices.rolling(20).mean()
        bb_std = close_prices.rolling(20).std()
        bb_upper = float(bb20.iloc[-1] + 2 * bb_std.iloc[-1])
        bb_middle = float(bb20.iloc[-1])
        bb_lower = float(bb20.iloc[-1] - 2 * bb_std.iloc[-1])
        bb_range = bb_upper - bb_lower
        bb_position = float((close_arr[-1] - bb_lower) / bb_range * 100) if bb_range > 0 else 50
        
        # === 唐奇安通道 Donchian Channel (20) ===
        dc_upper = float(high_prices.rolling(20).max().iloc[-1])
        dc_lower = float(low_prices.rolling(20).min().iloc[-1])
        dc_middle = float((dc_upper + dc_lower) / 2)
        
        # === 趨勢判斷 ===
        current_price = float(close_arr[-1])
        if current_price > ma20:
            trend = "上升"
        elif current_price < ma20:
            trend = "下降"
        else:
            trend = "橫行"
        
        return {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ema8': ema8,
            'ema13': ema13,
            'ema34': ema34,
            'rsi': rsi,
            'macd': macd_line,
            'macd_signal': signal_line,
            'macd_hist': macd_hist,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'bb_position': bb_position,
            'dc_upper': dc_upper,
            'dc_lower': dc_lower,
            'dc_middle': dc_middle,
            'trend': trend,
            'close': current_price
        }
    except Exception as e:
        print(f"Technical analysis error: {e}")
        return {}

def analyze_volume_pattern(kline_data):
    """3. 成交量八大法則分析"""
    if kline_data is None or kline_data.empty:
        return {'signal': 'UNKNOWN', 'reason': '無數據'}
    
    try:
        volumes = kline_data['volume'].astype(float)
        closes = kline_data['close'].astype(float)
        
        # 計算量比 (今早成交量/過去5日平均)
        avg_volume = volumes.rolling(5).mean().iloc[-1]
        current_volume = volumes.iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # 價格變化
        price_change = (closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2] * 100 if len(closes) > 1 else 0
        volume_change = (volumes.iloc[-1] - volumes.iloc[-2]) / volumes.iloc[-2] * 100 if len(volumes) > 1 and volumes.iloc[-2] > 0 else 0
        
        # 成交量八大法則
        signal = 'HOLD'
        reason = '正常成交量'
        
        # 法則1: 量漲價漲 - 健康上升趨勢
        if volume_ratio > 1.2 and price_change > 0.5:
            signal = 'BUY'
            reason = '量漲價漲 - 健康上升趨勢'
        
        # 法則2: 價漲量縮 - 警示信號
        elif price_change > 1 and volume_ratio < 0.7:
            signal = 'SELL'
            reason = '價漲量縮 - 警示信號'
        
        # 法則3: 量縮價漲 - 趨勢反轉
        elif volume_ratio < 0.5 and price_change > 0:
            signal = 'SELL'
            reason = '量縮價漲 - 趨勢反轉風險'
        
        # 法則4: 高位放量滯漲 - 下跌前兆
        elif volume_ratio > 2 and abs(price_change) < 0.3:
            signal = 'SELL'
            reason = '高位放量滯漲 - 下跌前兆'
        
        # 法則5: 底部成交量遞減 - 即將上漲
        elif volume_ratio < 0.3 and price_change > -0.5:
            signal = 'BUY'
            reason = '底部成交量遞減 - 即將上漲'
        
        # 法則6: 恐慌性拋售 - 空頭結束
        elif volume_ratio > 3 and price_change < -3:
            signal = 'BUY'
            reason = '恐慌性拋售 - 空頭可能結束'
        
        # 法則7: 跌破趨勢線放量 - 下跌信號
        elif volume_ratio > 1.5 and price_change < -2:
            signal = 'SELL'
            reason = '跌破趨勢線放量'
        
        # 法則8: 價跌量縮 - 可能見底
        elif volume_ratio < 0.6 and price_change < -1:
            signal = 'BUY'
            reason = '價跌量縮 - 可能見底'
        
        return {
            'signal': signal,
            'reason': reason,
            'volume_ratio': volume_ratio,
            'price_change': price_change
        }
    except Exception as e:
        return {'signal': 'UNKNOWN', 'reason': str(e)}

def generate_trading_signal(price_data, kline_analysis, volume_analysis, code=None, kline_data=None):
    """4. 自動交易信號生成 - ML模型優先 + R/R過濾"""
    if not price_data:
        return 'HOLD', 0.5, '無數據', None
    
    change_pct = price_data.get('change_pct', 0)
    current_price = price_data.get('price', 0)
    
    # === 首先嘗試ML模型預測 ===
    ml_result = None
    if code and kline_data is not None:
        ml_result = ensemble_predict(code, kline_data)
    
    # 如果ML模型成功，優先使用ML結果
    signal = 'HOLD'
    confidence = 0.5
    reasons = []
    
    if ml_result:
        ml_signal = ml_result['signal']
        ml_confidence = ml_result['confidence']
        sources = ml_result.get('sources', [])
        
        # 計算 R/R 比率 (傳入原始kline數據)
        rr_ratio, stop_loss, take_profit, recommendation = calculate_rr_ratio(
            code, current_price, kline_data, ml_signal
        )
        
        reasons = [f'Ensemble:{ml_signal}({ml_confidence:.0f}%)({"/".join(sources)})']
        
        # 只有 R/R >= 2.0 先交易
        if recommendation == 'TRADE':
            reasons.append(f'R/R={rr_ratio:.1f}✅')
            
            # 技術指標確認
            rsi = kline_analysis.get('rsi', 50)
            trend = kline_analysis.get('trend', '橫行')
            ema8 = kline_analysis.get('ema8', 0)
            ema13 = kline_analysis.get('ema13', 0)
            bb_position = kline_analysis.get('bb_position', 50)
            
            confirm_count = 0
            
            if trend == '上升':
                confirm_count += 1
                reasons.append('上升趨勢')
            elif trend == '下降':
                confirm_count -= 1
                reasons.append('下降趨勢')
            
            if ema8 > ema13:
                confirm_count += 1
                reasons.append('多頭')
            
            if rsi < 30:
                confirm_count += 1
                reasons.append(f'RSI超賣{int(rsi)}')
            elif rsi > 70:
                confirm_count -= 1
                reasons.append(f'RSI超買{int(rsi)}')
            
            if bb_position < 20:
                confirm_count += 1
                reasons.append('布林底')
            
            # ML信號強烈 + R/R OK
            if ml_confidence > 75 or (ml_signal == 'BUY' and confirm_count >= 0):
                signal = ml_signal
                confidence = ml_confidence / 100
        else:
            reasons.append(f'R/R={rr_ratio:.1f}❌(低於2.0)')
    
    # 如果冇ML信號或不符合R/R，用技術指標
    if signal == 'HOLD':
        # === 技術指標邏輯 ===
        rsi = kline_analysis.get('rsi', 50)
        trend = kline_analysis.get('trend', '橫行')
        volume_signal = volume_analysis.get('signal', 'HOLD')
        
        ema8 = kline_analysis.get('ema8', 0)
        ema13 = kline_analysis.get('ema13', 0)
        ema34 = kline_analysis.get('ema34', 0)
        
        macd = kline_analysis.get('macd', 0)
        macd_signal = kline_analysis.get('macd_signal', 0)
        
        bb_position = kline_analysis.get('bb_position', 50)
        
        score = 0
        reasons = ['技術指標']
        
        if trend == '上升':
            score += 2
            reasons.append('上升趨勢')
        elif trend == '下降':
            score -= 2
            reasons.append('下降趨勢')
        
        if ema8 > ema13 > ema34:
            score += 2
            reasons.append('多頭排列')
        elif ema8 < ema13 < ema34:
            score -= 2
            reasons.append('空頭排列')
        
        if macd > macd_signal and macd > 0:
            score += 1
        elif macd < macd_signal and macd < 0:
            score -= 1
        
        if change_pct < -2:
            score += 1
        elif change_pct > 2:
            score -= 1
        
        if bb_position < 20:
            score += 1
            reasons.append('布林底')
        elif bb_position > 80:
            score -= 1
            reasons.append('布林頂')
        
        if rsi < 30:
            score += 1
            reasons.append(f'RSI超賣{int(rsi)}')
        elif rsi > 70:
            score -= 1
            reasons.append(f'RSI超買{int(rsi)}')
        
        if volume_signal == 'BUY':
            score += 1
        elif volume_signal == 'SELL':
            score -= 1
        
        # 檢查 R/R
        rr_ratio, stop_loss, take_profit, recommendation = calculate_rr_ratio(
            code, current_price, kline_data, 'BUY' if score > 0 else 'SELL'
        )
        
        if score >= 3:
            if recommendation == 'TRADE':
                signal = 'BUY'
                confidence = min(0.90, 0.5 + score * 0.1)
                reasons.append(f'R/R={rr_ratio:.1f}✅')
            else:
                signal = 'HOLD'
                confidence = 0.6
                reasons.append(f'R/R={rr_ratio:.1f}❌')
        elif score <= -3:
            if recommendation == 'TRADE':
                signal = 'SELL'
                confidence = min(0.90, 0.5 + abs(score) * 0.1)
                reasons.append(f'R/R={rr_ratio:.1f}✅')
            else:
                signal = 'HOLD'
                confidence = 0.6
                reasons.append(f'R/R={rr_ratio:.1f}❌')
        elif score >= 1:
            signal = 'BUY'
            confidence = 0.6
        elif score <= -1:
            signal = 'SELL'
            confidence = 0.6
        else:
            signal = 'HOLD'
            confidence = 0.6
    
    reason = '+'.join(reasons) if reasons else '觀望'
    
    return signal, confidence, reason, None
    ema13 = kline_analysis.get('ema13', 0)
    ema34 = kline_analysis.get('ema34', 0)
    
    macd = kline_analysis.get('macd', 0)
    macd_signal = kline_analysis.get('macd_signal', 0)
    macd_hist = kline_analysis.get('macd_hist', 0)
    
    bb_position = kline_analysis.get('bb_position', 50)
    
    # 綜合評分
    score = 0
    
    if trend == '上升':
        score += 2
    elif trend == '下降':
        score -= 2
    
    if ema8 > ema13 > ema34:
        score += 2
    elif ema8 < ema13 < ema34:
        score -= 2
    
    if macd > macd_signal and macd > 0:
        score += 1
    elif macd < macd_signal and macd < 0:
        score -= 1
    
    if change_pct < -2:
        score += 1
    elif change_pct > 2:
        score -= 1
    
    if bb_position < 20:
        score += 1
    elif bb_position > 80:
        score -= 1
    
    if rsi < 30:
        score += 1
    elif rsi > 70:
        score -= 1
    
    if volume_signal == 'BUY':
        score += 1
    elif volume_signal == 'SELL':
        score -= 1
    
    if score >= 3:
        signal = 'BUY'
        confidence = min(0.90, 0.5 + score * 0.1)
    elif score <= -3:
        signal = 'SELL'
        confidence = min(0.90, 0.5 + abs(score) * 0.1)
    elif score >= 1:
        signal = 'BUY'
        confidence = 0.6
    elif score <= -1:
        signal = 'SELL'
        confidence = 0.6
    else:
        signal = 'HOLD'
        confidence = 0.6
    
    # 評估原因
    reasons = []
    if trend == '上升':
        reasons.append('上升趨勢')
    elif trend == '下降':
        reasons.append('下降趨勢')
    if ema8 > ema13 > ema34:
        reasons.append('多頭排列')
    elif ema8 < ema13 < ema34:
        reasons.append('空頭排列')
    if macd > macd_signal:
        reasons.append('MACD多頭')
    elif macd < macd_signal:
        reasons.append('MACD空頭')
    if bb_position < 20:
        reasons.append('布林底')
    elif bb_position > 80:
        reasons.append('布林頂')
    if rsi < 30:
        reasons.append(f'RSI超賣{int(rsi)}')
    elif rsi > 70:
        reasons.append(f'RSI超買{int(rsi)}')
    if volume_signal == 'BUY':
        reasons.append('成交量買入')
    elif volume_signal == 'SELL':
        reasons.append('成交量賣出')
    
    reason = '+'.join(reasons) if reasons else '觀望'
    
    return signal, confidence, reason

def analyze_all_stocks():
    """全面分析所有監控股票"""
    print(f"🚀 XGBoost多股票交易系統啟動 - {datetime.now()}")
    print("=" * 60)
    print("功能: 1)富途API獲取真實股價 2)K線數據分析 3)成交量八大法則 4)自動交易信號")
    print("=" * 60)
    
    # 1. 獲取實時價格
    print("\n📡 1. 獲取實時股價...")
    price_data = get_realtime_prices()
    print(f"   獲取到 {len(price_data)} 隻股票數據")
    
    results = []
    
    for code, stock_name in STOCKS.items():
        print(f"\n📊 分析 {code} {stock_name}...")
        
        if code not in price_data:
            print(f"   ❌ 無價格數據")
            continue
        
        # 2. K線數據分析 (增加日至60日確保有足夠數據)
        kline_data = get_kline_data(code, days=60)
        
        # 如果數據不足30日，嘗試獲取更多
        if kline_data is None or len(kline_data) < 30:
            kline_data = get_kline_data(code, days=90)
        
        kline_analysis = analyze_kline_technicals(kline_data)
        
        # 3. 成交量八大法則
        volume_analysis = analyze_volume_pattern(kline_data)
        
        # 4. 自動交易信號
        signal, confidence, reason, _ = generate_trading_signal(
            price_data[code], kline_analysis, volume_analysis, code, kline_data
        )
        
        price = price_data[code]['price']
        change = price_data[code]['change_pct']
        
        # 根據信號選擇emoji
        if signal == 'BUY':
            emoji = '🟢'
        elif signal == 'SELL':
            emoji = '🔴'
        else:
            emoji = '🟡'
        
        print(f"   價格: ${price:.2f} ({change:+.2f}%)")
        print(f"   信號: {emoji} {signal} (置信度: {confidence:.0%})")
        print(f"   原因: {reason}")
        
        if kline_analysis:
            # 顯示完整技術指標
            ma5 = kline_analysis.get('ma5', 0)
            ema8 = kline_analysis.get('ema8', 0)
            ema13 = kline_analysis.get('ema13', 0)
            rsi = kline_analysis.get('rsi', 0)
            macd = kline_analysis.get('macd', 0)
            bb_pos = kline_analysis.get('bb_position', 50)
            trend = kline_analysis.get('trend', 'N/A')
            print(f"   技術: MA5=${ma5:.2f}, EMA8/13={ema8:.2f}/{ema13:.2f}, RSI={rsi:.0f}, MACD={macd:.3f}, BB位置={bb_pos:.0f}%, 趨勢={trend}")
        
        if volume_analysis:
            print(f"   量價: {volume_analysis.get('reason', 'N/A')}")
        
        results.append({
            'code': code,
            'name': stock_name,
            'price': price,
            'change_pct': change,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'kline': kline_analysis,
            'volume': volume_analysis
        })
    
    return results

def generate_report(results):
    """生成報告"""
    report = []
    report.append(f"📊 XGBoost多股票交易報告 - {datetime.now().strftime('%H:%M')}")
    report.append("=" * 60)
    report.append("功能: 1)富途API✓ 2)K線分析✓ 3)成交量八大法則✓ 4)自動信號✓")
    report.append("=" * 60)
    
    signals = []
    
    for r in results:
        if r['signal'] == 'BUY':
            emoji = '🟢'
        elif r['signal'] == 'SELL':
            emoji = '🔴'
        else:
            emoji = '🟡'
        
        report.append(f"\n{emoji} {r['code']} {r['name']}")
        report.append(f"   價格: ${r['price']:.2f} ({r['change_pct']:+.2f}%)")
        report.append(f"   信號: {r['signal']} (置信度: {r['confidence']:.0%})")
        report.append(f"   原因: {r['reason']}")
        
        if r['signal'] in ['BUY', 'SELL']:
            signals.append(f"{r['code']}:{r['signal']}")
    
    report.append("\n" + "=" * 60)
    if signals:
        report.append(f"⚡ 關注信號: {', '.join(signals)}")
    else:
        report.append("✅ 市場觀望中")
    
    return "\n".join(report)

def main():
    results = analyze_all_stocks()
    
    if not results:
        print("❌ 無分析結果")
        sys.exit(1)
    
    report = generate_report(results)
    print("\n" + report)
    
    # 保存報告
    report_dir = Path('/Users/gordonlui/.openclaw/workspace/trading_reports')
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"xgboost_multi_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ 報告已保存: {report_file}")
    
    # 保存JSON格式報告（供自動交易使用）
    json_file = report_dir / "xgboost_multi_latest.json"
    signals_list = []
    for item in results:
        code = item.get('code', '')
        stock_code = code.replace('HK.', '') if code else ''
        signal = item.get('signal', 'HOLD')
        
        if 'SELL' in signal:
            signals_list.append({
                'stock': stock_code,
                'signal': 'SELL',
                'price': item.get('price', 0),
                'reason': item.get('reason', '')
            })
        elif 'BUY' in signal:
            signals_list.append({
                'stock': stock_code,
                'signal': 'BUY',
                'price': item.get('price', 0),
                'reason': item.get('reason', '')
            })
    
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'signals': signals_list,
        'results': results
    }
    
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✅ JSON報告已保存: {json_file}")
    
    # 自動執行交易
    print("\n🤖 準備執行自動交易...")
    os.system(f"python3 /Users/gordonlui/.openclaw/workspace/auto_trade_executor.py >> /Users/gordonlui/.openclaw/workspace/trading_reports/auto_trade.log 2>&1")

if __name__ == '__main__':
    main()
