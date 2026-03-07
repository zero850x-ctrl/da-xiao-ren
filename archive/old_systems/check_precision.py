#!/usr/bin/env python3
"""
檢查幣安API精度要求
"""

from binance.client import Client

def main():
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    client = Client(api_key, api_secret, testnet=True)
    
    symbol = 'BTCUSDT'
    info = client.get_symbol_info(symbol)
    
    print(f"📋 {symbol} 完整交易規則:")
    print(json.dumps(info, indent=2))

if __name__ == "__main__":
    import json
    main()