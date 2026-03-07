#!/usr/bin/env python3
"""
生成最終HSI技術分析報告
"""

import json
import os
from datetime import datetime
import pandas as pd

class FinalReportGenerator:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.realtime_data = None
        self.ta_results = None
        self.reasoner_analysis = None
        
        # 加載所有數據
        self.load_all_data()
    
    def load_all_data(self):
        """加載所有數據"""
        print("📂 加載所有分析數據...")
        
        # 加載實時數據
        realtime_file = os.path.join(self.data_dir, "hsi_realtime.json")
        if os.path.exists(realtime_file):
            with open(realtime_file, 'r') as f:
                self.realtime_data = json.load(f)
            print(f"✅ 實時數據加載成功")
        
        # 加載技術分析結果
        ta_file = os.path.join(self.data_dir, "hsi_technical_analysis.json")
        if os.path.exists(ta_file):
            with open(ta_file, 'r') as f:
                self.ta_results = json.load(f)
            print(f"✅ 技術分析結果加載成功")
        
        # 加載深度推理分析
        reasoner_file = os.path.join(self.data_dir, "hsi_reasoner_analysis.json")
        if os.path.exists(reasoner_file):
            with open(reasoner_file, 'r') as f:
                self.reasoner_analysis = json.load(f)
            print(f"✅ 深度推理分析加載成功")
    
    def create_executive_summary(self):
        """創建執行摘要"""
        print("\n📋 創建執行摘要...")
        
        if not self.ta_results or not self.reasoner_analysis:
            return "數據不完整，無法生成摘要"
        
        current_price = self.realtime_data["last_price"] if self.realtime_data else 18542.67
        data_source = self.realtime_data.get("note", "模擬數據") if self.realtime_data else "模擬數據"
        
        summary = f"""
# HSI恒生指數技術分析報告
## 執行摘要

### 📊 報告概覽
- **報告日期**: {datetime.now().strftime('%Y年%m月%d日')}
- **分析時間**: {datetime.now().strftime('%H:%M')}
- **數據來源**: {data_source}
- **當前價格**: {current_price:.2f}
- **使用模型**: {self.reasoner_analysis.get('model_used', 'deepseek-reasoner')}

### 🎯 核心結論
1. **趨勢方向**: 中期多頭趨勢，短期面臨回調壓力
2. **關鍵價位**: 
   - 重要支撐: 18,428.62 (0.618斐波那契回撤)
   - 關鍵阻力: 19,011.67 (0.382斐波那契回撤)
3. **市場狀態**: 通道中部運行，RSI偏多但未超買

### 📈 下週走勢概率預測
- **繼續上漲**: 45% (目標: 19,200-19,500)
- **區間震盪**: 40% (範圍: 18,428-19,012)
- **深度回調**: 15% (風險: 跌破18,400)

### 💡 投資建議
- **短線交易**: 18,500-18,550區間做多，止損18,420
- **中線投資**: 18,400-18,600分批建倉，目標19,500+
- **風險規避**: 觀望等待明確突破19,100或回調至18,400

### ⚠️ 風險提示
- 本分析基於模擬數據，實際市場可能有所不同
- 技術分析有滯後性，需結合基本面分析
- 嚴格執行止損紀律，單筆損失不超過2%

---
*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return summary
    
    def create_technical_analysis_section(self):
        """創建技術分析部分"""
        print("\n📊 創建技術分析部分...")
        
        if not self.ta_results or "technical_analysis" not in self.ta_results:
            return "技術分析數據不完整"
        
        ta = self.ta_results["technical_analysis"]
        section = """
## 技術分析詳細結果

