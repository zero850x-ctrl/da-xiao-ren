#!/usr/bin/env python3
"""
主動富途模擬交易系統
自動執行加倉、補倉、買賣操作
"""

import sys
import json
import time
import pandas as pd
from datetime import datetime, time as dt_time, timedelta
from futu import *

sys.path.append('/Users/gordonlui/.openclaw/workspace')

class ActiveFutuTrader:
    """主動富途交易系統"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trade_environment = TrdEnv.SIMULATE  # 模擬環境
        
        # 交易配置
        self.config = {
            'max_position_per_stock': 0.25,      # 單隻股票最大倉位25%
            'initial_trade_amount': 10000,       # 初始交易金額 HKD 10,000
            'add_position_amount': 5000,         # 加倉金額 HKD 5,000
            'dca_amount': 3000,                  # 定投補倉金額 HKD 3,000
            'stop_loss_pct': 0.08,               # 止損比例 8%
            'take_profit_pct': 0.15,             # 止盈比例 15%
            'trailing_stop_pct': 0.10,           # 移動止盈 10%
            'max_drawdown_pct': 0.20,            # 最大回撤 20%
            
            # 交易策略
            'strategies': {
                'momentum': True,      # 動量策略
                'value': True,         # 價值策略
                'dividend': True,      # 股息策略
                'breakout': True,      # 突破策略
                'dca': True           # 定投策略
            },
            
            # 重點交易股票
            'focus_stocks': [
                {
                    'code': 'HK.00992',      # 聯想集團
                    'name': '聯想集團',
                    'strategy': 'dca',       # 定投策略
                    'current_price': 9.17,
                    'buy_price': 8.59,
                    'position': 26000,
                    'target_price': 9.55,
                    'stop_loss': 8.42
                },
                {
                    'code': 'HK.09868',      # 小鵬汽車-W
                    'name': '小鵬汽車-W',
                    'strategy': 'momentum',  # 動量策略
                    'current_price': 42.30,
                    'target_price': 46.00,
                    'stop_loss': 38.90
                },
                {
                    'code': 'HK.02020',      # 安踏體育
                    'name': '安踏體育',
                    'strategy': 'value',     # 價值策略
                    'current_price': 78.40,
                    'target_price': 85.00,
                    'stop_loss': 72.10
                },
                {
                    'code': 'HK.00883',      # 中國海洋石油
                    'name': '中國海洋石油',
                    'strategy': 'dividend',  # 股息策略
                    'current_price': 18.25,
                    'dividend_yield': 0.065,
                    'target_price': 20.00,
                    'stop_loss': 16.80
                }
            ]
        }
        
        # 交易記錄
        self.trade_log = []
        self.positions = {}
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'total_loss': 0,
            'win_rate': 0
        }
    
    def connect_to_futu(self):
        """連接富途API"""
        try:
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1', 
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES,
                trd_env=self.trade_environment
            )
            
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            
            print(f"✅ 成功連接富途模擬交易API")
            return True
            
        except Exception as e:
            print(f"❌ 連接富途API失敗: {e}")
            return False
    
    def get_account_info(self):
        """獲取賬戶信息"""
        try:
            ret, data = self.trd_ctx.accinfo_query()
            if ret == RET_OK:
                print(f"💰 模擬賬戶信息:")
                print(f"   總資產: HKD {data['total_assets'].iloc[0]:,.2f}")
                print(f"   現金: HKD {data['cash'].iloc[0]:,.2f}")
                print(f"   持倉市值: HKD {data['market_val'].iloc[0]:,.2f}")
                return data
            else:
                print(f"❌ 獲取賬戶信息失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取賬戶信息異常: {e}")
            return None
    
    def get_position_info(self):
        """獲取持倉信息"""
        try:
            ret, data = self.trd_ctx.position_list_query()
            if ret == RET_OK:
                if len(data) > 0:
                    print(f"📊 當前持倉 ({len(data)}隻):")
                    for _, row in data.iterrows():
                        print(f"   {row['code']} - {row['stock_name']}")
                        print(f"     數量: {row['qty']:,}股")
                        print(f"     成本: HKD {row['cost_price']:.2f}")
                        print(f"     市價: HKD {row['market_val']/row['qty']:.2f}")
                        print(f"     盈虧: HKD {row['pl_val']:+,.2f}")
                        
                        # 記錄持倉
                        self.positions[row['code']] = {
                            'qty': row['qty'],
                            'cost_price': row['cost_price'],
                            'market_val': row['market_val'],
                            'pl_val': row['pl_val']
                        }
                else:
                    print("📭 當前沒有持倉")
                return data
            else:
                print(f"❌ 獲取持倉信息失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取持倉信息異常: {e}")
            return None
    
    def get_stock_price(self, stock_code):
        """獲取股票價格"""
        try:
            ret, data = self.quote_ctx.get_market_snapshot([stock_code])
            if ret == RET_OK:
                last_price = data['last_price'].iloc[0]
                return float(last_price)
            else:
                print(f"❌ 獲取{stock_code}價格失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取{stock_code}價格異常: {e}")
            return None
    
    def execute_buy_order(self, stock_code, amount_hkd, reason=""):
        """執行買入訂單"""
        try:
            # 獲取當前價格
            price = self.get_stock_price(stock_code)
            if price is None:
                return False, "無法獲取價格"
            
            # 計算股數
            quantity = int(amount_hkd / price)
            if quantity <= 0:
                return False, "股數為0"
            
            # 執行買入
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=quantity,
                code=stock_code,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                remark=f"主動交易: {reason}"
            )
            
            if ret == RET_OK:
                order_id = data['order_id'].iloc[0]
                
                # 記錄交易
                trade_record = {
                    'order_id': order_id,
                    'action': 'BUY',
                    'stock_code': stock_code,
                    'price': price,
                    'quantity': quantity,
                    'amount': amount_hkd,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'reason': reason
                }
                self.trade_log.append(trade_record)
                self.performance['total_trades'] += 1
                
                print(f"✅ 買入執行成功: {stock_code}")
                print(f"   價格: HKD {price:.2f}")
                print(f"   數量: {quantity:,}股")
                print(f"   金額: HKD {amount_hkd:,.2f}")
                print(f"   理由: {reason}")
                print(f"   訂單ID: {order_id}")
                
                return True, order_id
            else:
                print(f"❌ 買入執行失敗: {data}")
                return False, str(data)
                
        except Exception as e:
            print(f"❌ 買入執行異常: {e}")
            return False, str(e)
    
    def execute_sell_order(self, stock_code, quantity, reason=""):
        """執行賣出訂單"""
        try:
            # 獲取當前價格
            price = self.get_stock_price(stock_code)
            if price is None:
                return False, "無法獲取價格"
            
            # 執行賣出
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=quantity,
                code=stock_code,
                trd_side=TrdSide.SELL,
                order_type=OrderType.NORMAL,
                remark=f"主動交易: {reason}"
            )
            
            if ret == RET_OK:
                order_id = data['order_id'].iloc[0]
                
                # 計算盈虧
                amount = price * quantity
                
                # 記錄交易
                trade_record = {
                    'order_id': order_id,
                    'action': 'SELL',
                    'stock_code': stock_code,
                    'price': price,
                    'quantity': quantity,
                    'amount': amount,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'reason': reason
                }
                self.trade_log.append(trade_record)
                self.performance['total_trades'] += 1
                
                print(f"✅ 賣出執行成功: {stock_code}")
                print(f"   價格: HKD {price:.2f}")
                print(f"   數量: {quantity:,}股")
                print(f"   金額: HKD {amount:,.2f}")
                print(f"   理由: {reason}")
                print(f"   訂單ID: {order_id}")
                
                return True, order_id
            else:
                print(f"❌ 賣出執行失敗: {data}")
                return False, str(data)
                
        except Exception as e:
            print(f"❌ 賣出執行異常: {e}")
            return False, str(e)
    
    def analyze_stock_for_trading(self, stock_info):
        """分析股票交易機會"""
        stock_code = stock_info['code']
        current_price = self.get_stock_price(stock_code)
        
        if current_price is None:
            return None
        
        analysis = {
            'stock_code': stock_code,
            'name': stock_info['name'],
            'current_price': current_price,
            'strategy': stock_info['strategy'],
            'signals': [],
            'action': 'HOLD',
            'reason': '',
            'quantity': 0,
            'amount': 0
        }
        
        # 檢查持倉
        has_position = stock_code in self.positions
        if has_position:
            position = self.positions[stock_code]
            cost_price = position['cost_price']
            profit_pct = ((current_price - cost_price) / cost_price) * 100
            analysis['has_position'] = True
            analysis['cost_price'] = cost_price
            analysis['profit_pct'] = profit_pct
        else:
            analysis['has_position'] = False
        
        # 根據策略分析
        strategy = stock_info['strategy']
        
        if strategy == 'dca':  # 定投策略
            if 'buy_price' in stock_info:
                buy_price = stock_info['buy_price']
                if current_price <= buy_price * 0.95:  # 比買入價低5%
                    analysis['action'] = 'BUY'
                    analysis['reason'] = f'價格{HKD {current_price:.2f}}低於買入價{HKD {buy_price:.2f}}，定投補倉'
                    analysis['amount'] = self.config['dca_amount']
                    analysis['signals'].append('PRICE_BELOW_BUY')
        
        elif strategy == 'momentum':  # 動量策略
            if 'target_price' in stock_info and 'stop_loss' in stock_info:
                target_price = stock_info['target_price']
                stop_loss = stock_info['stop_loss']
                
                if current_price >= target_price * 0.98:  # 接近目標價
                    if has_position:
                        analysis['action'] = 'SELL'
                        analysis['reason'] = f'接近目標價{HKD {target_price:.2f}}，獲利了結'
                        analysis['quantity'] = int(position['qty'] * 0.5)  # 賣一半
                        analysis['signals'].append('NEAR_TARGET')
                
                elif current_price <= stop_loss * 1.02:  # 接近止損價
                    if has_position:
                        analysis['action'] = 'SELL'
                        analysis['reason'] = f'接近止損價{HKD {stop_loss:.2f}}，風險控制'
                        analysis['quantity'] = position['qty']  # 全賣
                        analysis['signals'].append('NEAR_STOPLOSS')
                
                elif not has_position and current_price <= target_price * 0.85:  # 有足夠安全邊際
                    analysis['action'] = 'BUY'
                    analysis['reason'] = f'價格{HKD {current_price:.2f}}有安全邊際，動量買入'
                    analysis['amount'] = self.config['initial_trade_amount']
                    analysis['signals'].append('MOMENTUM_BUY')
        
        elif strategy == 'value':  # 價值策略
            if 'target_price' in stock_info:
                target_price = stock_info['target_price']
                discount_pct = ((target_price - current_price) / target_price) * 100
                
                if discount_pct >= 15:  # 折扣15%以上
                    analysis['action'] = 'BUY'
                    analysis['reason'] = f'價值低估，折扣{discount_pct:.1f}%'
                    analysis['amount'] = self.config['initial_trade_amount']
                    analysis['signals'].append('VALUE_DISCOUNT')
        
        elif strategy == 'dividend':  # 股息策略
            if 'dividend_yield' in stock_info:
                dividend_yield = stock_info['dividend_yield']
                if dividend_yield >= 0.06:  # 股息率6%以上
                    analysis['action'] = 'BUY'
                    analysis['reason'] = f'高股息率{dividend_yield:.1%}，收息投資'
                    analysis['amount'] = self.config['initial_trade_amount']
                    analysis['signals'].append('HIGH_DIVIDEND')
        
        return analysis
    
    def execute_trading_decisions(self):
        """執行交易決策"""
        print(f"\n{'='*70}")
        print(f"🤖 執行主動交易決策")
        print(f"{'='*70}")
        
        # 獲取賬戶和持倉信息
        account_info = self.get_account_info()
        if account_info is None:
            print("❌ 無法獲取賬戶信息，跳過交易")
            return
        
        position_info = self.get_position_info()
        
        # 分析每隻重點股票
        trading_decisions = []
        for stock_info in self.config['focus_stocks']:
            analysis = self.analyze_stock_for_trading(stock_info)
            if analysis and analysis['action'] != 'HOLD':
                trading_decisions.append(analysis)
        
        # 執行交易
        executed_trades = []
        for decision in trading_decisions:
            print(f"\n📈 分析 {decision['stock_code']} - {decision['name']}:")
            print(f"   當前價格: HKD {decision['current_price']:.2f}")
            print(f"   策略: {decision['strategy']}")
            print(f"   信號: {', '.join(decision['signals'])}")
            print(f"   建議動作: {decision['action']}")
            print(f"   理由: {decision['reason']}")
            
            if decision['action'] == 'BUY':
                success, result = self.execute_buy_order(
                    decision['stock_code'],
                    decision['amount'],
                    decision['reason']
                )
                if success:
                    executed_trades.append({
                        'stock': decision['stock_code'],
                        'action': 'BUY',
                        'result': 'SUCCESS',
                        'order_id': result
                    })
                else:
                    executed_trades.append({
                        'stock': decision['stock_code'],
                        'action': 'BUY',
