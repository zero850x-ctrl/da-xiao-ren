#!/usr/bin/env python3
"""
價格驗證模塊 - 確保股票價格數據的合理性
"""

import json
import os
from datetime import datetime
import logging

print("=" * 70)
print("🔍 價格驗證模塊")
print("=" * 70)

# 設置日誌
log_dir = '/Users/gordonlui/.openclaw/workspace/validation_logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/price_validation_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PriceValidator:
    """價格驗證器"""
    
    # 港股合理價格範圍 (單位: 港幣)
    REASONABLE_PRICE_RANGES = {
        # 藍籌股
        '00005': {'min': 40.0, 'max': 200.0, 'typical': 134.20, 'name': '匯豐控股'},
        '00011': {'min': 400.0, 'max': 800.0, 'typical': 550.00, 'name': '恒生銀行'},
        '00016': {'min': 40.0, 'max': 80.0, 'typical': 55.00, 'name': '新鴻基地產'},
        
        # 科技股
        '00700': {'min': 300.0, 'max': 800.0, 'typical': 535.50, 'name': '騰訊控股'},
        '00992': {'min': 5.0, 'max': 15.0, 'typical': 9.30, 'name': '聯想集團'},
        '09988': {'min': 70.0, 'max': 200.0, 'typical': 158.60, 'name': '阿里巴巴'},
        '01810': {'min': 150.0, 'max': 300.0, 'typical': 220.00, 'name': '小米集團'},
        
        # 金融股
        '01398': {'min': 3.0, 'max': 8.0, 'typical': 6.40, 'name': '工商銀行'},
        '03988': {'min': 2.0, 'max': 5.0, 'typical': 3.50, 'name': '中國銀行'},
        
        # 公用事業
        '00002': {'min': 40.0, 'max': 80.0, 'typical': 55.00, 'name': '中電控股'},
        '00003': {'min': 40.0, 'max': 80.0, 'typical': 55.00, 'name': '香港中華煤氣'},
        '02638': {'min': 4.0, 'max': 8.0, 'typical': 6.97, 'name': '港燈-SS'},
        
        # 指數ETF
        '02800': {'min': 20.0, 'max': 30.0, 'typical': 27.17, 'name': '盈富基金'},
        '02828': {'min': 150.0, 'max': 250.0, 'typical': 200.00, 'name': '恒生中國企業指數'},
        
        # 其他
        '01299': {'min': 60.0, 'max': 100.0, 'typical': 84.30, 'name': '友邦保險'},
        '02318': {'min': 30.0, 'max': 60.0, 'typical': 45.00, 'name': '中國平安'},
        '09618': {'min': 80.0, 'max': 150.0, 'typical': 105.90, 'name': '京東集團'},
    }
    
    # 價格變動合理範圍 (單日最大變動百分比)
    MAX_DAILY_CHANGE = {
        'normal': 20.0,    # 正常股票單日最大變動
        'volatile': 30.0,  # 波動較大股票
        'penny': 50.0,     # 細價股
    }
    
    def __init__(self):
        self.validation_history = []
        self.results_dir = '/Users/gordonlui/.openclaw/workspace/validation_results'
        os.makedirs(self.results_dir, exist_ok=True)
        
        # 加載歷史價格記錄
        self.price_history = self.load_price_history()
    
    def load_price_history(self):
        """加載歷史價格記錄"""
        history_file = f'{self.results_dir}/price_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_price_history(self):
        """保存歷史價格記錄"""
        history_file = f'{self.results_dir}/price_history.json'
        with open(history_file, 'w') as f:
            json.dump(self.price_history, f, indent=2, ensure_ascii=False)
    
    def validate_price_range(self, stock_code, price):
        """驗證價格是否在合理範圍內"""
        stock_code = str(stock_code).zfill(5)  # 確保5位數
        
        if stock_code not in self.REASONABLE_PRICE_RANGES:
            logger.warning(f"股票 {stock_code} 沒有定義價格範圍，跳過範圍驗證")
            return {'valid': True, 'reason': '未定義範圍'}
        
        range_info = self.REASONABLE_PRICE_RANGES[stock_code]
        min_price = range_info['min']
        max_price = range_info['max']
        typical = range_info['typical']
        name = range_info['name']
        
        if price < min_price:
            return {
                'valid': False,
                'reason': f'價格過低: ${price:.2f} < 最低合理價 ${min_price:.2f}',
                'severity': 'high',
                'suggested_price': typical
            }
        
        if price > max_price:
            return {
                'valid': False,
                'reason': f'價格過高: ${price:.2f} > 最高合理價 ${max_price:.2f}',
                'severity': 'critical',
                'suggested_price': typical
            }
        
        # 檢查是否偏離典型值過多
        deviation = abs((price - typical) / typical) * 100
        if deviation > 50:  # 偏離超過50%
            return {
                'valid': True,  # 仍然在範圍內，但需要警告
                'reason': f'價格偏離典型值: ${price:.2f} vs 典型 ${typical:.2f} ({deviation:.1f}%)',
                'severity': 'warning',
                'suggested_price': typical
            }
        
        return {
            'valid': True,
            'reason': f'價格在合理範圍內: ${price:.2f} (範圍: ${min_price:.2f}-${max_price:.2f})',
            'severity': 'normal'
        }
    
    def validate_price_change(self, stock_code, current_price, previous_price=None):
        """驗證價格變動是否合理"""
        if previous_price is None:
            # 嘗試從歷史記錄獲取
            if stock_code in self.price_history:
                previous_price = self.price_history[stock_code].get('last_price')
            else:
                logger.info(f"股票 {stock_code} 無歷史價格，跳過變動驗證")
                return {'valid': True, 'reason': '無歷史數據'}
        
        if previous_price == 0:
            return {'valid': True, 'reason': '前價為零，跳過變動驗證'}
        
        change_percent = abs((current_price - previous_price) / previous_price) * 100
        
        # 根據股票類型確定最大變動
        max_change = self.MAX_DAILY_CHANGE['normal']
        if stock_code in ['00992', '09618', '01810']:  # 波動較大的科技股
            max_change = self.MAX_DAILY_CHANGE['volatile']
        elif current_price < 1.0:  # 細價股
            max_change = self.MAX_DAILY_CHANGE['penny']
        
        if change_percent > max_change:
            return {
                'valid': False,
                'reason': f'價格變動過大: {change_percent:.1f}% > 最大允許 {max_change}%',
                'severity': 'high',
                'change_percent': change_percent
            }
        
        return {
            'valid': True,
            'reason': f'價格變動合理: {change_percent:.1f}%',
            'severity': 'normal',
            'change_percent': change_percent
        }
    
    def validate_price_format(self, price):
        """驗證價格格式"""
        try:
            price_float = float(price)
            
            # 檢查是否為數字
            if not isinstance(price_float, (int, float)):
                return {'valid': False, 'reason': '價格不是數字', 'severity': 'critical'}
            
            # 檢查是否為有限數
            if not (price_float > 0 and price_float < 1e12):  # 小於1萬億
                return {'valid': False, 'reason': '價格數值異常', 'severity': 'critical'}
            
            # 檢查小數位數
            price_str = str(price)
            if '.' in price_str:
                decimal_places = len(price_str.split('.')[1])
                if decimal_places > 4:  # 港股通常最多4位小數
                    return {'valid': False, 'reason': f'小數位數過多: {decimal_places}', 'severity': 'warning'}
            
            return {'valid': True, 'reason': '價格格式正確', 'severity': 'normal'}
            
        except (ValueError, TypeError):
            return {'valid': False, 'reason': '無法解析為價格', 'severity': 'critical'}
    
    def validate_stock_code(self, stock_code):
        """驗證股票代碼"""
        stock_code = str(stock_code).strip()
        
        # 移除可能的後綴
        if '.' in stock_code:
            stock_code = stock_code.split('.')[0]
        
        # 檢查長度
        if len(stock_code) < 4 or len(stock_code) > 5:
            return {'valid': False, 'reason': f'股票代碼長度異常: {len(stock_code)}位', 'severity': 'critical'}
        
        # 補零到5位
        stock_code_5 = stock_code.zfill(5)
        
        # 檢查是否為數字
        if not stock_code_5.isdigit():
            return {'valid': False, 'reason': '股票代碼包含非數字字符', 'severity': 'critical'}
        
        return {
            'valid': True,
            'reason': '股票代碼格式正確',
            'severity': 'normal',
            'normalized_code': stock_code_5
        }
    
    def comprehensive_validation(self, stock_code, price, previous_price=None):
        """綜合驗證"""
        logger.info(f"開始驗證股票 {stock_code}, 價格 ${price}")
        
        validation_result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock_code': stock_code,
            'price': price,
            'previous_price': previous_price,
            'validations': {},
            'overall_valid': True,
            'issues': [],
            'warnings': []
        }
        
        # 1. 驗證股票代碼
        code_validation = self.validate_stock_code(stock_code)
        validation_result['validations']['stock_code'] = code_validation
        
        if not code_validation['valid']:
            validation_result['overall_valid'] = False
            validation_result['issues'].append(f"股票代碼: {code_validation['reason']}")
        elif 'normalized_code' in code_validation:
            stock_code = code_validation['normalized_code']  # 使用標準化代碼
        
        # 2. 驗證價格格式
        format_validation = self.validate_price_format(price)
        validation_result['validations']['price_format'] = format_validation
        
        if not format_validation['valid']:
            validation_result['overall_valid'] = False
            if format_validation['severity'] == 'critical':
                validation_result['issues'].append(f"價格格式: {format_validation['reason']}")
            else:
                validation_result['warnings'].append(f"價格格式: {format_validation['reason']}")
        
        # 3. 驗證價格範圍（僅在價格格式有效時進行）
        if format_validation['valid']:
            try:
                price_float = float(price)
                range_validation = self.validate_price_range(stock_code, price_float)
            except (ValueError, TypeError):
                range_validation = {'valid': False, 'reason': '無法解析價格進行範圍驗證', 'severity': 'critical'}
        else:
            range_validation = {'valid': False, 'reason': '價格格式無效，跳過範圍驗證', 'severity': 'warning'}
        
        validation_result['validations']['price_range'] = range_validation
        
        if not range_validation['valid']:
            validation_result['overall_valid'] = False
            validation_result['issues'].append(f"價格範圍: {range_validation['reason']}")
        elif 'severity' in range_validation and range_validation['severity'] == 'warning':
            validation_result['warnings'].append(f"價格範圍: {range_validation['reason']}")
        
        # 4. 驗證價格變動
        if previous_price is not None:
            change_validation = self.validate_price_change(stock_code, price, previous_price)
            validation_result['validations']['price_change'] = change_validation
            
            if not change_validation['valid']:
                validation_result['overall_valid'] = False
                validation_result['issues'].append(f"價格變動: {change_validation['reason']}")
        
        # 更新歷史記錄
        self.update_price_history(stock_code, price, validation_result['overall_valid'])
        
        # 記錄驗證結果
        self.record_validation(validation_result)
        
        return validation_result
    
    def update_price_history(self, stock_code, price, is_valid):
        """更新價格歷史記錄"""
        if stock_code not in self.price_history:
            self.price_history[stock_code] = {
                'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'prices': [],
                'validation_stats': {'total': 0, 'valid': 0, 'invalid': 0}
            }
        
        history = self.price_history[stock_code]
        history['prices'].append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price': price,
            'valid': is_valid
        })
        
        # 只保留最近100條記錄
        if len(history['prices']) > 100:
            history['prices'] = history['prices'][-100:]
        
        # 更新統計
        history['validation_stats']['total'] += 1
        if is_valid:
            history['validation_stats']['valid'] += 1
        else:
            history['validation_stats']['invalid'] += 1
        
        history['last_price'] = price
        history['last_validation'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.save_price_history()
    
    def record_validation(self, validation_result):
        """記錄驗證結果"""
        self.validation_history.append(validation_result)
        
        # 保存到文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f'{self.results_dir}/validation_{timestamp}.json'
        
        with open(result_file, 'w') as f:
            json.dump(validation_result, f, indent=2, ensure_ascii=False)
        
        # 保存到日誌文件
        log_file = f'{self.results_dir}/validation_log.json'
        log_data = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        
        log_data.append(validation_result)
        
        # 只保留最近1000條記錄
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return result_file
    
    def validate_batch(self, stock_prices):
        """批量驗證"""
        results = []
        for stock_code, price in stock_prices.items():
            result = self.comprehensive_validation(stock_code, price)
            results.append(result)
        
        # 生成批量報告
        report = self.generate_batch_report(results)
        return results, report
    
    def generate_batch_report(self, validation_results):
        """生成批量驗證報告"""
        total = len(validation_results)
        valid_count = sum(1 for r in validation_results if r['overall_valid'])
        invalid_count = total - valid_count
        
        issues = []
        warnings = []
        
        for result in validation_results:
            issues.extend(result['issues'])
            warnings.extend(result['warnings'])
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_stocks': total,
                'valid': valid_count,
                'invalid': invalid_count,
                'valid_percentage': (valid_count / total * 100) if total > 0 else 0
            },
            'issues': issues,
            'warnings': warnings,
            'critical_issues': [i for i in issues if 'critical' in i.lower() or '嚴重' in i],
            'detailed_results': validation_results
        }
        
        # 保存報告
        report_file = f'{self.results_dir}/batch_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"批量驗證完成: {valid_count}/{total} 有效")
        return report
    
    def get_suggested_price(self, stock_code):
        """獲取建議價格（當驗證失敗時使用）"""
        stock_code = str(stock_code).zfill(5)
        
        if stock_code in self.REASONABLE_PRICE_RANGES:
            return self.REASONABLE_PRICE_RANGES[stock_code]['typical']
        
        # 如果沒有定義，嘗試從歷史記錄獲取
        if stock_code in self.price_history and self.price_history[stock_code]['prices']:
            valid_prices = [p['price'] for p in self.price_history[stock_code]['prices'] if p['valid']]
            if valid_prices:
                return sum(valid_prices) / len(valid_prices)
        
        # 默認值
        return 100.0
    
    def run_daily_validation(self):
        """運行每日驗證"""
        logger.info("開始每日價格驗證")
        
        # 這裡可以添加自動從數據源獲取價格的邏輯
        # 暫時使用示例數據
        
        example_prices = {
            '00992': 9.30,
            '00700': 535.50,
            '09988': 158.60,
            '00005': 134.20,
            '01398': 6.40,
            '02638': 6.97,
            '09618': 105.90
        }
        
        results, report = self.validate_batch(example_prices)
        
        logger.info(f"每日驗證完成: {report['summary']['valid']}/{report['summary']['total_stocks']} 有效")
        
        # 如果有嚴重問題，發送警報
        if report['critical_issues']:
            logger.error(f"發現嚴重問題: {len(report['critical_issues'])} 個")
            self.send_alert(report)
        
        return report
    
    def send_alert(self, report):
        """發送警報"""
        alert_message = f"🚨 價格驗證發現嚴重問題\n"
        alert_message += f"時間: {report['timestamp']}\n"
        alert_message += f"有效股票: {report['summary']['valid']}/{report['summary']['total_stocks']}\n"
        
        if report['critical_issues']:
            alert_message += f"嚴重問題:\n"
            for issue in report['critical_issues'][:5]:  # 只顯示前5個
                alert_message += f"  • {issue}\n"
        
        logger.warning(alert_message)
        # 這裡可以集成Telegram、Email等通知
        
        return alert_message

