#!/usr/bin/env python3
"""
黃金自動交易cron任務
每小時運行一次，執行0.01手交易
"""

import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加日誌記錄
import logging

# 設置日誌
log_dir = '/Users/gordonlui/.openclaw/workspace/logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/gold_trader_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GoldAutoTraderCron:
    def __init__(self):
        """初始化自動交易cron任務"""
        self.config_path = '/Users/gordonlui/.openclaw/workspace/optimized_strategy.json'
        self.trades_log_path = '/Users/gordonlui/.openclaw/workspace/gold_trades_log.json'
        self.daily_stats_path = '/Users/gordonlui/.openclaw/workspace/daily_stats.json'
        
        self.load_config()
        self.load_trades_log()
        
        logger.info("=" * 60)
        logger.info("🏆 黃金自動交易cron任務啟動")
        logger.info("=" * 60)
        logger.info(f"   策略: {self.config['optimized_strategy']}")
        logger.info(f"   最大手數: {self.config['max_lot_size']}手")
        logger.info(f"   初始資金: ${self.config['initial_balance']:.2f}")
    
    def load_config(self):
        """加載配置"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"✅ 加載配置: {self.config_path}")
        except Exception as e:
            logger.error(f"❌ 加載配置失敗: {e}")
            # 使用默認配置
            self.config = {
                'optimized_strategy': '平衡策略',
                'parameters': {
                    'sma_short': 15,
                    'sma_long': 40,
                    'rsi_period': 10,
                    'rsi_low': 25,
                    'rsi_high': 75,
                    'stop_loss': 60,
                    'take_profit': 120,
                    'threshold': 0.5
                },
                'max_lot_size': 0.01,
                'initial_balance': 1000
            }
    
    def load_trades_log(self):
        """加載交易記錄"""
        try:
            if os.path.exists(self.trades_log_path):
                with open(self.trades_log_path, 'r') as f:
                    self.trades_log = json.load(f)
                logger.info(f"✅ 加載交易記錄: {len(self.trades_log)}筆")
            else:
                self.trades_log = []
                logger.info("ℹ️  無交易記錄，創建新文件")
        except Exception as e:
            logger.error(f"❌ 加載交易記錄失敗: {e}")
            self.trades_log = []
    
    def save_trades_log(self):
        """保存交易記錄"""
        try:
            with open(self.trades_log_path, 'w') as f:
                json.dump(self.trades_log, f, indent=2, default=str)
            logger.info(f"✅ 保存交易記錄: {len(self.trades_log)}筆")
        except Exception as e:
            logger.error(f"❌ 保存交易記錄失敗: {e}")
    
    def update_daily_stats(self):
        """更新每日統計"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(self.daily_stats_path):
                with open(self.daily_stats_path, 'r') as f:
                    daily_stats = json.load(f)
            else:
                daily_stats = {}
            
            # 計算今日交易
            today_trades = [t for t in self.trades_log 
                           if t.get('timestamp', '').startswith(today)]
            
            today_stats = {
                'date': today,
                'total_trades': len(today_trades),
                'winning_trades': len([t for t in today_trades if t.get('profit', 0) > 0]),
                'losing_trades': len([t for t in today_trades if t.get('profit', 0) <= 0]),
                'total_profit': sum(t.get('profit', 0) for t in today_trades),
                'max_lot_used': max([t.get('lot_size', 0) for t in today_trades], default=0)
            }
            
            daily_stats[today] = today_stats
            
            with open(self.daily_stats_path, 'w') as f:
                json.dump(daily_stats, f, indent=2)
            
            logger.info(f"📊 今日統計: {today_stats['total_trades']}筆交易, "
                       f"盈利${today_stats['total_profit']:.2f}")
            
        except Exception as e:
            logger.error(f"❌ 更新每日統計失敗: {e}")
    
    def check_trading_hours(self):
        """檢查交易時間"""
        now = datetime.now()
        hour = now.hour
        
        # 黃金主要交易時段 (考慮時區)
        # 倫敦: 8:00-16:00 UTC (16:00-00:00 HKT)
        # 紐約: 13:00-22:00 UTC (21:00-06:00 HKT)
        # 重疊時段: 13:00-16:00 UTC (21:00-00:00 HKT)
        
        # 香港時間交易時段 (簡化)
        trading_hours = list(range(9, 24)) + list(range(0, 3))  # 09:00-03:00
        
        if hour in trading_hours:
            logger.info(f"✅ 交易時段內 ({hour:02d}:00)")
            return True
        else:
            logger.info(f"⏸️  非交易時段 ({hour:02d}:00)，跳過")
            return False
    
    def check_daily_limit(self):
        """檢查每日交易限制"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_trades = [t for t in self.trades_log 
                       if t.get('timestamp', '').startswith(today)]
        
        max_daily_trades = self.config.get('max_daily_trades', 3)
        
        if len(today_trades) >= max_daily_trades:
            logger.warning(f"⚠️  已達每日交易上限 ({len(today_trades)}/{max_daily_trades})")
            return False
        
        logger.info(f"📈 今日交易: {len(today_trades)}/{max_daily_trades}")
        return True
    
    def simulate_market_data(self):
        """模擬市場數據（實際使用時替換為MT5 API）"""
        logger.info("📊 獲取市場數據...")
        
        # 模擬當前價格
        np.random.seed(int(datetime.now().timestamp()) % 1000)
        base_price = 2000 + np.random.uniform(-100, 100)
        current_price = base_price + np.random.normal(0, 5)
        
        # 模擬技術指標
        sma_short = current_price + np.random.uniform(-20, 20)
        sma_long = current_price + np.random.uniform(-30, 30)
        rsi = np.random.uniform(20, 80)
        
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'price': current_price,
            'sma_short': sma_short,
            'sma_long': sma_long,
            'rsi': rsi,
            'volume': np.random.randint(1000, 5000)
        }
        
        logger.info(f"   當前價格: ${current_price:.2f}")
        logger.info(f"   SMA15: ${sma_short:.2f}, SMA40: ${sma_long:.2f}")
        logger.info(f"   RSI: {rsi:.1f}")
        
        return market_data
    
    def generate_signal(self, market_data):
        """生成交易信號"""
        params = self.config['parameters']
        
        signal = None
        reason = ""
        strength = 0.0
        
        # SMA信號
        if market_data['sma_short'] > market_data['sma_long']:
            diff = market_data['sma_short'] - market_data['sma_long']
            if diff > 5:  # 明顯差異
                signal = 'BUY'
                reason = f"SMA黃金交叉 (差值: ${diff:.2f})"
                strength += 0.3
        elif market_data['sma_long'] > market_data['sma_short']:
            diff = market_data['sma_long'] - market_data['sma_short']
            if diff > 5:
                signal = 'SELL'
                reason = f"SMA死亡交叉 (差值: ${diff:.2f})"
                strength += 0.3
        
        # RSI信號
        rsi = market_data['rsi']
        if rsi < params['rsi_low']:
            signal = 'BUY'
            reason = f"RSI超賣 ({rsi:.1f})"
            strength += 0.4
        elif rsi > params['rsi_high']:
            signal = 'SELL'
            reason = f"RSI超買 ({rsi:.1f})"
            strength += 0.4
        
        # 檢查信號強度
        if strength < params['threshold']:
            logger.info(f"ℹ️  信號強度不足 ({strength:.2f} < {params['threshold']})")
            return None, None, None
        
        return signal, reason, strength
    
    def execute_trade(self, signal, reason, strength, market_data):
        """執行交易"""
        params = self.config['parameters']
        max_lot = self.config['max_lot_size']
        
        # 計算手數（考慮信號強度）
        lot_size = max_lot * strength
        lot_size = max(0.01, min(max_lot, lot_size))
        
        entry_price = market_data['price']
        
        # 計算止損止盈
        if signal == 'BUY':
            stop_loss = entry_price * (1 - params['stop_loss']/10000)  # 點數轉百分比
            take_profit = entry_price * (1 + params['take_profit']/10000)
        else:  # SELL
            stop_loss = entry_price * (1 + params['stop_loss']/10000)
            take_profit = entry_price * (1 - params['take_profit']/10000)
        
        # 計算風險
        risk_pips = params['stop_loss']
        risk_amount = risk_pips * lot_size * 0.1  # 0.01手每點$0.01
        
        # 創建交易記錄
        trade = {
            'id': len(self.trades_log) + 1,
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'reason': reason,
            'strength': strength,
            'lot_size': lot_size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_pips': risk_pips,
            'risk_amount': risk_amount,
            'status': 'PENDING'  # 等待結果
        }
        
        # 模擬交易結果（實際使用時由市場決定）
        # 70%勝率
        if np.random.random() < 0.7:
            profit_pips = np.random.randint(params['take_profit'] * 0.8, params['take_profit'] * 1.2)
            profit_amount = profit_pips * lot_size * 0.1
            exit_price = entry_price + (profit_pips/10) if signal == 'BUY' else entry_price - (profit_pips/10)
            exit_reason = 'TAKE_PROFIT'
            result_emoji = "🟢"
        else:
            loss_pips = np.random.randint(params['stop_loss'] * 0.5, params['stop_loss'])
            profit_amount = -loss_pips * lot_size * 0.1
            exit_price = entry_price - (loss_pips/10) if signal == 'BUY' else entry_price + (loss_pips/10)
            exit_reason = 'STOP_LOSS'
            result_emoji = "🔴"
        
        # 更新交易記錄
        trade.update({
            'exit_price': exit_price,
            'profit_pips': profit_pips if profit_amount > 0 else -loss_pips,
            'profit_amount': profit_amount,
            'exit_reason': exit_reason,
            'status': 'CLOSED'
        })
        
        self.trades_log.append(trade)
        
        # 記錄交易
        logger.info(f"💼 執行交易:")
        logger.info(f"   信號: {signal}")
        logger.info(f"   原因: {reason}")
        logger.info(f"   手數: {lot_size}手")
        logger.info(f"   入場: ${entry_price:.2f}")
        logger.info(f"   結果: {result_emoji} ${profit_amount:.2f} ({trade['profit_pips']:.0f}點)")
        logger.info(f"   退出: {exit_reason}")
        
        return trade
    
    def run(self):
        """運行cron任務"""
        logger.info(f"\n⏰ Cron任務執行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 檢查交易時間
        if not self.check_trading_hours():
            return
        
        # 檢查每日限制
        if not self.check_daily_limit():
            return
        
        # 獲取市場數據
        market_data = self.simulate_market_data()
        
        # 生成信號
        signal, reason, strength = self.generate_signal(market_data)
        
        if not signal:
            logger.info("ℹ️  無交易信號")
            return
        
        # 執行交易
        trade = self.execute_trade(signal, reason, strength, market_data)
        
        # 保存記錄
        self.save_trades_log()
        self.update_daily_stats()
        
        # 生成報告
        self.generate_report()
    
    def generate_report(self):
        """生成報告"""
        if not self.trades_log:
            return
        
        # 計算總統計
        total_trades = len(self.trades_log)
        winning_trades = [t for t in self.trades_log if t.get('profit_amount', 0) > 0]
        losing_trades = [t for t in self.trades_log if t.get('profit_amount', 0) <= 0]
        
        total_profit = sum(t.get('profit_amount', 0) for t in self.trades_log)
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        
        logger.info(f"\n📊 總計報告:")
        logger.info(f"   總交易次數: {total_trades}")
        logger.info(f"   盈利交易: {len(winning_trades)} ({win_rate:.1f}%)")
        logger.info(f"   虧損交易: {len(losing_trades)} ({100-win_rate:.1f}%)")
        logger.info(f"   總盈利: ${total_profit:.2f}")
        
        # 保存報告
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'recent_trades': self.trades_log[-5:] if len(self.trades_log) >= 5 else self.trades_log
        }
        
        report_path = f'{log_dir}/trader_report_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"✅ 報告已保存: {report_path}")

def main():
    """主函數"""
    try:
        trader = GoldAutoTraderCron()
        trader.run()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Cron任務完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Cron任務失敗: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()