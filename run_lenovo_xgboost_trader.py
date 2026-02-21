#!/usr/bin/env python3
"""
立即運行聯想集團XGBoost交易分析
"""

import sys
import json
from datetime import datetime
sys.path.append('/Users/gordonlui/.openclaw/workspace')

# 導入必要的模塊
try:
    from validated_xgboost_predictor import ValidatedXGBoostPredictor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

def analyze_lenovo_with_xgboost():
    """分析聯想集團使用XGBoost"""
    print(f"\n{'='*60}")
    print(f"📱 聯想集團即時XGBoost分析")
    print(f"{'='*60}")
    
    # 配置
    config = {
        'stock_code': '00992',
        'buy_price': 8.59,
        'current_position': 26000,
        'golden_ratio_levels': {
            '382': 8.89,
            '500': 9.17,
            '618': 9.55
        }
    }
    
    # 獲取當前價格（模擬）
    current_price = 9.17  # 從之前的報告中獲取
    
    print(f"💰 當前價格: HKD {current_price:.2f}")
    
    # 計算盈虧
    profit_pct = ((current_price - config['buy_price']) / config['buy_price']) * 100
    profit_amount = (current_price - config['buy_price']) * config['current_position']
    
    print(f"📈 當前盈虧: {profit_pct:+.2f}%")
    print(f"💵 盈利金額: HKD {profit_amount:+,.2f}")
    
    # 分析黃金分割位
    golden_levels = config['golden_ratio_levels']
    current_level = None
    
    if current_price < golden_levels['382']:
        current_level = 'BELOW_382'
    elif current_price < golden_levels['500']:
        current_level = 'BETWEEN_382_500'
    elif current_price < golden_levels['618']:
        current_level = 'BETWEEN_500_618'
    else:
        current_level = 'ABOVE_618'
    
    print(f"📊 黃金分割位: {current_level}")
    print(f"  38.2%: HKD {golden_levels['382']:.2f}")
    print(f"  50.0%: HKD {golden_levels['500']:.2f} ⚠️ 當前測試中")
    print(f"  61.8%: HKD {golden_levels['618']:.2f}")
    
    # XGBoost預測
    if XGBOOST_AVAILABLE:
        try:
            predictor = ValidatedXGBoostPredictor()
            prediction = predictor.predict_stock(config['stock_code'], current_price)
            
            xgb_prob = prediction.get('probability', 0.5)
            xgb_signal = prediction.get('signal', 'HOLD')
            xgb_confidence = prediction.get('confidence', 0.5)
            
            print(f"\n🤖 XGBoost預測:")
            print(f"  上漲概率: {xgb_prob:.2%}")
            print(f"  交易信號: {xgb_signal}")
            print(f"  信心程度: {xgb_confidence:.2%}")
            
            # 生成交易建議
            if xgb_prob >= 0.65:
                action = 'BUY'
                strength = 'STRONG' if xgb_prob >= 0.75 else 'MODERATE'
                reason = f"XGBoost高概率上漲 ({xgb_prob:.2%})"
            elif xgb_prob <= 0.35:
                action = 'SELL'
                strength = 'STRONG' if xgb_prob <= 0.25 else 'MODERATE'
                reason = f"XGBoost低概率上漲 ({xgb_prob:.2%})"
            else:
                action = 'HOLD'
                strength = 'NEUTRAL'
                reason = f"XGBoost中性區域 ({xgb_prob:.2%})"
            
            print(f"\n🎯 交易建議:")
            print(f"  建議動作: {action} ({strength})")
            print(f"  理由: {reason}")
            
            # 結合黃金分割位
            if current_level == 'BETWEEN_500_618' and action == 'BUY':
                print(f"  💡 提示: 價格在關鍵支撐位$9.17附近，可考慮輕倉買入")
            elif current_level == 'ABOVE_618' and action == 'SELL':
                print(f"  💡 提示: 價格接近阻力位$9.55，可考慮獲利了結")
            
        except Exception as e:
            print(f"❌ XGBoost預測錯誤: {e}")
    else:
        print("⚠️  XGBoost系統不可用，使用基礎分析")
        
        # 基礎分析
        if current_price <= golden_levels['500']:
            action = 'BUY'
            strength = 'MODERATE'
            reason = f"價格在支撐位${golden_levels['500']:.2f}附近"
        elif current_price >= golden_levels['618']:
            action = 'SELL'
            strength = 'MODERATE'
            reason = f"價格接近阻力位${golden_levels['618']:.2f}"
        else:
            action = 'HOLD'
            strength = 'NEUTRAL'
            reason = "價格在黃金分割中性區域"
        
        print(f"\n🎯 基礎交易建議:")
        print(f"  建議動作: {action} ({strength})")
        print(f"  理由: {reason}")
    
    # 風險管理建議
    print(f"\n⚠️  風險管理:")
    print(f"  止損位: HKD {config['buy_price'] * 0.98:.2f} (-2%)")
    print(f"  止盈位: HKD {config['buy_price'] * 1.08:.2f} (+8%)")
    
    if profit_pct >= 8:
        print(f"  ✅ 已達到止盈目標，建議考慮獲利了結")
    elif profit_pct <= -2:
        print(f"  🚨 已觸及止損位，建議嚴格執行止損")
    
    # 生成報告
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stock_code': config['stock_code'],
        'current_price': current_price,
        'buy_price': config['buy_price'],
        'profit_pct': profit_pct,
        'profit_amount': profit_amount,
        'current_position': config['current_position'],
        'golden_ratio_level': current_level,
        'golden_levels': golden_levels,
        'action': action if 'action' in locals() else 'HOLD',
        'strength': strength if 'strength' in locals() else 'NEUTRAL',
        'reason': reason if 'reason' in locals() else '基礎分析'
    }
    
    # 保存報告
    report_file = f"/Users/gordonlui/.openclaw/workspace/lenovo_instant_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 分析報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ 分析完成")
    print(f"{'='*60}")
    
    return report

def main():
    """主函數"""
    print("🚀 啟動聯想集團即時XGBoost分析...")
    
    try:
        report = analyze_lenovo_with_xgboost()
        
        # 顯示總結
        print(f"\n📋 分析總結:")
        print(f"  股票: {report['stock_code']}")
        print(f"  價格: HKD {report['current_price']:.2f}")
        print(f"  盈虧: {report['profit_pct']:+.2f}%")
        print(f"  建議: {report['action']} ({report['strength']})")
        print(f"  理由: {report['reason']}")
        
    except Exception as e:
        print(f"❌ 分析過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()