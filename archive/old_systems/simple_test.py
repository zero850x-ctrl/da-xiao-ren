from binance.client import Client
from datetime import datetime

api_key = '05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV'
api_secret = 'YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj'

try:
    client = Client(api_key, api_secret, testnet=True)
    server_time = client.get_server_time()
    print(f'✅ 連接成功: {datetime.fromtimestamp(server_time["serverTime"]/1000)}')
    
    # 簡單測試
    ticker = client.get_symbol_ticker(symbol='BTCUSDT')
    print(f'💰 BTC價格: ${float(ticker["price"]):,.2f}')
    
    account = client.get_account()
    usdt_balance = 0
    for b in account['balances']:
        if b['asset'] == 'USDT':
            usdt_balance = float(b['free']) + float(b['locked'])
            break
    
    print(f'💵 USDT餘額: ${usdt_balance:,.2f}')
    
    # 顯示其他餘額
    print(f'\n📊 其他資產:')
    for b in account['balances']:
        free = float(b['free'])
        locked = float(b['locked'])
        total = free + locked
        if total > 0 and b['asset'] != 'USDT':
            print(f'  {b["asset"]}: {total}')
    
    print(f'\n🎉 系統正常！可以開始學習')
    print(f'\n立即運行:')
    print(f'1. python3 crypto_24h_trader.py')
    print(f'2. python3 crypto_whatsapp_reporter.py')
    print(f'3. ./start_crypto_trading.sh')
    
except Exception as e:
    print(f'❌ 錯誤: {e}')