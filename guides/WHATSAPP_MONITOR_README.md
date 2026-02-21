# WhatsApp连接监控设置

## 当前状态
- **状态**: ⚠️ 警告 - 需要扫描QR码
- **最后检查**: 2026-02-10 14:14:51
- **QR码**: 已生成，等待扫描

## 已创建的脚本

### 1. `check_whatsapp.sh` (原始脚本)
- 路径: `/Users/gordonlui/.openclaw/workspace/check_whatsapp.sh`
- 功能: 检查状态并自动重连
- 问题: 可能会生成多个QR码冲突

### 2. `whatsapp_monitor.sh` (智能监控脚本)
- 路径: `/Users/gordonlui/.openclaw/workspace/whatsapp_monitor.sh`
- 功能: 智能检查状态，带重试机制
- 日志: `/Users/gordonlui/.openclaw/workspace/whatsapp_monitor.log`

### 3. `check_whatsapp_simple.sh` (简单检查脚本)
- 路径: `/Users/gordonlui/.openclaw/workspace/check_whatsapp_simple.sh`
- 功能: 只检查状态，不自动重连
- 日志: `/Users/gordonlui/.openclaw/workspace/whatsapp_check.log`
- **推荐用于cron作业**

## 当前需要的手动操作

1. **扫描QR码**:
   - WhatsApp已经生成了QR码
   - 请在WhatsApp手机应用中扫描二维码连接

2. **验证连接**:
   - 扫描后，运行检查脚本确认连接状态:
   ```bash
   /Users/gordonlui/.openclaw/workspace/check_whatsapp_simple.sh
   ```

## 设置cron监控（推荐）

### 方案1: 使用OpenClaw cron
```bash
# 每30分钟检查一次
openclaw cron add --name "WhatsApp监控" --schedule "0 */30 * * * *" --payload '{"kind":"systemEvent","text":"检查WhatsApp连接状态"}' --sessionTarget main
```

### 方案2: 系统crontab
```bash
# 编辑crontab
crontab -e

# 添加以下行（每30分钟检查一次）
*/30 * * * * /Users/gordonlui/.openclaw/workspace/check_whatsapp_simple.sh
```

## 故障排除

### 如果QR码过期:
1. 终止所有WhatsApp相关进程
2. 运行重连脚本:
   ```bash
   /Users/gordonlui/.openclaw/workspace/whatsapp_monitor.sh
   ```
3. 扫描新的QR码

### 检查连接状态:
```bash
openclaw status | grep -A2 "WhatsApp"
```

### 查看详细日志:
```bash
tail -f /Users/gordonlui/.openclaw/workspace/whatsapp_monitor.log
```

## 下一步操作

1. **立即操作**: 扫描当前显示的QR码
2. **设置监控**: 配置cron作业定期检查
3. **验证**: 确认连接成功后测试消息发送

---
*最后更新: 2026-02-10 14:15*