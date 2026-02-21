#!/usr/bin/env python3
"""
運行潛力股發現系統
"""

import sys
sys.path.append('/Users/gordonlui/.openclaw/workspace')

from potential_stocks_scanner import PotentialStocksScanner

def main():
    """主函數"""
    print("🚀 啟動潛力股主動發現系統...")
    
    try:
        # 創建掃描器
        scanner = PotentialStocksScanner()
        
        print(f"\n{'='*70}")
        print(f"🔍 主動尋找潛力股")
        print(f"{'='*70}")
        print(f"掃描策略:")
        print(f"├── 技術突破股: 突破關鍵阻力位，動能強勁")
        print(f"├── 價值低估股: 基本面良好，價格低於內在價值")
        print(f"├── 高股息股: 穩定派息，現金流強勁")
        print(f"├── 行業龍頭股: 市場領導者，競爭優勢明顯")
        print(f"└── 近期利好股: 有催化劑，業績或消息面利好")
        print(f"{'='*70}")
        
        # 生成掃描報告
        report = scanner.generate_scan_report()
        
        # 精選推薦
        print(f"\n{'='*70}")
        print(f"🏆 本日精選潛力股推薦")
        print(f"{'='*70}")
        
        top_picks = scanner.get_top_picks(5)
        
        for i, stock in enumerate(top_picks, 1):
            print(f"\n{i}. {stock['code']} - {stock['name']}")
            print(f"   價格: HKD {stock['price']:.2f} ({stock['change']})")
            print(f"   類別: {scanner.get_category_name(stock['category'])}")
            print(f"   行業: {stock['sector']}")
            print(f"   推薦理由: {stock['reason']}")
            
            # 投資建議
            if stock['category'] == 'undervalued':
                print(f"   💡 投資建議: 價值投資，適合長期持有")
            elif stock['category'] == 'high_dividend':
                print(f"   💡 投資建議: 收息投資，穩定現金流")
            elif stock['category'] == 'technical_breakout':
                print(f"   💡 投資建議: 趨勢交易，設好止損")
            elif stock['category'] == 'sector_leader':
                print(f"   💡 投資建議: 核心持倉，龍頭優勢")
        
        # 與現有組合對比
        print(f"\n{'='*70}")
        print(f"📊 與你現有投資組合的互補性")
        print(f"{'='*70}")
        
        your_portfolio = ['00992', '00005', '01398', '02638', '09618', '00700', '09988']
        new_suggestions = []
        
        for pick in top_picks:
            if pick['code'] not in your_portfolio:
                new_suggestions.append(pick)
        
        if new_suggestions:
            print(f"建議新增以下股票到你的組合:")
            for stock in new_suggestions:
                print(f"  {stock['code']} {stock['name']} - {stock['sector']}股")
                print(f"    可補充你的{stock['sector']}行業配置")
        else:
            print(f"精選股票與你現有組合重疊較多")
            print(f"建議關注不同行業或風格的股票")
        
        # 行動建議
        print(f"\n{'='*70}")
        print(f"🎯 具體行動建議")
        print(f"{'='*70}")
        
        print(f"1. 研究階段:")
        print(f"   ├── 深入研究推薦股票的基本面")
        print(f"   ├── 查看最新財報和業績指引")
        print(f"   └── 分析技術圖表和關鍵價位")
        
        print(f"\n2. 試倉階段:")
        print(f"   ├── 選擇1-2隻最看好的股票")
        print(f"   ├── 小額試倉，觀察市場反應")
        print(f"   └── 設置明確的止損位")
        
        print(f"\n3. 加倉階段:")
        print(f"   ├── 如果走勢符合預期，逐步加倉")
        print(f"   ├── 達到目標價位部分獲利了結")
        print(f"   └── 保留核心倉位長期持有")
        
        # 風險提示
        print(f"\n{'='*70}")
        print(f"⚠️  重要風險提示")
        print(f"{'='*70}")
        
        print(f"1. 市場風險:")
        print(f"   ├── 宏觀經濟變化影響整體市場")
        print(f"   ├── 政策風險可能影響特定行業")
        print(f"   └── 國際關係影響跨境投資")
        
        print(f"\n2. 個股風險:")
        print(f"   ├── 公司基本面可能惡化")
        print(f"   ├── 行業競爭加劇影響盈利")
        print(f"   └── 管理層變動帶來不確定性")
        
        print(f"\n3. 操作風險:")
        print(f"   ├── 必須設置止損，控制虧損")
        print(f"   ├── 避免過度交易，保持耐心")
        print(f"   └── 分散投資，不要重倉單一股票")
        
        # 設置定期掃描
        print(f"\n{'='*70}")
        print(f"🔧 建議設置定期掃描")
        print(f"{'='*70}")
        
        print(f"建議掃描頻率:")
        print(f"├── 每日掃描: 技術突破股、近期利好股")
        print(f"├── 每周掃描: 價值低估股、行業龍頭股")
        print(f"├── 每月掃描: 高股息股、基本面變化")
        print(f"└── 每季掃描: 全面審視，調整組合")
        
        print(f"\n可設置Cron任務:")
        print(f"openclaw cron create --name \"潛力股每日掃描\" \\")
        print(f"  --cron \"0 9 * * 1-5\" --tz \"Asia/Hong_Kong\" \\")
        print(f"  --message \"運行潛力股掃描系統\" \\")
        print(f"  --model deepseek-coder --announce --to 7955740007")
        
        print(f"\n{'='*70}")
        print(f"✅ 潛力股發現完成")
        print(f"   發現潛力股: {report['total_potential']} 隻")
        print(f"   精選推薦: 5 隻")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"❌ 掃描過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()