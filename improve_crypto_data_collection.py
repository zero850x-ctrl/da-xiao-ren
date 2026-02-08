#!/usr/bin/env python3
"""
立即改善加密貨幣數據收集工作
使用agent-browser自動化市場數據收集
"""

import os
import json
import time
from datetime import datetime
import subprocess

class CryptoDataCollector:
    def __init__(self):
        self.agent_browser_path = "/Users/gordonlui/.npm-global/bin/agent-browser"
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_collected_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 要監控的加密貨幣網站
        self.crypto_sites = {
            "coingecko": "https://www.coingecko.com",
            "coinmarketcap": "https://coinmarketcap.com",
            "binance": "https://www.binance.com/en/markets",
            "cryptopanic": "https://cryptopanic.com",  # 加密貨幣新聞
        }
        
        # 主要加密貨幣對
        self.main_cryptos = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOT"]
    
    def run_agent_browser(self, args, timeout=60):
        """運行agent-browser命令"""
        cmd = [self.agent_browser_path] + args
        
        try:
            print(f"執行: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"錯誤: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"超時: {timeout}秒")
            return None
        except Exception as e:
            print(f"異常: {e}")
            return None
    
    def collect_market_overview(self):
        """收集市場概覽數據"""
        print("\n📊 收集加密貨幣市場概覽")
        print("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_file = os.path.join(self.data_dir, f"market_overview_{timestamp}.json")
        
        # 打開CoinGecko網站
        print("1. 訪問CoinGecko...")
        self.run_agent_browser(["open", self.crypto_sites["coingecko"]])
        time.sleep(5)  # 等待頁面加載
        
        # 獲取頁面快照
        print("2. 獲取頁面快照...")
        snapshot = self.run_agent_browser(["snapshot", "-i", "--json"])
        
        if snapshot:
            try:
                data = json.loads(snapshot)
                
                # 保存原始快照
                snapshot_file = os.path.join(self.data_dir, f"snapshot_{timestamp}.json")
                with open(snapshot_file, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"✅ 快照已保存: {snapshot_file}")
                
                # 分析快照數據
                analysis = self.analyze_snapshot(data, timestamp)
                
                # 保存分析結果
                with open(data_file, "w") as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)
                print(f"✅ 市場數據已保存: {data_file}")
                
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析錯誤: {e}")
                return None
        else:
            print("❌ 無法獲取頁面快照")
            return None
    
    def analyze_snapshot(self, snapshot_data, timestamp):
        """分析快照數據"""
        analysis = {
            "timestamp": timestamp,
            "collection_time": datetime.now().isoformat(),
            "site": "coingecko",
            "market_summary": {},
            "top_cryptos": [],
            "analysis_notes": []
        }
        
        # 這裡可以添加實際的頁面分析邏輯
        # 由於不同網站結構不同，需要針對性分析
        
        # 模擬分析結果
        analysis["market_summary"] = {
            "total_market_cap": "待分析",
            "24h_volume": "待分析", 
            "btc_dominance": "待分析",
            "market_sentiment": "待分析"
        }
        
        for crypto in self.main_cryptos[:5]:  # 前5個主要加密貨幣
            analysis["top_cryptos"].append({
                "symbol": crypto,
                "price": "待分析",
                "24h_change": "待分析",
                "market_cap": "待分析"
            })
        
        analysis["analysis_notes"] = [
            "這是自動收集的市場數據快照",
            "需要進一步分析頁面結構來提取具體數據",
            "可以訓練AI識別價格和變化元素",
            "建議定期收集建立時間序列數據"
        ]
        
        return analysis
    
    def create_data_collection_workflow(self):
        """創建數據收集工作流腳本"""
        print("\n🔧 創建自動化數據收集工作流")
        print("=" * 50)
        
        workflow_script = os.path.join(self.data_dir, "automated_collection.sh")
        
        script_content = f'''#!/bin/bash
# 自動化加密貨幣數據收集工作流
# 生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo "🚀 啟動加密貨幣數據收集工作流"
echo "時間: $(date)"

# 設置PATH
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

# 數據目錄
DATA_DIR="{self.data_dir}"
mkdir -p "$DATA_DIR"

# 收集函數
collect_from_site() {{
    local site_name=$1
    local site_url=$2
    
    echo ""
    echo "📊 收集來自 $site_name 的數據..."
    echo "URL: $site_url"
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    # 打開網站
    agent-browser open "$site_url"
    sleep 10  # 等待頁面加載
    
    # 獲取快照
    agent-browser snapshot -i --json > "$DATA_DIR/{site_name}_snapshot_$TIMESTAMP.json"
    
    # 獲取頁面標題
    agent-browser get title --json > "$DATA_DIR/{site_name}_title_$TIMESTAMP.json"
    
    # 獲取當前URL
    agent-browser get url --json > "$DATA_DIR/{site_name}_url_$TIMESTAMP.json"
    
    echo "✅ $site_name 數據收集完成"
}}

# 收集各網站數據
collect_from_site "coingecko" "{self.crypto_sites['coingecko']}"
collect_from_site "coinmarketcap" "{self.crypto_sites['coinmarketcap']}"

# 生成報告
echo ""
echo "📋 數據收集報告:"
echo "收集時間: $(date)"
echo "數據目錄: $DATA_DIR"
echo "文件列表:"
ls -la "$DATA_DIR/"*.json 2>/dev/null | tail -5

echo ""
echo "🎉 數據收集工作流完成！"
echo "下一步: 分析收集的數據，提取有價值信息"
'''

        with open(workflow_script, "w") as f:
            f.write(script_content)
        
        os.chmod(workflow_script, 0o755)
        print(f"✅ 工作流腳本已創建: {workflow_script}")
        
        return workflow_script
    
    def create_learning_plan(self):
        """創建學習計劃"""
        print("\n📚 創建agent-browser學習計劃")
        print("=" * 50)
        
        plan_file = os.path.join(self.data_dir, "learning_plan.md")
        
        plan_content = f'''# 🕸️ agent-browser學習計劃
## 目標: 掌握加密貨幣數據收集自動化

### 階段1: 基礎掌握 (今天)
1. **基本命令學習**
   - agent-browser open <url>
   - agent-browser snapshot -i --json
   - agent-browser get title/url --json

2. **簡單網站測試**
   - 測試頁面: https://httpbin.org/html
   - 測試頁面: https://example.com
   - 練習獲取頁面結構

3. **數據保存練習**
   - 保存快照到JSON文件
   - 分析JSON結構
   - 識別有用數據

### 階段2: 實際應用 (周末)
1. **加密貨幣網站分析**
   - 分析CoinGecko頁面結構
   - 識別價格和變化元素
   - 練習提取特定數據

2. **創建收集腳本**
   - 編寫自動化收集腳本
   - 設置定時任務
   - 數據存儲和管理

3. **錯誤處理優化**
   - 處理網絡超時
   - 處理頁面變化
   - 數據驗證和清洗

### 階段3: 高級應用 (下周)
1. **多網站同時收集**
   - 並行收集多個網站
   - 數據去重和合併
   - 建立統一數據格式

2. **智能元素識別**
   - 訓練識別價格元素
   - 自動適應頁面變化
   - 提高數據準確性

3. **整合到學習系統**
   - 與現有加密貨幣學習系統整合
   - 自動生成市場報告
   - 實時監控和警報

### 學習資源
1. **官方文檔**
   - SKILL.md: {os.path.join(os.path.dirname(self.agent_browser_path), "../lib/node_modules/agent-browser/README.md")}
   - 示例和最佳實踐

2. **實踐項目**
   - 每日市場數據收集
   - 價格變化趨勢分析
   - 市場情緒監控

3. **社區資源**
   - OpenClaw Discord社區
   - GitHub問題和討論
   - 技術博客和教程

### 成功標準
- ✅ 能夠自動收集至少3個網站的數據
- ✅ 數據準確率達到90%以上
- ✅ 每天定時運行收集任務
- ✅ 整合到現有學習系統

### 時間安排
- **今天**: 完成階段1學習
- **周末**: 完成階段2實踐
- **下周**: 完成階段3整合
- **持續**: 優化和改進

開始你的agent-browser學習之旅吧！ 🚀
'''

        with open(plan_file, "w") as f:
            f.write(plan_content)
        
        print(f"✅ 學習計劃已創建: {plan_file}")
        return plan_file
    
    def run_improvement(self):
        """運行改善工作"""
        print("🚀 開始改善加密貨幣數據收集工作")
        print("=" * 60)
        
        # 1. 收集市場數據
        market_data = self.collect_market_overview()
        
        # 2. 創建自動化工作流
        workflow = self.create_data_collection_workflow()
        
        # 3. 創建學習計劃
        learning_plan = self.create_learning_plan()
        
        # 總結
        print("\n" + "=" * 60)
        print("🎉 加密貨幣數據收集改善完成！")
        print("=" * 60)
        
        print("\n📋 創建的文件:")
        print(f"• 數據目錄: {self.data_dir}")
        print(f"• 工作流腳本: {workflow}")
        print(f"• 學習計劃: {learning_plan}")
        
        if market_data:
            data_file = os.path.join(self.data_dir, f"market_overview_*.json")
            print(f"• 市場數據: {data_file}")
        
        print("\n🚀 下一步行動:")
        print("1. 運行工作流腳本: bash " + workflow)
        print("2. 學習agent-browser: 閱讀學習計劃")
        print("3. 測試其他網站: 修改腳本測試不同網站")
        print("4. 設置定時任務: 使用cron定期運行")
        
        print("\n💡 提示:")
        print("• 從簡單網站開始，逐步增加複雜度")
        print("• 尊重網站服務條款，合理設置請求間隔")
        print("• 保存會話狀態，避免重複登錄")
        print("• 定期備份收集的數據")
        
        print("\n🎯 改善目標:")
        print("• 自動化數據收集，節省時間")
        print("• 提高數據質量和覆蓋面")
        print("• 建立系統化的數據管道")
        print("• 為分析和決策提供更好支持")

def main():
    collector = CryptoDataCollector()
    collector.run_improvement()

if __name__ == "__main__":
    main()