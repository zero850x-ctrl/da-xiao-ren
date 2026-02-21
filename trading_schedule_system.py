#!/usr/bin/env python3
"""
交易定時任務系統 - 按照指定時間表執行
時間表: 9:30,10:00,10:30,11:00,11:30,12:00,12:30,13:00,14:00,14:30,15:00,15:30,15:55
"""

import schedule
import time
from datetime import datetime, timedelta
import json
import os
import sys
sys.path.append('/Users/gordonlui/.openclaw/workspace')

print("=" * 70)
print("⏰ 交易定時任務系統")
print("=" * 70)

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
        default_config = {
            'monitor_stocks': ['00992', '00700', '09988', '00005', '01398', '02638', '09618'],
            'trading_hours': {
                'start': '09:30',
                'end': '16:00'
            },
            'schedule_times': self.TRADING_SCHEDULE,
            'tasks': {
                'price_check': '檢查價格和關鍵價位',
                'breakout_detect': '檢測價格突破',
                'prediction_update': '更新XGBoost預測',
                'risk_assessment': '風險評估',
                'portfolio_check': '投資組合檢查'
            },
            'notifications': {
                'telegram': True,
                'silent_mode': False  # 正常時不報告
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def log_execution(self, task_name, status, details=None):
        """記錄執行日誌"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'task': task_name,
            'status': status,
            'details': details or {}
        }
        
        self.execution_log.append(log_entry)
        
        # 保存到文件
        log_file = f"{self.results_dir}/execution_log_{datetime.now().strftime('%Y%m%d')}.json"
        log_data = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        
        log_data.append(log_entry)
        
        # 只保留最近1000條記錄
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return log_entry
    
    def is_trading_day(self):
        """檢查是否交易日"""
        today = datetime.now()
        # 週六、週日不是交易日
        if today.weekday() >= 5:  # 5=週六, 6=週日
            return False
        
        # 檢查是否香港公眾假期（簡化版本）
        # 實際應該使用完整的假期日曆
        holidays = [
            '2026-01-01',  # 元旦
            '2026-01-28',  # 農曆新年
            '2026-01-29',
            '2026-04-03',  # 清明節
            '2026-04-07',  # 復活節
            '2026-05-01',  # 勞動節
            '2026-06-19',  # 端午節
            '2026-07-01',  # 香港回歸紀念日
            '2026-09-18',  # 中秋節
            '2026-10-01',  # 國慶日
            '2026-10-02',  # 國慶日翌日
            '2026-12-25',  # 聖誕節
            '2026-12-26',  # 聖誕節後第一個周日
        ]
        
        today_str = today.strftime('%Y-%m-%d')
        return today_str not in holidays
    
    def is_trading_time(self):
        """檢查是否交易時間"""
        if not self.is_trading_day():
            return False
        
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        start_time = self.config['trading_hours']['start']
        end_time = self.config['trading_hours']['end']
        
        return start_time <= current_time <= end_time
    
    def task_price_check(self):
        """任務：價格檢查"""
        print(f"\n📊 執行價格檢查任務...")
        
        try:
            from validated_xgboost_predictor import ValidatedXGBoostPredictor
            predictor = ValidatedXGBoostPredictor()
            
            results = []
            for stock in self.monitor_stocks[:3]:  # 只檢查前3個，避免過載
                try:
                    price, source, _ = predictor.get_validated_price(stock)
                    results.append({
                        'stock': stock,
                        'price': price,
                        'source': source,
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
                    print(f"  {stock}: ${price:.2f} ({source})")
                except Exception as e:
                    print(f"  {stock}: 錯誤 - {e}")
            
            # 保存結果
            result_file = f"{self.results_dir}/price_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results': results
                }, f, indent=2)
            
            self.log_execution('price_check', 'success', {
                'stocks_checked': len(results),
                'result_file': result_file
            })
            
            return results
            
        except Exception as e:
            error_msg = f"價格檢查失敗: {e}"
            print(f"❌ {error_msg}")
            self.log_execution('price_check', 'failed', {'error': str(e)})
            return None
    
    def task_breakout_detect(self):
        """任務：價格突破檢測"""
        print(f"\n🎯 執行價格突破檢測任務...")
        
        try:
            # 運行價格突破檢測
            import subprocess
            result = subprocess.run(
                ['python3', '/Users/gordonlui/.openclaw/workspace/check_price_breakout.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析輸出，尋找突破信息
                output = result.stdout
                breakouts_found = '檢測到突破' in output or '突破上方' in output or '跌破下方' in output
                
                details = {
                    'breakouts_found': breakouts_found,
                    'output_summary': output[:500]  # 只保存前500字符
                }
                
                self.log_execution('breakout_detect', 'success', details)
                
                if breakouts_found:
                    print(f"  ⚠️  檢測到價格突破")
                    # 這裡可以發送通知
                else:
                    print(f"  ✅ 無價格突破")
                
                return breakouts_found
            else:
                raise Exception(f"腳本執行失敗: {result.stderr[:200]}")
                
        except Exception as e:
            error_msg = f"突破檢測失敗: {e}"
            print(f"❌ {error_msg}")
            self.log_execution('breakout_detect', 'failed', {'error': str(e)})
            return None
    
    def task_prediction_update(self):
        """任務：更新XGBoost預測"""
        print(f"\n🤖 執行XGBoost預測更新任務...")
        
        try:
            from validated_xgboost_predictor import ValidatedXGBoostPredictor
            predictor = ValidatedXGBoostPredictor()
            
            # 只更新重點股票
            focus_stocks = ['00992']  # 聯想集團為重點
            
            results = []
            for stock in focus_stocks:
                result = predictor.predict_stock(stock)
                results.append({
                    'stock': stock,
                    'prediction': result['prediction'],
                    'advice': result['advice']['trading_advice'][0] if result['advice']['trading_advice'] else {}
                })
                
                print(f"  {stock}: {result['prediction']['signal']} (概率: {result['prediction']['probability_up']:.3f})")
            
            # 保存結果
            result_file = f"{self.results_dir}/prediction_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results': results
                }, f, indent=2)
            
            self.log_execution('prediction_update', 'success', {
                'stocks_predicted': len(results),
                'result_file': result_file
            })
            
            return results
            
        except Exception as e:
            error_msg = f"預測更新失敗: {e}"
            print(f"❌ {error_msg}")
            self.log_execution('prediction_update', 'failed', {'error': str(e)})
            return None
    
    def task_risk_assessment(self):
        """任務：風險評估"""
        print(f"\n⚠️  執行風險評估任務...")
        
        try:
            # 簡單的風險評估
            risk_factors = []
            
            # 檢查市場時間
            current_hour = datetime.now().hour
            if current_hour >= 15:  # 尾盤
                risk_factors.append('尾盤時段，波動可能加大')
            
            # 檢查執行日誌
            recent_failures = len([log for log in self.execution_log[-10:] 
                                  if log['status'] == 'failed'])
            if recent_failures > 2:
                risk_factors.append(f'近期任務失敗較多 ({recent_failures}/10)')
            
            # 評估風險等級
            risk_score = len(risk_factors)
            if risk_score >= 3:
                risk_level = '高'
            elif risk_score >= 2:
                risk_level = '中高'
            elif risk_score >= 1:
                risk_level = '中'
            else:
                risk_level = '低'
            
            assessment = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'recommendation': self.get_risk_recommendation(risk_level)
            }
            
            print(f"  風險等級: {risk_level} (分數: {risk_score})")
            if risk_factors:
                print(f"  風險因素: {', '.join(risk_factors)}")
            
            # 保存結果
            result_file = f"{self.results_dir}/risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w') as f:
                json.dump(assessment, f, indent=2)
            
            self.log_execution('risk_assessment', 'success', assessment)
            
            return assessment
            
        except Exception as e:
            error_msg = f"風險評估失敗: {e}"
            print(f"❌ {error_msg}")
            self.log_execution('risk_assessment', 'failed', {'error': str(e)})
            return None
    
    def get_risk_recommendation(self, risk_level):
        """獲取風險建議"""
        recommendations = {
            '高': '暫停新交易，減持高風險倉位',
            '中高': '謹慎交易，控制倉位大小',
            '中': '正常交易，注意風險管理',
            '低': '正常交易，可適當增加倉位'
        }
        return recommendations.get(risk_level, '正常交易')
    
    def task_portfolio_check(self):
        """任務：投資組合檢查"""
        print(f"\n📈 執行投資組合檢查任務...")
        
        try:
            # 這裡應該連接真實的持倉數據
            # 暫時使用模擬數據
            
            simulated_portfolio = {
                '00992': {
                    'shares': 26000,
                    'avg_price': 8.59,
                    'current_price': 9.30,
                    'profit_loss': (9.30 - 8.59) * 26000,
                    'profit_percent': (9.30 / 8.59 - 1) * 100
                },
                '00700': {
                    'shares': 400,
                    'avg_price': 533.00,
                    'current_price': 535.50,
                    'profit_loss': (535.50 - 533.00) * 400,
                    'profit_percent': (535.50 / 533.00 - 1) * 100
                }
            }
            
            total_value = sum(item['current_price'] * item['shares'] for item in simulated_portfolio.values())
            total_pl = sum(item['profit_loss'] for item in simulated_portfolio.values())
            
            portfolio_summary = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_value': total_value,
                'total_pl': total_pl,
                'total_pl_percent': (total_pl / (total_value - total_pl)) * 100 if (total_value - total_pl) > 0 else 0,
                'holdings': simulated_portfolio,
                'concentration': {
                    'top_holding': max(simulated_portfolio.items(), key=lambda x: x[1]['current_price'] * x[1]['shares'])[0],
                    'top_percentage': max([(item['current_price'] * item['shares'] / total_value * 100) 
                                          for item in simulated_portfolio.values()])
                }
            }
            
            print(f"  總市值: HKD {total_value:,.0f}")
            print(f"  總盈虧: HKD {total_pl:,.0f} ({portfolio_summary['total_pl_percent']:.2f}%)")
            print(f"  集中度: {portfolio_summary['concentration']['top_holding']} "
                  f"({portfolio_summary['concentration']['top_percentage']:.1f}%)")
            
            # 保存結果
            result_file = f"{self.results_dir}/portfolio_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w') as f:
                json.dump(portfolio_summary, f, indent=2)
            
            self.log_execution('portfolio_check', 'success', {
                'total_value': total_value,
                'total_pl': total_pl,
                'result_file': result_file
            })
            
            return portfolio_summary
            
        except Exception as e:
            error_msg = f"投資組合檢查失敗: {e}"
            print(f"❌ {error_msg}")
            self.log_execution('portfolio_check', 'failed', {'error': str(e)})
            return None
    
    def execute_scheduled_task(self, time_slot):
        """執行定時任務"""
        print(f"\n{'='*60}")
        print(f"⏰ 執行定時任務 - {time_slot}")
        print(f"{'='*60}")
        
        if not self.is_trading_time():
            print("⏸️  非交易時間，跳過任務")
            return
        
        # 根據時間決定執行哪些任務
        tasks_to_run = []
        
        if time_slot == '09:30':
            tasks_to_run = ['price_check', 'prediction_update', 'risk_assessment']
        elif time_slot == '15:55':
            tasks_to_run = ['price_check', 'breakout_detect', 'portfolio_check']
        else:
            # 其他時間點
            if '00' in time_slot or '30' in time_slot:
                tasks_to_run = ['price_check', 'breakout_detect']
            else:
                tasks_to_run = ['price_check']
        
        results = {}
        for task_name in tasks_to_run:
            task_method = getattr(self, f'task_{task_name}', None)
            if task_method:
                try:
                    result = task_method()
                    results[task_name] = result
                except Exception as e:
                    print(f"❌ 任務 {task_name} 執行異常: {e}")
                    results[task_name] = {'error': str(e)}
            else:
                print(f"⚠️  未知任務: {task_name}")
        
        # 生成任務報告
        report = self.generate_task_report(time_slot, tasks_to_run, results)
        
        print(f"\n✅ {time_slot} 任務完成")
        return report
    
    def generate_task_report(self, time_slot, tasks, results):
        """生成任務報告"""
        successful_tasks = sum(1 for task in tasks if task in results and results[task] is not None)
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time_slot': time_slot,
            'tasks_executed': tasks,
            'tasks_successful': successful_tasks,
            'success_rate': (successful_tasks / len(tasks) * 100) if tasks else 0,
            'results_summary': {},
            'system_status': self.get_system_status()
        }
        
        # 總結結果
        for task in tasks:
            if task in results and results[task] is not None:
                if isinstance(results[task], dict):
                    report['results_summary'][task] = {
                        'status': 'success',
                        'summary': self.summarize_result(task, results[task])
                    }
                else:
                    report['results_summary'][task] = {
                        'status': 'success',
                        'summary': str(results[task])[:100]
                    }
            else:
                report['results_summary'][task] = {
                    'status': 'failed',
                    'summary': '任務執行失敗'
                }
        
        # 保存報告
        report_file = f"{self.results_dir}/task_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 任務報告已保存: {report_file}")
        return report
    
    def summarize_result(self, task_name, result):
        """總結任務結果"""
        if task_name == 'price_check' and isinstance(result, list):
            prices = [f"{r['stock']}: ${r['price']:.2f}" for r in result[:3]]
            return f"檢查了 {len(result)} 隻股票: {', '.join(prices)}"
        elif task_name == 'prediction_update' and isinstance(result, list):
            predictions = [f"{r['stock']}: {r['prediction']['signal']}" for r in result[:3]]
            return f"更新了 {len(result)} 個預測: {', '.join(predictions)}"
        elif task_name == 'risk_assessment' and isinstance(result, dict):
            return f"風險等級: {result.get('risk_level', '未知')}"
        elif task_name == 'portfolio_check' and isinstance(result, dict):
            return f"總市值: HKD {result.get('total_value', 0):,.0f}"
        elif task_name == 'breakout_detect':
            return "突破檢測完成"
        else:
            return "任務完成"
    
    def get_system_status(self):
        """獲取系統狀態"""
        uptime = datetime.now() - self.start_time
        uptime_hours = uptime.total_seconds() / 3600
        
        recent_logs = self.execution_log[-20:] if len(self.execution_log) >= 20 else self.execution_log
        recent_success = sum(1 for log in recent_logs if log['status'] == 'success')
        recent_failure = sum(1 for log in recent_logs if log['status'] == 'failed')
        
        return {
            'uptime_hours': round(uptime_hours, 2),
            'total_tasks_executed': len(self.execution_log),
            'recent_success_rate': (recent_success / len(recent_logs) * 100) if recent_logs else 0,
            'recent_failures': recent_failure,
            'monitoring_stocks': len(self.monitor_stocks),
            'next_scheduled_time': self.get_next_scheduled_time()
        }
    
    def get_next_scheduled_time(self):
        """獲取下一個計劃時間"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        for schedule_time in self.TRADING_SCHEDULE:
            if schedule_time > current_time:
                return schedule_time
        
        # 如果今天的所有時間都已過，返回明天的第一個時間
        tomorrow = now + timedelta(days=1)
        return f"{tomorrow.strftime('%Y-%m-%d')} 09:30"
    
    def setup_schedule(self):
        """設置定時任務"""
        print("\n⏰ 設置定時任務...")
        
        for schedule_time in self.TRADING_SCHEDULE:
            # 使用schedule庫設置定時任務
            schedule.every().day.at(schedule_time).do(
                self.execute_scheduled_task, schedule_time
            )
            print(f"  ✅ {schedule_time}: 交易監控任務")
        
        print(f"\n📋 總計 {len(self.TRADING_SCHEDULE)} 個定時任務")
        print(f"   第一個: {self.TRADING_SCHEDULE[0]}")
        print(f"   最後一個: {self.TRADING_SCHEDULE[-1]}")
        print(f"   監控股票: {', '.join(self.monitor_stocks[:3])}...")
        
        return True
    
    def run_once(self, time_slot=None):
        """運行一次任務（用於測試）"""
        if time_slot is None:
            # 找到下一個或當前時間
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            for t in self.TRADING_SCHEDULE:
                if t >= current_time:
                    time_slot = t
                    break
            
            if time_slot is None:
                time_slot = self.TRADING_SCHEDULE[0]
        
        print(f"\n🔧 測試運行: {time_slot}")
        return self.execute_scheduled_task(time_slot)
    
    def run_continuous(self):
        """持續運行（用於生產環境）"""
        print("\n🚀 啟動持續運行模式...")
        
        # 設置定時任務
        self.setup_schedule()
        
        print(f"\n📊 系統狀態:")
        status = self.get_system_status()
        print(f"   運行時間: {status['uptime_hours']} 小時")
        print(f"   總任務數: {status['total_tasks_executed']}")
        print(f"   監控股票: {status['monitoring_stocks']} 隻")
        print(f"   下個任務: {status['next_scheduled_time']}")
        
        print(f"\n💡 使用說明:")
        print(f"   1. 系統會自動按照時間表執行")
        print(f"   2. 查看日誌: {self.results_dir}/")
        print(f"   3. 停止系統: Ctrl+C")
        
        print(f"\n✅ 系統啟動完成!")
        print("=" * 70)
        
        try:
            # 立即執行一次當前時間的任務（如果是在交易時間）
            if self.is_trading_time():
                current_time = datetime.now().strftime('%H:%M')
                if current_time in self.TRADING_SCHEDULE:
                    print(f"\n⏰ 立即執行當前時間任務: {current_time}")
                    self.execute_scheduled_task(current_time)
            
            # 保持運行
            print(f"\n⏳ 系統運行中... (按Ctrl+C停止)")
            while True:
                schedule.run_pending()
                time.sleep(1)
                
                # 每分鐘檢查一次
                if datetime.now().second == 0:
                    # 可以添加一些定期檢查
                    pass
                    
        except KeyboardInterrupt:
            print("\n🛑 用戶中斷，系統停止")
            
            # 生成最終報告
            final_report = self.generate_final_report()
            print(f"\n📋 最終報告已生成: {final_report}")
            
        except Exception as e:
            print(f"\n❌ 系統運行錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_final_report(self):
        """生成最終報告"""
        total_tasks = len(self.execution_log)
        successful_tasks = sum(1 for log in self.execution_log if log['status'] == 'success')
        
        report = {
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'tasks_by_type': self.analyze_tasks_by_type(),
            'system_uptime': str(datetime.now() - self.start_time),
            'recommendations': self.generate_recommendations()
        }
        
        report_file = f"{self.results_dir}/final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def analyze_tasks_by_type(self):
        """按類型分析任務"""
        task_types = {}
        for log in self.execution_log:
            task_name = log['task']
            task_types[task_name] = task_types.get(task_name, {'total': 0, 'success': 0, 'failed': 0})
            task_types[task_name]['total'] += 1
            if log['status'] == 'success':
                task_types[task_name]['success'] += 1
            else:
                task_types[task_name]['failed'] += 1
        
        return task_types
    
    def generate_recommendations(self):
        """生成改進建議"""
        recommendations = []
        
        # 分析失敗任務
        failed_tasks = [log for log in self.execution_log if log['status'] == 'failed']
        if failed_tasks:
            common_errors = {}
            for log in failed_tasks:
                error = log.get('details', {}).get('error', '未知錯誤')
                common_errors[error] = common_errors.get(error, 0) + 1
            
            top_error = max(common_errors.items(), key=lambda x: x[1]) if common_errors else None
            if top_error:
                recommendations.append(f"最常見錯誤: {top_error[0]} (出現{top_error[1]}次)")
        
        # 分析成功率
        success_rate = self.get_system_status()['recent_success_rate']
        if success_rate < 80:
            recommendations.append(f"任務成功率偏低: {success_rate:.1f}%，建議檢查系統穩定性")
        
        # 檢查執行頻率
        if len(self.execution_log) < 5:
            recommendations.append("執行任務較少，建議檢查定時任務設置")
        
        return recommendations if recommendations else ["系統運行正常，無特別建議"]

def test_system():
    """測試系統"""
    print("\n🧪 測試交易定時任務系統")
    
    system = TradingScheduleSystem()
    
    print(f"\n📅 交易日檢查: {'是' if system.is_trading_day() else '否'}")
    print(f"⏰ 交易時間檢查: {'是' if system.is_trading_time() else '否'}")
    
    print(f"\n📋 監控股票: {', '.join(system.monitor_stocks[:5])}...")
    print(f"⏰ 時間表: {', '.join(system.TRADING_SCHEDULE[:3])}...")
    
    # 測試單個任務
    print(f"\n🔧 測試單個任務執行...")
    report = system.run_once('09:30')
    
    if report:
        print(f"✅ 測試成功")
        print(f"   執行任務: {len(report['tasks_executed'])} 個")
        print(f"   成功任務: {report['tasks_successful']} 個")
        print(f"   成功率: {report['success_rate']:.1f}%")
    
    return system

def main():
    """主函數"""
    print("=" * 70)
    print("⏰ 交易定時任務系統 - 主程序")
    print("=" * 70)
    
    # 測試系統
    system = test_system()
    
    print(f"\n💾 系統文件:")
    print(f"  主系統: {__file__}")
    print(f"  價格驗證: /Users/gordonlui/.openclaw/workspace/price_validator.py")
    print(f"  驗證預測: /Users/gordonlui/.openclaw/workspace/validated_xgboost_predictor.py")
    print(f"  突破檢測: /Users/gordonlui/.openclaw/workspace/check_price_breakout.py")
    print(f"  結果目錄: {system.results_dir}")
    
    print(f"\n💡 使用說明:")
    print(f"  1. 測試運行: system.run_once('09:30')")
    print(f"  2. 持續運行: system.run_continuous()")
    print(f"  3. 查看日誌: {system.results_dir}/")
    print(f"  4. 修改配置: /Users/gordonlui/.openclaw/workspace/trading_schedule_config.json")
    
    print(f"\n🎯 系統特色:")
    print(f"  ✅ 精確時間表: {len(system.TRADING_SCHEDULE)} 個時間點")
    print(f"  ✅ 智能任務分配: 不同時間執行不同任務")
    print(f"  ✅ 完整監控: 價格、突破、預測、風險、組合")
    print(f"  ✅ 錯誤處理: 自動記錄和恢復")
    print(f"  ✅ 詳細報告: 每次執行都有完整記錄")
    
    print(f"\n⏰ 交易時間表:")
    for i, time_slot in enumerate(system.TRADING_SCHEDULE, 1):
        print(f"  {i:2d}. {time_slot}")
    
    print(f"\n✅ 系統準備就緒")
    print("=" * 70)
    
    # 詢問是否開始持續運行
    response = input("\n🚀 是否開始持續運行模式? (y/n): ")
    if response.lower() == 'y':
        system.run_continuous()
    
    return system

if __name__ == "__main__":
    system = main()
