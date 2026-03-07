#!/usr/bin/env python3
"""
全自動交易系統
根據XGBoost信號自動買賣，遵守2%規則
"""

import sys
import json
import time
import subprocess
from datetime import datetime
from futu import *
from datetime import datetime

# 配置
TRADING_MODE = "SIMULATE"  # 改為 "REAL" 使用真實倉
TRD_ENV = TrdEnv.SIMULATE if TRADING_MODE == "SIMULATE" else TrdEnv.REAL
MAX_LOSS_PCT = 0.02  # 2%規則
CASH_BUFFER = 50000    # 預留5萬現金

def get_account_info(trd_ctx):
    """獲取帳戶信息"""
    ret, data = trd_ctx.accinfo_query(trd_env=TRD_ENV)
    if ret == RET_OK:
        return {
            'cash': data['cash'].iloc[0],
            'total': data['total_assets'].iloc[0]
        }
    return None

def get_pending_orders(trd_ctx):
    """獲取待成交訂單，防止重複下單"""
    ret, orders = trd_ctx.order_list_query(trd_env=TRD_ENV)
    pending = {}
    if ret == RET_OK:
        for _, o in orders.iterrows():
            status = o.get('order_status', '')
            if status == 'SUBMITTED' or status == 'PENDING':
                code = o.get('code', '')
                qty = o.get('qty', 0)
                key = f"{code}:{int(qty)}"
                if key not in pending:
                    pending[key] = True
    return pending

def cancel_all_pending(trd_ctx):
    """取消所有待成交訂單 (僅適用於真實倉)"""
    if TRADING_MODE == "SIMULATE":
        print("⚠️ 模擬倉不支持取消訂單")
        return 0
    
    ret, data = trd_ctx.cancel_all_order(trd_env=TRD_ENV)
    if ret == 0:
        print(f"✅ 成功取消所有待成交訂單")
        return 1
    else:
        print(f"❌ 取消訂單失敗: {data}")
        return 0

def get_positions(trd_ctx):
    """獲取持倉"""
    ret, data = trd_ctx.position_list_query(trd_env=TRD_ENV)
    if ret == RET_OK and len(data) > 0:
        positions = {}
        for _, row in data.iterrows():
            if row['qty'] > 0:
                positions[row['code']] = {
                    'qty': row['qty'],
                    'cost': row.get('cost_price', 0),
                    'market_val': row.get('market_val', 0)
                }
        return positions
    return {}

def get_stock_price(ctx, code):
    """獲取股票價格"""
    ret, data = ctx.get_stock_quote(code_list=[code])
    if ret == 0:
        return data.iloc[0]['last_price']
    return None

