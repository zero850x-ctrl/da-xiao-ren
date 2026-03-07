#!/usr/bin/env python3
"""
OANDA API 黃金交易測試腳本
使用OANDA REST API進行黃金(XAU/USD)交易
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from typing import Dict, List, Optional

class OandaGoldTrader:
    def __init__(self, account_id: str, api_key: str, environment: str = "practice"):
        """
        初始化OANDA黃金交易器
        
        :param account_id: OANDA賬戶ID
        :param api_key: OANDA API密鑰
        :param environment: 環境 ("practice" 或 "live")
        """
        self.account_id = account_id
        self.api_key = api_key
        self.environment = environment
        
        # 設置API端點
        if environment == "practice":
            self.base_url = "https://api-fxpractice.oanda.com"
        else:
            self.base_url = "https://api-fxtrade.oanda.com"
            
        self.symbol = "XAU_USD"  # OANDA的黃金交易對
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def test_connection(self) -> bool:
        """測試API連接"""
        print("🔗 測試OANDA API連接...")
        
        url = f"{self.base_url}/v3/accounts"
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 連接成功!")
                print(f"   賬戶數量: {len(data['accounts'])}")
                
                # 顯示賬戶信息
                for account in data['accounts']:
                    if account['id'] == self.account_id:
                        print(f"   找到目標賬戶: {account['id']}")
                        print(f"   賬戶類型: {account.get('type', 'N/A')}")
                        print(f"   賬戶貨幣: {account.get('currency', 'N/A')}")
                        return True
                        
                print(f"⚠️ 未找到賬戶ID: {self.account_id}")
                return False
                
            else:
                print(f"❌ 連接失敗: {response.status_code}")
                print(f"   錯誤信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 連接異常: {e}")
            return False
    
    def get_account_summary(self) -> Optional[Dict]:
        """獲取賬戶摘要"""
        print("\n📊 獲取賬戶摘要...")
        
        url = f"{self.base_url}/v3/accounts/{self.account_id}/summary"
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                account = data['account']
                
                print(f"   賬戶ID: {account['id']}")
                print(f"   餘額: ${float(account['balance']):.2f}")
                print(f"   淨值: ${float(account['NAV']):.2f}")
                print(f"   浮動盈虧: ${float(account['pl']):.2f}")
                print(f"   已用保證金: ${float(account['marginUsed']):.2f}")
                print(f"   可用保證金: ${float(account['marginAvailable']):.2f}")
                print(f"   保證金比例: {float(account['marginRate'])*100:.1f}%")
                
                return account
            else:
                print(f"❌ 獲取失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 獲取異常: {e}")
            return None
    
    def get_gold_price(self) -> Optional[Dict]:
        """獲取黃金當前價格"""
        print(f"\n💰 獲取黃金(XAU_USD)價格...")
        
        url = f"{self.base_url}/v3/accounts/{self.account_id}/pricing"
        params = {"instruments": self.symbol}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                prices = data['prices'][0]
                
                bid = float(prices['bids'][0]['price'])
                ask = float(prices['asks'][0]['price'])
                spread = (ask - bid) * 100  # 轉換為點數
                
                print(f"   交易對: {prices['instrument']}")
                print(f"   買入價: ${bid:.2f}")
                print(f"   賣出價: ${ask:.2f}")
                print(f"   點差: {spread:.1f} 點")
                print(f"   時間: {prices['time']}")
                
                return {
                    "bid": bid,
                    "ask": ask,
                    "spread": spread,
                    "time": prices['time']
                }
            else:
                print(f"❌ 獲取價格失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 獲取價格異常: {e}")
            return None
    
    def get_gold_candles(self, count: int = 100, granularity: str = "H1") -> Optional[pd.DataFrame]:
        """
        獲取黃金K線數據
        
        :param count: K線數量
        :param granularity: 時間粒度 (S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4, H6, H8, H12, D, W, M)
        """
        print(f"\n📈 獲取黃金K線數據 ({granularity})...")
        
        url = f"{self.base_url}/v3/instruments/{self.symbol}/candles"
        params = {
            "count": count,
            "granularity": granularity,
            "price": "M"  # 中間價
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                candles = data['candles']
                
                # 轉換為DataFrame
                records = []
                for candle in candles:
                    if candle['complete']:
                        records.append({
                            'time': candle['time'],
                            'open': float(candle['mid']['o']),
                            'high': float(candle['mid']['h']),
                            'low': float(candle['mid']['l']),
                            'close': float(candle['mid']['c']),
                            'volume': candle['volume']
                        })
                
                df = pd.DataFrame(records)
                df['time'] = pd.to_datetime(df['time'])
                
                print(f"   獲取到 {len(df)} 根K線")
                print(f"   時間範圍: {df['time'].min()} 到 {df['time'].max()}")
                print(f"   最新收盤價: ${df['close'].iloc[-1]:.2f}")
                print(f"   最高價: ${df['high'].max():.2f}")
                print(f"   最低價: ${df['low'].min():.2f}")
                
                return df
            else:
                print(f"❌ 獲取K線失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 獲取K線異常: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        print(f"\n📊 計算技術指標...")
        
        # 移動平均線
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        
        # RSI計算
        df['RSI'] = self.calculate_rsi(df['close'], period=14)
        
        # 布林帶
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # 最新值
        latest = df.iloc[-1]
        print(f"   SMA20: ${latest['SMA_20']:.2f}")
        print(f"   SMA50: ${latest['SMA_50']:.2f}")
        print(f"   RSI: {latest['RSI']:.2f}")
        print(f"   布林帶上軌: ${latest['BB_upper']:.2f}")
        print(f"   布林帶中軌: ${latest['BB_middle']:.2f}")
        print(f"   布林帶下軌: ${latest['BB_lower']:.2f}")
        
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI指標"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_open_positions(self) -> List[Dict]:
        """獲取當前持倉"""
        print(f"\n📦 獲取當前持倉...")
        
        url = f"{self.base_url}/v3/accounts/{self.account_id}/openPositions"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                positions = data['positions']
                
                if len(positions) == 0:
                    print("   沒有持倉")
                    return []
                
                print(f"   找到 {len(positions)} 個持倉")
                
                for pos in positions:
                    instrument = pos['instrument']
                    long_units = float(pos['long']['units'])
                    short_units = float(pos['short']['units'])
                    
                    if long_units > 0:
                        direction = "買入"
                        units = long_units
                        avg_price = float(pos['long']['averagePrice'])
                        pl = float(pos['long']['pl'])
                    elif short_units < 0:
                        direction = "賣出"
                        units = abs(short_units)
                        avg_price = float(pos['short']['averagePrice'])
                        pl = float(pos['short']['pl'])
                    else:
                        continue
                    
                    profit_color = "🟢" if pl >= 0 else "🔴"
                    
                    print(f"   {direction} {units}單位 {instrument}")
                    print(f"     平均價格: ${avg_price:.2f}")
                    print(f"     浮動盈虧: {profit_color} ${pl:.2f}")
                
                return positions
            else:
                print(f"❌ 獲取持倉失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 獲取持倉異常: {e}")
            return []
    
    def calculate_position_size(self, risk_percent: float = 1.0, stop_loss_pips: float = 50.0) -> float:
        """
        計算合適的倉位大小
        
        :param risk_percent: 風險百分比
        :param stop_loss_pips: 止損點數
        :return: 建議交易單位數
        """
        print(f"\n🎯 風險管理計算...")
        
        # 獲取賬戶信息
        account = self.get_account_summary()
        if not account:
            return 1000  # 默認最小單位
        
        balance = float(account['balance'])
        
        # 黃金每點價值 (1000單位 ≈ 1盎司)
        # 實際值需要根據經紀商調整
        pip_value_per_unit = 0.01  # 每單位每點價值約$0.01
        
        # 計算風險金額
        risk_amount = balance * (risk_percent / 100)
        
        # 計算單位數
        units = risk_amount / (stop_loss_pips * pip_value_per_unit)
        
        # 取整到1000的倍數 (OANDA最小單位通常是1000)
        units = round(units / 1000) * 1000
        
        # 最小單位檢查
        units = max(1000, units)  # 最小1000單位
        
        print(f"   賬戶餘額: ${balance:.2f}")
        print(f"   風險比例: {risk_percent}%")
        print(f"   風險金額: ${risk_amount:.2f}")
        print(f"   止損點數: {stop_loss_pips}點")
        print(f"   建議單位數: {units:.0f}")
        
        return units
    
    def analyze_signals(self, df: pd.DataFrame):
        """分析交易信號"""
        print(f"\n🔍 交易信號分析:")
        
        if df is None or len(df) < 50:
            print("   數據不足，無法分析")
            return
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 1. 移動平均線交叉信號
        if prev['SMA_20'] <= prev['SMA_50'] and latest['SMA_20'] > latest['SMA_50']:
            print("   🟢 買入信號: SMA20上穿SMA50 (黃金交叉)")
        elif prev['SMA_20'] >= prev['SMA_50'] and latest['SMA_20'] < latest['SMA_50']:
            print("   🔴 賣出信號: SMA20下穿SMA50 (死亡交叉)")
        else:
            print("   ⚪ 移動平均線: 無交叉信號")
        
        # 2. RSI信號
        rsi = latest['RSI']
        if pd.notna(rsi):
            if rsi < 30:
                print(f"   🟢 買入信號: RSI超賣 ({rsi:.1f} < 30)")
            elif rsi > 70:
                print(f"   🔴 賣出信號: RSI超買 ({rsi:.1f} > 70)")
            else:
                print(f"   ⚪ RSI: {rsi:.1f} (中性)")
        
        # 3. 布林帶信號
        price = latest['close']
        if price <= latest['BB_lower']:
            print(f"   🟢 買入信號: 價格觸及布林帶下軌 (${price:.2f})")
        elif price >= latest['BB_upper']:
            print(f"   🔴 賣出信號: 價格觸及布林帶上軌 (${price:.2f})")
        else:
            print(f"   ⚪ 布林帶: 價格在中軌附近 (${price:.2f})")
    
    def run_demo(self):
        """運行演示"""
        print("=" * 60)
        print("🏆 OANDA API 黃金交易系統演示")
        print("=" * 60)
        
        # 1. 測試連接
        if not self.test_connection():
            print("❌ 無法連接OANDA API，請檢查API密鑰和賬戶ID")
            return
        
        try:
            # 2. 獲取賬戶信息
            self.get_account_summary()
            
            # 3. 獲取黃金價格
            price_info = self.get_gold_price()
            
            if price_info:
                # 4. 獲取K線數據
                df = self.get_gold_candles(count=200, granularity="H1")
                
                if df is not None:
                    # 5. 計算技術指標
                    df = self.calculate_indicators(df)
                    
                    # 6. 分析交易信號
                    self.analyze_signals(df)
            
            # 7. 檢查持倉
            self.get_open_positions()
            
            # 8. 風險管理計算
            self.calculate_position_size(risk_percent=1.0, stop_loss_pips=50.0)
            
            print("\n" + "=" * 60)
            print("✅ 演示完成！")
            print("=" * 60)
            print("\n📝 下一步:")
            print("1. 註冊OANDA模擬賬戶獲取API密鑰")
            print("2. 使用真實API密鑰運行此腳本")
            print("3. 實現實際交易功能")
            
        except Exception as e:
            print(f"\n❌ 演示過程中出錯: {e}")
            import traceback