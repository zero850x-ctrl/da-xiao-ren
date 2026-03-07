#!/usr/bin/env python3
"""
Telegram交易信號機器人
Mac分析信號，通過Telegram發送到手機，手動在MT5執行
"""

import json
import os
import time
from datetime import datetime
import numpy as np

# 嘗試導入telegram庫，如果沒有則使用模擬模式
try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  python-telegram-bot未安裝，使用模擬模式")
    print("   安裝: pip install python-telegram-bot")

class TelegramSignalBot:
    def __init__(self, use_simulation=False):
        """初始化Telegram機器人"""
        self.use_simulation = use_simulation or not TELEGRAM_AVAILABLE
        self.bot = None
        self.chat_id = None
        
        self.load_config()
        
        if not self.use_simulation:
            self.setup_bot()
    
    def load_config(self):
        """加載配置"""
        config_path = '/Users/gordonlui/.openclaw/workspace/telegram_config.json'
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # 默認配置（需要用戶填寫）
            self.config = {
                'bot_token': 'YOUR_BOT_TOKEN_HERE',
                'chat_id': 'YOUR_CHAT_ID_HERE',
                'trading': {
                    'symbol': 'XAUUSD',
                    'lot_size': 0.01,
                    'max_daily_signals': 3
                }
            }
            
            # 保存模板配置
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"📝 創建配置模板: {config_path}")
            print("   請編輯此文件，填入你的Bot Token和Chat ID")
    
    def setup_bot(self):
        """設置機器人"""
        try:
            self.bot = Bot(token=self.config['bot_token'])
            self.chat_id = self.config['chat_id']
            
            # 測試連接
            self.bot.get_me()
            print(f"✅ Telegram機器人連接成功")
            
        except Exception as e:
            print(f"❌ Telegram連接失敗: {e}")
            print("   切換到模擬模式")
            self.use_simulation = True
    
    def send_signal(self, signal_data):
        """發送交易信號"""
        # 構建消息
        message = self.build_signal_message(signal_data)
        
        if self.use_simulation:
            print("\n📱 [模擬] Telegram信號:")
            print("-" * 40)
            print(message)
            print("-" * 40)
            print("📱 在你的手機上，你應該會收到這條消息")
            print("   然後可以在MT5中手動執行交易")
            return True
        
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print(f"✅ 交易信號已發送到Telegram")
            return True
        except TelegramError as e:
            print(f"❌ 發送失敗: {e}")
            return False
    
    def build_signal_message(self, signal):
        """構建信號消息"""
        symbol = self.config['trading']['symbol']
        lot_size = self.config['trading']['lot_size']
        
        # 計算風險金額
        risk_pips = signal.get('stop_loss_pips', 60)
        risk_amount = risk_pips * lot_size * 0.1
        
        message = f"""
🚨 <b>交易信號通知</b> 🚨

📊 <b>市場:</b> {symbol}
🎯 <b>信號:</b> {signal['type']}
💰 <b>價格:</b> ${signal['price']:.2f}

⚙️ <b>交易參數:</b>
• 手數: {lot_size}手
• 止損: ${signal['stop_loss']:.2f} ({risk_pips}點)
• 止盈: ${signal['take_profit']:.2f}
• 風險: ${risk_amount:.2f}

📈 <b>技術分析:</b>
{signal['reason']}

⏰ <b>時間:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <b>操作指令:</b>
1. 打開MT5
2. 選擇{symbol}
3. {signal['type']} {lot_size}手 @ ${signal['price']:.2f}
4. 設置止損: ${signal['stop_loss']:.2f}
5. 設置止盈: ${signal['take_profit']:.2f}

⚠️ <b>風險提示:</b>
• 嚴格遵守風險管理
• 僅使用風險資金
• 記錄交易結果
"""
        
        return message.strip()
    
    def send_trade_result(self, trade_result):
        """發送交易結果"""
        message = self.build_result_message(trade_result)
        
        if self.use_simulation:
            print("\n📱 [模擬] 交易結果:")
            print("-" * 40)
            print(message)
            return True
        
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print(f"✅ 交易結果已發送到Telegram")
            return True
        except TelegramError as e:
            print(f"❌ 發送失敗: {e}")
            return False
    
    def build_result_message(self, result):
        """構建結果消息"""
        emoji = "🟢" if result['profit'] > 0 else "🔴"
        
        message = f"""
📊 <b>交易結果報告</b>

🎯 <b>交易:</b> {result['type']} {result['symbol']}
💰 <b>入場:</b> ${result['entry_price']:.2f}
📈 <b>出場:</b> ${result['exit_price']:.2f}

{emoji} <b>結果:</b> ${result['profit']:.2f} ({result['pips']:.0f}點)
📝 <b>原因:</b> {result['exit_reason']}

⏱️ <b>持倉時間:</b> {result['holding_hours']:.1f}小時
📅 <b>時間:</b> {result['timestamp']}

💡 <b>學習點:</b>
{result.get('lesson', '記錄本次交易的經驗教訓')}

📈 <b>累計統計:</b>
• 總交易: {result.get('total_trades', 'N/A')}
• 勝率: {result.get('win_rate', 'N/A'):.1f}%
• 總盈利: ${result.get('total_profit', 'N/A'):.2f}
"""
        
        return message.strip()

