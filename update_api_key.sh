#!/bin/bash
# OANDA API密鑰更新腳本

echo "="
echo "🔑 OANDA API密鑰更新"
echo "="

echo "請輸入你的OANDA API密鑰:"
read -p "API密鑰: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API密鑰不能為空"
    exit 1
fi

# 更新配置文件
config_file="/Users/gordonlui/.openclaw/workspace/oanda_config.json"

# 檢查文件是否存在
if [ ! -f "$config_file" ]; then
    echo "❌ 配置文件不存在: $config_file"
    exit 1
fi

# 創建備份
cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ 創建備份: ${config_file}.backup"

# 更新API密鑰
python3 -c "
import json
import sys

config_file = '$config_file'
api_key = '$api_key'

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # 確保API密鑰格式正確
    if not api_key.startswith('Bearer '):
        api_key = 'Bearer ' + api_key
    
    config['api_key'] = api_key
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print('✅ API密鑰更新成功')
    print(f'   賬戶ID: {config.get(\"account_id\", \"未設置\")}')
    print(f'   環境: {config.get(\"environment\", \"practice\")}')
    
except Exception as e:
    print(f'❌ 更新失敗: {e}')
    sys.exit(1)
"

echo ""
echo "🔍 測試API連接..."
cd /Users/gordonlui/.openclaw/workspace
python3 -c "
import oandapyV20
import json

try:
    with open('oanda_config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('api_key', '')
    account_id = config.get('account_id', '')
    
    if not api_key:
        print('❌ API密鑰未設置')
        exit(1)
    
    # 移除Bearer前綴用於測試
    access_token = api_key.replace('Bearer ', '')
    
    api = oandapyV20.API(
        access_token=access_token,
        environment=config.get('environment', 'practice')
    )
    
    from oandapyV20.endpoints.accounts import AccountDetails
    r = AccountDetails(accountID=account_id)
    response = api.request(r)
    
    if 'account' in response:
        account_info = response['account']
        print('✅ OANDA API連接成功')
        print(f'   賬戶: {account_info[\"id\"]}')
        print(f'   餘額: {account_info[\"balance\"]} {account_info[\"currency\"]}')
        print(f'   環境: {config.get(\"environment\", \"practice\")}')
    else:
        print(f'❌ API連接失敗: {response}')
        
except ImportError:
    print('❌ oandapyV20未安裝')
    print('   安裝: pip install oandapyV20')
except Exception as e:
    print(f'❌ 連接測試失敗: {e}')
"

echo ""
echo "🚀 現在可以開始交易了！"
echo "   運行: python3 start_oanda_trader.py"
echo ""