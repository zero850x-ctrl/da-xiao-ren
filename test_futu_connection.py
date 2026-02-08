#!/usr/bin/env python3
import socket
import time

def test_port(host='127.0.0.1', port=11111, timeout=5):
    """測試端口是否開放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {port} 開放，連接成功！")
            return True
        else:
            print(f"❌ 端口 {port} 關閉，錯誤代碼: {result}")
            return False
    except Exception as e:
        print(f"❌ 連接端口 {port} 時出錯: {e}")
        return False

def test_common_ports():
    """測試常見的Futu端口"""
    common_ports = [11111, 11112, 11113, 11114, 11115]
    for port in common_ports:
        print(f"\n測試端口 {port}...")
        if test_port(port=port):
            print(f"🎯 發現OpenD在端口 {port} 上運行！")
            return port
    return None

if __name__ == "__main__":
    print("🔍 開始測試Futu OpenD連接...")
    print(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 先測試默認端口
    print("\n1. 測試默認端口 11111...")
    if test_port():
        print("✅ OpenD連接正常！")
    else:
        print("⚠️  默認端口連接失敗，嘗試其他端口...")
        found_port = test_common_ports()
        if found_port:
            print(f"\n🎉 發現OpenD在端口 {found_port} 上運行！")
            print(f"請使用 host='127.0.0.1', port={found_port} 連接")
        else:
            print("\n❌ 所有常見端口都無法連接")
            print("可能原因:")
            print("1. OpenD未正確啟動")
            print("2. 防火牆阻止了連接")
            print("3. OpenD配置了非標準端口")
            print("4. 網絡配置問題")
    
    print("\n" + "=" * 50)
    print("測試完成")