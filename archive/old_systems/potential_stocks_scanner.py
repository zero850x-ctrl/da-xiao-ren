#!/usr/bin/env python3
"""
潛力股發現系統
主動尋找技術突破、價值低估、資金流入的潛力股
"""

import sys
import json
import pandas as pd
from datetime import datetime, timedelta
sys.path.append('/Users/gordonlui/.openclaw/workspace')

class PotentialStocksScanner:
    """潛力股掃描系統"""
    
    def __init__(self):
        # 掃描配置
        self.scan_config = {
            'sectors': {
                '科技': ['騰訊', '阿里巴巴', '美團', '京東', '小米', '比亞迪電子'],
                '金融': ['匯豐', '友邦', '平保', '工行', '建行', '中銀香港'],
                '地產': ['新鴻基', '長實', '恆隆', '九倉', '領展'],
                '消費': ['安踏', '李寧', '蒙牛', '海底撈', '百威亞太'],
                '醫藥': ['藥明生物', '石藥', '中生製藥', '翰森製藥'],
                '公用事業': ['中電', '港燈', '煤氣', '粵海投資'],
                '工業': ['中車', '中鐵建', '中交建', '中國建築']
            },
            'scan_criteria': {
                'technical_breakout': True,      # 技術突破
                'undervalued': True,            # 價值低估
                'high_dividend': True,          # 高股息
                'sector_leader': True,          # 行業龍頭
                'recent_news': True,            # 近期利好
                'volume_spike': True            # 成交量暴增
            },
            'thresholds': {
                'min_market_cap': 10,           # 最小市值(十億)
                'min_volume': 1000000,          # 最小成交量
                'dividend_yield': 0.04,         # 股息率閾值
                'pe_ratio_max': 20,             # 市盈率上限
                'pb_ratio_max': 1.5             # 市淨率上限
            }
        }
        
        # 潛力股數據庫（模擬數據）
        self.potential_stocks_db = self.load_potential_stocks_db()
    
    def load_potential_stocks_db(self):
        """加載潛力股數據庫（模擬）"""
        return {
            'technical_breakout': [
                {'code': '03690', 'name': '美團-W', 'price': 85.50, 'change': '+3.2%', 
                 'reason': '突破三角形整理，成交量放大', 'sector': '科技'},
                {'code': '09868', 'name': '小鵬汽車-W', 'price': 42.30, 'change': '+5.1%',
                 'reason': '突破50日線，RSI轉強', 'sector': '新能源車'},
                {'code': '09999', 'name': '網易-S', 'price': 156.80, 'change': '+2.8%',
                 'reason': '突破下降趨勢線，MACD金叉', 'sector': '科技'}
            ],
            'undervalued': [
                {'code': '00883', 'name': '中國海洋石油', 'price': 18.25, 'change': '+1.1%',
                 'reason': '市盈率8倍，股息率6.5%', 'sector': '能源'},
                {'code': '00386', 'name': '中國石油化工', 'price': 4.15, 'change': '+0.5%',
                 'reason': '市淨率0.6倍，嚴重低估', 'sector': '能源'},
                {'code': '00939', 'name': '建設銀行', 'price': 5.80, 'change': '+0.9%',
                 'reason': '市盈率4倍，股息率7%', 'sector': '金融'}
            ],
            'high_dividend': [
                {'code': '00003', 'name': '香港中華煤氣', 'price': 6.20, 'change': '+0.3%',
                 'reason': '連續多年派息，股息率4.8%', 'sector': '公用事業'},
                {'code': '00006', 'name': '電能實業', 'price': 45.50, 'change': '+0.4%',
                 'reason': '穩定高息股，股息率5.2%', 'sector': '公用事業'},
                {'code': '00857', 'name': '中國石油股份', 'price': 6.85, 'change': '+0.7%',
                 'reason': '油價回升，股息率5.8%', 'sector': '能源'}
            ],
            'sector_leader': [
                {'code': '00700', 'name': '騰訊控股', 'price': 522.00, 'change': '-1.3%',
                 'reason': '科技股龍頭，生態系統強大', 'sector': '科技'},
                {'code': '01299', 'name': '友邦保險', 'price': 84.50, 'change': '+0.6%',
                 'reason': '亞洲保險龍頭，增長穩定', 'sector': '金融'},
                {'code': '02318', 'name': '中國平安', 'price': 48.30, 'change': '+0.8%',
                 'reason': '綜合金融平台，轉型科技', 'sector': '金融'}
            ],
            'recent_news': [
                {'code': '01810', 'name': '小米集團-W', 'price': 14.85, 'change': '+2.1%',
                 'reason': '新車型發布，進軍電動車', 'sector': '科技'},
                {'code': '02020', 'name': '安踏體育', 'price': 78.40, 'change': '+1.8%',
                 'reason': '奧運贊助商，業績超預期', 'sector': '消費'},
                {'code': '02269', 'name': '藥明生物', 'price': 32.50, 'change': '+3.5%',
                 'reason': '獲大額合同，產能擴張', 'sector': '醫藥'}
            ]
        }
    
    def scan_by_sector(self, sector):
        """按行業掃描潛力股"""
        print(f"\n🔍 掃描{sector}行業潛力股...")
        
        potential_stocks = []
        
        # 模擬掃描邏輯
        if sector == '科技':
            potential_stocks.extend([
                {'code': '03690', 'name': '美團-W', 'reason': '外賣業務恢復增長，到店酒旅強勁'},
                {'code': '09999', 'name': '網易-S', 'reason': '遊戲業務穩定，雲音樂分拆'},
                {'code': '01810', 'name': '小米集團-W', 'reason': '手機市佔率提升，汽車業務起步'}
            ])
        elif sector == '金融':
            potential_stocks.extend([
                {'code': '00005', 'name': '匯豐控股', 'reason': '加息周期受益，股息率吸引'},
                {'code': '01299', 'name': '友邦保險', 'reason': '亞洲市場擴張，內含價值增長'},
                {'code': '03988', 'name': '中國銀行', 'reason': '估值低廉，股息率超過7%'}
            ])
        elif sector == '消費':
            potential_stocks.extend([
                {'code': '02020', 'name': '安踏體育', 'reason': '國潮崛起，多品牌戰略成功'},
                {'code': '02331', 'name': '李寧', 'reason': '品牌升級，毛利率提升'},
                {'code': '09633', 'name': '農夫山泉', 'reason': '飲料龍頭，現金流強勁'}
            ])
        
        return potential_stocks
    
    def generate_scan_report(self):
        """生成掃描報告"""
        print(f"\n{'='*70}")
        print(f"🎯 潛力股發現系統報告")
        print(f"{'='*70}")
        print(f"掃描時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"掃描條件: {len(self.scan_config['scan_criteria'])} 項")
        print(f"{'='*70}")
        
        total_potential = 0
        reports = []
        
        # 按類別掃描
        for category, enabled in self.scan_config['scan_criteria'].items():
            if enabled and category in self.potential_stocks_db:
                stocks = self.potential_stocks_db[category]
                total_potential += len(stocks)
                
                print(f"\n📈 {self.get_category_name(category)} ({len(stocks)}隻):")
                print("-" * 70)
                
                for stock in stocks:
                    print(f"  {stock['code']} - {stock['name']}")
                    print(f"     價格: HKD {stock['price']:.2f} ({stock['change']})")
                    print(f"     行業: {stock['sector']}")
                    print(f"     理由: {stock['reason']}")
                    print()
                
                reports.append({
                    'category': category,
                    'count': len(stocks),
                    'stocks': stocks
                })
        
        # 按行業掃描
        print(f"\n{'='*70}")
        print(f"🏢 按行業掃描潛力股")
        print(f"{'='*70}")
        
        sector_reports = []
        for sector in self.scan_config['sectors']:
            stocks = self.scan_by_sector(sector)
            if stocks:
                print(f"\n{sector}行業:")
                for stock in stocks[:3]:  # 顯示前3隻
                    print(f"  {stock['code']} - {stock['name']}: {stock['reason']}")
                
                sector_reports.append({
                    'sector': sector,
                    'count': len(stocks),
                    'stocks': stocks[:5]  # 保存前5隻
                })
        
        # 生成投資建議
        print(f"\n{'='*70}")
        print(f"💡 投資建議")
        print(f"{'='*70}")
        
        recommendations = self.generate_recommendations(reports, sector_reports)
        for rec in recommendations:
            print(f"{rec}")
        
        # 保存報告
        self.save_scan_report(reports, sector_reports, total_potential)
        
        print(f"\n{'='*70}")
        print(f"✅ 潛力股掃描完成")
        print(f"   發現潛力股: {total_potential} 隻")
        print(f"   掃描行業: {len(sector_reports)} 個")
        print(f"{'='*70}")
        
        return {
            'total_potential': total_potential,
            'category_reports': reports,
            'sector_reports': sector_reports,
            'recommendations': recommendations
        }
    
    def get_category_name(self, category):
        """獲取類別名稱"""
        names = {
            'technical_breakout': '技術突破股',
            'undervalued': '價值低估股',
            'high_dividend': '高股息股',
            'sector_leader': '行業龍頭股',
            'recent_news': '近期利好股',
            'volume_spike': '成交量暴增股'
        }
        return names.get(category, category)
    
    def generate_recommendations(self, category_reports, sector_reports):
        """生成投資建議"""
        recommendations = []
        
        # 分析當前市場
        recommendations.append("📊 市場分析:")
        recommendations.append("  1. 港股估值處於歷史低位，長期投資價值顯現")
        recommendations.append("  2. 科技股經過深度調整，優質公司出現買入機會")
        recommendations.append("  3. 高息股在加息環境下吸引力增加")
        
        # 具體建議
        recommendations.append("\n🎯 具體投資建議:")
        
        # 檢查各類別
        for report in category_reports:
            category = report['category']
            count = report['count']
            
            if count > 0:
                if category == 'undervalued':
                    recommendations.append(f"  1. 價值低估股 ({count}隻): 適合價值投資者，風險較低")
                elif category == 'high_dividend':
                    recommendations.append(f"  2. 高股息股 ({count}隻): 適合收息投資者，現金流穩定")
                elif category == 'technical_breakout':
                    recommendations.append(f"  3. 技術突破股 ({count}隻): 適合趨勢交易者，動能強勁")
        
        # 行業建議
        recommendations.append("\n🏢 行業配置建議:")
        tech_count = sum(1 for r in sector_reports if r['sector'] == '科技')
        finance_count = sum(1 for r in sector_reports if r['sector'] == '金融')
        
        if tech_count > 0:
            recommendations.append("  1. 科技股: 精選優質龍頭，分批布局")
        if finance_count > 0:
            recommendations.append("  2. 金融股: 加息受益，估值修復機會")
        
        recommendations.append("  3. 消費股: 內需復甦，品牌升級機會")
        recommendations.append("  4. 醫藥股: 創新驅動，長期成長")
        
        # 風險提示
        recommendations.append("\n⚠️  風險提示:")
        recommendations.append("  1. 市場波動風險，建議分批買入")
        recommendations.append("  2. 個股選擇風險，做好基本面研究")
        recommendations.append("  3. 流動性風險，關注成交量")
        
        return recommendations
    
    def save_scan_report(self, category_reports, sector_reports, total_potential):
        """保存掃描報告"""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'scan_config': self.scan_config,
            'summary': {
                'total_potential_stocks': total_potential,
                'categories_scanned': len(category_reports),
                'sectors_scanned': len(sector_reports)
            },
            'category_findings': category_reports,
            'sector_findings': sector_reports
        }
        
        # 保存文件
        report_file = f"/Users/gordonlui/.openclaw/workspace/potential_stocks_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 潛力股掃描報告已保存: {report_file}")
        except Exception as e:
            print(f"❌ 保存報告失敗: {e}")
    
    def get_top_picks(self, count=5):
        """獲取精選潛力股"""
        all_stocks = []
        for category, stocks in self.potential_stocks_db.items():
            for stock in stocks:
                stock['category'] = category
                all_stocks.append(stock)
        
        # 簡單排序（可按更多指標排序）
        top_picks = sorted(all_stocks, key=lambda x: self.calculate_score(x))[:count]
        
        return top_picks
    
    def calculate_score(self, stock):
        """計算股票評分（模擬）"""
        score = 50  # 基礎分
        
        # 根據類別加分
        category_bonus = {
            'technical_breakout': 20,
            'undervalued': 15,
            'high_dividend': 10,
            'sector_leader': 25,
            'recent_news': 15
        }
        
        if stock['category'] in category_bonus:
            score += category_bonus[stock['category']]
        
        # 根據行業加分
        sector_bonus = {
            '科技': 10,
            '金融': 5,
            '醫藥': 15,
            '新能源': 20
        }
        
        if stock.get('sector') in sector_bonus:
            score += sector_bonus[stock['sector']]
        
        return score

def main():
    """主函數"""
    print("🚀 啟動潛力股發現系統...")
    
    try:
        # 創建掃描器
        scanner = PotentialStocksScanner()
        
        # 生成掃描報告
        report = scanner.generate_scan_report()
        
        # 顯示精選潛力股
        print(f"\n{'='*70}")
        print(f"🏆 精選潛力股 (Top 5)")
        print(f"{'='*70}")
        
        top_picks = scanner.get_top_picks(5)
        for i, stock in enumerate(top_picks, 1):
            print(f"{i}. {stock['code']} - {stock['name']}")
            print(f"   價格: HKD {stock['price']:.2f}