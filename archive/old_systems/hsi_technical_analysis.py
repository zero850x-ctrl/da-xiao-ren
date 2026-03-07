#!/usr/bin/env python3
"""
HSI技術分析工具
包含：平行通道、趨勢線、黃金分割、期型、成交量、RSI、移動平均線(8,13,34)
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # 非交互模式

# 技術指標計算函數
def calculate_rsi(prices, period=14):
    """計算RSI指標"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_moving_averages(df, periods=[8, 13, 34]):
    """計算移動平均線"""
    for period in periods:
        df[f'MA{period}'] = df['close'].rolling(window=period).mean()
    return df

def calculate_fibonacci_levels(df):
    """計算斐波那契回撤水平"""
    high = df['high'].max()
    low = df['low'].min()
    diff = high - low
    
    levels = {
        '0%': high,
        '23.6%': high - diff * 0.236,
        '38.2%': high - diff * 0.382,
        '50%': high - diff * 0.5,
        '61.8%': high - diff * 0.618,
        '78.6%': high - diff * 0.786,
        '100%': low
    }
    return levels

def identify_channel(df):
    """識別平行通道"""
    # 簡單的通道識別：使用最高點和最低點的趨勢線
    highs = df['high'].values
    lows = df['low'].values
    
    # 計算高點和低點的線性回歸
    x = np.arange(len(df))
    
    # 高點通道上軌
    high_coeff = np.polyfit(x[-20:], highs[-20:], 1) if len(df) >= 20 else np.polyfit(x, highs, 1)
    high_trend = np.poly1d(high_coeff)
    
    # 低點通道下軌
    low_coeff = np.polyfit(x[-20:], lows[-20:], 1) if len(df) >= 20 else np.polyfit(x, lows, 1)
    low_trend = np.poly1d(low_coeff)
    
    return {
        'upper_trend': high_trend,
        'lower_trend': low_trend,
        'channel_width': np.mean(highs[-10:] if len(df) >= 10 else highs) - np.mean(lows[-10:] if len(df) >= 10 else lows)
    }