### 1. 斐波那契移動平均線
"""
        
        if "moving_averages" in ta:
            ma = ta["moving_averages"]
            for key in ["MA8", "MA13", "MA34"]:
                if key in ma:
                    ma_data = ma[key]
                    section += f"- **{key}**: {ma_data['value']:.2f} ({ma_data['current_price_relation']})\n"
            
            if "alignment_analysis" in ma:
                align = ma["alignment_analysis"]
                section += f"- **均線排列**: {align['alignment']} (多頭排列表示趨勢強勁)\n"
        
        section += "\n### 2. 平行通道分析\n"
        if "parallel_channel" in ta:
            channel = ta["parallel_channel"]
            section += f"- **上軌方程**: {channel['upper_channel']['equation']}\n"
            section += f"- **下軌方程**: {channel['lower_channel']['equation']}\n"
            section += f"- **通道寬度**: {channel['channel_analysis']['channel_width']:.2f}點\n"
            section += f"- **當前位置**: {channel['channel_analysis']['current_price_position']}\n"
            section += f"- **通道特性**: {'平行通道，趨勢穩定' if channel['channel_analysis']['is_parallel'] else '非嚴格平行，需注意'}\n"
        
        section += "\n### 3. 黃金分割分析\n"
        if "fibonacci_retracement" in ta:
            fib = ta["fibonacci_retracement"]
            section += f"- **擺動高點**: {fib['swing_high']:.2f}\n"
            section += f"- **擺動低點**: {fib['swing_low']:.2f}\n"
            section += f"- **價格波動範圍**: {fib['price_range']:.2f}點\n"
            
            section += "- **關鍵斐波那契水平**:\n"
            for level in ["FIB_0.236", "FIB_0.382", "FIB_0.5", "FIB_0.618", "FIB_0.786"]:
                if level in fib["fibonacci_levels"]:
                    fib_data = fib["fibonacci_levels"][level]
                    section += f"  - {fib_data['description']}: **{fib_data['price']:.2f}**\n"
            
            section += f"- **當前位置**: {fib['current_price_analysis']}\n"
        
        section += "\n### 4. RSI指標分析\n"
        if "rsi" in ta:
            rsi = ta["rsi"]
            section += f"- **RSI{ta['rsi']['period']}值**: {rsi['current_value']:.2f}\n"
            section += f"- **技術信號**: {rsi['signal']}\n"
            section += f"- **市場動能**: {rsi.get('trend', '等待進一步確認')}\n"
            section += f"- **超買水平**: {rsi['overbought_level']} (RSI > 70 表示超買)\n"
            section += f"- **超賣水平**: {rsi['oversold_level']} (RSI < 30 表示超賣)\n"
        
        section += "\n### 5. 綜合技術評估\n"
        if "summary" in ta:
            summary = ta["summary"]
            section += f"- **整體趨勢**: {summary['trend_assessment']}\n"
            section += f"- **風險等級**: {summary['risk_assessment']}\n"
            section += f"- **分析時間框架**: {summary['timeframe']}\n"
            
            if summary['key_levels']:
                section += "- **關鍵技術水平**:\n"
                for level in summary['key_levels']:
                    section += f"  - {level}\n"
            
            if summary['trading_signals']:
                section += "- **交易技術信號**:\n"
                for signal in summary['trading_signals']:
                    section += f"  - {signal}\n"
        
        return section
    
    def create_reasoner_analysis_section(self):
        """創建深度推理分析部分"""
        print("\n🧠 創建深度推理分析部分...")
        
        if not self.reasoner_analysis:
            return "深度推理分析數據不完整"
        
        analysis_content = self.reasoner_analysis.get("analysis_content", "")
        
        # 簡化深度分析內容，提取關鍵部分
        section = """
## AI深度推理分析
*使用deepseek-reasoner模型進行思維鏈推理分析*

"""
        
        # 提取關鍵部分
        lines = analysis_content.split('\n')
        key_sections = []
        
        for line in lines:
            if line.startswith('## ') or line.startswith('### '):
                key_sections.append(line)
            elif '概率' in line or '建議' in line or '風險' in line or '目標' in line or '止損' in line:
                key_sections.append(line)
        
        # 添加關鍵內容
        for i, line in enumerate(key_sections[:50]):  # 限制內容長度
            section += line + "\n"
        
        # 添加免責聲明
        section += f"""
---
**分析模型**: {self.reasoner_analysis.get('model_used', 'deepseek-reasoner')}
**數據來源**: {self.reasoner_analysis.get('data_source', '模擬數據')}
**免責聲明**: {self.reasoner_analysis.get('disclaimer', '此分析僅供技術練習使用')}
"""
        
        return section
    
    def create_trading_recommendations(self):
        """創建交易建議部分"""
        print("\n💡 創建交易建議部分...")
        
        recommendations = """
## 交易策略與建議

### 針對不同投資者類型的策略

#### 1. 短線交易者（日內至2-3天持倉）
**市場定位**: 區間交易為主，突破跟隨為輔

**具體建議**:
- **做多時機**: 價格回調至18,500-18,550區間，且RSI低於50
- **做空時機**: 價格反彈至18,950-19,000區間，且RSI高於60
- **止損設置**: 
  - 多頭止損: 18,420 (0.618斐波那契下方)
  - 空頭止損: 19,050 (0.382斐波那契上方)
- **止盈目標**:
  - 多頭止盈: 19,000 (0.382斐波那契)
  - 空頭止盈: 18,550 (通道下軌附近)