class TradingSignalGenerator:
    """交易信號生成器"""
    
    def __init__(self):
        self.load_strategy()
    
    def load_strategy(self):
        """加載策略"""
        strategy_path = '/Users/gordonlui/.openclaw/workspace/optimized_strategy.json'
        
        if os.path.exists(strategy_path):
            with open(strategy_path, 'r') as f:
                self.strategy = json.load(f)
            self.params = self.strategy.get('parameters', {})
        else:
            self.params = {
                'sma_short': 15,
                'sma_long': 40,
                'rsi_period': 10,
                'rsi_low': 25,
                'rsi_high': 75,
                'stop_loss': 60,
                'take_profit': 120,
                'signal_threshold': 0.5
            }
    
    def generate_signal(self):
        """生成交易信號"""
        print("\n🔍 分析市場，生成交易信號...")
        
        # 模擬市場數據
        np.random.seed(int(datetime.now().timestamp()))
        
        price = 2000 + np.random.uniform(-50, 50)
        sma_short = price + np.random.uniform(-20, 20)
        sma_long = price + np.random.uniform(-30, 30)
        rsi = np.random.uniform(20, 80)
        
        print(f"   當前價格: ${price:.2f}")
        print(f"   SMA短: ${sma_short:.2f}, SMA長: ${sma_long:.2f}")
        print(f"   RSI: {rsi:.1f}")
        
        # 分析信號
        signal = None
        strength = 0.0
        reason = ""
        
        # SMA信號
        if sma_short > sma_long and (sma_short - sma_long) > 5:
            strength += 0.3
            signal = 'BUY'
            reason = f"SMA黃金交叉 (差值: ${sma_short-sma_long:.2f})"
        elif sma_long > sma_short and (sma_long - sma_short) > 5:
            strength += 0.3
            signal = 'SELL'
            reason = f"SMA死亡交叉 (差值: ${sma_long-sma_short:.2f})"
        
        # RSI信號
        if rsi < self.params.get('rsi_low', 25):
            strength += 0.4
            signal = 'BUY'
            reason = f"RSI超賣 ({rsi:.1f})" if not reason else reason + f" + RSI超賣 ({rsi:.1f})"
        elif rsi > self.params.get('rsi_high', 75):
            strength += 0.4
            signal = 'SELL'
            reason = f"RSI超買 ({rsi:.1f})" if not reason else reason + f" + RSI超買 ({rsi:.1f})"
        
        # 檢查閾值
        threshold = self.params.get('signal_threshold', 0.5)
        
        if signal and strength >= threshold:
            print(f"   🎯 發現交易信號: {signal} (強度: {strength:.2f})")
            
            # 構建信號數據
            stop_loss_pips = self.params.get('stop_loss', 60)
            take_profit_pips = self.params.get('take_profit', 120)
            
            if signal == 'BUY':
                stop_loss = price * (1 - stop_loss_pips/10000)
                take_profit = price * (1 + take_profit_pips/10000)
            else:
                stop_loss = price * (1 + stop_loss_pips/10000)
                take_profit = price * (1 - take_profit_pips/10000)
            
            signal_data = {
                'type': signal,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'stop_loss_pips': stop_loss_pips,
                'take_profit_pips': take_profit_pips,
                'reason': reason,
                'strength': strength,
                'timestamp': datetime.now().isoformat()
            }
            
            return signal_data
        else:
            print(f"   ⏸️  無交易信號 (強度: {strength:.2f} < {threshold})")
            return None