def calculate_max_qty(price, total_assets):
    """根據2%規則計算最大買入股數（調整為整手）"""
    max_loss = total_assets * MAX_LOSS_PCT
    max_qty = int(max_loss / price)
    # 四捨五入到整手（港股通常為100股一手）
    lot_size = 100
    max_qty = (max_qty // lot_size) * lot_size
    return max_qty

def check_stop_loss(trd_ctx, quote_ctx, positions):
    """檢查並執行止損 (-2%)"""
    print("\n🛡️ 檢查止損...")
    
    for code, pos in positions.items():
        if pos.get('qty', 0) > 0:
            try:
                cost = pos.get('cost_price', 0)
                if not cost or cost <= 0:
                    continue
                
                # 獲取現價
                ret, data = quote_ctx.get_stock_quote(code)
                if ret != 0:
                    continue
                
                current_price = float(data.iloc[0]['last_price'])
                pnl_pct = (current_price - cost) / cost * 100
                
                # 如果虧損超過2%，止損
                if pnl_pct <= -2.0:
                    print(f"   ⚠️ {code}: 虧損 {pnl_pct:.1f}% (成本 ${cost:.2f}, 現價 ${current_price:.2f})")
                    print(f"      → 執行止損!")
                    
                    qty = int(pos['qty'])
                    ret2, order = trd_ctx.place_order(
                        price=0, qty=qty, code=code,
                        trd_side=TrdSide.SELL, order_type=OrderType.MARKET,
                        trd_env=TRD_ENV
                    )
                    
                    if ret2 == 0:
                        print(f"      ✅ 止損成功! 賣出 {qty}股")
                    else:
                        print(f"      ❌ 止損失敗: {order}")
                    
                    time.sleep(0.5)
                else:
                    print(f"   ✅ {code}: {pnl_pct:+.1f}% (正常)")
                    
            except Exception as e:
                print(f"   ❌ {code} 止損檢查失敗: {e}")

def execute_hsi_hedge(trd_ctx, quote_ctx, positions, total_assets):
    """HSI波段對沖策略"""
    print("\n🎯 執行HSI波段對沖...")
    
    # 獲取HSI數據
    hsi_code = "HK.800000"
    
    # 先訂閱HSI報價
    quote_ctx.subscribe([hsi_code], [SubType.QUOTE])
    time.sleep(0.5)
    
    ret, data = quote_ctx.get_stock_quote(code_list=[hsi_code])
    if ret != 0:
        print("   ❌ 無法獲取HSI數據")
        return
    
    hsi_price = data.iloc[0]['last_price']
    try:
        hsi_change = float(data.iloc[0].get('pre_change_rate', '0').replace('%', '').replace('N/A', '0'))
    except:
        hsi_change = 0
    
    print(f"   HSI: {hsi_price} ({hsi_change:+.2f}%)")
    
    # 獲取HSI的RSI和技術指標（從報告讀取）
    try:
        with open('/Users/gordonlui/.openclaw/workspace/trading_reports/xgboost_multi_latest.json', 'r') as f:
            report = json.load(f)
        
        hsi_data = None
        for item in report.get('results', []):
            if item.get('code') == 'HK.800000':
                hsi_data = item
                break
        
        if hsi_data:
            rsi = hsi_data.get('kline', {}).get('rsi', 50)
            signal = hsi_data.get('signal', 'HOLD')
            
            print(f"   RSI: {rsi:.1f}, 信號: {signal}")
            
            # 02800 = 做多HSI, 07500 = 做空HSI
            pos_02800 = positions.get('HK.02800', {}).get('qty', 0)
            pos_07500 = positions.get('HK.07500', {}).get('qty', 0)
            
            # RSI > 70 超買：減02800，加07500
            if rsi > 70:
                print(f"   📉 HSI超買(RSI={rsi:.1f}) → 減02800，加07500")
                if pos_02800 > 1000:
                    sell_qty = min(1000, pos_02800)
                    print(f"      賣出02800: {sell_qty}股")
                    trd_ctx.place_order(price=0, qty=sell_qty, code='HK.02800', 
                                       trd_side=TrdSide.SELL, order_type=OrderType.MARKET,
                                       trd_env=TRD_ENV)
                    time.sleep(0.5)
                
                # 買入07500對沖
                price_07500 = get_stock_price(quote_ctx, 'HK.07500')
                if price_07500:
                    buy_qty = int(10000 / price_07500)
                    if buy_qty > 0:
                        print(f"      買入07500: {buy_qty}股")
                        trd_ctx.place_order(price=0, qty=buy_qty, code='HK.07500',
                                           trd_side=TrdSide.BUY, order_type=OrderType.MARKET,
                                           trd_env=TRD_ENV)
            
            # RSI < 30 超賣：減07500，加02800
            elif rsi < 30:
                print(f"   📈 HSI超賣(RSI={rsi:.1f}) → 減07500，加02800")
                if pos_07500 > 5000:
                    sell_qty = min(10000, pos_07500)
                    print(f"      賣出07500: {sell_qty}股")
                    trd_ctx.place_order(price=0, qty=sell_qty, code='HK.07500',
                                       trd_side=TrdSide.SELL, order_type=OrderType.MARKET,
                                       trd_env=TRD_ENV)
                    time.sleep(0.5)
                
                # 買入02800
                price_02800 = get_stock_price(quote_ctx, 'HK.02800')
                if price_02800:
                    buy_qty = int(10000 / price_02800)
                    if buy_qty > 0:
                        print(f"      買入02800: {buy_qty}股")
                        trd_ctx.place_order(price=0, qty=buy_qty, code='HK.02800',
                                           trd_side=TrdSide.BUY, order_type=OrderType.MARKET,
                                           trd_env=TRD_ENV)
            else:
                print(f"   🟡 RSI喺30-70之間，唔洗郁")
    except Exception as e:
        print(f"   ⚠️ 對沖策略執行失敗: {e}")

def execute_auto_trade():
    """執行自動交易"""
    print(f"🤖 全自動交易系統啟動 - {datetime.now().strftime('%H:%M:%S')}")
    print(f"📊 交易模式: {TRADING_MODE}")
    print("=" * 50)
    
    # 連接
    trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 嘗試取消待成交訂單 (僅真實倉)
    cancel_all_pending(trd_ctx)
    
    # 獲取帳戶信息
    account = get_account_info(trd_ctx)
    if not account:
        print("❌ 無法獲取帳戶信息")
        trd_ctx.close()
        quote_ctx.close()
        return
    
    total_assets = account['total']
    available_cash = account['cash'] - CASH_BUFFER
    
    print(f"💰 總資產: HKD {total_assets:,.2f}")
    print(f"💵 可用現金: HKD {available_cash:,.2f}")
    print(f"🎯 2%止損上限: HKD {total_assets * MAX_LOSS_PCT:,.2f}")
    
    # 獲取持倉
    positions = get_positions(trd_ctx)
    print(f"📦 當前持倉: {list(positions.keys())}")
    
    # 檢查止損 (-2%)
    check_stop_loss(trd_ctx, quote_ctx, positions)
    
    # 執行HSI波段對沖
    execute_hsi_hedge(trd_ctx, quote_ctx, positions, total_assets)
    
    # 獲取待成交訂單，防止重複下單
    pending_orders = get_pending_orders(trd_ctx)
    if pending_orders:
        print(f"\n⚠️ 發現 {len(pending_orders)} 個待成交訂單: {list(pending_orders.keys())}")
    
    # 讀取最新分析報告
    try:
        with open('/Users/gordonlui/.openclaw/workspace/trading_reports/xgboost_multi_latest.json', 'r') as f:
            report = json.load(f)
    except:
        print("❌ 無法讀取分析報告")
        trd_ctx.close()
        quote_ctx.close()
        return
    
    signals = report.get('signals', [])
    
    # 追蹤實際執行的交易
    executed_trades = []
    
    # 處理SELL信號
    sell_signals = [s for s in signals if s.get('signal') == 'SELL']
    if sell_signals:
        print(f"\n🔴 發現 {len(sell_signals)} 個SELL信號:")
        for sig in sell_signals:
            code = f"HK.{sig['stock']}"
            price = sig.get('price', 0)
            reason = sig.get('reason', '')
            print(f"   {code}: ${price} - {reason}")
            
            # 檢查是否持有
            if code in positions:
                qty = positions[code]['qty']
                print(f"   → 賣出 {qty} 股 @ ${price}")
                
                # 執行賣出
                ret, data = trd_ctx.place_order(
                    price=price,
                    qty=qty,
                    code=code,
                    trd_side=TrdSide.SELL,
                    order_type=OrderType.MARKET,
                    trd_env=TRD_ENV
                )
                
                if ret == RET_OK:
                    print(f"   ✅ 賣出成功!")
                    executed_trades.append(('SELL', code, price))
                else:
                    print(f"   ❌ 賣出失敗: {data}")
                time.sleep(0.5)
    
    # 處理BUY信號（如果有）
    buy_signals = [s for s in signals if s.get('signal') == 'BUY']
    if buy_signals and available_cash > 10000:
        print(f"\n🟢 發現 {len(buy_signals)} 個BUY信號:")
        for sig in buy_signals:
            code = f"HK.{sig['stock']}"
            
            # 如果已經持有，唔再買入！
            if code in positions:
                print(f"   {code}: 已有持倉 {positions[code]['qty']}股，跳過")
                continue
            
            # 檢查是否有待成交訂單
            order_key = f"{code}:{max_qty}"
            if order_key in pending_orders:
                print(f"   {code}: 已有待成交訂單 {max_qty}股，跳過")
                continue
            
            price = sig.get('price', 0)
            if not price or price <= 0:
                price = get_stock_price(quote_ctx, code)
            
            if price and price > 0:
                max_qty = calculate_max_qty(price, total_assets)
                # 限制最大買入量
                max_qty = min(max_qty, int(available_cash / price * 0.5))
                
                if max_qty > 0:
                    print(f"   {code}: ${price} - 最多買入 {max_qty} 股")
                    
                    # 執行買入
                    ret, data = trd_ctx.place_order(
                        price=price,
                        qty=max_qty,
                        code=code,
                        trd_side=TrdSide.BUY,
                        order_type=OrderType.MARKET,
                        trd_env=TRD_ENV
                    )
                    
                    if ret == RET_OK:
                        print(f"   ✅ 買入成功!")
                        executed_trades.append(('BUY', code, price))
                    else:
                        print(f"   ❌ 買入失敗: {data}")
                    time.sleep(0.5)
    
    # 更新持倉顯示
    print("\n📊 更新後持倉:")
    positions = get_positions(trd_ctx)
    for code, pos in positions.items():
        print(f"   {code}: {pos['qty']}股 (成本 ${pos['cost']:.2f})")
    
    trd_ctx.close()
    quote_ctx.close()
    print("\n✅ 自動交易完成!")
    print("=" * 50)
    
    # 只係有實際交易先至發送通知
    if executed_trades:
        notification = f"🦊 **久留美自動交易** - {datetime.now().strftime('%H:%M')}\n\n"
        for action, code, price in executed_trades:
            emoji = "🟢" if action == "BUY" else "🔴"
            notification += f"{emoji} {action} {code} @ ${price:.2f}\n"
        
        # 發送通知
        try:
            subprocess.run([
                'openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--target', '7955740007',
                '--message', notification
            ], timeout=10, capture_output=True)
            print("📨 已發送交易通知")
        except Exception as e:
            print(f"⚠️ 通知發送失敗: {e}")

if __name__ == '__main__':
    execute_auto_trade()
