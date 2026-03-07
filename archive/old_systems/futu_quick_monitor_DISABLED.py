#!/usr/bin/env python3
"""
富途快速監控 - 用於WhatsApp通知
每30分鐘運行，發送關鍵信息到WhatsApp
"""

import sys
import json
from datetime import datetime, timedelta
from futu import *

# 交易成本設定
PLATFORM_FEE = 15.0  # 每筆平台費 HKD 15
TAX_RATE = 0.001     # 0.1% 稅

def calculate_trading_cost(price, quantity, is_buy=True):
    """計算交易成本"""
    trade_value = price * quantity
    tax = trade_value * TAX_RATE
    platform_fee = PLATFORM_FEE
    total_cost = tax + platform_fee
    
    if is_buy:
        return trade_value + total_cost, total_cost
    else:
        return trade_value - total_cost, total_cost

def get_quick_portfolio_summary():
    """獲取投資組合快速摘要"""
    try:
        # 連接
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        quote_ctx = OpenQuoteContext(
            host='127.0.0.1',
            port=11111
        )
        
        # 檢查持倉
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        summary = {
            'timestamp': datetime.now().strftime('%H:%M'),
            'total_positions': 0,
            'total_value': 0,
            'total_pnl': 0,
            'total_pnl_pct': 0,
            'holdings': [],
            'alerts': []
        }
        
        if ret == RET_OK and len(positions) > 0:
            summary['total_positions'] = len(positions)
            
            total_cost = 0
            total_market_val = 0
            
            for idx, row in positions.iterrows():
                code = row['code']
                qty = float(row['qty'])
                cost_price = float(row.get('cost_price', 0))
                market_val = float(row.get('market_val', 0))
                current_price = market_val / qty if qty > 0 else 0
                
                # 計算盈虧
                pnl = market_val - (cost_price * qty)
                pnl_pct = (pnl / (cost_price * qty) * 100) if cost_price > 0 else 0
                
                # 計算賣出淨收入
                sell_net, sell_cost = calculate_trading_cost(current_price, qty, is_buy=False)
                cost_pct = (sell_cost / market_val * 100) if market_val > 0 else 0
                
                # 保存持倉信息
                holding = {
                    'code': code,
                    'qty': qty,
                    'current_price': current_price,
                    'market_val': market_val,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'sell_net': sell_net,
                    'cost_pct': cost_pct
                }
                summary['holdings'].append(holding)
                
                # 累計總值
                total_cost += cost_price * qty
                total_market_val += market_val
                
                # 檢查警報條件
                if pnl_pct < -5:
                    summary['alerts'].append(f"❗ {code}: 虧損{pnl_pct:.1f}%")
                elif pnl_pct > 10:
                    summary['alerts'].append(f"💰 {code}: 盈利{pnl_pct:.1f}%")
            
            # 計算總盈虧
            summary['total_value'] = total_market_val
            summary['total_pnl'] = total_market_val - total_cost
            summary['total_pnl_pct'] = (summary['total_pnl'] / total_cost * 100) if total_cost > 0 else 0
        
        trd_ctx.close()
        quote_ctx.close()
        
        return summary
        
    except Exception as e:
        return {'error': str(e)}

