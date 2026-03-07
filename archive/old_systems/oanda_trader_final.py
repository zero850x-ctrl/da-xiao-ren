#!/usr/bin/env python3
"""
OANDA黃金自動交易系統 - 完整版
在Mac上直接運行，無需虛擬機
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# OANDA Python SDK
try:
    import oandapyV20
    import oandapyV20.endpoints.instruments as instruments
    import oandapyV20.endpoints.orders as orders
    import oandapyV20.endpoints.trades as trades
    import oandapyV20.endpoints.accounts as accounts
    OANDA_AVAILABLE = True
except ImportError:
    OANDA_AVAILABLE = False
    print("⚠️  OANDA SDK未安裝，使用模擬模式")
    print("   安裝: pip install oandapyV20")

import pandas as pd
import numpy as np

class OANDAGoldTrader:
    def __init__(self, use_demo=True):
        """初始化OANDA交易器"""
        print("=" * 70)
        print("🌐 OANDA黃金自動交易系統 (Mac原生)")
        print("=" * 70)
        
        # 設置日誌
        self.setup_logging()
        
        # 加載配置
        self.config = self.load_config()
        
        # 初始化OANDA
        self.oanda_client = None
        self.account_id = None
        self.initialized = False
        
        if OANDA_AVAILABLE:
            self.initialize_oanda(use_demo)
        
        # 交易狀態
        self.today_trades = 0
        self.max_daily_trades = self.config.get('max_daily_trades', 3)
        self.symbol = self.config.get('symbol', 'XAU_USD')
        
    def setup_logging(self):
        """設置日誌"""
        log_dir = Path("/Users/gordonlui/.openclaw/workspace/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"oanda_trader_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("OANDA黃金自動交易系統啟動")
    
    def load_config(self):
        """加載配置"""
        config_path = "/Users/gordonlui/.openclaw/workspace/oanda_config.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"加載配置: {config_path}")
                return config
            except Exception as e:
                self.logger.error(f"加載配置失敗: {e}")
        
        # 默認配置
        default_config = {
            'api_key': os.environ.get('OANDA_API_KEY', ''),
            'account_id': os.environ.get('OANDA_ACCOUNT_ID', ''),
            'environment': 'practice',  # practice 或 live
            'symbol': 'XAU_USD',
            'lot_size': 0.01,
            'max_daily_trades': 3,
            'max_concurrent_trades': 2,
            'strategies': {
                'trend_following': True,
                'mean_reversion': True,
                'breakout': True
            }
        }
        
        # 保存默認配置
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.logger.warning(f"創建默認配置: {config_path}")
        self.logger.info("請編輯此文件，填入你的OANDA API密鑰")
        
        return default_config
    
    def initialize_oanda(self, use_demo=True):
        """初始化OANDA連接"""
        try:
            api_key = self.config['api_key']
            account_id = self.config['account_id']
            environment = 'practice' if use_demo else 'live'
            
            if not api_key or api_key == '':
                self.logger.error("OANDA API密鑰未設置")
                self.logger.info("請設置環境變量 OANDA_API_KEY 或編輯 oanda_config.json")
                return False
            
            # 創建OANDA客戶端
            self.oanda_client = oandapyV20.API(
                access_token=api_key,
                environment=environment
            )
            
            self.account_id = account_id
            
            # 測試連接
            r = accounts.AccountDetails(accountID=self.account_id)
            response = self.oanda_client.request(r)
            
            if 'account' in response:
                account_info = response['account']
                self.logger.info(f"OANDA連接成功")
                self.logger.info(f"賬戶: {account_info['id']}")
                self.logger.info(f"餘額: {account_info['balance']} {account_info['currency']}")
                self.logger.info(f"環境: {environment}")
                
                self.initialized = True
                return True
            else:
                self.logger.error(f"OANDA連接失敗: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"OANDA初始化異常: {e}")
            return False
    
    def get_market_data(self):
        """獲取市場數據"""
        if not self.initialized:
            self.logger.warning("OANDA未初始化，使用模擬數據")
            return self.get_simulated_data()
        
        try:
            # 獲取歷史數據
            params = {
                "count": 100,
                "granularity": "H1",  # 1小時數據
                "price": "M"  # 中間價
            }
            
            r = instruments.InstrumentsCandles(
                instrument=self.symbol,
                params=params
            )
            
            response = self.oanda_client.request(r)
            
            if 'candles' in response:
                candles = response['candles']
                
                # 轉換為DataFrame
                data = []
                for candle in candles:
                    if candle['complete']:
                        data.append({
                            'time': pd.to_datetime(candle['time']),
                            'open': float(candle['mid']['o']),
                            'high': float(candle['mid']['h']),
                            'low': float(candle['mid']['l']),
                            'close': float(candle['mid']['c']),
                            'volume': int(candle['volume'])
                        })
                
                df = pd.DataFrame(data)
                df.set_index('time', inplace=True)
                
                # 獲取當前價格
                current_price = df['close'].iloc[-1]
                
                current_data = {
                    'timestamp': datetime.now(),
                    'open': current_price,
                    'high': current_price,
                    'low': current_price,
                    'close': current_price,
                    'volume': 1
                }
                
                self.logger.info(f"獲取市場數據: {self.symbol} @ {current_price:.2f}")
                self.logger.info(f"數據點: {len(df)} 小時")
                
                return df, current_data
            else:
                self.logger.error(f"獲取市場數據失敗: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"獲取市場數據異常: {e}")
            return None
    
    def get_simulated_data(self):
        """獲取模擬數據"""
        np.random.seed(int(datetime.now().timestamp()))
        
        # 生成歷史數據
        periods = 100
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
        
        base_price = 2000
        trend = np.linspace(0, 50, periods)
        seasonal = 30 * np.sin(np.linspace(0, 8*np.pi, periods))
        noise = 20 * np.random.randn(periods)
        
        prices = base_price + trend + seasonal + noise
        
        data = []
        for i in range(periods):
            base = prices[i]
            high = base + abs(np.random.randn() * 5)
            low = base - abs(np.random.randn() * 5)
            close = base + np.random.randn() * 3
            
            if high < low:
                high, low = low, high
            close = np.clip(close, low, high)
            
            if i == 0:
                open_price = base
            else:
                open_price = data[i-1]['close']
            
            data.append({
                'time': dates[i],
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': np.random.randint(100, 1000)
            })
        
        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)
        
        # 當前價格
        current_price = prices[-1] + np.random.randn() * 2
        current_data = {
            'timestamp': datetime.now(),
            'open': current_price,
            'high': current_price,
            'low': current_price,
            'close': current_price,
            'volume': 1
        }
        
        self.logger.info(f"使用模擬數據: {current_price:.2f}")
        return df, current_data
    
    def check_trading_hours(self):
        """檢查交易時間"""
        now = datetime.now()
        hour = now.hour
        
        # 黃金主要交易時段（GMT+8）
        # 悉尼: 7:00-16:00
        # 東京: 8:00-17:00  
        # 倫敦: 15:00-00:00
        # 紐約: 20:00-05:00
        
        # 重疊時段（流動性最好）
        london_overlap = 15 <= hour < 24  # 倫敦下午
        ny_overlap = 20 <= hour or hour < 5  # 紐約時段
        
        return london_overlap or ny_overlap
    
    def check_existing_positions(self):
        """檢查現有持倉"""
        if not self.initialized:
            return 0
        
        try:
            r = trades.OpenTrades(accountID=self.account_id)
            response = self.oanda_client.request(r)
            
            if 'trades' in response:
                trades_list = response['trades']
                current_positions = len(trades_list)
                
                self.logger.info(f"當前持倉: {current_positions}筆")
                
                for trade in trades_list:
                    profit = float(trade.get('unrealizedPL', 0))
                    status = "盈利" if profit > 0 else "虧損"
                    self.logger.info(f"  交易 {trade['id']}: {trade['currentUnits']}單位, {status} ${profit:.2f}")
                
                return current_positions
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"檢查持倉失敗: {e}")
            return 0
    
    def analyze_market(self, df, current_data):
        """分析市場，生成交易信號"""
        self.logger.info("分析市場數據...")
        
        # 加載策略配置
        strategy_path = "/Users/gordonlui/.openclaw/workspace/optimized_strategy.json"
        
        if os.path.exists(strategy_path):
            try:
                with open(strategy_path, 'r') as f:
                    strategy = json.load(f)
                params = strategy.get('parameters', {})
                self.logger.info(f"使用策略: {strategy.get('optimized_strategy', '平衡策略')}")
            except Exception as e:
                self.logger.error(f"加載策略失敗: {e}")
                params = {}
        else:
            params = {}
        
        # 默認參數
        default_params = {
            'sma_short': 15,
            'sma_long': 40,
            'rsi_period': 10,
            'rsi_low': 25,
            'rsi_high': 75,
            'stop_loss': 60,
            'take_profit': 120,
            'signal_threshold': 0.5
        }
        
        # 合併參數
        for key, value in default_params.items():
            if key not in params:
                params[key] = value
        
        # 計算技術指標
        df = self.calculate_indicators(df, params)
        
        # 生成信號
        signal = self.generate_signal(df, current_data, params)
        
        return signal
    
    def calculate_indicators(self, df, params):
        """計算技術指標"""
        # 只處理有足夠數據的情況
        if len(df) < max(params['sma_long'], params['rsi_period']) * 2:
            return df
        
        # SMA
        df['SMA_short'] = df['close'].rolling(params['sma_short']).mean()
        df['SMA_long'] = df['close'].rolling(params['sma_long']).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(params['rsi_period']).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signal(self, df, current_data, params):
        """生成交易信號"""
        if len(df) < 50:
            self.logger.warning("數據不足，無法生成信號")
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signal_score = 0.0
        reasons = []
        
        # SMA信號
        if pd.notna(latest['SMA_short']) and pd.notna(latest['SMA_long']):
            if prev['SMA_short'] <= prev['SMA_long'] and latest['SMA_short'] > latest['SMA_long']:
                diff = latest['SMA_short'] - latest['SMA_long']
                if diff > 5:
                    signal_score += 0.3
                    reasons.append(f"SMA黃金交叉 (差值: ${diff:.2f})")
            elif prev['SMA_short'] >= prev['SMA_long'] and latest['SMA_short'] < latest['SMA_long']:
                diff = latest['SMA_long'] - latest['SMA_short']
                if diff > 5:
                    signal_score += 0.3
                    reasons.append(f"SMA死亡交叉 (差值: ${diff:.2f})")
        
        # RSI信號
        rsi = latest['RSI']
        if pd.notna(rsi):
            if rsi < params['rsi_low']:
                signal_score += 0.4
                reasons.append(f"RSI超賣 ({rsi:.1f})")
            elif rsi > params['rsi_high']:
                signal_score += 0.4
                reasons.append(f"RSI超買 ({rsi:.1f})")
        
        # 檢查信號強度
        threshold = params['signal_threshold']
        
        if signal_score >= threshold:
            signal_type = 'BUY' if '黃金交叉' in str(reasons) or '超賣' in str(reasons) else 'SELL'
            
            # 計算止損止盈
            price = current_data['close']
            stop_loss_pips = params['stop_loss']
            take_profit_pips = params['take_profit']
            
            if signal_type == 'BUY':
                stop_loss = round(price * (1 - stop_loss_pips/10000), 2)
                take_profit = round(price * (1 + take_profit_pips/10000), 2)
            else:
                stop_loss = round(price * (1 + stop_loss_pips/10000), 2)
                take_profit = round(price * (1 - take_profit_pips/10000), 2)
            
            signal = {
                'type': signal_type,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'stop_loss_pips': stop_loss_pips,
                'take_profit_pips': take_profit_pips,
                'reason': " + ".join(reasons),
                'strength': signal_score,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"生成交易信號: {signal_type} (強度: {signal_score:.2f})")
            self.logger.info(f"原因: {signal['reason']}")
            
            return signal
        else:
            self.logger.info(f"無交易信號 (強度: {signal_score:.2f} < {threshold})")
            return None
    
    def execute_trade(self, signal):
        """執行交易"""
        if not self.initialized:
            self.logger.warning("OANDA未初始化，模擬執行交易")
            return self.execute_simulated_trade(signal)
        
        if self.today_trades >= self.config['max_daily_trades']:
            self.logger.warning(f"今日已達最大交易次數: {self.today_trades}/{self.config['max_daily_trades']}")
            return False
        
        # 檢查最大持倉
        current_positions = self.check_existing_positions()
        if current_positions >= self.config.get('max_concurrent_trades', 2):
            self.logger.warning(f"已達最大持倉限制: {current_positions}/{self.config.get('max_concurrent_trades', 2)}")
            return False
        
        try:
            lot_size = str(self.config['lot_size'])
            
            # 準備訂單數據
            if signal['type']