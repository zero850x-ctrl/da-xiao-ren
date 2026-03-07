#!/usr/bin/env python3
"""
分析ASUS SN號碼並生成新號碼
SN: T3RCQV00A091AC2
"""

import re
import random
import string
from collections import Counter

def analyze_sn(sn):
    """分析SN號碼結構"""
    print(f"🔍 分析ASUS SN號碼: {sn}")
    print(f"長度: {len(sn)} 字符")
    
    # 字符統計
    char_count = Counter(sn)
    print(f"\n📊 字符統計:")
    for char, count in sorted(char_count.items()):
        print(f"  '{char}': {count}次")
    
    # 字符類型分析
    letters = sum(1 for c in sn if c.isalpha())
    digits = sum(1 for c in sn if c.isdigit())
    uppercase = sum(1 for c in sn if c.isupper())
    
    print(f"\n📈 類型分析:")
    print(f"  字母: {letters}個 ({letters/len(sn)*100:.1f}%)")
    print(f"  數字: {digits}個 ({digits/len(sn)*100:.1f}%)")
    print(f"  大寫: {uppercase}個 ({uppercase/len(sn)*100:.1f}%)")
    
    # 嘗試識別模式
    print(f"\n🎯 模式分析:")
    
    # 常見ASUS SN模式
    patterns = [
        (r'^[A-Z][0-9][A-Z]{2}[A-Z0-9]{2}[A-Z][0-9]{3}[A-Z]{2}[0-9]$', "可能的產品線+生產信息"),
        (r'^[A-Z][0-9][A-Z]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]{2}[0-9]$', "型號+批次+序號"),
        (r'^[A-Z][0-9][A-Z]{2}Q[A-Z0-9].*$', "包含Q的特殊標識"),
    ]
    
    for pattern, description in patterns:
        if re.match(pattern, sn):
            print(f"  匹配模式: {description}")
    
    # 分割分析
    print(f"\n🔧 結構拆解:")
    
    # 嘗試不同分割方式
    segments = [
        (0, 1, "產品系列/地區碼"),      # T
        (1, 2, "年份/版本碼"),          # 3
        (2, 5, "型號識別碼"),           # RCQ
        (5, 7, "生產周/批次"),          # V0
        (7, 8, "生產線/工廠"),          # 0
        (8, 9, "產品類別"),            # A
        (9, 12, "生產序號"),           # 091
        (12, 14, "校驗碼/配置碼"),     # AC
        (14, 15, "版本/修訂")          # 2
    ]
    
    for start, end, description in segments:
        segment = sn[start:end]
        print(f"  位置{start}-{end}: '{segment}' - {description}")
    
    return char_count