def format_whatsapp_message(summary):
    """格式化WhatsApp消息"""
    if 'error' in summary:
        return f"❌ 監控錯誤: {summary['error']}"
    
    timestamp = summary['timestamp']
    message = f"📊 交易監控 ({timestamp})\n"
    message += "═" * 30 + "\n"
    
    if summary['total_positions'] == 0:
        message += "📭 無持倉\n"
        message += "💡 建議: 可考慮建立新倉位"
        return message
    
    # 總體信息
    message += f"📦 持倉: {summary['total_positions']}個\n"
    message += f"💰 總市值: HKD {summary['total_value']:,.0f}\n"
    message += f"📈 總盈虧: HKD {summary['total_pnl']:+,.0f} ({summary['total_pnl_pct']:+.1f}%)\n"
    message += "─" * 30 + "\n"
    
    # 各持倉詳情
    for i, holding in enumerate(summary['holdings'], 1):
        pnl_emoji = "🟢" if holding['pnl'] >= 0 else "🔴"
        message += f"{i}. {holding['code']}:\n"
        message += f"   {pnl_emoji} {holding['pnl_pct']:+.1f}% (HKD {holding['pnl']:+,.0f})\n"
        message += f"   📊 {holding['qty']:,.0f}股 @ {holding['current_price']:.2f}\n"
        message += f"   💰 市值: HKD {holding['market_val']:,.0f}\n"
        message += f"   ⚖️  賣出成本: {holding['cost_pct']:.2f}%\n"
    
    # 警報信息
    if summary['alerts']:
        message += "─" * 30 + "\n"
        message += "⚠️  警報:\n"
        for alert in summary['alerts']:
            message += f"• {alert}\n"
    
    # 交易成本提醒
    message += "═" * 30 + "\n"
    message += f"💡 成本: 平台費HKD{PLATFORM_FEE} + {TAX_RATE*100}%稅\n"
    message += f"⏰ 下次監控: {(datetime.now() + timedelta(minutes=30)).strftime('%H:%M')}"
    
    return message

def send_to_whatsapp(message):
    """發送到WhatsApp"""
    try:
        import subprocess
        # 限制消息長度（WhatsApp有長度限制）
        if len(message) > 1000:
            message = message[:997] + "..."
        
        # 使用openclaw發送消息
        cmd = [
            "openclaw", "message", "send",
            "--target", "+85298104938",
            "--message", message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ WhatsApp消息已發送")
            return True
        else:
            print(f"❌ WhatsApp發送失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp發送錯誤: {e}")
        return False

def send_to_email(summary, detailed_report=None):
    """發送到電郵"""
    try:
        # 導入電郵報告系統
        import sys
        sys.path.append('/Users/gordonlui/.openclaw/workspace')
        
        from email_report_system import EmailReporter
        
        reporter = EmailReporter()
        
        # 發送交易監控報告
        success = reporter.send_trade_monitor_report(summary)
        
        if success:
            print("✅ 電郵報告已發送")
            reporter.log_email_sent('trade_monitor', True)
        else:
            print("❌ 電郵報告發送失敗")
            reporter.log_email_sent('trade_monitor', False)
            
        return success
        
    except Exception as e:
        print(f"❌ 電郵發送錯誤: {e}")
        return False

def main():
    """主函數"""
    print(f"📱 富途快速監控 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("=" * 50)
    
    # 獲取投資組合摘要
    print("獲取投資組合信息...")
    summary = get_quick_portfolio_summary()
    
    if 'error' in summary:
        print(f"❌ 錯誤: {summary['error']}")
        error_msg = f"❌ 交易監控錯誤 ({datetime.now().strftime('%H:%M')})\n{summary['error']}"
        send_to_whatsapp(error_msg)
        return
    
    # 格式化消息
    print("格式化消息...")
    whatsapp_msg = format_whatsapp_message(summary)
    
    # 顯示在控制台
    print("\n" + whatsapp_msg + "\n")
    
    # 發送到WhatsApp和電郵
    print("發送到WhatsApp...")
    whatsapp_success = send_to_whatsapp(whatsapp_msg)
    
    print("發送到電郵...")
    email_success = send_to_email(summary)
    
    success = whatsapp_success or email_success  # 只要一個成功就認為成功
    
    if success:
        print("✅ 監控完成，消息已發送")
    else:
        print("⚠️  監控完成，但WhatsApp發送失敗")
    
    # 保存日誌
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'summary': summary,
        'whatsapp_sent': success,
        'message_preview': whatsapp_msg[:100] + "..." if len(whatsapp_msg) > 100 else whatsapp_msg
    }
    
    log_file = f"/Users/gordonlui/.openclaw/workspace/monitor_reports/quick_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    
    try:
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2, default=str)
        
        print(f"📁 日誌已保存: {log_file}")
        
    except Exception as e:
        print(f"❌ 保存日誌失敗: {e}")

if __name__ == "__main__":
    main()