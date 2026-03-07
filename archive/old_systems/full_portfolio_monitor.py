#!/usr/bin/env python3
"""
完整投資組合監控系統
監控所有持倉股票
"""

import sys
import json
from datetime import datetime

def analyze_full_portfolio():
    """分析完整投資組合"""
    print(f"\n{'='*70}")
    print(f"📊 你的完整投資組合監控報告")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # 投資組合數據
    portfolio = [
        {
            'code': '00992',
            'name': '聯想集團',
            'category': '科技股',
            'position': 26000,
            'buy_price': 8.59,
            'current_price': 9.17,
            'notes': '重點持倉，正在測試關鍵支撐位'
        },
        {
            'code': '00005',
            'name': '匯豐控股',
            'category': '銀行股',
            'position': '持有',
            'buy_price': 59.40,
            'current_price': 134.20,
            'notes': '收息股，長期表現優秀'
        },
        {
            'code': '01398',
            'name': '工商銀行',
            'category': '銀行股',
            'position': '持有',
            'buy_price': 4.46,
            'current_price': 6.40,
            'notes': '收息股，穩定增長'
        },
        {
            'code': '02638',
            'name': '港燈-SS',
            'category': '公用事業',
            'position': '持有',
            'buy_price': 4.85,
            'current_price': 6.97,
            'notes': '防守型收息股'
        },
        {
            'code': '09618',
            'name': '京東集團',
            'category': '科技股',
            'position': '持有',
            'buy_price': 120.00,
            'current_price': 105.90,
            'notes': '當前虧損，可考慮成本平均'
        },
        {
            'code': '00700',
            'name': '騰訊控股',
            'category': '科技股',
            'position': '監控',
            'current_price': 522.00,
            'notes': '市場風向標，密切監控'
        },
        {
            'code': '09988',
            'name': '阿里巴巴',
            'category': '科技股',
            'position': '監控',
            'current_price': 148.70,
            'notes': '科技股代表，跟隨大市'
        }
    ]
    
    # 分析每隻股票
    print(f"\n📈 股票詳細分析:")
    print(f"{'-'*70}")
    
    total_profit = 0
    total_investment = 0
    stocks_with_profit = 0
    stocks_with_loss = 0
    
    for stock in portfolio:
        print(f"\n{stock['code']} - {stock['name']} ({stock['category']})")
        print(f"  狀態: {stock['position']}")
        
        if 'buy_price' in stock and 'current_price' in stock:
            buy_price = stock['buy_price']
            current_price = stock['current_price']
            profit_pct = ((current_price - buy_price) / buy_price) * 100
            
            print(f"  買入價: HKD {buy_price:.2f}")
            print(f"  當前價: HKD {current_price:.2f}")
            print(f"  盈虧: {profit_pct:+.2f}%")
            
            # 計算盈利金額（如果知道股數）
            if isinstance(stock['position'], int):
                profit_amount = (current_price - buy_price) * stock['position']
                print(f"  盈利金額: HKD {profit_amount:+,.2f}")
                total_profit += profit_amount
                total_investment += buy_price * stock['position']
            
            # 記錄盈虧狀態
            if profit_pct > 0:
                stocks_with_profit += 1
            elif profit_pct < 0:
                stocks_with_loss += 1
            
            # 特別分析
            if stock['code'] == '00992':  # 聯想集團
                if current_price <= 9.17:
                    print(f"  ⚠️  警告: 正在測試關鍵支撐位 $9.17")
                if profit_pct >= 8:
                    print(f"  ✅ 建議: 已達8%止盈目標，可部分獲利了結")
            
            elif stock['code'] == '00005':  # 匯豐控股
                print(f"  💰 表現: 優秀 (+{profit_pct:.1f}%)")
                print(f"      建議: 長期持有，享受股息")
            
            elif stock['code'] == '09618':  # 京東集團
                print(f"  📉 狀態: 虧損 ({profit_pct:.1f}%)")
                print(f"      建議: 可考慮分批買入降低成本")
        
        else:
            print(f"  當前價: HKD {stock.get('current_price', 'N/A')}")
        
        print(f"  備註: {stock['notes']}")
    
    # 總體表現
    print(f"\n{'='*70}")
    print(f"💰 投資組合總體表現")
    print(f"{'='*70}")
    
    total_stocks = len(portfolio)
    if total_investment > 0:
        total_return_pct = (total_profit / total_investment) * 100
    else:
        total_return_pct = 0
    
    print(f"監控股票數: {total_stocks} 隻")
    print(f"盈利股票: {stocks_with_profit} 隻")
    print(f"虧損股票: {stocks_with_loss} 隻")
    print(f"總投資金額: HKD {total_investment:,.2f}")
    print(f"總盈利金額: HKD {total_profit:+,.2f}")
    print(f"總回報率: {total_return_pct:+.2f}%")
    
    # 分類表現
    print(f"\n📊 按類別分析:")
    categories = {}
    for stock in portfolio:
        category = stock['category']
        if category not in categories:
            categories[category] = {'count': 0, 'stocks': []}
        categories[category]['count'] += 1
        categories[category]['stocks'].append(stock['code'])
    
    for category, data in categories.items():
        print(f"  {category}: {data['count']}隻 - {', '.join(data['stocks'])}")
    
    # 投資建議
    print(f"\n{'='*70}")
    print(f"🎯 投資組合建議")
    print(f"{'='*70}")
    
    if total_return_pct >= 20:
        print(f"✅ 組合表現優秀 (+{total_return_pct:.1f}%)")
        print(f"   建議行動:")
        print(f"   1. 部分獲利了結，鎖定盈利")
        print(f"   2. 將盈利轉入防守型股票")
        print(f"   3. 保持核心持倉，長期持有")
    
    elif total_return_pct >= 10:
        print(f"👍 組合表現良好 (+{total_return_pct:.1f}%)")
        print(f"   建議行動:")
        print(f"   1. 繼續持有表現良好的股票")
        print(f"   2. 優化虧損股票配置")
        print(f"   3. 考慮增加現金比例")
    
    elif total_return_pct >= 0:
        print(f"⚠️  組合表現一般 (+{total_return_pct:.1f}%)")
        print(f"   建議行動:")
        print(f"   1. 檢討投資策略")
        print(f"   2. 增加表現較好股票的權重")
        print(f"   3. 考慮止損虧損較大的股票")
    
    else:
        print(f"🚨 組合虧損中 ({total_return_pct:.1f}%)")
        print(f"   建議行動:")
        print(f"   1. 嚴格執行止損紀律")
        print(f"   2. 重新評估投資組合")
        print(f"   3. 考慮專業投資建議")
    
    # 監控系統狀態
    print(f"\n{'='*70}")
    print(f"🔧 當前監控系統狀態")
    print(f"{'='*70}")
    
    print(f"已設置的監控任務:")
    print(f"├── 聯想集團XGBoost融合交易 (每30分鐘)")
    print(f"├── 價格驗證檢查 (每小時整點 09-16)")
    print(f"├── 交易監控 (11:30, 13:00, 15:30, 15:55)")
    print(f"├── 收市前綜合檢查 (15:55)")
    print(f"└── 收市後總結 (16:05)")
    
    print(f"\n建議新增監控:")
    print(f"├── 投資組合每日總結 (16:10)")
    print(f"├── 收息股表現月度報告 (每月首個交易日)")
    print(f"├── 風險評估每周報告 (每周一)")
    print(f"└── 市場情緒監控 (每日開市前)")
    
    # 保存報告
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'portfolio': portfolio,
        'summary': {
            'total_stocks': total_stocks,
            'stocks_with_profit': stocks_with_profit,
            'stocks_with_loss': stocks_with_loss,
            'total_investment': total_investment,
            'total_profit': total_profit,
            'total_return_pct': total_return_pct
        }
    }
    
    report_file = f"/Users/gordonlui/.openclaw/workspace/full_portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 完整投資組合報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ 完整投資組合監控完成")
    print(f"{'='*70}")
    
    return report

def main():
    """主函數"""
    print("🚀 啟動完整投資組合監控系統...")
    
    try:
        report = analyze_full_portfolio()
        
        # 簡要總結
        print(f"\n📋 監控總結:")
        print(f"  監控股票: {report['summary']['total_stocks']} 隻")
        print(f"  盈利股票: {report['summary']['stocks_with_profit']} 隻")
        print(f"  虧損股票: {report['summary']['stocks_with_loss']} 隻")
        print(f"  總回報率: {report['summary']['total_return_pct']:+.2f}%")
        
        # 重點關注
        print(f"\n🎯 重點關注:")
        for stock in report['portfolio']:
            if stock['code'] in ['00992', '00005', '09618']:
                if 'buy_price' in stock and 'current_price' in stock:
                    profit_pct = ((stock['current_price'] - stock['buy_price']) / stock['buy_price']) * 100
                    print(f"  {stock['code']} {stock['name']}: {profit_pct:+.2f}% - {stock['notes']}")
        
    except Exception as e:
        print(f"❌ 監控過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()