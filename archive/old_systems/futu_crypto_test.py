#!/usr/bin/env python3
"""
富途加密貨幣模擬交易測試
測試加密貨幣24小時模擬交易功能
"""

from futu import *
import pandas as pd
import time
from datetime import datetime
import sys

class FutuCryptoTester:
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.simulate_acc_id = None
        self.simulate_acc_type = None
        
    def connect(self):
        """連接到富途OpenD"""
        print("🔗 連接到富途OpenD...")
        
        try:
            # 創建交易上下文
            self.trd_ctx = OpenSecTradeContext(
                filter_trdmarket=TrdMarket.NONE,  # 不過濾市場，獲取所有賬戶
                host='127.0.0.1',
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES
            )
            print("✅ 交易上下文創建成功")
            
            # 創建報價上下文
            self.quote_ctx = OpenQuoteContext(
                host='127.0.0.1',
                port=11111
            )
            print("✅ 報價上下文創建成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def find_simulate_account(self):
        """查找模擬交易賬戶"""
        print("\n🔍 查找模擬交易賬戶...")
        
        try:
            # 獲取所有賬戶
            ret, data = self.trd_ctx.get_acc_list()
            
            if ret != RET_OK:
                print(f"❌ 獲取賬戶列表失敗: {data}")
                return False
            
            print(f"✅ 找到 {len(data)} 個賬戶")
            
            # 查找模擬賬戶
            simulate_accounts = data[data['trd_env'] == 'SIMULATE']
            
            if len(simulate_accounts) == 0:
                print("❌ 未找到模擬交易賬戶")
                print("\n🔧 需要:")
                print("1. 在富途牛牛中開通模擬交易")
                print("2. 確認模擬交易功能已啟用")
                return False
            
            print(f"✅ 找到 {len(simulate_accounts)} 個模擬賬戶")
            
            # 顯示模擬賬戶信息
            print("\n📋 模擬賬戶列表:")
            for idx, acc in simulate_accounts.iterrows():
                print(f"  賬戶{idx+1}:")
                print(f"    ID: {acc['acc_id']}")
                print(f"    類型: {acc.get('acc_type', 'N/A')}")
                print(f"    模擬類型: {acc.get('sim_acc_type', 'N/A')}")
                print(f"    市場權限: {acc.get('trdmarket_auth', 'N/A')}")
                print(f"    狀態: {acc.get('acc_status', 'N/A')}")
            
            # 選擇第一個模擬賬戶
            self.simulate_acc_id = simulate_accounts.iloc[0]['acc_id']
            self.simulate_acc_type = simulate_accounts.iloc[0].get('sim_acc_type', 'UNKNOWN')
            
            print(f"\n🎯 選擇模擬賬戶: ID={self.simulate_acc_id}, 類型={self.simulate_acc_type}")
            
            return True
            
        except Exception as e:
            print(f"❌ 查找模擬賬戶失敗: {e}")
            return False
    
    def test_crypto_symbols(self):
        """測試加密貨幣代碼"""
        print("\n💰 測試加密貨幣代碼...")
        
        # 常見的加密貨幣對
        crypto_pairs = [
            'BTCUSDT',    # 比特幣/USDT
            'ETHUSDT',    # 以太坊/USDT
            'BNBUSDT',    # BNB/USDT
            'XRPUSDT',    # XRP/USDT
            'ADAUSDT',    # Cardano/USDT
            'SOLUSDT',    # Solana/USDT
            'DOTUSDT',    # Polkadot/USDT
            'DOGEUSDT',   # Dogecoin/USDT
        ]
        
        # 嘗試不同的代碼格式
        test_formats = [
            lambda x: x,                    # BTCUSDT
            lambda x: f"CRYPTO.{x}",        # CRYPTO.BTCUSDT
            lambda x: f"CRYPTO.{x}.FP",     # CRYPTO.BTCUSDT.FP
            lambda x: f"{x}.FP",            # BTCUSDT.FP
        ]
        
        working_symbols = []
        
        for pair in crypto_pairs:
            print(f"\n測試 {pair}...")
            
            for fmt in test_formats:
                symbol = fmt(pair)
                print(f"  嘗試格式: {symbol}")
                
                try:
                    # 嘗試獲取市場快照
                    ret, data = self.quote_ctx.get_market_snapshot([symbol])
                    
                    if ret == RET_OK and len(data) > 0:
                        print(f"  ✅ {symbol} 可用")
                        snapshot = data.iloc[0]
                        
                        print(f"    最新價: {snapshot.get('last_price', 'N/A')}")
                        print(f"    漲跌: {snapshot.get('change_rate', 'N/A')}")
                        print(f"    成交量: {snapshot.get('volume', 'N/A')}")
                        
                        working_symbols.append({
                            'symbol': symbol,
                            'name': pair,
                            'price': snapshot.get('last_price', 0),
                            'change': snapshot.get('change_rate', 0)
                        })
                        break  # 找到可用格式，跳出循環
                    else:
                        print(f"  ❌ {symbol} 不可用: {data}")
                        
                except Exception as e:
                    print(f"  ❌ {symbol} 錯誤: {e}")
        
        print(f"\n📊 找到 {len(working_symbols)} 個可用的加密貨幣對")
        
        if working_symbols:
            print("\n可用加密貨幣:")
            for crypto in working_symbols:
                print(f"  {crypto['symbol']} ({crypto['name']}): {crypto['price']}")
        
        return working_symbols
    
    def test_simulate_trading(self, test_symbol):
        """測試模擬交易功能"""
        print(f"\n🛒 測試模擬交易 ({test_symbol})...")
        
        try:
            # 1. 獲取賬戶信息
            print("1. 獲取模擬賬戶信息...")
            ret, acc_info = self.trd_ctx.accinfo_query(
                trd_env=TrdEnv.SIMULATE,
                acc_id=self.simulate_acc_id
            )
            
            if ret == RET_OK:
                print("✅ 模擬賬戶信息獲取成功")
                if len(acc_info) > 0:
                    info = acc_info.iloc[0]
                    print(f"   總資產: {info.get('total_assets', 'N/A')}")
                    print(f"   現金: {info.get('cash', 'N/A')}")
                    print(f"   可用資金: {info.get('available_funds', 'N/A')}")
            else:
                print(f"❌ 獲取賬戶信息失敗: {acc_info}")
            
            # 2. 獲取當前價格
            print("\n2. 獲取當前市場價格...")
            ret, snapshot = self.quote_ctx.get_market_snapshot([test_symbol])
            
            if ret != RET_OK or len(snapshot) == 0:
                print(f"❌ 獲取價格失敗: {snapshot}")
                return False
            
            current_price = snapshot.iloc[0]['last_price']
            print(f"   {test_symbol} 當前價格: {current_price}")
            
            # 3. 測試下單（使用不會成交的價格）
            print("\n3. 測試模擬下單...")
            
            # 使用極端價格避免成交
            test_price = current_price * 0.5  # 半價，不會成交
            
            ret, order_data = self.trd_ctx.place_order(
                price=test_price,
                qty=0.001,  # 最小數量
                code=test_symbol,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=TrdEnv.SIMULATE,
                acc_id=self.simulate_acc_id,
                remark="API連接測試單"
            )
            
            if ret == RET_OK:
                print("✅ 模擬下單成功")
                order_id = order_data['order_id'].iloc[0]
                print(f"   訂單ID: {order_id}")
                print(f"   訂單狀態: {order_data['order_status'].iloc[0]}")
                
                # 4. 取消測試單
                print("\n4. 取消測試單...")
                ret_cancel, cancel_data = self.trd_ctx.modify_order(
                    modify_order_op=ModifyOrderOp.CANCEL,
                    order_id=order_id,
                    qty=0,
                    price=0,
                    trd_env=TrdEnv.SIMULATE,
                    acc_id=self.simulate_acc_id
                )
                
                if ret_cancel == RET_OK:
                    print("✅ 測試單取消成功")
                else:
                    print(f"⚠️  取消失敗: {cancel_data}")
                
                return True
                
            else:
                print(f"❌ 下單失敗: {order_data}")
                
                # 檢查錯誤信息
                error_msg = str(order_data)
                if "解锁" in error_msg or "unlock" in error_msg.lower():
                    print("\n🔓 提示: 模擬交易應該不需要解鎖")
                    print("請在富途牛牛中確認模擬交易已正確設置")
                elif "资金" in error_msg or "fund" in error_msg.lower():
                    print("\n💰 提示: 可能模擬賬戶資金不足")
                    print("請在富途牛牛模擬交易界面檢查資金")
                
                return False
                
        except Exception as e:
            print(f"❌ 模擬交易測試失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_crypto_market_data(self, symbol, interval='1m', limit=100):
        """獲取加密貨幣市場數據"""
        print(f"\n📈 獲取 {symbol} 市場數據...")
        
        try:
            # 嘗試獲取K線數據
            ret, kline_data = self.quote_ctx.get_cur_kline(
                symbol,
                interval,  # 1m, 5m, 15m, 30m, 60m, 1d
                max_count=limit
            )
            
            if ret == RET_OK:
                print(f"✅ 獲取到 {len(kline_data)} 條K線數據")
                
                if len(kline_data) > 0:
                    # 顯示最新幾條數據
                    print("\n最新K線數據:")
                    recent = kline_data.tail(3)
                    for idx, row in recent.iterrows():
                        time_str = row['time_key']
                        close_price = row['close']
                        volume = row['volume']
                        print(f"  {time_str}: 收盤價={close_price}, 成交量={volume}")
                
                return kline_data
            else:
                print(f"❌ 獲取K線數據失敗: {kline_data}")
                return None
                
        except Exception as e:
            print(f"❌ 獲取市場數據失敗: {e}")
            return None
    
    def close(self):
        """關閉連接"""
        if self.trd_ctx:
            self.trd_ctx.close()
            print("✅ 交易連接已關閉")
        
        if self.quote_ctx:
            self.quote_ctx.close()
            print("✅ 報價連接已關閉")

def main():
    print("🚀 富途加密貨幣模擬交易測試")
    print("=" * 60)
    
    tester = FutuCryptoTester()
    
    try:
        # 1. 連接測試
        if not tester.connect():
            print("\n❌ 連接失敗，測試中止")
            return False
        
        # 2. 查找模擬賬戶
        if not tester.find_simulate_account():
            print("\n❌ 未找到模擬賬戶，測試中止")
            return False
        
        # 3. 測試加密貨幣代碼
        crypto_symbols = tester.test_crypto_symbols()
        
        if not crypto_symbols:
            print("\n❌ 未找到可用的加密貨幣對")
            print("\n🔧 可能原因:")
            print("1. 富途可能不支持加密貨幣API")
            print("2. 需要特定的代碼格式")
            print("3. 需要開通加密貨幣交易權限")
            return False
        
        # 4. 使用第一個可用的加密貨幣進行測試
        test_symbol = crypto_symbols[0]['symbol']
        
        # 5. 測試模擬交易
        trading_success = tester.test_simulate_trading(test_symbol)
        
        # 6. 獲取市場數據
        market_data = tester.get_crypto_market_data(test_symbol, '5m', 50)
        
        # 7. 總結
        print("\n" + "=" * 60)
        print("📊 測試結果總結")
        print("=" * 60)
        
        print(f"✅ 連接狀態: 成功")
        print(f"✅ 模擬賬戶: 找到 (ID: {tester.simulate_acc_id})")
        print(f"✅ 加密貨幣對: 找到 {len(crypto_symbols)} 個")
        
        if trading_success:
            print("✅ 模擬交易: 成功 (下單/取消測試通過)")
        else:
            print("❌ 模擬交易: 失敗 (需要進一步檢查)")
        
        if market_data is not None:
            print("✅ 市場數據: 可獲取")
        else:
            print("❌ 市場數據: 不可用")
        
        print("\n🎯 可用於24小時交易的加密貨幣:")
        for crypto in crypto_symbols[:5]:  # 顯示前5個
            print(f"  • {crypto['symbol']}: {crypto['price']}")
        
        print("\n📋 下一步行動:")
        if trading_success:
            print("1. 🚀 立即開始加密貨幣模擬交易")
            print("2. 📊 設置24小時監控系統")
            print("3. ⚖️  實施2%風險管理")
            print("4. 📈 開發交易策略")
        else:
            print("1. 🔧 檢查模擬交易設置")
            print("2. 💰 確認模擬賬戶資金")
            print("3. 📱 在富途牛牛中測試模擬交易")
            print("4. 🔄 重新運行測試")
        
        return trading_success
        
    except Exception as e:
        print(f"\n❌ 測試過程中出錯: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        tester.close()

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 加密貨幣模擬交易測試成功！")
        print("現在可以開始24小時交易學習 🚀")
    else:
        print("❌ 測試遇到問題，需要進一步檢查")
    
    sys.exit(0 if success else 1)