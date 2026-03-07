#!/usr/bin/env python3
"""
OpenClaw 2026安全審計工具 - 基於Leo Laboratory安全指南
"""

import json
import os
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class OpenClawSecurityAudit:
    """OpenClaw安全審計類"""
    
    def __init__(self):
        self.config_path = Path.home() / ".openclaw" / "openclaw.json"
        self.credentials_dir = Path.home() / ".openclaw" / "credentials"
        self.results = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "passed": []
        }
    
    def log_result(self, level, title, description, fix=None):
        """記錄審計結果"""
        result = {
            "title": title,
            "description": description,
            "fix": fix,
            "timestamp": datetime.now().isoformat()
        }
        self.results[level].append(result)
    
    def check_vulnerability_1_gateway_exposure(self):
        """漏洞一：Gateway暴露在公網上"""
        print("🔍 檢查漏洞一：Gateway暴露風險...")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            gateway = config.get('gateway', {})
            bind = gateway.get('bind', 'loopback')
            port = gateway.get('port', 18789)
            auth = gateway.get('auth', {})
            
            if bind == 'loopback':
                self.log_result("passed", 
                    "Gateway綁定安全",
                    f"Gateway綁定到回環地址 (bind={bind}, port={port})",
                    "✅ 已正確配置")
            else:
                self.log_result("critical",
                    "Gateway可能暴露在公網",
                    f"Gateway綁定到 {bind}:{port}，可能允許外部訪問",
                    "將 gateway.bind 設置為 'loopback'")
            
            # 檢查認證
            auth_mode = auth.get('mode', 'none')
            if auth_mode in ['token', 'password']:
                self.log_result("passed",
                    "Gateway認證已啟用",
                    f"Gateway使用 {auth_mode} 認證",
                    "✅ 已正確配置")
            else:
                self.log_result("high",
                    "Gateway缺乏認證",
                    "Gateway未啟用認證機制",
                    "設置 gateway.auth.mode 為 'token' 並生成強密碼")
                
        except Exception as e:
            self.log_result("critical",
                "無法讀取Gateway配置",
                f"讀取配置文件時出錯: {e}",
                "檢查配置文件格式和權限")
    
    def check_vulnerability_2_dm_policy(self):
        """漏洞二：DM政策允許所有使用者"""
        print("🔍 檢查漏洞二：DM政策風險...")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # 檢查WhatsApp配置
            whatsapp = config.get('channels', {}).get('whatsapp', {})
            dm_policy = whatsapp.get('dmPolicy', 'unknown')
            allow_from = whatsapp.get('allowFrom', [])
            
            if dm_policy == 'allowlist' and allow_from:
                self.log_result("passed",
                    "DM政策安全",
                    f"WhatsApp使用白名單模式，允許 {len(allow_from)} 個號碼",
                    "✅ 已正確配置")
            elif dm_policy == 'open':
                self.log_result("critical",
                    "DM政策開放",
                    "WhatsApp允許任何人發送消息",
                    "設置 dmPolicy 為 'allowlist' 並指定允許的號碼")
            else:
                self.log_result("medium",
                    "DM政策配置不明確",
                    f"DM政策: {dm_policy}, 允許的號碼: {len(allow_from)}",
                    "明確設置為白名單模式並指定允許的號碼")
                
        except Exception as e:
            self.log_result("medium",
                "無法檢查DM政策",
                f"檢查DM政策時出錯: {e}",
                "檢查通道配置")
    
    def check_vulnerability_4_credentials_storage(self):
        """漏洞四：憑證明文存放"""
        print("🔍 檢查漏洞四：憑證存儲風險...")
        
        # 檢查憑證目錄權限
        if self.credentials_dir.exists():
            mode = os.stat(self.credentials_dir).st_mode
            if mode & stat.S_IROTH or mode & stat.S_IWOTH:
                self.log_result("high",
                    "憑證目錄權限過寬",
                    "其他用戶可以讀取憑證目錄",
                    "執行: chmod 700 " + str(self.credentials_dir))
            else:
                self.log_result("passed",
                    "憑證目錄權限安全",
                    "憑證目錄權限設置正確",
                    "✅ 已正確配置")
        else:
            self.log_result("low",
                "憑證目錄不存在",
                "未找到憑證目錄",
                "如果使用憑證，確保目錄權限安全")
        
        # 檢查配置文件權限
        if self.config_path.exists():
            mode = os.stat(self.config_path).st_mode
            if mode & stat.S_IROTH:
                self.log_result("high",
                    "配置文件可被其他用戶讀取",
                    "配置文件包含敏感信息",
                    "執行: chmod 600 " + str(self.config_path))
            else:
                self.log_result("passed",
                    "配置文件權限安全",
                    "配置文件權限設置正確",
                    "✅ 已正確配置")
    
    def check_vulnerability_6_dangerous_commands(self):
        """漏洞六：危險指令沒有封鎖"""
        print("🔍 檢查漏洞六：危險指令風險...")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # 檢查是否有命令限制配置
            tools_config = config.get('tools', {})
            exec_config = tools_config.get('exec', {})
            
            if exec_config.get('security') == 'deny' or exec_config.get('ask') == 'always':
                self.log_result("passed",
                    "命令執行有安全限制",
                    "命令執行需要確認或已被限制",
                    "✅ 已正確配置")
            else:
                self.log_result("high",
                    "命令執行缺乏限制",
                    "AI可能執行危險命令",
                    "設置 tools.exec.security 為 'deny' 或 tools.exec.ask 為 'always'")
                
        except Exception as e:
            self.log_result("medium",
                "無法檢查命令限制",
                f"檢查命令限制時出錯: {e}",
                "檢查工具配置")
    
    def check_vulnerability_9_logging(self):
        """漏洞九：沒有啟用日誌記錄"""
        print("🔍 檢查漏洞九：日誌記錄風險...")
        
        # 檢查日誌目錄
        log_dir = Path.home() / ".openclaw" / "logs"
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            if log_files:
                self.log_result("passed",
                    "日誌記錄已啟用",
                    f"找到 {len(log_files)} 個日誌文件",
                    "✅ 已正確配置")
            else:
                self.log_result("medium",
                    "日誌目錄存在但無日誌文件",
                    "可能未啟用日誌記錄",
                    "確保啟用日誌記錄功能")
        else:
            self.log_result("medium",
                "日誌目錄不存在",
                "可能未啟用日誌記錄",
                "創建日誌目錄並啟用日誌記錄")
    
    def check_qwen_removal(self):
        """檢查Qwen是否完全移除"""
        print("🔍 檢查Qwen移除情況...")
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            config_str = json.dumps(config).lower()
            
            # 檢查各種Qwen相關關鍵字
            qwen_keywords = ['qwen', '通義', 'aliyun']
            found = False
            
            for keyword in qwen_keywords:
                if keyword in config_str:
                    found = True
                    break
            
            if found:
                self.log_result("critical",
                    "發現Qwen殘留配置",
                    "配置文件中可能還有Qwen相關設定",
                    "徹底檢查並移除所有Qwen相關配置")
            else:
                self.log_result("passed",
                    "Qwen已完全移除",
                    "配置文件中未發現Qwen相關設定",
                    "✅ 已正確移除")
                
        except Exception as e:
            self.log_result("high",
                "無法檢查Qwen移除情況",
                f"檢查時出錯: {e}",
                "手動檢查配置文件")
    
    def check_overall_security(self):
        """整體安全評估"""
        print("🔍 進行整體安全評估...")
        
        # 檢查安全審計結果
        critical_count = len(self.results["critical"])
        high_count = len(self.results["high"])
        medium_count = len(self.results["medium"])
        low_count = len(self.results["low"])
        passed_count = len(self.results["passed"])
        
        total_checks = critical_count + high_count + medium_count + low_count + passed_count
        
        if critical_count > 0:
            security_level = "❌ 危險 - 需要立即處理"
        elif high_count > 0:
            security_level = "⚠️  高風險 - 建議儘快處理"
        elif medium_count > 0:
            security_level = "⚠️  中風險 - 建議處理"
        elif low_count > 0:
            security_level = "ℹ️  低風險 - 可考慮處理"
        else:
            security_level = "✅ 安全 - 配置良好"
        
        self.results["summary"] = {
            "security_level": security_level,
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "passed": passed_count,
            "total_checks": total_checks,
            "audit_date": datetime.now().isoformat(),
            "auditor": "久留美安全審計工具"
        }
    
    def run_all_checks(self):
        """運行所有檢查"""
        print("=" * 60)
        print("🛡️  OpenClaw 2026安全審計")
        print("=" * 60)
        print("基於Leo Laboratory安全指南進行全面檢查")
        print()
        
        self.check_vulnerability_1_gateway_exposure()
        self.check_vulnerability_2_dm_policy()
        self.check_vulnerability_4_credentials_storage()
        self.check_vulnerability_6_dangerous_commands()
        self.check_vulnerability_9_logging()
        self.check_qwen_removal()
        self.check_overall_security()
    
    def generate_report(self):
        """生成安全報告"""
        print("\n" + "=" * 60)
        print("📋 安全審計報告")
        print("=" * 60)
        
        summary = self.results.get("summary", {})
        
        print(f"安全等級: {summary.get('security_level', '未知')}")
        print(f"審計時間: {summary.get('audit_date', '未知')}")
        print(f"審計員: {summary.get('auditor', '未知')}")
        print()
        print("檢查統計:")
        print(f"  ✅ 通過: {summary.get('passed', 0)}")
        print(f"  ⚠️  低風險: {summary.get('low', 0)}")
        print(f"  ⚠️  中風險: {summary.get('medium', 0)}")
        print(f"  ⚠️  高風險: {summary.get('high', 0)}")
        print(f"  ❌ 嚴重: {summary.get('critical', 0)}")
        print(f"  總檢查數: {summary.get('total_checks', 0)}")
        
        # 顯示嚴重問題
        if self.results["critical"]:
            print("\n" + "=" * 60)
            print("❌ 嚴重問題 (需要立即處理):")
            print("=" * 60)
            for i, issue in enumerate(self.results["critical"], 1):
                print(f"\n{i}. {issue['title']}")
                print(f"   描述: {issue['description']}")
                print(f"   修復: {issue['fix']}")
        
        # 顯示高風險問題
        if self.results["high"]:
            print("\n" + "=" * 60)
            print("⚠️  高風險問題 (建議儘快處理):")
            print("=" * 60)
            for i, issue in enumerate(self.results["high"], 1):
                print(f"\n{i}. {issue['title']}")
                print(f"   描述: {issue['description']}")
                print(f"   修復: {issue['fix']}")
        
        # 生成修復建議
        print("\n" + "=" * 60)
        print("🔧 立即修復建議 (5分鐘安全清單):")
        print("=" * 60)
        
        immediate_fixes = []
        
        # 收集所有修復建議
        for level in ["critical", "high", "medium"]:
            for issue in self.results[level]:
                if issue.get('fix'):
                    immediate_fixes.append({
                        "title": issue['title'],
                        "fix": issue['fix'],
                        "priority": level
                    })
        
        if immediate_fixes:
            print("按照以下優先順序修復:")
            for i, fix in enumerate(immediate_fixes[:5], 1):  # 只顯示前5個
                priority_emoji = "❌" if fix["priority"] == "critical" else "⚠️ "
                print(f"\n{i}. {priority_emoji} {fix['title']}")
                print(f"   操作: {fix['fix']}")
        else:
            print("✅ 無需立即修復的問題")
        
        # 保存詳細報告
        report_file = Path.home() / ".openclaw" / "workspace" / "security_audit_report_2026.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 詳細報告已保存到: {report_file}")
        
        return self.results
    
    def apply_critical_fixes(self):
        """應用關鍵修復"""
        print("\n" + "=" * 60)
        print("🛠️  應用關鍵安全修復")
        print("=" * 60)
        
        applied_fixes = []
        
        # 修復憑證目錄權限
        if self.credentials_dir.exists():
            try:
                os.chmod(self.credentials_dir, stat.S_IRWXU)
                applied_fixes.append("已修復憑證目錄權限 (chmod 700)")
            except Exception as e:
                print(f"❌ 修復憑證目錄權限失敗: {e}")
        
        # 修復配置文件權限
        if self.config_path.exists():
            try:
                os.chmod(self.config_path, stat.S_IRUSR | stat.S_IWUSR)
                applied_fixes.append("已修復配置文件權限 (chmod 600)")
            except Exception as e:
                print(f"❌ 修復配置文件權限失敗: {e}")
        
        if applied_fixes:
            print("✅ 已應用以下修復:")
            for fix in applied_fixes:
                print(f"  - {fix}")
        else:
            print("ℹ️  無需應用自動修復")