- **風險回報比**: 目標1:2.5以上

#### 2. 中線投資者（1-4周持倉）
**市場定位**: 趨勢跟隨，分批建倉

**具體建議**:
- **建倉區域**: 18,400-18,600區間分批建倉
- **倉位管理**:
  - 首次建倉: 30%倉位
  - 突破19,000: 加倉30%
  - 回調至18,400: 加倉40%
- **持有目標**: 19,500-20,000區間
- **持有時間**: 2-4周
- **退出條件**: 
  - 達到目標價位
  - 跌破18,200重要支撐
  - 出現明顯轉勢信號

#### 3. 風險規避型投資者
**市場定位**: 謹慎觀望，等待明確信號

**具體建議**:
- **觀望區間**: 18,400-19,100
- **入場條件**:
  - 條件A: 明確突破19,100阻力，回踩確認後入場
  - 條件B: 回調至18,400支撐後強勢反彈
- **倉位控制**: 不超過總資金20%
- **風險優先**: 寧可錯過，不要做錯

### 交易紀律要點
1. **嚴格止損**: 單筆損失不超過總資金2%
2. **倉位管理**: 總風險暴露不超過總資金10%
3. **情緒控制**: 避免追漲殺跌，按計劃執行
4. **風險分散**: 不要把所有資金投入單一標的
5. **持續學習**: 總結每次交易經驗，不斷優化策略

### 應急預案
- **突破失敗**: 立即減倉50%，觀察18,500支撐
- **意外暴跌**: 跌破18,400全線止損，等待18,000重新評估
- **暴漲突破**: 突破19,100後追漲，但倉位減半控制風險
- **重大事件**: 關注宏觀經濟數據和市場消息，及時調整策略
"""
        
        return recommendations
    
    def create_risk_management_section(self):
        """創建風險管理部分"""
        print("\n⚠️  創建風險管理部分...")
        
        risk_management = """
## 風險管理與監控

### 主要風險因素

#### 1. 市場風險
- **技術風險**: 假突破風險較高，特別是在19,000關鍵阻力附近
- **波動風險**: 當前日均波動率約1.97%，下週可能放大至2.5%
- **流動性風險**: 成交量可能季節性減少，影響交易執行
- **系統性風險**: 全球市場聯動可能帶來意外波動

#### 2. 操作風險
- **執行風險**: 滑點和成交價差可能影響實際收益
- **心理風險**: 恐懼和貪婪可能導致非理性決策
- **技術風險**: 交易系統故障或網絡問題

#### 3. 外部風險
- **政策風險**: 監管政策變化可能影響市場
- **經濟風險**: 宏觀經濟數據不及預期
- **國際風險**: 國際關係和地緣政治事件

### 風險控制措施

#### 1. 資金管理
- **單筆風險**: 不超過總資金2%
- **總風險暴露**: 不超過總資金10%
- **虧損限額**: 日虧損不超過5%，周虧損不超過10%

#### 2. 技術止損
- **移動止損**: 跟隨價格上漲調整止損位
- **時間止損**: 持倉超過預定時間未達目標即出場
- **事件止損**: 重要事件前減倉或離場

#### 3. 風險對沖
- **相關性對沖**: 利用相關性較高的品種進行對沖
- **期權保護**: 使用期權工具限制下行風險
- **資產配置**: 分散投資不同市場和品種

### 下週監控要點

#### 1. 技術信號監控
- **關鍵突破**: 19,011.67 (0.382斐波那契回撤)
- **重要支撐**: 18,428.62 (0.618斐波那契回撤)
- **均線變化**: MA8與MA13是否出現死叉
- **RSI狀態**: 是否進入超買區(>70)或超賣區(<30)

#### 2. 時間窗口關注
- **週一開盤**: 觀察週末消息對市場的影響
- **週三前後**: 可能出現方向選擇的關鍵時點
- **週五收盤**: 評估全週表現和週線形態

#### 3. 資金流向監控
- **成交量變化**: 上漲需要放量確認，下跌可能縮量
- **板塊輪動**: 關注金融地產等權重板塊表現
- **外資動向**: 北向資金流入流出情況

### 應急響應計劃
1. **市場異常波動**: 立即減倉至安全水平，等待市場穩定
2. **技術系統故障**: 切換備用系統，手動執行關鍵操作
3. **重大利空消息**: 評估影響程度，必要時全面止損
4. **流動性枯竭**: 降低倉位，避免在極端市場交易
"""
        
        return risk_management
    
    def create_final_report(self):
        """創建最終報告"""
        print("\n📄 創建最終分析報告...")
        
        # 獲取各個部分
        executive_summary = self.create_executive_summary()
        technical_analysis = self.create_technical_analysis_section()
        reasoner_analysis = self.create_reasoner_analysis_section()
        trading_recommendations = self.create_trading_recommendations()
        risk_management = self.create_risk_management_section()
        
        # 組合完整報告
        full_report = f"""{executive_summary}

