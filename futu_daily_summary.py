#!/usr/bin/env python3
"""
富途模擬交易每日總結
每天收盤後運行（16:30）
"""

import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from futu import *

class DailySummary:
    """每日交易總結"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.summary_date = datetime.now().strftime('%Y-%m-%d')
        
    def connect(self):
        """連接富途API"""
        print("🔗 連接富途API...")
        try:
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1',
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES
            )
            
            self.quote_ctx = OpenQuoteContext(
                host='127.0.0.1',
                port=11111
            )
            
            print("✅ 連接成功")
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def get_portfolio_summary(self):
        """獲取投資組合總結"""
        print("\n📊 投資組合總結")
        print("=" * 50)
        
        try:
            # 獲取持倉
            ret, positions = self.trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
            
            portfolio_data = {
                "date": self.summary_date,
                "total_positions": 0,
                "total_market_value": 0,
                "total_cost": 0,
                "total_pnl": 0,
                "total_pnl_percent": 0,
                "positions": []
            }
            
            if ret == RET_OK and len(positions) > 0:
                portfolio_data["total_positions"] = len(positions)
                
                total_market_value = 0
                total_cost = 0
                total_pnl = 0
                
                print(f"📦 持倉數量: {len(positions)}")
                print("-" * 50)
                
                for idx, row in positions.iterrows():
                    position = {
                        "code": row['code'],
                        "name": row.get('stock_name', 'N/A'),
                        "quantity": int(row['qty']),
                        "cost_price": float(row.get('cost_price', 0)),
                        "market_price": float(row.get('market_price', 0)),
                        "market_value": float(row.get('market_val', 0)),
                        "pnl": float(row.get('pl_val', 0)),
                        "pnl_percent": float(row.get('pl_ratio', 0))
                    }
                    
                    portfolio_data["positions"].append(position)
                    
                    total_market_value += position["market_value"]
                    total_cost += position["cost_price"] * position["quantity"]
                    total_pnl += position["pnl"]
                    
                    # 顯示每個持倉
                    print(f"{position['code']} ({position['name']}):")
                    print(f"  數量: {position['quantity']:,}")
                    print(f"  成本價: {position['cost_price']:.2f}")
                    print(f"  市價: {position['market_price']:.2f}")
                    print(f"  市值: HKD {position['market_value']:,.2f}")
                    print(f"  盈虧: HKD {position['pnl']:+,.2f} ({position['pnl_percent']:+.2f}%)")
                    print()
                
                portfolio_data["total_market_value"] = total_market_value
                portfolio_data["total_cost"] = total_cost
                portfolio_data["total_pnl"] = total_pnl
                portfolio_data["total_pnl_percent"] = (total_pnl / total_cost * 100) if total_cost > 0 else 0
                
                print("-" * 50)
                print(f"💰 總市值: HKD {total_market_value:,.2f}")
                print(f"📈 總盈虧: HKD {total_pnl:+,.2f} ({portfolio_data['total_pnl_percent']:+.2f}%)")
                
            else:
                print("📭 無持倉")
                print("💰 總市值: HKD 0.00")
                print("📈 總盈虧: HKD 0.00 (0.00%)")
            
            return portfolio_data
            
        except Exception as e:
            print(f"❌ 獲取持倉失敗: {e}")
            return None
    
    def get_account_balance(self):
        """獲取賬戶餘額"""
        print("\n💰 賬戶資金狀況")
        print("=" * 50)
        
        try:
            ret, assets = self.trd_ctx.get_acc_assets(trd_env=TrdEnv.SIMULATE)
            
            account_data = {
                "date": self.summary_date,
                "total_assets": 0,
                "cash": 0,
                "market_value": 0,
                "available_funds": 0
            }
            
            if ret == RET_OK and not assets.empty:
                # 嘗試提取關鍵信息
                for col in assets.columns:
                    value = assets[col].iloc[0]
                    print(f"{col}: {value}")
                    
                    # 根據列名提取關鍵數據
                    if 'cash' in col.lower():
                        account_data["cash"] = float(value)
                    elif 'market_val' in col.lower():
                        account_data["market_value"] = float(value)
                    elif 'total_assets' in col.lower() or 'net_assets' in col.lower():
                        account_data["total_assets"] = float(value)
                    elif 'available' in col.lower():
                        account_data["available_funds"] = float(value)
                
                print(f"\n📊 總結:")
                print(f"  總資產: HKD {account_data['total_assets']:,.2f}")
                print(f"  現金: HKD {account_data['cash']:,.2f}")
                print(f"  持倉市值: HKD {account_data['market_value']:,.2f}")
                print(f"  可用資金: HKD {account_data['available_funds']:,.2f}")
                
            else:
                print("❌ 無法獲取資金數據")
                # 使用默認值
                account_data["total_assets"] = 979000
                account_data["cash"] = 979000
                account_data["market_value"] = 0
                account_data["available_funds"] = 979000
                
                print(f"\n📊 使用默認值:")
                print(f"  總資產: HKD {account_data['total_assets']:,.2f}")
                print(f"  現金: HKD {account_data['cash']:,.2f}")
                print(f"  持倉市值: HKD {account_data['market_value']:,.2f}")
                print(f"  可用資金: HKD {account_data['available_funds']:,.2f}")
            
            return account_data
            
        except Exception as e:
            print(f"❌ 獲取資金失敗: {e}")
            return None
    
    def get_today_trades(self):
        """獲取今日交易記錄"""
        print("\n📝 今日交易記錄")
        print("=" * 50)
        
        try:
            # 獲取今日日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            ret, trades = self.trd_ctx.history_order_list_query(
                trd_env=TrdEnv.SIMULATE,
                status_filter_list=[OrderStatus.FILLED, OrderStatus.FILLED_PART]
            )
            
            trades_data = {
                "date": self.summary_date,
                "total_trades": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "total_volume": 0,
                "total_value": 0,
                "trades": []
            }
            
            if ret == RET_OK and len(trades) > 0:
                # 過濾今日交易
                today_trades = []
                for idx, row in trades.iterrows():
                    trade_time = row.get('create_time', '')
                    if today in str(trade_time):
                        today_trades.append(row)
                
                trades_data["total_trades"] = len(today_trades)
                
                if today_trades:
                    print(f"📈 今日交易次數: {len(today_trades)}")
                    print("-" * 50)
                    
                    for trade in today_trades:
                        trade_info = {
                            "code": trade['code'],
                            "name": trade.get('stock_name', 'N/A'),
                            "side": trade['trd_side'],
                            "price": float(trade['price']),
                            "quantity": int(trade['qty']),
                            "value": float(trade['qty']) * float(trade['price']),
                            "time": str(trade.get('create_time', 'N/A')),
                            "status": trade['order_status']
                        }
                        
                        trades_data["trades"].append(trade_info)
                        
                        if trade_info["side"] == "BUY":
                            trades_data["buy_trades"] += 1
                        else:
                            trades_data["sell_trades"] += 1
                        
                        trades_data["total_volume"] += trade_info["quantity"]
                        trades_data["total_value"] += trade_info["value"]
                        
                        # 顯示交易
                        side_emoji = "🟢" if trade_info["side"] == "BUY" else "🔴"
                        print(f"{side_emoji} {trade_info['code']} ({trade_info['name']}):")
                        print(f"  方向: {trade_info['side']}")
                        print(f"  價格: {trade_info['price']:.2f}")
                        print(f"  數量: {trade_info['quantity']:,}")
                        print(f"  金額: HKD {trade_info['value']:,.2f}")
                        print(f"  時間: {trade_info['time']}")
                        print()
                    
                    print("-" * 50)
                    print(f"📊 交易統計:")
                    print(f"  買入: {trades_data['buy_trades']} 次")
                    print(f"  賣出: {trades_data['sell_trades']} 次")
                    print(f"  總成交量: {trades_data['total_volume']:,} 股")
                    print(f"  總交易額: HKD {trades_data['total_value']:,.2f}")
                    
                else:
                    print("📭 今日無交易記錄")
                    
            else:
                print("📭 無交易記錄或查詢失敗")
            
            return trades_data
            
        except Exception as e:
            print(f"❌ 獲取交易記錄失敗: {e}")
            return None
    
    def generate_daily_report(self, portfolio, account, trades):
        """生成每日報告"""
        print("\n📄 生成每日報告")
        print("=" * 50)
        
        report = {
            "report_date": self.summary_date,
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "portfolio_summary": portfolio,
            "account_summary": account,
            "trade_summary": trades,
            "performance_metrics": {}
        }
        
        # 計算績效指標
        initial_capital = 979000
        current_assets = account.get("total_assets", initial_capital)
        
        report["performance_metrics"] = {
            "initial_capital": initial_capital,
            "current_assets": current_assets,
            "total_return": current_assets - initial_capital,
            "total_return_percent": ((current_assets - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0,
            "daily_pnl": portfolio.get("total_pnl", 0),
            "daily_pnl_percent": portfolio.get("total_pnl_percent", 0),
            "positions_count": portfolio.get("total_positions", 0),
            "trades_count": trades.get("total_trades", 0)
        }
        
        # 顯示績效總結
        print("🎯 績效總結")
        print("-" * 50)
        print(f"初始資金: HKD {initial_capital:,.2f}")
        print(f"當前總資產: HKD {current_assets:,.2f}")
        print(f"總回報: HKD {report['performance_metrics']['total_return']:+,.2f}")
        print(f"總回報率: {report['performance_metrics']['total_return_percent']:+.2f}%")
        print(f"今日盈虧: HKD {report['performance_metrics']['daily_pnl']:+,.2f}")
        print(f"今日盈虧率: {report['performance_metrics']['daily_pnl_percent']:+.2f}%")
        print(f"持倉數量: {report['performance_metrics']['positions_count']}")
        print(f"交易次數: {report['performance_metrics']['trades_count']}")
        
        # 保存報告
        report_filename = f"futu_daily_report_{self.summary_date}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 報告已保存: {report_filename}")
        
        # 創建簡要文本報告
        text_report = f"""富途模擬交易每日報告
