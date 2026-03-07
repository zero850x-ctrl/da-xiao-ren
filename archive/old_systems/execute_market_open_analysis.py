#!/usr/bin/env python3
"""
開市綜合分析執行腳本
強制執行開市分析任務，忽略時間檢查
"""

import sys
import os
sys.path.append('/Users/gordonlui/.openclaw/workspace')

print("=" * 70)
print("🔧 開市綜合分析執行腳本")
print("=" * 70)

try:
    from trading_schedule_system import TradingScheduleSystem
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("請確保 trading_schedule_system.py 在正確路徑")
    sys.exit(1)

def main():
    """主函數"""
    # 創建系統實例
    system = TradingScheduleSystem()
    
    # 強制執行開市分析任務，忽略時間檢查
    print("\n🎯 強制執行開市綜合分析任務 (09:30)")
    print("=" * 60)
    
    # 手動執行開市任務
    tasks_to_run = ['price_check', 'prediction_update', 'risk_assessment']
    
    results = {}
    for task_name in tasks_to_run:
        print(f"\n📊 執行 {task_name}...")
        task_method = getattr(system, f'task_{task_name}', None)
        if task_method:
            try:
                result = task_method()
                results[task_name] = result
                print(f"  ✅ {task_name} 完成")
            except Exception as e:
                print(f"  ❌ {task_name} 失敗: {e}")
                results[task_name] = {'error': str(e)}
        else:
            print(f"  ⚠️  未知任務: {task_name}")
    
    # 生成報告
    print(f"\n📋 任務完成總結:")
    print(f"  執行任務數: {len(tasks_to_run)}")
    successful_tasks = sum(1 for task in tasks_to_run if task in results and results[task] is not None)
    print(f"  成功任務數: {successful_tasks}")
    print(f"  成功率: {(successful_tasks/len(tasks_to_run)*100):.1f}%")
    
    # 重點監控股票結果
    if 'price_check' in results and results['price_check']:
        print(f"\n🎯 重點監控股票價格:")
        for stock in ['00992', '00700', '09988']:
            stock_data = next((r for r in results['price_check'] if r['stock'] == stock), None)
            if stock_data:
                print(f"  {stock}: ${stock_data['price']:.2f} ({stock_data['source']})")
            else:
                print(f"  {stock}: 數據獲取失敗")
    
    if 'prediction_update' in results and results['prediction_update']:
        print(f"\n🤖 XGBoost預測更新:")
        for pred in results['prediction_update']:
            stock = pred['stock']
            signal = pred['prediction']['signal']
            prob = pred['prediction']['probability_up']
            print(f"  {stock}: {signal} (上漲概率: {prob:.3f})")
    
    if 'risk_assessment' in results and results['risk_assessment']:
        risk = results['risk_assessment']
        print(f"\n⚠️  風險評估:")
        print(f"  風險等級: {risk['risk_level']}")
        print(f"  風險分數: {risk['risk_score']}")
        if risk['risk_factors']:
            print(f"  風險因素: {', '.join(risk['risk_factors'])}")
        print(f"  建議: {risk['recommendation']}")
    
    # 生成綜合建議
    print(f"\n💡 綜合交易建議:")
    
    # 基於價格和預測生成建議
    if 'price_check' in results and results['price_check'] and 'prediction_update' in results and results['prediction_update']:
        print("  1. 價格監控:")
        for stock in ['00992', '00700', '09988']:
            price_data = next((r for r in results['price_check'] if r['stock'] == stock), None)
            pred_data = next((r for r in results['prediction_update'] if r['stock'] == stock), None)
            
            if price_data and pred_data:
                price = price_data['price']
                signal = pred_data['prediction']['signal']
                prob = pred_data['prediction']['probability_up']
                
                if signal == 'BUY' and prob > 0.6:
                    print(f"    {stock}: 強烈買入信號 (${price:.2f}, 上漲概率: {prob:.1%})")
                elif signal == 'BUY':
                    print(f"    {stock}: 買入信號 (${price:.2f}, 上漲概率: {prob:.1%})")
                elif signal == 'SELL':
                    print(f"    {stock}: 賣出信號 (${price:.2f}, 上漲概率: {prob:.1%})")
                else:
                    print(f"    {stock}: 持有 (${price:.2f}, 上漲概率: {prob:.1%})")
    
    # 基於風險評估的建議
    if 'risk_assessment' in results and results['risk_assessment']:
        risk_level = results['risk_assessment']['risk_level']
        if risk_level in ['高', '中高']:
            print(f"  2. 風險警告: 當前風險等級為{risk_level}，建議謹慎交易")
        else:
            print(f"  2. 風險狀況: 當前風險等級為{risk_level}，可正常交易")
    
    print(f"\n✅ 開市綜合分析完成")
    print("=" * 60)
    
    # 保存詳細報告
    save_detailed_report(results)
    
    return results

def save_detailed_report(results):
    """保存詳細報告"""
    import json
    from datetime import datetime
    
    report_dir = '/Users/gordonlui/.openclaw/workspace/schedule_results'
    os.makedirs(report_dir, exist_ok=True)
    
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'task_type': 'market_open_analysis',
        'execution_time': '09:30',
        'results': results,
        'summary': generate_summary(results)
    }
    
    report_file = f"{report_dir}/market_open_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 詳細報告已保存: {report_file}")
    
    return report_file

def generate_summary(results):
    """生成總結"""
    summary = {
        'tasks_executed': [],
        'tasks_successful': [],
        'tasks_failed': [],
        'key_findings': []
    }
    
    for task_name, result in results.items():
        summary['tasks_executed'].append(task_name)
        
        if result and 'error' not in result:
            summary['tasks_successful'].append(task_name)
            
            # 提取關鍵發現
            if task_name == 'price_check' and isinstance(result, list):
                prices = {r['stock']: r['price'] for r in result[:3]}
                summary['key_findings'].append(f"價格檢查: {len(result)}隻股票")
            
            elif task_name == 'prediction_update' and isinstance(result, list):
                signals = {r['stock']: r['prediction']['signal'] for r in result}
                summary['key_findings'].append(f"預測更新: {len(result)}個預測")
            
            elif task_name == 'risk_assessment' and isinstance(result, dict):
                summary['key_findings'].append(f"風險評估: {result['risk_level']}")
        else:
            summary['tasks_failed'].append(task_name)
    
    return summary

if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)