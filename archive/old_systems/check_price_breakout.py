#!/usr/bin/env python3
"""
價格突破檢測系統
專門監控聯想集團(00992)關鍵價位突破
"""

import json
from datetime import datetime
import os

print("=" * 70)
print("🎯 價格突破檢測系統 - 聯想集團(00992)")
print("=" * 70)

class PriceBreakoutDetector:
    """價格突破檢測器"""
    
    def __init__(self):
        self.stock_code = "00992"
        self.key_levels = {
            'golden_618': 9.12,  # 0.618黃金分割位
            'golden_500': 9.00,  # 0.5中心位
            'golden_382': 8.88,  # 0.382黃金分割位
            'current_price': 9.30,  # 當前價格
            'stop_loss': 9.02,  # 止損位
            'target_1': 9.58,  # 目標1 (+3%)
            'target_2': 10.04  # 目標2 (+8%)
        }
        
        self.breakout_history = []
        self.results_dir = '/Users/gordonlui/.openclaw/workspace/breakout_detection'
        os.makedirs(self.results_dir, exist_ok=True)
        
    def get_current_price(self):
        """獲取當前價格"""
        # 嘗試連接富途API
        try:
            import futu as ft
            
            quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
            ret, data = quote_ctx.get_market_snapshot([f"HK.{self.stock_code}"])
            
            if ret == ft.RET_OK and len(data) > 0:
                price = float(data.iloc[0]['last_price'])
                quote_ctx.close()
                return price
            
            quote_ctx.close()
            
        except Exception as e:
            print(f"⚠️  富途API連接失敗: {e}")
        
        # 備用：使用最後已知價格
        return self.key_levels['current_price']
    
    def check_breakouts(self, current_price):
        """檢查價格突破"""
        print(f"\n📊 當前價格: ${current_price:.2f}")
        print(f"📈 關鍵價位:")
        
        breakouts = []
        
        for level_name, level_price in self.key_levels.items():
            if level_name in ['current_price', 'stop_loss', 'target_1', 'target_2']:
                continue
                
            distance = current_price - level_price
            distance_percent = (distance / level_price) * 100
            
            print(f"   {level_name}: ${level_price:.2f} ({distance_percent:+.2f}%)")
            
            # 檢查突破
            if abs(distance_percent) < 1.0:  # 在1%範圍內
                if distance > 0:
                    breakout_type = "突破上方"
                else:
                    breakout_type = "跌破下方"
                
                breakout = {
                    'level': level_name,
                    'level_price': level_price,
                    'current_price': current_price,
                    'distance_percent': distance_percent,
                    'type': breakout_type,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'urgency': '高' if abs(distance_percent) < 0.5 else '中'
                }
                
                breakouts.append(breakout)
                
                print(f"   ⚠️  檢測到{breakout_type}: {level_name}")
        
        return breakouts
    
    def check_stop_loss_target(self, current_price):
        """檢查止損和目標位"""
        alerts = []
        
        # 檢查止損
        if current_price < self.key_levels['stop_loss']:
            alerts.append({
                'type': '止損觸發',
                'level': 'stop_loss',
                'level_price': self.key_levels['stop_loss'],
                'current_price': current_price,
                'distance_percent': (current_price / self.key_levels['stop_loss'] - 1) * 100,
                'action': '立即賣出',
                'urgency': '緊急'
            })
        
        # 檢查目標1
        elif current_price >= self.key_levels['target_1']:
            alerts.append({
                'type': '達到目標1',
                'level': 'target_1',
                'level_price': self.key_levels['target_1'],
                'current_price': current_price,
                'distance_percent': (current_price / self.key_levels['target_1'] - 1) * 100,
                'action': '考慮獲利了結',
                'urgency': '高'
            })
        
        # 檢查目標2
        elif current_price >= self.key_levels['target_2']:
            alerts.append({
                'type': '達到目標2',
                'level': 'target_2',
                'level_price': self.key_levels['target_2'],
                'current_price': current_price,
                'distance_percent': (current_price / self.key_levels['target_2'] - 1) * 100,
                'action': '強烈建議獲利了結',
                'urgency': '非常高'
            })
        
        return alerts
    
    def generate_trading_advice(self, breakouts, alerts):
        """生成交易建議"""
        advice = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock': self.stock_code,
            'current_price': self.get_current_price(),
            'breakouts': breakouts,
            'alerts': alerts,
            'recommendations': []
        }
        
        # 基於突破生成建議
        for breakout in breakouts:
            if breakout['type'] == "突破上方":
                if breakout['level'] == 'golden_618':
                    advice['recommendations'].append({
                        'action': '加倉',
                        'reason': '突破0.618黃金分割位，趨勢轉強',
                        'urgency': '高'
                    })
                elif breakout['level'] == 'golden_500':
                    advice['recommendations'].append({
                        'action': '持有',
                        'reason': '在0.5中心位之上，偏強',
                        'urgency': '中'
                    })
            
            elif breakout['type'] == "跌破下方":
                if breakout['level'] == 'golden_382':
                    advice['recommendations'].append({
                        'action': '減倉',
                        'reason': '跌破0.382黃金分割位，技術轉弱',
                        'urgency': '高'
                    })
                elif breakout['level'] == 'golden_500':
                    advice['recommendations'].append({
                        'action': '謹慎持有',
                        'reason': '跌破0.5中心位，需觀察',
                        'urgency': '中'
                    })
        
        # 基於警報生成建議
        for alert in alerts:
            advice['recommendations'].append({
                'action': alert['action'],
                'reason': f"{alert['type']}: ${alert['level_price']:.2f}",
                'urgency': alert['urgency']
            })
        
        # 如果沒有特別情況，給出一般建議
        if not advice['recommendations']:
            current_price = self.get_current_price()
            if current_price > self.key_levels['golden_618']:
                advice['recommendations'].append({
                    'action': '持有',
                    'reason': '價格在0.618之上，趨勢良好',
                    'urgency': '低'
                })
            elif current_price > self.key_levels['golden_500']:
                advice['recommendations'].append({
                    'action': '持有觀察',
                    'reason': '價格在0.5-0.618之間，震盪',
                    'urgency': '低'
                })
            else:
                advice['recommendations'].append({
                    'action': '謹慎持有',
                    'reason': '價格在0.5之下，偏弱',
                    'urgency': '中'
                })
        
        return advice
    
    def save_results(self, breakouts, alerts, advice):
        """保存結果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存突破記錄
        if breakouts:
            breakout_file = f"{self.results_dir}/breakouts_{timestamp}.json"
            with open(breakout_file, 'w') as f:
                json.dump(breakouts, f, indent=2, ensure_ascii=False)
            print(f"💾 突破記錄已保存: {breakout_file}")
        
        # 保存警報記錄
        if alerts:
            alert_file = f"{self.results_dir}/alerts_{timestamp}.json"
            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
            print(f"💾 警報記錄已保存: {alert_file}")
        
        # 保存建議
        advice_file = f"{self.results_dir}/advice_{timestamp}.json"
        with open(advice_file, 'w') as f:
            json.dump(advice, f, indent=2, ensure_ascii=False)
        print(f"💾 交易建議已保存: {advice_file}")
        
        # 保存到歷史
        history_file = f"{self.results_dir}/breakout_history.json"
        history_data = []
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        
        history_data.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'breakouts': breakouts,
            'alerts': alerts,
            'advice': advice
        })
        
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        return advice_file
    
    def send_notification(self, breakouts, alerts, advice):
        """發送通知"""
        print(f"\n📢 通知摘要:")
        
        if breakouts:
            print(f"  突破檢測:")
            for breakout in breakouts:
                print(f"    • {breakout['type']} {breakout['level']} (${breakout['level_price']:.2f})")
        
        if alerts:
            print(f"  警報:")
            for alert in alerts:
                print(f"    • {alert['type']}: {alert['action']}")
        
        if advice['recommendations']:
            print(f"  交易建議:")
            for rec in advice['recommendations']:
                print(f"    • [{rec['urgency']}] {rec['action']}: {rec['reason']}")
        
        # 這裡可以集成Telegram、Email等通知
        # 暫時只打印到控制台
    
    def run(self):
        """運行檢測系統"""
        print(f"股票: HK.{self.stock_code}")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 獲取當前價格
        current_price = self.get_current_price()
        
        # 檢查突破
        breakouts = self.check_breakouts(current_price)
        
        # 檢查止損和目標
        alerts = self.check_stop_loss_target(current_price)
        
        # 生成交易建議
        advice = self.generate_trading_advice(breakouts, alerts)
        
        # 顯示結果
        print(f"\n🎯 檢測結果:")
        
        if breakouts:
            print(f"  發現{len(breakouts)}個突破")
        else:
            print(f"  無突破檢測")
        
        if alerts:
            print(f"  發現{len(alerts)}個警報")
        else:
            print(f"  無警報")
        
        # 保存結果
        advice_file = self.save_results(breakouts, alerts, advice)
        
        # 發送通知
        self.send_notification(breakouts, alerts, advice)
        
        print(f"\n✅ 檢測完成")
        print(f"💾 詳細建議: {advice_file}")
        
        return {
            'breakouts': breakouts,
            'alerts': alerts,
            'advice': advice,
            'advice_file': advice_file
        }

def main():
    """主函數"""
    detector = PriceBreakoutDetector()
    result = detector.run()
    
    print(f"\n{'='*70}")
    print(f"🎯 價格突破檢測系統完成")
    print(f"{'='*70}")
    
    # 如果有緊急情況，特別提示
    urgent_alerts = [a for a in result['alerts'] if a['urgency'] in ['緊急', '非常高']]
    if urgent_alerts:
        print(f"\n🚨 緊急情況！需要立即行動:")
        for alert in urgent_alerts:
            print(f"   • {alert['type']}: {alert['action']}")
    
    print(f"\n💡 使用說明:")
    print(f"   1. 定時運行: 設置Cron任務每5-15分鐘運行")
    print(f"   2. 手動運行: python3 {__file__}")
    print(f"   3. 查看歷史: {detector.results_dir}/breakout_history.json")
    
    print(f"\n✅ 系統準備就緒")
    print("=" * 70)

if __name__ == "__main__":
    main()