日期: {self.summary_date}
生成時間: {datetime.now().strftime('%H:%M:%S')}

📊 績效總結:
初始資金: HKD {initial_capital:,.2f}
當前總資產: HKD {current_assets:,.2f}
總回報: HKD {report['performance_metrics']['total_return']:+,.2f}
總回報率: {report['performance_metrics']['total_return_percent']:+.2f}%
今日盈虧: HKD {report['performance_metrics']['daily_pnl']:+,.2f}
今日盈虧率: {report['performance_metrics']['daily_pnl_percent']:+.2f}%

📦 持倉狀況:
持倉數量: {report['performance_metrics']['positions_count']}
持倉市值: HKD {portfolio.get('total_market_value', 0):,.2f}

📝 交易活動:
交易次數: {report['performance_metrics']['trades_count']}
買入次數: {trades.get('buy_trades', 0)}
賣出次數: {trades.get('sell_trades', 0)}

💰 資金狀況:
現金餘額: HKD {account.get('cash', 0):,.2f}
可用資金: HKD {account.get('available_funds', 0):,.2f}

---
OpenClaw 自動化交易報告系統
"""
        
        text_filename = f"futu_daily_summary_{self.summary_date}.txt"
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        print(f"📝 文本報告已保存: {text_filename}")
        
        return report_filename, text_filename
    
    def send_email_report(self, text_filename):
        """發送郵件報告（可選）"""
        print("\n📧 可選: 發送郵件報告")
        print("=" * 50)
        
        try:
            with open(text_filename, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            print("📋 報告內容摘要:")
            lines = report_content.split('\n')
            for i in range(min(15, len(lines))):
                print(f"  {lines[i]}")
            
            print("\n📧 要發送郵件，請運行:")
            print(f'  python3 send_email_direct.py "zero850x@gmail.com" "富途每日交易報告 {self.summary_date}" "{report_content}"')
            
        except Exception as e:
            print(f"❌ 讀取報告失敗: {e}")
    
    def close(self):
        """關閉連接"""
        if self.trd_ctx:
            self.trd_ctx.close()
        if self.quote_ctx:
            self.quote_ctx.close()
        print("\n🔒 連接已關閉")

def main():
    print("📊 富途模擬交易每日總結")
    print("=" * 60)
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    summary = DailySummary()
    
    # 1. 連接
    if not summary.connect():
        print("❌ 無法連接，跳過今日總結")
        return
    
    # 2. 獲取投資組合總結
    portfolio = summary.get_portfolio_summary()
    
    # 3. 獲取賬戶餘額
    account = summary.get_account_balance()
    
    # 4. 獲取今日交易
    trades = summary.get_today_trades()
    
    # 5. 生成報告
    if portfolio is not None and account is not None:
        json_report, text_report = summary.generate_daily_report(portfolio, account, trades)
        
        # 6. 可選: 發送郵件
        summary.send_email_report(text_report)
    else:
        print("❌ 無法生成完整報告")
    
    # 7. 關閉連接
    summary.close()
    
    print("\n" + "=" * 60)
    print("🎉 每日總結完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()