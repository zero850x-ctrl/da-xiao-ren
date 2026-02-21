#!/usr/bin/env python3
"""
交易定時任務系統 - 專門為cron作業設計
支持命令行參數執行特定時間任務
"""

import schedule
import time
from datetime import datetime, timedelta
import json
import os
import sys
import argparse

sys.path.append('/Users/gordonlui/.openclaw/workspace')

# 導入現有模塊
try:
    from price_validator import PriceValidator
    from validated_xgboost_predictor import ValidatedXGBoostPredictor
    from check_price_breakout import PriceBreakoutDetector
except ImportError as e:
    print(f"❌ 導入模塊失敗: {e}")
    sys.exit(1)

class TradingScheduleSystem:
    """交易定時任務系統"""
    
    # 交易時間表 (香港時間)
    TRADING_SCHEDULE = [
        '09:30',  # 開市
        '10:00',  # 早盤
        '10:30',  # 早盤
        '11:00',  # 早盤
        '11:30',  # 午前
        '12:00',  # 午休前
        '12:30',  # 午休
        '13:00',  # 午後開市
        '14:00',  # 午後
        '14:30',  # 午後
        '15:00',  # 尾盤
        '15:30',  # 尾盤
        '15:55',  # 收市前5分鐘
    ]
    
    def __init__(self):
        self.config = self.load_config()
        self.monitor_stocks = self.config.get('monitor_stocks', ['00992', '00700', '09988'])
        self.results_dir = '/Users/gordonlui/.openclaw/workspace/schedule_results'
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.execution_log = []
        self.start_time = datetime.now()
        
    def load_config(self):
        """加載配置"""
        config_path = '/Users/gordonlui/.openclaw/workspace/trading_schedule_config.json'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加載配置失敗: {e}")
        return {}
    
    def is_trading_day(self):
        """檢查是否交易日"""
        now = datetime.now()
        # 簡單檢查：週一至週五
        return now.weekday() < 5  # 0=週一, 4=週五
    
    def is_trading_time(self):
        """檢查是否交易時間"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # 檢查是否在時間表內
        for time_slot in self.TRADING_SCHEDULE:
            if current_time == time_slot:
                return True
        
        # 檢查是否在交易時段內 (09:30-16:00)
        hour_min = now.hour * 100 + now.minute
        return 930 <= hour_min <= 1600
    
    def get_tasks_for_time(self, time_slot):
        """根據時間獲取任務列表"""
        tasks = []
        
        # 基本任務：所有時間都執行價格檢查
        tasks.append('price_check')
        
        # 根據時間添加特定任務
        if time_slot in ['09:30', '13:00']:
            # 開市時間：執行預測更新
            tasks.append('prediction_update')
        
        if time_slot in ['10:00', '11:00', '14:00', '15:00']:
            # 整點：執行突破檢測
            tasks.append('breakout_check')
        
        if time_slot in ['12:00', '15:30']:
            # 午休前和收市前：執行風險評估
            tasks.append('risk_assessment')
        
        if time_slot == '15:55':
            # 收市前：執行組合評估
            tasks.append('portfolio_assessment')
        
        return tasks
    
    def execute_price_check(self):
        """執行價格檢查任務"""
        print(f"\n📊 執行價格檢查任務...")
        
        # 使用validated_xgboost_predictor中的方法獲取價格
        predictor = ValidatedXGBoostPredictor()
        results = []
        
        for stock in self.monitor_stocks:
            try:
                price, source, validation = predictor.get_validated_price(stock)
                if price:
                    results.append({
                        'stock': stock,
                        'price': price,
                        'source': source,
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
                    print(f"  {stock}: ${price:.2f} ({source})")
            except Exception as e:
                print(f"  ❌ {stock}: 價格檢查失敗 - {e}")
        
        return {
            'status': 'success' if results else 'partial',
            'results': results,
            'summary': f"檢查了 {len(results)}/{len(self.monitor_stocks)} 隻股票"
        }
    
    def execute_prediction_update(self):
        """執行預測更新任務"""
        print(f"\n🤖 執行XGBoost預測更新任務...")
        
        predictor = ValidatedXGBoostPredictor()
        results = []
        
        for stock in self.monitor_stocks[:3]:  # 只預測前3隻股票
            try:
                print(f"\n🎯 預測股票: {stock}")
                print("-" * 50)
                
                prediction_result = predictor.predict_stock(stock)
                if prediction_result:
                    results.append({
                        'stock': stock,
                        'prediction': prediction_result
                    })
                    
                    # 顯示預測結果
                    prediction = prediction_result.get('prediction', {})
                    prob_up = prediction.get('probability_up', 0)
                    signal = prediction.get('signal', '未知')
                    confidence = prediction.get('confidence', 0)
                    
                    print(f"📊 預測結果:")
                    print(f"   上漲概率: {prob_up:.3f}")
                    print(f"   交易信號: {signal}")
                    print(f"   信心程度: {confidence:.3f}")
                    
                    # 交易建議
                    advice = prediction_result.get('advice', {})
                    if 'trading_advice' in advice and advice['trading_advice']:
                        print(f"💰 交易建議: {advice['trading_advice'][0].get('action', '未知')}")
                    
                    # 風險評估
                    risk = advice.get('risk_assessment', {})
                    if 'risk_level' in risk:
                        print(f"⚠️  風險評估: {risk['risk_level']} (分數: {risk['risk_score']})")
                    
                    # 保存結果
                    if 'result_file' in prediction_result:
                        print(f"💾 預測結果已保存: {prediction_result['result_file']}")
                    
                    print(f"\n✅ 預測完成")
                    if 'result_file' in prediction_result:
                        print(f"💾 詳細結果: {prediction_result['result_file']}")
                    
                    print(f"  {stock}: {signal} (概率: {prob_up:.3f})")
                    
            except Exception as e:
                print(f"  ❌ {stock}: 預測失敗 - {e}")
        
        return {
            'status': 'success' if results else 'partial',
            'results': results,
            'summary': f"更新了 {len(results)}/{min(3, len(self.monitor_stocks))} 隻股票預測"
        }
    
    def execute_breakout_check(self):
        """執行突破檢測任務"""
        print(f"\n🚀 執行價格突破檢測任務...")
        
        results = []
        for stock in self.monitor_stocks[:5]:  # 只檢查前5隻股票
            try:
                detector = PriceBreakoutDetector()
                # 暫時修改股票代碼進行測試
                detector.stock_code = stock
                breakout_result = detector.run()
                if breakout_result:
                    results.append({
                        'stock': stock,
                        'breakout': breakout_result
                    })
                    
                    # 嘗試獲取當前價格
                    current_price = 0
                    try:
                        from price_validator import PriceValidator
                        validator = PriceValidator()
                        price_data = validator.get_validated_price(stock)
                        if price_data:
                            current_price = price_data['price']
                    except:
                        pass
                    
                    print(f"  {stock}: ${current_price:.2f} - 突破檢測完成")
            except Exception as e:
                print(f"  ❌ {stock}: 突破檢測失敗 - {e}")
        
        return {
            'status': 'success' if results else 'partial',
            'results': results,
            'summary': f"檢測了 {len(results)}/{min(5, len(self.monitor_stocks))} 隻股票突破"
        }
    
    def execute_risk_assessment(self):
        """執行風險評估任務"""
        print(f"\n⚠️  執行風險評估任務...")
        
        # 簡單的風險評估邏輯
        risk_score = 0
        risk_factors = []
        
        # 檢查時間因素
        now = datetime.now()
        hour = now.hour
        
        if hour >= 14 and hour <= 15:
            risk_score += 1
            risk_factors.append("尾盤時段波動增加")
        
        # 檢查是否接近收市
        current_time = now.strftime('%H:%M')
        if current_time >= '15:30':
            risk_score += 1
            risk_factors.append("接近收市時間")
        
        # 確定風險等級
        if risk_score == 0:
            risk_level = "低"
        elif risk_score == 1:
            risk_level = "中"
        else:
            risk_level = "高"
        
        print(f"  風險等級: {risk_level} (分數: {risk_score})")
        if risk_factors:
            print(f"  風險因素: {', '.join(risk_factors)}")
        
        return {
            'status': 'success',
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'summary': f"風險等級: {risk_level}"
        }
    
    def execute_portfolio_assessment(self):
        """執行組合評估任務"""
        print(f"\n📈 執行組合評估任務...")
        
        # 簡單的組合評估
        total_stocks = len(self.monitor_stocks)
        print(f"  監控股票數量: {total_stocks}")
        print(f"  組合多樣性: {'良好' if total_stocks >= 5 else '一般'}")
        
        return {
            'status': 'success',
            'portfolio_size': total_stocks,
            'diversity': '良好' if total_stocks >= 5 else '一般',
            'summary': f"組合評估完成 ({total_stocks} 隻股票)"
        }
    
    def run_once(self, time_slot):
        """執行單次任務"""
        print("=" * 60)
        print(f"⏰ 執行定時任務 - {time_slot}")
        print("=" * 60)
        
        # 檢查是否交易日
        if not self.is_trading_day():
            print("📅 非交易日，跳過執行")
            return None
        
        # 檢查是否交易時間
        if not self.is_trading_time():
            print("⏰ 非交易時間，跳過執行")
            return None
        
        # 獲取任務列表
        tasks = self.get_tasks_for_time(time_slot)
        print(f"📋 計劃執行任務: {', '.join(tasks)}")
        
        # 執行任務
        task_results = {}
        tasks_executed = []
        tasks_successful = 0
        
        for task_name in tasks:
            try:
                print(f"\n🔧 執行任務: {task_name}")
                
                if task_name == 'price_check':
                    result = self.execute_price_check()
                elif task_name == 'prediction_update':
                    result = self.execute_prediction_update()
                elif task_name == 'breakout_check':
                    result = self.execute_breakout_check()
                elif task_name == 'risk_assessment':
                    result = self.execute_risk_assessment()
                elif task_name == 'portfolio_assessment':
                    result = self.execute_portfolio_assessment()
                else:
                    print(f"  ⚠️  未知任務: {task_name}")
                    continue
                
                task_results[task_name] = result
                tasks_executed.append(task_name)
                
                if result.get('status') in ['success', 'partial']:
                    tasks_successful += 1
                    print(f"  ✅ {task_name}: 成功")
                else:
                    print(f"  ❌ {task_name}: 失敗")
                    
            except Exception as e:
                print(f"  ❌ {task_name}: 執行失敗 - {e}")
                task_results[task_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                tasks_executed.append(task_name)
        
        # 生成報告
        success_rate = (tasks_successful / len(tasks_executed) * 100) if tasks_executed else 0
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time_slot': time_slot,
            'tasks_executed': tasks_executed,
            'tasks_successful': tasks_successful,
            'success_rate': success_rate,
            'results_summary': {task: {
                'status': result.get('status', 'unknown'),
                'summary': result.get('summary', '無摘要')
            } for task, result in task_results.items()},
            'system_status': {
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
                'total_tasks_executed': len(tasks_executed),
                'recent_success_rate': success_rate,
                'recent_failures': len(tasks_executed) - tasks_successful,
                'monitoring_stocks': len(self.monitor_stocks),
                'next_scheduled_time': self.get_next_scheduled_time(time_slot)
            }
        }
        
        # 保存報告
        report_filename = f"task_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(self.results_dir, report_filename)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 任務報告已保存: {report_path}")
        except Exception as e:
            print(f"\n⚠️  保存報告失敗: {e}")
        
        print(f"\n✅ {time_slot} 任務完成")
        print(f"   執行任務: {len(tasks_executed)} 個")
        print(f"   成功任務: {tasks_successful} 個")
        print(f"   成功率: {success_rate:.1f}%")
        
        return report
    
    def get_next_scheduled_time(self, current_time):
        """獲取下一個計劃時間"""
        try:
            current_idx = self.TRADING_SCHEDULE.index(current_time)
            if current_idx < len(self.TRADING_SCHEDULE) - 1:
                return self.TRADING_SCHEDULE[current_idx + 1]
        except ValueError:
            pass
        return "未知"
    
    def run_continuous(self):
        """持續運行模式"""
        print("\n🔄 開始持續運行模式...")
        print("📅 只在交易日執行")
        print("⏰ 按照時間表自動執行")
        
        # 為每個時間點安排任務
        for time_slot in self.TRADING_SCHEDULE:
            schedule.every().day.at(time_slot).do(self.run_once, time_slot)
            print(f"  ✅ 已安排: {time_slot}")
        
        print(f"\n⏰ 已安排 {len(self.TRADING_SCHEDULE)} 個時間點")
        print("🔄 開始監控...")
        
        # 主循環
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
            except KeyboardInterrupt:
                print("\n⏹️  用戶中斷，停止運行")
                break
            except Exception as e:
                print(f"⚠️  運行錯誤: {e}")
                time.sleep(300)  # 錯誤後等待5分鐘

def main():
    """主函數 - 支持命令行參數"""
    parser = argparse.ArgumentParser(description='交易定時任務系統')
    parser.add_argument('--time', type=str, help='執行特定時間的任務 (格式: HH:MM)')
    parser.add_argument('--continuous', action='store_true', help='啟動持續運行模式')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("⏰ 交易定時任務系統 - Cron版本")
    print("=" * 70)
    
    system = TradingScheduleSystem()
    
    print(f"\n📅 交易日檢查: {'是' if system.is_trading_day() else '否'}")
    print(f"⏰ 交易時間檢查: {'是' if system.is_trading_time() else '否'}")
    
    print(f"\n📋 監控股票: {', '.join(system.monitor_stocks[:5])}...")
    print(f"⏰ 時間表: {', '.join(system.TRADING_SCHEDULE)}")
    
    if args.time:
        # 執行特定時間的任務
        print(f"\n🔧 執行指定時間任務: {args.time}")
        report = system.run_once(args.time)
        
        if report:
            print(f"\n✅ 任務執行完成")
            print(f"   執行任務: {len(report['tasks_executed'])} 個")
            print(f"   成功任務: {report['tasks_successful']} 個")
            print(f"   成功率: {report['success_rate']:.1f}%")
        else:
            print(f"\n⚠️  任務未執行 (非交易日或非交易時間)")
    
    elif args.continuous:
        # 啟動持續運行模式
        print(f"\n🚀 啟動持續運行模式")
        system.run_continuous()
    
    else:
        # 默認執行當前時間的任務
        current_time = datetime.now().strftime('%H:%M')
        print(f"\n🔧 執行當前時間任務: {current_time}")
        report = system.run_once(current_time)
        
        if report:
            print(f"\n✅ 任務執行完成")
            print(f"   執行任務: {len(report['tasks_executed'])} 個")
            print(f"   成功任務: {report['tasks_successful']} 個")
            print(f"   成功率: {report['success_rate']:.1f}%")
        else:
            print(f"\n⚠️  任務未執行 (非交易日或非交易時間)")
    
    return system

if __name__ == "__main__":
    try:
        system = main()
    except KeyboardInterrupt:
        print("\n⏹️  程式被中斷")
    except Exception as e:
        print(f"\n❌ 程式執行錯誤: {e}")
        sys.exit(1)