def test_validation():
    """測試驗證功能"""
    print("\n🧪 測試價格驗證模塊")
    
    validator = PriceValidator()
    
    # 測試案例
    test_cases = [
        ('00992', 9.30, "正常價格"),
        ('00700', 59230463285.48, "異常高價（系統錯誤）"),
        ('09988', 0.01, "異常低價"),
        ('INVALID', 100.0, "無效股票代碼"),
        ('00992', "not_a_number", "非數字價格"),
        ('00992', 9.3012345, "過多小數位"),
    ]
    
    for stock_code, price, description in test_cases:
        print(f"\n📊 測試: {description}")
        print(f"  股票: {stock_code}, 價格: {price}")
        
        result = validator.comprehensive_validation(stock_code, price)
        
        if result['overall_valid']:
            print(f"  ✅ 驗證通過")
        else:
            print(f"  ❌ 驗證失敗")
            for issue in result['issues']:
                print(f"    問題: {issue}")
        
        for warning in result['warnings']:
            print(f"    ⚠️  警告: {warning}")
    
    # 批量測試
    print(f"\n📦 批量測試")
    batch_prices = {
        '00992': 9.30,
        '00700': 535.50,
        '09988': 158.60,
        '00005': 134.20,
    }
    
    results, report = validator.validate_batch(batch_prices)
    print(f"  批量驗證結果: {report['summary']['valid']}/{report['summary']['total_stocks']} 有效")
    
    return validator