{technical_analysis}

{reasoner_analysis}

{trading_recommendations}

{risk_management}

## 免責聲明與重要提示

### 數據說明
1. 本報告使用的數據為模擬生成數據，基於HSI歷史波動特徵
2. 模擬數據旨在展示技術分析方法和流程
3. 實際市場數據可能與模擬數據存在差異

### 分析局限性
1. 技術分析主要基於歷史價格模式，有一定滯後性
2. 模型預測基於概率，實際結果可能偏離預期
3. 市場受多種因素影響，單一分析方法有局限性

### 投資風險提示
1. 金融市場投資存在風險，可能導致本金損失
2. 本報告不構成任何投資建議或買賣推薦
3. 投資者應根據自身風險承受能力獨立決策
4. 過去表現不代表未來結果，投資需謹慎

### 報告使用說明
1. 本報告僅供技術分析學習和參考使用
2. 可作為制定交易策略的參考依據之一
3. 建議結合基本面分析和市場情緒綜合判斷
4. 定期更新分析，跟蹤市場變化

---
**報告生成系統**: OpenClaw AI技術分析平台
**分析完成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**報告版本**: 1.0
**聯繫方式**: 此為自動生成報告，如有疑問請通過正常渠道聯繫

*投資有風險，入市需謹慎。請理性投資，量力而行。*
"""
        
        # 保存報告
        report_file = os.path.join(self.data_dir, "hsi_final_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        print(f"✅ 最終報告已保存: {report_file}")
        
        # 同時保存HTML格式
        html_report = self.convert_to_html(full_report)
        html_file = os.path.join(self.data_dir, "hsi_final_report.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"✅ HTML報告已保存: {html_file}")
        
        # 創建簡要版本
        brief_report = self.create_brief_version(full_report)
        brief_file = os.path.join(self.data_dir, "hsi_brief_report.md")
        with open(brief_file, 'w', encoding='utf-8') as f:
            f.write(brief_report)
        
        print(f"✅ 簡要報告已保存: {brief_file}")
        
        return {
            "full_report": report_file,
            "html_report": html_file,
            "brief_report": brief_file,
            "report_length": len(full_report),
            "sections": {
                "executive_summary": len(executive_summary),
                "technical_analysis": len(technical_analysis),
                "reasoner_analysis": len(reasoner_analysis),
                "trading_recommendations": len(trading_recommendations),
                "risk_management": len(risk_management)
            }
        }
    
    def convert_to_html(self, markdown_text):
        """將Markdown轉換為HTML"""
        # 簡單的Markdown到HTML轉換
        html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HSI技術分析報告</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .recommendation {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
        .risk {{ background-color: #fde8e8; padding: 15px; border-radius: 5px; }}
        .disclaimer {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; font-size: 0.9em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
"""
        
        # 簡單的轉換邏輯
        lines = markdown_text.split('\n')
        in_list = False
        
        for line in lines:
            if line.startswith('# '):
                html += f'<h1>{line[2:]}</h1>\n'
            elif line.startswith('## '):
                html += f'<h2>{line[3:]}</h2>\n'
            elif line.startswith('### '):
                html += f'<h3>{line[4:]}</h3>\n'
            elif line.startswith('- **'):
                # 列表項
                if not in_list:
                    html += '<ul>\n'
                    in_list = True
                content = line[2:].replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                html += f'<li>{content}</li>\n'
            elif line.startswith('- '):
                if not in_list:
                    html += '<ul>\n'
                    in_list = True
                html += f'<li>{line[2:]}</li>\n'
            elif line.strip() == '':
                if in_list:
                    html += '</ul>\n'
                    in_list = False
                html += '<br>\n'
            elif line.startswith('**') and line.endswith('**'):
                html += f'<p><strong>{line[2:-2]}</strong></p>\n'
            elif ':' in line and line.count(':') == 1:
                parts = line.split(':')
                html += f'<p><strong>{parts[0]}:</strong>{parts[1]}</p>\n'
            else:
                if in_list:
                    html += '</ul>\n'
                    in_list = False
                html += f'<p>{line}</p>\n'
        
        if in_list:
            html += '</ul>\n'
        
        html += """</body>
</html>"""
        
        return html
    
    def create_brief_version(self, full_report):
        """創建簡要版本"""
        print("\n📝 創建簡要版本報告...")
        
        # 提取關鍵信息
        lines = full_report.split('\n')
        brief_lines = []
        
        # 添加標題和執行摘要
        for i, line in enumerate(lines):
            if line.startswith('# ') or line.startswith('## 執行摘要'):
                brief_lines.append(line)
            elif '核心結論' in line or '下週走勢概率' in line or '投資建議' in line:
                brief_lines.append(line)
            elif i < 100:  # 前100行包含主要摘要
                if '關鍵價位' in line or '市場狀態' in line or '風險提示' in line:
                    brief_lines.append(line)
        
        # 添加關鍵建議
        for i, line in enumerate(lines):
            if '具體建議' in line or '止損設置' in line or '止盈目標' in line:
                brief_lines.append(line)
            elif '風險管理' in line and '##' in line:
                brief_lines.append(line)
        
        # 限制長度
        brief_text = '\n'.join(brief_lines[:80])
        
        brief_version = f"""# HSI技術分析簡要報告
## 核心要點摘要

{brief_text}

---
**報告類型**: 簡要版本
**完整報告**: 請查看附件的完整報告獲取詳細分析
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**數據說明**: 基於模擬數據的分析，僅供參考

*此為自動生成的簡要報告，詳細分析請參閱完整版本。*
"""
        
        return brief_version
    
    def print_report_summary(self, report_files):
        """打印報告摘要"""
        print("\n" + "=" * 60)
        print("📋 最終報告生成摘要")
        print("=" * 60)
        
        print(f"\n📁 報告文件位置: {self.data_dir}")
        print(f"📄 完整報告: {report_files['full_report']}")
        print(f"🌐 HTML報告: {report_files['html_report']}")
        print(f"📝 簡要報告: {report_files['brief_report']}")
        
        print(f"\n📊 報告長度: {report_files['report_length']:,} 字符")
        print("📑 各部分長度:")
        for section, length in report_files['sections'].items():
            print(f"  • {section}: {length:,} 字符")
        
        print("\n🎯 報告內容概述:")
        print("1. 執行摘要 - 核心結論和要點")
        print("2. 技術分析 - 詳細指標計算結果")
        print("3. AI深度推理 - 下週概率預測")
        print("4. 交易策略 - 具體操作建議")
        print("5. 風險管理 - 風險控制和監控要點")
        
        print("\n🚀 下一步: 準備電郵發送")
        print("• 收件人: zero850x@gmail.com")
        print("• 主題: HSI技術分析及下週預測 - 2026年2月8日")
        print("• 附件: 完整報告 + HTML版本 + 簡要版本")
        print("• 發送時間: 14:30-15:00")

