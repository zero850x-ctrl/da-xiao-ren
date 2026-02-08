#!/usr/bin/env python3
"""
加密貨幣學習觀察系統
專注於觀察和學習，不進行實際交易
"""

import os
import json
import time
from datetime import datetime, timedelta
from binance.client import Client
import pandas as pd

class CryptoLearningObserver:
    def __init__(self):
        # API密鑰
        self.api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
        self.api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
        
        # 學習配置
        self.observation_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        self.observation_interval = 3600  # 每小時觀察一次（秒）
        self.learning_days = 3
        
        # 數據存儲
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_learning"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 學習記錄
        self.observations = []
        self.lessons_learned = []
        
        # 連接
        self.client = None
    
    def connect(self):
        """連接到幣安API"""
        print("🔗 連接到幣安Testnet...")
        
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            
            # 測試連接
            server_time = self.client.get_server_time()
            server_dt = datetime.fromtimestamp(server_time['serverTime']/1000)
            print(f"✅ 連接成功！服務器時間: {server_dt}")
            
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def observe_market(self):
        """觀察市場"""
        print(f"\n👀 觀察市場 - {datetime.now().strftime('%H:%M:%S')}")
        
        observation = {
            'timestamp': datetime.now().isoformat(),
            'symbols': {}
        }
        
        for symbol in self.observation_symbols:
            try:
                # 獲取當前價格
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                
                # 獲取24小時統計
                stats = self.client.get_ticker(symbol=symbol)
                change_percent = float(stats['priceChangePercent'])
                high_24h = float(stats['highPrice'])
                low_24h = float(stats['lowPrice'])
                volume = float(stats['volume'])
                
                observation['symbols'][symbol] = {
                    'price': current_price,
                    'change_24h': change_percent,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'volume': volume
                }
                
                print(f"  {symbol}:")
                print(f"    價格: ${current_price:.2f}")
                print(f"    24小時變化: {change_percent:+.2f}%")
                print(f"    波動範圍: ${low_24h:.2f} - ${high_24h:.2f}")
                print(f"    成交量: {volume:,.2f}")
                
            except Exception as e:
                print(f"  {symbol}: 觀察失敗 - {e}")
                observation['symbols'][symbol] = {'error': str(e)}
        
        # 保存觀察記錄
        self.observations.append(observation)
        self.save_observation(observation)
        
        return observation
    
    def analyze_observations(self):
        """分析觀察數據"""
        if len(self.observations) < 2:
            return
        
        print("\n📊 分析觀察數據...")
        
        latest = self.observations[-1]
        previous = self.observations[-2] if len(self.observations) >= 2 else None
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'volatility_analysis': {},
            'trend_analysis': {},
            'learning_points': []
        }
        
        for symbol in self.observation_symbols:
            if symbol in latest['symbols'] and symbol in previous['symbols']:
                latest_data = latest['symbols'][symbol]
                previous_data = previous['symbols'][symbol]
                
                if 'price' in latest_data and 'price' in previous_data:
                    # 計算價格變化
                    price_change = latest_data['price'] - previous_data['price']
                    price_change_pct = (price_change / previous_data['price']) * 100
                    
                    # 波動分析
                    volatility = latest_data['high_24h'] - latest_data['low_24h']
                    volatility_pct = (volatility / latest_data['price']) * 100
                    
                    analysis['volatility_analysis'][symbol] = {
                        'price_change': price_change,
                        'price_change_pct': price_change_pct,
                        'volatility': volatility,
                        'volatility_pct': volatility_pct
                    }
                    
                    # 學習點
                    if abs(price_change_pct) > 2:
                        lesson = f"{symbol} 在觀察期間變化 {price_change_pct:+.2f}%，顯示加密貨幣的高波動性"
                        analysis['learning_points'].append(lesson)
                    
                    if volatility_pct > 5:
                        lesson = f"{symbol} 24小時波動率 {volatility_pct:.2f}%，需要謹慎的風險管理"
                        analysis['learning_points'].append(lesson)
        
        # 保存分析
        self.save_analysis(analysis)
        
        # 顯示學習點
        if analysis['learning_points']:
            print("\n💡 學習點:")
            for point in analysis['learning_points'][:3]:  # 顯示前3個
                print(f"  • {point}")
        
        return analysis
    
    def simulate_risk_management(self, observation):
        """模擬風險管理決策"""
        print("\n🛡️ 模擬風險管理決策:")
        
        decisions = []
        
        for symbol, data in observation['symbols'].items():
            if 'price' in data:
                current_price = data['price']
                
                # 模擬2%止損計算
                stop_loss_price = current_price * 0.98  # 2%止損
                take_profit_price = current_price * 1.04  # 4%止盈
                
                decision = {
                    'symbol': symbol,
                    'current_price': current_price,
                    'stop_loss': stop_loss_price,
                    'take_profit': take_profit_price,
                    'risk_reward_ratio': 2.0  # 風險回報比 1:2
                }
                
                decisions.append(decision)
                
                print(f"  {symbol}:")
                print(f"    當前價: ${current_price:.2f}")
                print(f"    止損價: ${stop_loss_price:.2f} (-2.0%)")
                print(f"    止盈價: ${take_profit_price:.2f} (+4.0%)")
                print(f"    風險回報比: 1:2")
        
        # 保存決策記錄
        self.save_decisions(decisions)
        
        return decisions
    
    def generate_learning_report(self):
        """生成學習報告"""
        print("\n" + "=" * 60)
        print("📚 加密貨幣學習報告")
        print("=" * 60)
        
        report = {
            'report_date': datetime.now().isoformat(),
            'total_observations': len(self.observations),
            'observation_period': f"{self.learning_days}天",
            'key_learnings': [],
            'recommendations': []
        }
        
        # 總結學習點
        if hasattr(self, 'lessons_learned') and self.lessons_learned:
            report['key_learnings'] = self.lessons_learned[-5:]  # 最近5個學習點
        
        # 添加推薦
        report['recommendations'] = [
            "繼續觀察市場波動模式",
            "實踐2%風險管理紀律",
            "記錄每次觀察的見解",
            "比較不同加密貨幣的行為"
        ]
        
        # 顯示報告
        print(f"📅 報告日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"👀 觀察次數: {report['total_observations']}")
        print(f"⏱️  觀察期間: {report['observation_period']}")
        
        if report['key_learnings']:
            print(f"\n💡 關鍵學習點:")
            for learning in report['key_learnings']:
                print(f"  • {learning}")
        
        print(f"\n🎯 學習建議:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        # 保存報告
        report_file = os.path.join(self.data_dir, f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 學習報告已保存: {report_file}")
        
        return report
    
    def save_observation(self, observation):
        """保存觀察記錄"""
        obs_file = os.path.join(self.data_dir, "observations.json")
        
        # 讀取現有記錄
        if os.path.exists(obs_file):
            with open(obs_file, 'r') as f:
                observations = json.load(f)
        else:
            observations = []
        
        # 添加新記錄
        observations.append(observation)
        
        # 保存（只保留最近100條）
        if len(observations) > 100:
            observations = observations[-100:]
        
        with open(obs_file, 'w') as f:
            json.dump(observations, f, indent=2)
    
    def save_analysis(self, analysis):
        """保存分析結果"""
        analysis_file = os.path.join(self.data_dir, "analyses.json")
        
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analyses = json.load(f)
        else:
            analyses = []
        
        analyses.append(analysis)
        
        if len(analyses) > 50:
            analyses = analyses[-50:]
        
        with open(analysis_file, 'w') as f:
            json.dump(analyses, f, indent=2)
    
    def save_decisions(self, decisions):
        """保存決策記錄"""
        decisions_file = os.path.join(self.data_dir, "decisions.json")
        
        if os.path.exists(decisions_file):
            with open(decisions_file, 'r') as f:
                all_decisions = json.load(f)
        else:
            all_decisions = []
        
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'decisions': decisions
        }
        
        all_decisions.append(decision_record)
        
        if len(all_decisions) > 50:
            all_decisions = all_decisions[-50:]
        
        with open(decisions_file, 'w') as f:
            json.dump(all_decisions, f, indent=2)
    
    def run_learning_session(self, duration_hours=24):
        """運行學習觀察會話"""
        print("=" * 60)
        print("🧠 加密貨幣學習觀察會話開始")
        print("=" * 60)
        
        print(f"🎯 學習目標: 觀察加密貨幣市場 {duration_hours} 小時")
        print(f"📊 觀察對象: {', '.join(self.observation_symbols)}")
        print(f"⏰ 觀察間隔: 每 {self.observation_interval//3600} 小時")
        print(f"🛡️  學習重點: 風險管理、市場波動、交易心理")
        
        if not self.connect():
            print("❌ 連接失敗，學習會話中止")
            return
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        print(f"\n⏳ 會話時間: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        print("按 Ctrl+C 提前結束")
        
        observation_count = 0
        
        try:
            while datetime.now() < end_time:
                # 進行觀察
                observation = self.observe_market()
                observation_count += 1
                
                # 分析數據（至少2次觀察後）
                if observation_count >= 2:
                    self.analyze_observations()
                
                # 模擬風險管理
                self.simulate_risk_management(observation)
                
                # 記錄學習點
                if observation_count % 3 == 0:  # 每3次觀察記錄一次學習點
                    lesson = f"第{observation_count}次觀察: 市場持續波動，需要嚴格止損紀律"
                    self.lessons_learned.append(lesson)
                
                # 計算下次觀察時間
                next_observation = datetime.now() + timedelta(seconds=self.observation_interval)
                wait_time = (next_observation - datetime.now()).total_seconds()
                
                if wait_time > 0:
                    print(f"\n⏰ 下次觀察: {next_observation.strftime('%H:%M:%S')}")
                    print(f"  等待 {wait_time/60:.1f} 分鐘...")
                    time.sleep(min(wait_time, 300))  # 最多等待5分鐘
            
            # 會話結束
            print(f"\n✅ 學習會話完成！")
            print(f"   總觀察次數: {observation_count}")
            print(f"   總學習時間: {duration_hours} 小時")
            
        except KeyboardInterrupt:
            print(f"\n🛑 學習會話提前結束")
            print(f"   完成觀察次數: {observation_count}")
        
        # 生成最終報告
        self.generate_learning_report()
        
        print("\n" + "=" * 60)
        print("🎉 學習觀察會話結束")
        print("=" * 60)
        
        print(f"\n📁 學習數據保存在: {self.data_dir}")
        print(f"📊 觀察記錄: {self.data_dir}/observations.json")
        print(f"📈 分析結果: {self.data_dir}/analyses.json")
        print(f"🛡️  決策記錄: {self.data_dir}/decisions.json")
        
        print(f"\n💪 繼續學習，明天再觀察！")

def main():
    # 創建學習觀察器
    observer = CryptoLearningObserver()
    
    # 運行24小時學習會話
    observer.run_learning_session(duration_hours=24)

if __name__ == "__main__":
    main()