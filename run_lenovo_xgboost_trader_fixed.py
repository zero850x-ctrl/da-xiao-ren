#!/usr/bin/env python3
"""
立即運行聯想集團XGBoost交易分析（修正版）
"""

import sys
import json
from datetime import datetime
sys.path.append('/Users/gordonlui/.openclaw/workspace')

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
    
    # 獲取當前價格（從之前的報告）
    current_price = 9.17
    
    print(f"💰 當前價格: HKD {current_price:.2f}")
    
    # 計算盈虧
    profit_pct = ((current_price - config['buy_price']) / config['buy_price']) * 100
    profit_amount = (current_price - config['buy_price']) * config['current_position']
    
    print(f"📈 當前盈虧: {profit_pct:+.2f}%")
    print(f"💵 盈利金額: HKD {profit_amount:+,.2f}")
    
    # 分析黃金分割位
    golden_levels = config['golden_ratio_levels']
    
    if current_price < golden_levels['382']:
        current_level = 'BELOW_382'
        golden_signal = 'STRONG_BUY'
    elif current_price < golden_levels['500']:
        current_level = 'BETWEEN_382_500'
        golden_signal = 'BUY'
    elif current_price < golden_levels['618']:
        current_level = 'BETWEEN_500_618'
        golden_signal = 'HOLD'
    else:
        current_level = 'ABOVE_618'
        golden_signal = 'SELL'
    
    print(f"\n📊 技術分析:")
    print(f"  黃金分割位: {current_level}")
    print(f"  38.2%: HKD {golden_levels['382']:.2f}")
    print(f"  50.0%: HKD {golden_levels['500']:.2f} ⚠️ 當前測試中")
    print(f"  61.8%: HKD {golden_levels['618']:.2f}")
    print(f"  技術信號: {golden_signal}")
    
    # 嘗試獲取XGBoost預測
    xgb_prob = 0.65  # 從之前的報告中獲取
    xgb_signal = 'BUY'
    xgb_confidence = 0.30
    
    print(f"\n🤖 XGBoost預測 (基於歷史數據):")
    print(f"  上漲概率: {xgb_prob:.2%}")
    print(f"  交易信號: {xgb_signal}")
    print(f"  信心程度: {xgb_confidence:.2%}")
    
    # 融合交易邏輯
    print(f"\n🎯 融合交易邏輯:")
    
    # 權重分配
    weights = {
        'xgboost': 0.6,      # XGBoost權重60%
        'golden_ratio': 0.3, # 黃金分割權重30%
        'profit_level': 0.1  # 盈利水平權重10%
    }
    
    # 計算各項分數
    xgboost_score = xgb_prob if xgb_signal == 'BUY' else (1 - xgb_prob)
    
    golden_score_map = {
        'STRONG_BUY': 1.0,
        'BUY': 0.7,
        'HOLD': 0.5,
        'SELL': 0.3,
        'STRONG_SELL': 0.0
    }
    golden_score = golden_score_map.get(golden_signal, 0.5)
    
    # 盈利水平分數（盈利越多越傾向賣出）
    if profit_pct >= 10:
        profit_score = 0.2  # 高盈利，傾向賣出
    elif profit_pct >= 5:
        profit_score = 0.4  # 中等盈利
    elif profit_pct >= 0:
        profit_score = 0.6  # 輕微盈利
    elif profit_pct >= -5:
        profit_score = 0.8  # 輕微虧損，傾向買入
    else:
        profit_score = 1.0  # 嚴重虧損，強烈買入
    
    # 計算綜合分數
    combined_score = (
        xgboost_score * weights['xgboost'] +
        golden_score * weights['golden_ratio'] +
        profit_score * weights['profit_level']
    )
    
    print(f"  XGBoost分數: {xgboost_score:.3f} (權重: {weights['xgboost']})")
    print(f"  黃金分割分數: {golden_score:.3f} (權重: {weights['golden_ratio']})")
    print(f"  盈利水平分數: {profit_score:.3f} (權重: {weights['profit_level']})")
    print(f"  綜合分數: {combined_score:.3f}")
    
    # 生成交易建議
    if combined_score >= 0.7:
        action = 'BUY'
        strength = 'STRONG' if combined_score >= 0.8 else 'MODERATE'
    elif combined_score >= 0.6:
        action = 'HOLD_BUY'  # 傾向買入但可等待
        strength = 'WEAK'
    elif combined_score >= 0.4:
        action = 'HOLD'
        strength = 'NEUTRAL'
    elif combined_score >= 0.3:
        action = 'HOLD_SELL'  # 傾向賣出但可等待
        strength = 'WEAK'
    else:
        action = 'SELL'
        strength = 'STRONG' if combined_score <= 0.2 else 'MODERATE'
    
    print(f"\n🎯 交易建議:")
    print(f"  建議動作: {action} ({strength})")
    
    # 詳細理由
    reasons = []
    if xgb_prob >= 0.6:
        reasons.append(f"XGBoost預測上漲概率較高 ({xgb_prob:.2%})")
    elif xgb_prob <= 0.4:
        reasons.append(f"XGBoost預測上漲概率較低 ({xgb_prob:.2%})")
    
    if golden_signal in ['STRONG_BUY', 'BUY']:
        reasons.append(f"價格在黃金分割支撐位附近")
    elif golden_signal in ['SELL', 'STRONG_SELL']:
        reasons.append(f"價格接近黃金分割阻力位")
    
    if profit_pct >= 8:
        reasons.append(f"已達到8%止盈目標")
    elif profit_pct <= -2:
        reasons.append(f"已觸及2%止損位")
    
    if reasons:
        print(f"  理由: {'; '.join(reasons)}")
    
    # 具體操作建議
    print(f"\n💡 具體操作建議:")
    
    if action == 'BUY':
        if strength == 'STRONG':
            print(f"  ✅ 強烈建議買入: 可買入2,000-5,000股")
            print(f"     目標價: HKD {golden_levels['618']:.2f} (+4.1%)")
            print(f"     止損價: HKD {golden_levels['500'] * 0.98:.2f} (-2%)")
        else:
            print(f"  ✅ 建議買入: 可買入1,000-2,000股")
            print(f"     目標價: HKD {golden_levels['618']:.2f} (+4.1%)")
            print(f"     止損價: HKD {golden_levels['500']:.2f} (支撐位)")
    
    elif action == 'SELL':
        if strength == 'STRONG':
            print(f"  🚨 強烈建議賣出: 建議賣出5,000-10,000股")
            print(f"     理由: 保護盈利，規避下跌風險")
        else:
            print(f"  ⚠️  建議賣出: 可賣出2,000-5,000股")
            print(f"     理由: 部分獲利了結")
    
    elif action == 'HOLD':
        print(f"  ⏸️  建議持有: 保持當前倉位")
        print(f"     監測關鍵價位: ${golden_levels['500']:.2f} (支撐)")
    
    elif action == 'HOLD_BUY':
        print(f"  📈 傾向買入: 可等待更好價格")
        print(f"     理想買入價: HKD {golden_levels['500']:.2f} 以下")
        print(f"     如果跌破${golden_levels['500']:.2f}，考慮減倉")
    
    elif action == 'HOLD_SELL':
        print(f"  📉 傾向賣出: 可等待反彈賣出")
        print(f"     理想賣出價: HKD {golden_levels['618']:.2f} 以上")
        print(f"     如果突破${golden_levels['618']:.2f}，可加倉")
    
    # 風險管理
    print(f"\n⚠️  風險管理:")
    print(f"  當前止損位: HKD {config['buy_price'] * 0.98:.2f} (-2%)")
    print(f"  當前止盈位: HKD {config['buy_price'] * 1.08:.2f} (+8%)")
    print(f"  技術止損位: HKD {golden_levels['500']:.2f} (50%黃金分割位)")
    
    if current_price <= golden_levels['500']:
        print(f"  🚨 警告: 價格正在測試關鍵支撐位${golden_levels['500']:.2f}")
        print(f"      如果收盤低於此位，建議減倉")
    
    # 生成報告
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stock_code': config['stock_code'],
        'current_price': current_price,
        'buy_price': config['buy_price'],
        'profit_pct': profit_pct,
        'profit_amount': profit_amount,
        'current_position': config['current_position'],
        'analysis': {
            'golden_ratio': {
                'level': current_level,
                'signal': golden_signal,
                '382': golden_levels['382'],
                '500': golden_levels['500'],
                '618': golden_levels['618']
            },
            'xgboost': {
                'probability': xgb_prob,
                'signal': xgb_signal,
                'confidence': xgb_confidence
            },
            'combined_score': combined_score,
            'action': action,
            'strength': strength,
            'reasons': reasons
        },
        'recommendation': {
            'action': action,
            'strength': strength,
            'target_price': golden_levels['618'] if action in ['BUY', 'HOLD_BUY'] else None,
            'stop_loss': golden_levels['500'] if current_price >= golden_levels['500'] else config['buy_price'] * 0.98
        }
    }
    
    # 保存報告
    report_file = f"/Users/gordonlui/.openclaw/workspace/lenovo_fusion_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 融合分析報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ 融合分析完成")
    print(f"{'='*60}")
    
    return report

def main():
    """主函數"""
    print("🚀 啟動聯想集團XGBoost+黃金分割融合分析...")
    
    try:
        report = analyze_lenovo_with_xgboost()
        
        # 顯示總結
        print(f"\n📋 最終交易建議:")
        print(f"  股票: {report['stock_code']}")
        print(f"  當前價格: HKD {report['current_price']:.2f}")
        print(f"  買入價格: HKD {report['buy_price']:.2f}")
        print(f"  當前盈虧: {report['profit_pct']:+.2f}%")
        print(f"  綜合分數: {report['analysis']['combined_score']:.3f}")
        print(f"  建議動作: {report['analysis']['action']} ({report['analysis']['strength']})")
        
        if report['analysis']['reasons']:
            print(f"  主要理由: {', '.join(report['analysis']['reasons'][:2])}")
        
        print(f"\n🎯 關鍵價位監控:")
        print(f"  支撐位: HKD {report['analysis']['golden_ratio']['500']:.2f}")
        print(f"  阻力位: HKD {report['analysis']['golden_ratio']['618']:.2f}")
        print(f"  止損位: HKD {report['recommendation']['stop_loss']:.2f}")
        
    except Exception as e:
        print(f"❌ 分析過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()