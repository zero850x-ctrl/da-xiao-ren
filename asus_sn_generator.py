#!/usr/bin/env python3
"""
ASUS SN號碼生成器 - 批量生成和驗證
"""

import random
import string
import re
from datetime import datetime
from collections import Counter

class ASUSSNGenerator:
    """ASUS SN生成器"""
    
    def __init__(self, template_sn="T3RCQV00A091AC2"):
        self.template = template_sn
        self.analyze_template()
    
    def analyze_template(self):
        """分析模板SN"""
        print(f"📋 模板SN: {self.template}")
        print(f"長度: {len(self.template)}")
        
        # 分析結構
        self.structure = self.guess_structure(self.template)
        
    def guess_structure(self, sn):
        """猜測SN結構"""
        # 常見ASUS SN結構模式
        structures = {
            'standard_15': {
                'pattern': r'^([A-Z])([0-9])([A-Z]{3})([A-Z][0-9])([0-9])([A-Z])([0-9]{3})([A-Z]{2})([0-9])$',
                'parts': ['系列', '年份', '型號', '批次', '生產線', '類別', '序號', '校驗', '版本']
            },
            'compact_12': {
                'pattern': r'^([A-Z]{2})([0-9]{2})([A-Z]{2})([0-9]{3})([A-Z]{3})$',
                'parts': ['系列型號', '年份周', '工廠', '序號', '配置']
            },
            'extended_18': {
                'pattern': r'^([A-Z]{3})([0-9]{2})([A-Z]{2})([0-9]{4})([A-Z]{3})([0-9]{2})$',
                'parts': ['品牌系列', '生產日期', '地區', '唯一碼', '配置', '校驗']
            }
        }
        
        for name, struct in structures.items():
            if re.match(struct['pattern'], sn):
                print(f"匹配結構: {name}")
                return struct
        
        # 自定義結構分析
        print("使用自定義結構分析")
        return {
            'pattern': None,
            'parts': ['未知'] * len(sn)
        }
    
    def generate_similar(self, count=10):
        """生成類似的SN"""
        print(f"\n🎲 生成 {count} 個類似SN:")
        
        generated = []
        
        for i in range(count):
            # 方法1: 基於模板的智能生成
            if i < 5:
                sn = self.generate_by_structure()
            # 方法2: 隨機但保持格式
            else:
                sn = self.generate_random_similar()
            
            generated.append(sn)
            print(f"  {i+1:2d}. {sn}")
            
            # 驗證基本有效性
            is_valid = self.validate_sn(sn)
            status = "✅" if is_valid else "❌"
            print(f"       {status} 基本驗證: {'有效' if is_valid else '無效'}")
        
        return generated
    
    def generate_by_structure(self):
        """基於結構生成"""
        # 根據模板結構生成
        
        # 產品系列 (保持T或隨機)
        series = random.choice(['T', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'U', 'V', 'W', 'X', 'Y', 'Z'])
        
        # 年份 (3-9，可能代表2023-2029)
        year = random.choice('3456789')
        
        # 型號識別 (3字母，第二個可能是Q)
        model_chars = []
        model_chars.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        model_chars.append(random.choice(['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']))
        model_chars.append(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        model = ''.join(model_chars)
        
        # 批次 (字母+數字)
        batch_letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        batch_number = random.choice('0123456789')
        batch = batch_letter + batch_number
        
        # 生產線 (0-9)
        line = random.choice('0123456789')
        
        # 產品類別 (A-Z)
        category = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        # 生產序號 (3位數字，避免000)
        serial = f"{random.randint(0,9)}{random.randint(0,9)}{random.randint(1,9)}"
        
        # 校驗碼 (2字母，避免重複)
        checksum1 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        checksum2 = random.choice([c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c != checksum1])
        checksum = checksum1 + checksum2
        
        # 版本 (1位數字，避免0)
        version = random.choice('123456789')
        
        return f"{series}{year}{model}{batch}{line}{category}{serial}{checksum}{version}"
    
    def generate_random_similar(self):
        """隨機生成但保持相似性"""
        # 保持相同的字符集和分布
        chars = list(self.template)
        random.shuffle(chars)
        
        # 但確保某些位置是數字/字母
        result = list(chars)
        
        # 確保位置1是數字（年份）
        if not result[1].isdigit():
            result[1] = random.choice('0123456789')
        
        # 確保位置5是字母（批次字母）
        if not result[5].isalpha():
            result[5] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        # 確保位置6是數字（批次數字）
        if not result[6].isdigit():
            result[6] = random.choice('0123456789')
        
        # 確保位置9-11是數字（序號）
        for i in range(9, 12):
            if not result[i].isdigit():
                result[i] = random.choice('0123456789')
        
        return ''.join(result)
    
    def validate_sn(self, sn):
        """驗證SN有效性"""
        # 基本檢查
        if len(sn) != 15:
            return False
        
        if not sn.isalnum():
            return False
        
        if sn != sn.upper():
            return False
        
        # 檢查是否有連續三個相同字符
        for i in range(len(sn) - 2):
            if sn[i] == sn[i+1] == sn[i+2]:
                return False
        
        # 檢查字符分布
        char_count = Counter(sn)
        if max(char_count.values()) > 4:  # 單字符最多出現4次
            return False
        
        # 檢查數字字母比例
        digits = sum(1 for c in sn if c.isdigit())
        letters = sum(1 for c in sn if c.isalpha())
        
        if digits < 5 or letters < 5:  # 至少5個數字和5個字母
            return False
        
        return True
    
    def generate_batch(self, count=20, output_file=None):
        """批量生成"""
        print(f"\n📦 批量生成 {count} 個SN號碼:")
        print("-" * 50)
        
        valid_sns = []
        invalid_sns = []
        
        for i in range(count):
            sn = self.generate_by_structure() if i % 2 == 0 else self.generate_random_similar()
            
            if self.validate_sn(sn):
                valid_sns.append(sn)
                print(f"✅ {i+1:3d}. {sn}")
            else:
                invalid_sns.append(sn)
                print(f"❌ {i+1:3d}. {sn} (無效)")
        
        print(f"\n📊 生成統計:")
        print(f"  有效SN: {len(valid_sns)} 個")
        print(f"  無效SN: {len(invalid_sns)} 個")
        print(f"  成功率: {len(valid_sns)/count*100:.1f}%")
        
        # 保存到文件
        if output_file and valid_sns:
            with open(output_file, 'w') as f:
                f.write(f"# ASUS SN號碼生成列表\n")
                f.write(f"# 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 模板: {self.template}\n")
                f.write(f"# 總數: {len(valid_sns)} 個有效SN\n\n")
                
                for i, sn in enumerate(valid_sns, 1):
                    f.write(f"{i:3d}. {sn}\n")
            
            print(f"\n💾 已保存到: {output_file}")
        
        return valid_sns, invalid_sns
    
    def create_special_sns(self):
        """創建特殊意義的SN"""
        print(f"\n🎯 創建特殊意義的SN:")
        
        special_sns = []
        
        # 1. 序列號模式
        for i in range(1, 6):
            serial_num = f"{i:03d}"  # 001, 002, ...
            sn = f"T3RCQV00A{serial_num}AC2"
            special_sns.append(sn)
            print(f"  序列{i}: {sn}")
        
        # 2. 年份變化
        years = ['3', '4', '5', '6', '7']  # 2023-2027
        for year in years:
            sn = f"T{year}RCQV00A091AC2"
            special_sns.append(sn)
            print(f"  年份{year}: {sn}")
        
        # 3. 產品線變化
        product_lines = ['T', 'A', 'B', 'C', 'D']
        for line in product_lines:
            sn = f"{line}3RCQV00A091AC2"
            special_sns.append(sn)
            print(f"  產品線{line}: {sn}")
        
        # 4. 配置變化
        configs = ['AC', 'AD', 'AE', 'BC', 'BD']
        for config in configs:
            sn = f"T3RCQV00A091{config}2"
            special_sns.append(sn)
            print(f"  配置{config}: {sn}")
        
        return special_sns

def main():
    """主函數"""
    print("=" * 70)
    print("🔧 ASUS SN號碼批量生成器")
    print("=" * 70)
    
    # 初始化生成器
    generator = ASUSSNGenerator("T3RCQV00A091AC2")
    
    # 生成類似SN
    generator.generate_similar(10)
    
    # 批量生成
    output_file = "/Users/gordonlui/.openclaw/workspace/asus_sn_list.txt"
    valid_sns, invalid_sns = generator.generate_batch(20, output_file)
    
    # 創建特殊SN
    special_sns = generator.create_special_sns()
    
    # 生成報告
    print(f"\n📄 生成報告:")
    print(f"  總生成數: {20 + len(special_sns)}")
    print(f"  有效數量: {len(valid_sns) + len(special_sns)}")
    print(f"  文件保存: {output_file}")
    
    print(f"\n💡 使用說明:")
    print(f"  1. 這些SN僅供測試、學習、開發使用")
    print(f"  2. 請勿用於正式產品或欺詐目的")
    print(f"  3. 真實ASUS SN需要官方系統驗證")
    print(f"  4. 可用於軟件測試、數據庫填充等")
    
    print(f"\n🎯 應用場景:")
    print(f"  • 軟件測試: 測試SN驗證功能")
    print(f"  • 數據分析: 分析SN模式規律")
    print(f"  • 教學演示: 展示編碼系統")
    print(f"  • 開發測試: 測試相關API接口")
    
    print(f"\n⚠️  免責聲明:")
    print(f"  本工具生成的SN號碼並非官方ASUS序列號")
    print(f"  僅供技術研究和學習使用")
    print(f"  使用這些SN造成的任何問題自行負責")
    
    print(f"\n📅 生成完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()