def main():
    """主函數"""
    auditor = OpenClawSecurityAudit()
    
    # 運行所有檢查
    auditor.run_all_checks()
    
    # 生成報告
    report = auditor.generate_report()
    
    # 應用關鍵修復
    auditor.apply_critical_fixes()
    
    print("\n" + "=" * 60)
    print("🎯 後續行動建議")
    print("=" * 60)
    
    print("""
1. **立即行動**:
   - 處理所有「嚴重」和「高風險」問題
   - 定期運行安全審計

2. **持續監控**:
   - 每月檢查一次安全設定
   - 更新OpenClaw後重新審計

3. **深度防護**:
   - 考慮使用沙盒環境
   - 實施網路隔離
   - 啟用完整日誌記錄

4. **資源參考**:
   - Leo Laboratory安全指南
   - OpenClaw官方文檔
   - 定期安全更新
    """)
    
    print("\n" + "=" * 60)
    print("🛡️  安全審計完成")
    print("=" * 60)
    
    # 根據安全等級提供建議
    summary = report.get("summary", {})
    security_level = summary.get("security_level", "")
    
    if "危險" in security_level:
        print("❌ 系統存在嚴重安全風險，請立即處理！")
    elif "高風險" in security_level:
        print("⚠️  系統存在高風險問題，建議儘快處理")
    elif "中風險" in security_level:
        print("⚠️  系統存在中風險問題，建議處理")
    elif "安全" in security_level:
        print("✅ 系統安全配置良好，保持定期檢查")
    
    return report

if __name__ == "__main__":
    main()