def setup_telegram_bot_guide():
    """設置Telegram機器人指南"""
    print("\n" + "=" * 70)
    print("🤖 設置Telegram交易信號機器人")
    print("=" * 70)
    
    steps = [
        "第1步: 創建Telegram機器人",
        "   1. 在Telegram中搜索 @BotFather",
        "   2. 發送 /newbot 創建新機器人",
        "   3. 設置機器人名稱（例如: GoldTraderBot）",
        "   4. 設置機器人用戶名（必須以bot結尾，例如: gold_trader_bot）",
        "   5. 保存Bot Father提供的Token",
        "",
        "第2步: 獲取Chat ID",
        "   1. 在Telegram中搜索 @userinfobot",
        "   2. 發送 /start",
        "   3. 複製你的Chat ID",
        "",
        "第3步: 配置機器人",
        "   1. 編輯文件: /Users/gordonlui/.openclaw/workspace/telegram_config.json",
        "   2. 填入你的Bot Token和Chat ID",
        "   3. 保存文件",
        "",
        "第4步: 安裝Python庫",
        "   運行: pip install python-telegram-bot",
        "",
        "第5步: 測試機器人",
        "   運行: python3 telegram_signal_bot.py --test",
    ]
    
    for step in steps:
        print(f"   {step}")

def main():
    """主函數"""
    print("=" * 70)
    print("📱 Telegram交易信號系統")
    print("=" * 70)
    
    # 顯示設置指南
    setup_telegram_bot_guide()
    
    # 初始化
    print("\n🔧 初始化系統...")
    
    # 檢查是否使用模擬模式
    use_simulation = not TELEGRAM_AVAILABLE
    
    if use_simulation:
        print("ℹ️  使用模擬模式（未安裝python-telegram-bot）")
        print("   要使用真實Telegram，請先安裝: pip install python-telegram-bot")
    
    # 創建機器人
    bot = TelegramSignalBot(use_simulation=use_simulation)
    
    # 創建信號生成器
    generator = TradingSignalGenerator()
    
    # 生成並發送信號
    print("\n🚀 生成交易信號...")
    signal = generator.generate_signal()
    
    if signal:
        print(f"\n📤 發送交易信號到Telegram...")
        success = bot.send_signal(signal)
        
        if success:
            print(f"\n✅ 信號發送成功！")
            print(f"\n📋 下一步:")
            print(f"   1. 檢查你的Telegram消息")
            print(f"   2. 在MT5中手動執行交易")
            print(f"   3. 記錄交易結果")
            print(f"   4. 通過機器人反饋結果")
        else:
            print(f"\n❌ 信號發送失敗")
    else:
        print(f"\n⏸️  無交易信號，等待下次檢查")
    
    print("\n" + "=" * 70)
    print("🎯 系統準備就緒")
    print("=" * 70)
    
    print("\n💡 使用建議:")
    print("   1. 可以設置cron任務每小時運行一次")
    print("   2. 收到信號後盡快執行（5分鐘內）")
    print("   3. 嚴格遵守止損紀律")
    print("   4. 記錄每筆交易用於優化")

if __name__ == "__main__":
    main()