#!/bin/bash

echo "設定 Mac Finder 顯示隱藏檔案..."
echo ""

# 設定 Finder 顯示隱藏檔案
defaults write com.apple.finder AppleShowAllFiles YES

# 設定 Finder 顯示路徑列
defaults write com.apple.finder ShowPathbar -bool true

# 設定 Finder 顯示狀態列
defaults write com.apple.finder ShowStatusBar -bool true

# 設定 Finder 顯示標題列
defaults write com.apple.finder ShowTabView -bool true

# 重新啟動 Finder 以套用設定
echo "重新啟動 Finder 以套用設定..."
killall Finder

echo ""
echo "設定完成！Finder 現在會："
echo "1. 顯示所有隱藏檔案（以 . 開頭的檔案）"
echo "2. 顯示路徑列"
echo "3. 顯示狀態列"
echo "4. 顯示標題列"

echo ""
echo "若要取消顯示隱藏檔案，請執行："
echo "defaults write com.apple.finder AppleShowAllFiles NO && killall Finder"