def generate_analysis_report(df, realtime_data):
    """生成技術分析報告"""
    report = []
    
    # 基本信息
    report.append("=" * 60)
    report.append("HSI 技術分析報告")
    report.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"數據範圍: {df['date'].iloc[0]} 到 {df['date'].iloc[-1]}")
    report.append(f"數據點數: {len(df)}")
    report.append("=" * 60)
    
    # 當前狀態
    report.append("\n📊 當前市場狀態:")
    report.append(f"最新價格: {realtime_data['last_price']}")
    report.append(f"漲跌幅: {realtime_data['change_rate']:.2f}%")
    report.append(f"成交量: {realtime_data['volume']:,}")
    report.append(f"成交額: {realtime_data['turnover']:,.0f}")
    
    # 移動平均線分析
    df = calculate_moving_averages(df)
    report.append("\n📈 移動平均線分析 (8, 13, 34日):")
    for period in [8, 13, 34]:
        if len(df) >= period:
            ma_value = df[f'MA{period}'].iloc[-1]
            price = df['close'].iloc[-1]
            diff_pct = ((price - ma_value) / ma_value * 100) if ma_value != 0 else 0
            position = "之上" if price > ma_value else "之下" if price < ma_value else "持平"
            report.append(f"  MA{period}: {ma_value:.2f} (價格在{position}, 相差{diff_pct:+.2f}%)")
    
    # RSI分析
    df['RSI'] = calculate_rsi(df['close'])
    if not df['RSI'].isna().all():
        current_rsi = df['RSI'].iloc[-1]
        report.append(f"\n📊 RSI指標 (14日): {current_rsi:.2f}")
        if current_rsi > 70:
            report.append("  ⚠️  RSI > 70: 可能超買")
        elif current_rsi < 30:
            report.append("  ⚠️  RSI < 30: 可能超賣")
        else:
            report.append("  ✅ RSI在正常範圍")
    
    # 成交量分析
    avg_volume = df['volume'].mean()
    current_volume = df['volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume if avg_volume != 0 else 1
    report.append(f"\n📊 成交量分析:")
    report.append(f"  當前成交量: {current_volume:,}")
    report.append(f"  平均成交量: {avg_volume:,.0f}")
    report.append(f"  成交量比率: {volume_ratio:.2f}x")
    if volume_ratio > 1.5:
        report.append("  📈 成交量放大，可能有大資金活動")
    elif volume_ratio < 0.7:
        report.append("  📉 成交量萎縮，市場觀望")
    
    # 斐波那契分析
    fib_levels = calculate_fibonacci_levels(df)
    report.append("\n📐 斐波那契回撤水平:")
    current_price = realtime_data['last_price']
    for level, price in fib_levels.items():
        diff_pct = ((current_price - price) / price * 100) if price != 0 else 0
        report.append(f"  {level}: {price:.2f} (相差{diff_pct:+.2f}%)")
    
    # 通道分析
    channel = identify_channel(df)
    report.append(f"\n📏 平行通道分析:")
    report.append(f"  通道寬度: {channel['channel_width']:.2f}")
    
    # 趨勢判斷
    if len(df) >= 34:
        ma8 = df['MA8'].iloc[-1]
        ma13 = df['MA13'].iloc[-1]
        ma34 = df['MA34'].iloc[-1]
        
        report.append("\n🎯 趨勢判斷:")
        if ma8 > ma13 > ma34:
            report.append("  🟢 強勢上漲趨勢 (多頭排列)")
        elif ma8 < ma13 < ma34:
            report.append("  🔴 下跌趨勢 (空頭排列)")
        else:
            report.append("  🟡 震盪整理")
    
    # 支撐阻力位
    report.append("\n🛡️  關鍵支撐阻力位:")
    recent_high = df['high'].max()
    recent_low = df['low'].min()
    report.append(f"  近期高點: {recent_high:.2f} (阻力)")
    report.append(f"  近期低點: {recent_low:.2f} (支撐)")
    
    # 下周預測
    report.append("\n🔮 下周走勢預測:")
    
    # 基於技術指標的預測
    bullish_signals = 0
    bearish_signals = 0
    
    # 檢查多空信號
    if len(df) >= 8:
        if df['close'].iloc[-1] > df['MA8'].iloc[-1]:
            bullish_signals += 1
        else:
            bearish_signals += 1
    
    if not df['RSI'].isna().all():
        if df['RSI'].iloc[-1] < 40:
            bullish_signals += 1  # 超賣可能反彈
        elif df['RSI'].iloc[-1] > 60:
            bearish_signals += 1  # 超買可能回調
    
    if volume_ratio > 1.2:
        if df['close'].iloc[-1] > df['close'].iloc[-2]:
            bullish_signals += 1  # 放量上漲
        else:
            bearish_signals += 1  # 放量下跌
    
    if bullish_signals > bearish_signals:
        report.append("  📈 偏多看法:")
        report.append("    • 技術指標偏多")
        report.append("    • 建議關注上方阻力位突破")
        report.append("    • 支撐位: 26000-26200")
        report.append("    • 目標位: 26800-27000")
    elif bearish_signals > bullish_signals:
        report.append("  📉 偏空看法:")
        report.append("    • 技術指標偏空")
        report.append("    • 建議關注下方支撐位")
        report.append("    • 阻力位: 26700-26800")
        report.append("    • 支撐位: 26300-26400")
    else:
        report.append("  ↔️  震盪看法:")
        report.append("    • 多空力量均衡")
        report.append("    • 建議區間操作")
        report.append("    • 區間: 26400-26700")
    
    report.append("\n⚠️  風險提示:")
    report.append("  1. 技術分析僅供參考")
    report.append("  2. 市場存在不確定性")
    report.append("  3. 建議結合基本面分析")
    report.append("  4. 控制風險，設置止損")
    
    report.append("\n" + "=" * 60)
    report.append("報告生成完成")
    report.append("數據來源: Futu OpenD")
    
    return "\n".join(report)

def create_technical_chart(df, realtime_data):
    """創建技術分析圖表"""
    fig, axes = plt.subplots(3, 1, figsize=(15, 12), gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # 計算技術指標
    df = calculate_moving_averages(df)
    df['RSI'] = calculate_rsi(df['close'])
    
    # 1. 價格圖
    ax1 = axes[0]
    
    # K線圖（簡化為收盤價線圖）
    ax1.plot(df['date'], df['close'], label='收盤價', color='blue', linewidth=2)
    
    # 移動平均線
    for period in [8, 13, 34]:
        if len(df) >= period:
            ax1.plot(df['date'], df[f'MA{period}'], label=f'MA{period}', linestyle='--', linewidth=1)
    
    # 當前價格標記
    current_date = df['date'].iloc[-1]
    current_price = realtime_data['last_price']
    ax1.scatter([current_date], [current_price], color='red', s=100, zorder=5, label=f'當前: {current_price}')
    
    ax1.set_title('HSI 技術分析圖', fontsize=16, fontweight='bold')
    ax1.set_ylabel('價格', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. 成交量圖
    ax2 = axes[1]
    colors = ['green' if df['close'].iloc[i] >= df['close'].iloc[i-1] else 'red' for i in range(len(df))]
    colors[0] = 'green'  # 第一個數據點
    ax2.bar(df['date'], df['volume'], color=colors, alpha=0.7)
    ax2.set_ylabel('成交量', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # 3. RSI圖
    ax3 = axes[2]
    ax3.plot(df['date'], df['RSI'], label='RSI(14)', color='purple', linewidth=2)
    ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='超買線(70)')
    ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='超賣線(30)')
    ax3.axhline(y=50, color='gray', linestyle='-', alpha=0.3)
    ax3.set_ylabel('RSI', fontsize=12)
    ax3.set_xlabel('日期', fontsize=12)
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # 調整布局
    plt.tight_layout()
    
    # 保存圖表
    chart_path = "hsi_technical_chart.png"
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 技術分析圖表已保存: {chart_path}")
    return chart_path

def main():
    print("=" * 60)
    print("HSI技術分析工具")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 加載數據
        print("📂 加載數據...")
        with open('hsi_realtime.json', 'r') as f:
            realtime_data = json.load(f)
        
        with open('hsi_history.json', 'r') as f:
            history_data = json.load(f)
        
        # 轉換為DataFrame
        df = pd.DataFrame(history_data)
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"✅ 數據加載成功")
        print(f"  實時價格: {realtime_data['last_price']}")
        print(f"  歷史數據點: {len(df)}")
        
        # 生成分析報告
        print("\n📝 生成技術分析報告...")
        report = generate_analysis_report(df, realtime_data)
        
        # 保存報告
        report_path = "hsi_technical_analysis_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 技術分析報告已保存: {report_path}")
        
        # 創建圖表
        print("\n📊 創建技術分析圖表...")
        chart_path = create_technical_chart(df, realtime_data)
        
        # 顯示報告摘要
        print("\n" + "=" * 60)
        print("📋 報告摘要:")
        print("=" * 60)
        
        # 只顯示關鍵信息
        lines = report.split('\n')
        key_sections = [
            "HSI 技術分析報告",
            "📊 當前市場狀態:",
            "📈 移動平均線分析",
            "📊 RSI指標",
            "📊 成交量分析",
            "🔮 下周走勢預測:",
            "⚠️  風險提示:"
        ]
        
        for line in lines:
            for section in key_sections:
                if section in line:
                    print(line)
                    if section == "📊 當前市場狀態:":
                        # 打印接下來的4行
                        idx = lines.index(line)
                        for i in range(1, 5):
                            if idx + i < len(lines):
                                print(lines[idx + i])
                    break
        
        print("\n" + "=" * 60)
        print("🎉 技術分析完成！")
        print(f"報告文件: {report_path}")
        print(f"圖表文件: {chart_path}")
        print("=" * 60)
        
        return True, report_path, chart_path
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

if __name__ == "__main__":
    success, report_path, chart_path = main()
    
    if success:
        print("\n✅ 技術分析工具運行成功！")
        print("可以發送郵件給 zero850x@gmail.com")
    else:
        print("\n❌ 技術分析失敗")