#!/bin/bash

# OpenClaw Git安裝轉換腳本
# 此腳本將把您的OpenClaw從當前安裝方式轉換為Git安裝，以實現自動更新功能

echo "==========================================="
echo "OpenClaw Git安裝轉換腳本"
echo "==========================================="
echo ""

echo "警告：此腳本將替換您當前的OpenClaw安裝"
echo "但您的配置文件將被保留"
echo ""

read -p "是否繼續？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "操作已取消"
    exit 1
fi

echo ""
echo "開始備份當前配置..."
cp -r ~/.openclaw ~/openclaw-backup
echo "配置備份完成 -> ~/openclaw-backup"

echo ""
echo "停止當前OpenClaw服務..."
openclaw gateway stop 2>/dev/null || echo "服務未運行或無法停止"

echo ""
echo "卸載當前OpenClaw版本..."
npm uninstall -g openclaw 2>/dev/null || echo "npm全局包不存在或已卸載"

echo ""
echo "下載OpenClaw Git版本..."
rm -rf ~/openclaw-git
git clone https://github.com/openclaw/openclaw.git ~/openclaw-git

if [ $? -eq 0 ]; then
    echo "Git克隆成功"
else
    echo "Git克隆失敗，請檢查網絡連接"
    exit 1
fi

echo ""
echo "安裝OpenClaw..."
cd ~/openclaw-git
npm install

if [ $? -eq 0 ]; then
    echo "依賴安裝成功"
else
    echo "依賴安裝失敗"
    exit 1
fi

echo ""
echo "鏈接OpenClaw到全局..."
npm link

if [ $? -eq 0 ]; then
    echo "npm link成功"
else
    echo "npm link失敗，可能需要使用sudo"
    echo "嘗試使用sudo執行: sudo npm link"
    sudo npm link
    if [ $? -ne 0 ]; then
        echo "npm link最終失敗"
        exit 1
    fi
fi

echo ""
echo "啟動OpenClaw服務..."
openclaw gateway start

echo ""
echo "==========================================="
echo "轉換完成！"
echo "==========================================="
echo ""
echo "您的配置已保留，現在OpenClaw將從Git版本運行"
echo "您可以使用以下命令來更新OpenClaw："
echo "  cd ~/openclaw-git"
echo "  git pull"
echo "  npm install"
echo ""
echo "要驗證安裝，請運行：openclaw --version"
echo "要檢查配置是否正常：openclaw channels status"
echo ""