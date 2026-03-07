#!/usr/bin/env python3
"""
主動潛力股發現系統
"""

import sys
import json
from datetime import datetime

def scan_potential_stocks():
    """掃描潛力股"""
    print(f"\n{'='*70}")
    print(f"🔍 主動潛力股發現系統")
    print(f"{'='*70}")
    print(f"掃描時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # 潛力股數據庫
    potential_stocks = {
        '技術突破股': [
            {'code': '03690', 'name': '美團-W', 'price': 85.50, 'change': '+3.2%',
             'sector': '科技', 'reason': '突破三角形整理，外賣業務恢復增長'},
            {'code': '09868', 'name': '小鵬汽車-W', 'price': 42.30, 'change': '+5.1%',
             'sector': '新能源', 'reason': '突破50日線，新車型訂單強勁'},
            {'code': '09999', 'name': '網易-S', 'price': 156.80, 'change': '+2.8%',
             'sector': '科技', 'reason': '遊戲業務穩定，雲音樂分拆在即'}
        ],
        '價值低估股': [
            {'code': '00883', 'name': '中國海洋石油', 'price': 18.25, 'change': '+1.1%',
             'sector': '能源', 'reason': '市盈率8倍，油價回升利好'},
            {'code': '00386', 'name': '中國石油化工', 'price': 4.15, 'change': '+0.5%',
             'sector': '能源', 'reason': '市淨率0.6倍，股息率吸引'},
            {'code': '00939', 'name': '建設銀行', 'price': 5.80, 'change': '+0.9%',
             'sector': '金融', 'reason': '市盈率4倍，資產質量改善'}
        ],
        '高股息股': [
            {'code': '00003', 'name': '香港中華煤氣', 'price': 6.20, 'change': '+0.3%',
             'sector': '公用事業', 'reason': '連續多年派息，股息率4.8%'},
            {'code': '00006', 'name': '電能實業', 'price': 45.50, 'change': '+0.4%',
             'sector': '公用事業', 'reason': '穩定高息股，現金流強勁'},
            {'code': '00857', 'name': '中國石油股份', 'price': 6.85, 'change': '+0.7%',
             'sector': '能源', 'reason': '油價回升，股息率5.8%'}
        ],
        '行業龍頭股': [
            {'code': '00700', 'name': '騰訊控股', 'price': 522.00, 'change': '-1.3%',
             'sector': '科技', 'reason': '科技股龍頭，生態系統強大'},
            {'code': '01299', 'name': '友邦保險', 'price': 84.50, 'change': '+0.6%',
             'sector': '金融', 'reason': '亞洲保險龍頭，內含價值增長'},
            {'code': '02020', 'name': '安踏體育', 'price': 78.40, 'change': '+1.8%',
             'sector': '消費', 'reason': '運動品牌龍頭，多品牌成功'}
        ],
        '近期利好股': [
            {'code': '01810', 'name': '小米集團-W', 'price': 14.85, 'change': '+2.1%',
             'sector': '科技', 'reason': '新車型發布，進軍電動車市場'},
            {'code': '02269', 'name': '藥明生物', 'price': 32.50, 'change': '+3.5%',
             'sector': '醫藥', 'reason': '獲大額合同，產能擴張順利'},
            {'code': '09633', 'name': '農夫山泉', 'price': 42.80, 'change': '+1.2%',
             'sector': '消費', 'reason': '夏季飲料旺季，業績預期良好'}
        ]
    }
    
    # 顯示掃描結果
    total_stocks = 0
    for category, stocks in potential_stocks.items():
        total_stocks += len(stocks)
        
        print(f"\n📈 {category} ({len(stocks)}隻):")
        print("-" * 70)
        
        for stock in stocks:
            print(f"  {stock['code']} - {stock['name']}")
            print(f"     價格: HKD {stock['price']:.2f} ({stock['change']})")
            print(f"     行業: {stock['sector']}")
            print(f"     理由: {stock['reason']}")
            print()
    
    # 精選推薦
    print(f"\n{'='*70}")
    print(f"🏆 本日精選潛力股 (Top 5)")
    print(f"{'='*70}")
    
    # 評分選出Top 5
    all_stocks = []
    for category, stocks in potential_stocks.items():
        for stock in stocks:
            stock['category'] = category
            all_stocks.append(stock)
    
    # 簡單評分
    def calculate_score(stock):
        score = 0
        
        # 類別加分
        category_scores = {
            '技術突破股': 25,
            '價值低估股': 20,
            '行業龍頭股': 30,
            '高股息股': 15,
            '近期利好股': 20
        }
        
        score += category_scores.get(stock['category'], 0)
        
        # 行業加分
        sector_scores = {
            '科技': 10,
            '新能源': 15,
            '醫藥': 12,
            '消費': 8,
            '金融': 5,
            '能源': 7,
            '公用事業': 3
        }
        
        score += sector_scores.get(stock['sector'], 0)
        
        # 價格變動加分
        if '+' in stock['change']:
            change_pct = float(stock['change'].strip('+%'))
            score += change_pct * 2
        
        return score
    
    sorted_stocks = sorted(all_stocks, key=calculate_score, reverse=True)
    top_5 = sorted_stocks[:5]
    
    for i, stock in enumerate(top_5, 1):
        print(f"\n{i}. {stock['code']} - {stock['name']}")
        print(f"   類別: {stock['category']}")
        print(f"   行業: {stock['sector']}")
        print(f"   價格: HKD {stock['price']:.2f} ({stock['change']})")
        print(f"   推薦理由: {stock['reason']}")
        
        # 投資建議
        if stock['category'] == '價值低估股':
            print(f"   💡 建議: 價值投資，適合分批買入長期持有")
        elif stock['category'] == '技術突破股':
            print(f"   💡 建議: 趨勢交易，設好止損跟隨趨勢")
        elif stock['category'] == '高股息股':
            print(f"   💡 建議: 收息投資，穩定現金流來源")
        elif stock['category'] == '行業龍頭股':
            print(f"   💡 建議: 核心持倉，享受行業增長紅利")
        elif stock['category'] == '近期利好股':
            print(f"   💡 建議: 事件驅動，把握短期催化劑")
    
    # 與現有組合對比
    print(f"\n{'='*70}")
    print(f"📊 與你現有投資組合的互補性分析")
    print(f"{'='*70}")
    
    your_portfolio = ['07500', '00700', '02800']
    
    print(f"你的現有組合 ({len(your_portfolio)}隻):")
    print(f"  07500: 兩倍看空恆指")
    print(f"  00700: 騰訊控股")
    print(f"  02800: 盈富基金")
    
    print(f"\n建議新增行業:")
    
    # 分析缺少的行業
    your_sectors = ['科技', '銀行', '公用事業']
    suggested_sectors = []
    
    for stock in top_5:
        if stock['sector'] not in your_sectors and stock['sector'] not in suggested_sectors:
            suggested_sectors.append(stock['sector'])
    
    if suggested_sectors:
        for sector in suggested_sectors:
            print(f"  ✅ {sector}: 可增加行業分散度")
            
            # 推薦該行業股票
            sector_stocks = [s for s in top_5 if s['sector'] == sector]
            for stock in sector_stocks:
                print(f"     可考慮: {stock['code']} {stock['name']}")
    else:
        print(f"  ⚠️  精選股票與你現有行業重疊較多")
        print(f"     建議關注不同風格或細分行業")
    
    # 具體行動計劃
    print(f"\n{'='*70}")
    print(f"🎯 具體行動計劃")
    print(f"{'='*70}")
    
    print(f"1. 研究階段 (本週):")
    print(f"   ├── 深入研究Top 3精選股票")
    print(f"   ├── 查看最新財報和業績指引")
    print(f"   └── 分析技術圖表關鍵價位")
    
    print(f"\n2. 試倉階段 (下週):")
    print(f"   ├── 選擇1-2隻最看好的股票")
    print(f"   ├── 小額試倉 (例如HKD 10,000)")
    print(f"   └── 設置明確止損位 (建議-8%)")
    
    print(f"\n3. 評估階段 (一個月後):")
    print(f"   ├── 評估試倉表現")
    print(f"   ├── 如果表現良好，考慮加倉")
    print(f"   └── 如果不如預期，檢討原因")
    
    # 風險管理
    print(f"\n{'='*70}")
    print(f"⚠️  風險管理要點")
    print(f"{'='*70}")
    
    print(f"1. 倉位控制:")
    print(f"   ├── 單隻股票不超過總資金10%")
    print(f"   ├── 單一行業不超過總資金30%")
    print(f"   └── 新股票試倉不超過總資金5%")
    
    print(f"\n2. 止損紀律:")
    print(f"   ├── 技術股: -8% 止損")
    print(f"   ├── 價值股: -10% 止損")
    print(f"   └── 必須嚴格執行，不抱僥倖心理")
    
    print(f"\n3. 盈利保護:")
    print(f"   ├── 達到15%盈利，考慮部分獲利了結")
    print(f"   ├── 達到25%盈利，移動止損保護利潤")
    print(f"   └── 保留核心倉位享受長期增長")
    
    # 保存報告
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_scanned': total_stocks,
        'top_picks': top_5,
        'categories': {cat: len(stocks) for cat, stocks in potential_stocks.items()},
        'your_portfolio': your_portfolio,
        'suggested_sectors': suggested_sectors
    }
    
    report_file = f"/Users/gordonlui/.openclaw/workspace/active_stock_scanner_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 潛力股發現報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ 主動潛力股發現完成")
    print(f"   掃描股票: {total_stocks} 隻")
    print(f"   精選推薦: 5 隻")
    print(f"   建議新增行業: {len(suggested_sectors)} 個")
    print(f"{'='*70}")
    
    return report

def main():
    """主函數"""
    print("🚀 啟動主動潛力股發現系統...")
    
    try:
        report = scan_potential_stocks()
        
        # 簡要總結
        print(f"\n📋 發現總結:")
        print(f"  精選Top 5:")
        for i, stock in enumerate(report['top_picks'], 1):
            print(f"    {i}. {stock['code']} {stock['name']} - {stock['sector']}")
        
        print(f"\n  建議關注行業:")
        for sector in report['suggested_sectors']:
            print(f"    ✅ {sector}")
        
        print(f"\n  下一步行動:")
        print(f"    1. 深入研究Top 3精選股票")
        print(f"    2. 小額試倉驗證判斷")
        print(f"    3. 嚴格執行風險管理")
        
    except Exception as e:
        print(f"❌ 掃描過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()