#!/bin/bash

echo "=== Cursor CLI 安裝驗證 ==="
echo ""

# 檢查安裝
echo "1. 檢查安裝狀態:"
which agent
agent --version
echo ""

# 檢查系統信息
echo "2. 系統信息:"
agent about 2>&1 | head -20
echo ""

# 創建一個簡單的測試
echo "3. 創建測試文件:"
cat > /tmp/test_cursor.py << 'EOF'
def calculate_fibonacci(n):
    """計算斐波那契數列的前n項"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

# 測試
print("斐波那契數列前10項:")
print(calculate_fibonacci(10))
EOF

echo "測試文件創建在: /tmp/test_cursor.py"
echo ""

# 顯示可用命令
echo "4. 可用命令:"
echo "   agent login                    # 登錄Cursor賬號"
echo "   agent status                   # 檢查登錄狀態"
echo "   agent models                   # 查看可用模型"
echo "   agent chat '你的提示'          # 開始對話"
echo "   agent --print '分析代碼'       # 非交互模式"
echo "   agent install-shell-integration # 安裝shell集成"
echo ""

echo "=== 使用示例 ==="
echo ""
echo "A. 基本使用:"
echo "   agent chat '幫我寫一個Python函數計算階乘'"
echo ""
echo "B. 代碼分析:"
echo "   agent --print '分析/tmp/test_cursor.py中的代碼'"
echo ""
echo "C. 計劃模式:"
echo "   agent --plan '設計一個股票價格監控系統'"
echo ""
echo "=== 注意事項 ==="
echo "1. 需要Cursor訂閱才能使用完整功能"
echo "2. 首次使用需要登錄: agent login"
echo "3. 可以使用環境變量設置API密鑰: export CURSOR_API_KEY='your-key'"
echo "4. 安全模式會限制文件寫入和命令執行"