def main():
    """主函數"""
    print("=" * 70)
    print("🔍 價格驗證模塊 - 主程序")
    print("=" * 70)
    
    # 創建驗證器
    validator = PriceValidator()
    
    # 運行測試
    test_validation()
    
    # 運行每日驗證
    print(f"\n📅 運行每日驗證...")
    report = validator.run_daily_validation()
    
    print(f"\n📊 驗證結果總結:")
    print(f"  總股票數: {report['summary']['total_stocks']}")
    print(f"  有效: {report['summary']['valid']}")
    print(f"  無效: {report['summary']['total_stocks'] - report['summary']['valid']}")
    print(f"  有效比例: {report['summary']['valid_percentage']:.1f}%")
    
    if report['issues']:
        print(f"\n🚨 發現問題:")
        for issue in report['issues'][:3]:  # 只顯示前3個
            print(f"  • {issue}")
    
    if report['warnings']:
        print(f"\n⚠️  警告:")
        for warning in report['warnings'][:3]:  # 只顯示前3個
            print(f"  • {warning}")
    
    print(f"\n💾 結果已保存到:")
    print(f"  日誌目錄: {log_dir}")
    print(f"  結果目錄: {validator.results_dir}")
    
    print(f"\n💡 使用說明:")
    print(f"  1. 單個驗證: validator.comprehensive_validation('00992', 9.30)")
    print(f"  2. 批量驗證: validator.validate_batch({{'00992': 9.30, '00700': 535.50}})")
    print(f"  3. 每日驗證: validator.run_daily_validation()")
    print(f"  4. 獲取建議價: validator.get_suggested_price('00992')")
    
    print(f"\n✅ 價格驗證模塊準備就緒")
    print("=" * 70)
    
    return validator

if __name__ == "__main__":
    validator = main()