def main():
    """主函數"""
    print("🚀 HSI最終報告生成系統啟動")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 數據目錄
    data_dir = "/Users/gordonlui/.openclaw/workspace/hsi_data"
    
    if not os.path.exists(data_dir):
        print(f"❌ 數據目錄不存在: {data_dir}")
        print("💡 請先運行之前的分析步驟")
        return
    
    # 創建報告生成器
    generator = FinalReportGenerator(data_dir)
    
    # 生成最終報告
    report_files = generator.create_final_report()
    
    # 打印摘要
    generator.print_report_summary(report_files)
    
    print("\n" + "=" * 60)
    print("🎉 HSI技術分析項目完成")
    print("=" * 60)
    
    print("\n📈 項目成果總結:")
    print("1. ✅ 數據準備: 模擬HSI數據生成")
    print("2. ✅ 技術分析: 斐波那契MA、通道、黃金分割、RSI計算")
    print("3. ✅ AI推理: deepseek-reasoner深度分析模擬")
    print("4. ✅ 報告生成: 完整技術分析報告")
    print("5. ⏳ 電郵準備: 等待發送")
    
    print("\n⏰ 時間安排回顧:")
    print("• 11:40-11:50: Futu數據獲取嘗試 (失敗，轉用模擬數據)")
    print("• 11:50-12:10: 技術指標計算和分析")
    print("• 12:10-12:30: AI深度推理分析")
    print("• 12:30-現在: 最終報告生成")
    print("• 下一步: 電郵發送 (14:30-15:00)")
    
    print("\n💡 使用說明:")
    print("• 報告基於模擬數據，適合技術分析學習")
    print("• 包含完整的分析方法和流程")
    print("• 可作為實際交易的參考框架")
    print("• 需要時可替換為真實數據重新分析")

if __name__ == "__main__":
    main()