def generate_similar_sn(original_sn, char_count):
    """生成類似的SN號碼"""
    print(f"\n🎲 生成類似SN號碼:")
    
    # 保持相同字符分布
    all_chars = list(original_sn)
    
    # 方法1: 隨機重排
    random.shuffle(all_chars)
    shuffled = ''.join(all_chars)
    print(f"  1. 隨機重排: {shuffled}")
    
    # 方法2: 保持結構，替換部分字符
    new_sn = list(original_sn)
    
    # 替換數字部分
    for i in range(len(new_sn)):
        if new_sn[i].isdigit():
            new_sn[i] = random.choice('0123456789')
    
    # 替換字母部分（保持大寫）
    for i in range(len(new_sn)):
        if new_sn[i].isalpha():
            new_sn[i] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    random_replace = ''.join(new_sn)
    print(f"  2. 隨機替換: {random_replace}")
    
    # 方法3: 基於模式的生成
    print(f"\n🔧 基於模式的生成:")
    
    # 推測的模式生成
    patterns = [
        # 產品系列 + 年份 + 型號 + 批次 + 生產線 + 類別 + 序號 + 校驗 + 版本
        (r'^([A-Z])([0-9])([A-Z]{2}[A-Z])([A-Z0-9]{2})([0-9])([A-Z])([0-9]{3})([A-Z]{2})([0-9])$', 
         "完整模式生成"),
        
        # 簡化模式
        (r'^([A-Z][0-9][A-Z]{2})([A-Z0-9]{4})([A-Z0-9]{6})$',
         "三段式生成"),
    ]
    
    for i, (pattern, desc) in enumerate(patterns, 3):
        if re.match(pattern, original_sn):
            # 生成類似結構
            new_parts = []
            
            # 根據不同部分生成
            if i == 3:  # 完整模式
                # 產品系列 (保持原系列或隨機)
                series = random.choice(['T', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'U', 'V', 'W', 'X', 'Y', 'Z'])
                
                # 年份 (3-9)
                year = random.choice('3456789')
                
                # 型號識別 (3字母，第二個可能是Q)
                model = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                model += random.choice(['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
                model += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                
                # 批次 (字母+數字)
                batch = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                batch += random.choice('0123456789')
                
                # 生產線 (0-9)
                line = random.choice('0123456789')
                
                # 產品類別 (A-Z)
                category = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                
                # 生產序號 (3位數字)
                serial = f"{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}"
                
                # 校驗碼 (2字母)
                checksum = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                checksum += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                
                # 版本 (1位數字)
                version = random.choice('0123456789')
                
                new_sn = f"{series}{year}{model}{batch}{line}{category}{serial}{checksum}{version}"
                print(f"  {i}. {desc}: {new_sn}")
                
            elif i == 4:  # 三段式
                # 第一部分：產品識別
                part1 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                part1 += random.choice('0123456789')
                part1 += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                part1 += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                
                # 第二部分：生產信息
                part2 = ''
                for _ in range(4):
                    if random.random() > 0.5:
                        part2 += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    else:
                        part2 += random.choice('0123456789')
                
                # 第三部分：序號校驗
                part3 = ''
                for _ in range(6):
                    if random.random() > 0.5:
                        part3 += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    else:
                        part3 += random.choice('0123456789')
                
                new_sn = f"{part1}{part2}{part3}"
                print(f"  {i}. {desc}: {new_sn}")
    
    # 方法4: 創建有意义的號碼
    print(f"\n🎯 創建有意義的SN號碼:")
    
    # ASUS常見前綴
    asus_prefixes = ['T3RC', 'A3RC', 'B3RC', 'C3RC', 'D3RC', 'E3RC', 'F3RC']
    prefix = random.choice(asus_prefixes)
    
    # 中間部分
    middle_options = ['QV', 'QA', 'QB', 'QC', 'VA', 'VB', 'VC']
    middle = random.choice(middle_options)
    
    # 數字部分
    numbers = f"{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}"
    
    # 結尾部分
    suffix_options = ['AC', 'AD', 'AE', 'BC', 'BD', 'BE']
    suffix = random.choice(suffix_options)
    
    # 版本
    version = random.choice('123456789')
    
    meaningful_sn = f"{prefix}{middle}0{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{numbers}{suffix}{version}"
    print(f"  5. 有意義生成: {meaningful_sn}")
    
    # 方法5: 基於原SN的變體
    print(f"\n🔄 原SN變體:")
    
    # 變體1: 替換相似字符
    variant1 = original_sn.replace('3', '8').replace('0', '6').replace('1', '7')
    print(f"  6. 數字替換: {variant1}")
    
    # 變體2: 字母替換
    variant2 = original_sn.replace('T', 'B').replace('R', 'P').replace('C', 'G').replace('Q', 'K').replace('V', 'X').replace('A', 'M')
    print(f"  7. 字母替換: {variant2}")
    
    # 變體3: 位置交換
    variant3 = list(original_sn)
    # 交換位置1和2
    variant3[1], variant3[2] = variant3[2], variant3[1]
    # 交換位置12和13
    variant3[12], variant3[13] = variant3[13], variant3[12]
    variant3 = ''.join(variant3)
    print(f"  8. 位置交換: {variant3}")

def validate_sn(sn):
    """驗證SN號碼有效性"""
    print(f"\n✅ 驗證SN號碼 {sn}:")
    
    # 基本檢查
    checks = [
        (len(sn) == 15, "長度正確 (15位)"),
        (sn.isalnum(), "只包含字母和數字"),
        (sn == sn.upper(), "全部大寫"),
        (any(c.isdigit() for c in sn), "包含數字"),
        (any(c.isalpha() for c in sn), "包含字母"),
    ]
    
    for condition, message in checks:
        status = "✅" if condition else "❌"
        print(f"  {status} {message}")
    
    # 檢查是否有連續重複
    has_repeat = any(sn[i] == sn[i+1] == sn[i+2] for i in range(len(sn)-2))
    print(f"  {'❌' if has_repeat else '✅'} 無連續三個相同字符")
    
    # 檢查字符分布
    char_dist = Counter(sn)
    max_repeat = max(char_dist.values())
    print(f"  {'⚠️ ' if max_repeat > 3 else '✅'} 單字符最多重複{max_repeat}次")

def main():
    original_sn = "T3RCQV00A091AC2"
    
    print("=" * 70)
    print("🔧 ASUS SN號碼分析與生成工具")
    print("=" * 70)
    
    # 分析原SN
    char_count = analyze_sn(original_sn)
    
    # 生成新SN
    generate_similar_sn(original_sn, char_count)
    
    # 驗證原SN
    validate_sn(original_sn)
    
    print(f"\n💡 使用提示:")
    print(f"  1. ASUS SN通常包含產品線、生產日期、序號等信息")
    print(f"  2. 真實SN需要通過ASUS系統驗證")
    print(f"  3. 生成的SN僅供測試和學習使用")
    print(f"  4. 避免在正式場合使用生成的SN")
    
    print(f"\n📅 生成時間: 2026-02-19 14:00")
    print("=" * 70)

if __name__ == "__main__":
    main()