# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 項目概述
這是一個即時監控 Claude 服務連接狀態和使用統計的終端應用程序。提供清晰的界面顯示服務狀態、對話信息和歷史使用趨勢。

## 核心架構
- **主程序**: `claude_monitor.py` - Claude Code 監測器，包含 `NetworkMonitor` 類
- **啟動腳本**: 
  - `start_monitor.sh` - Shell 啟動腳本
  - `claude_monitor.command` - macOS 雙擊啟動腳本（包含環境設置）
- **AppleScript 應用**: `Network Monitor.app` - macOS 應用包裝（需更新路徑）

## 常用命令

### 運行監控器
```bash
# 方法 1: 直接執行主程序
python3 claude_monitor.py

# 方法 2: 使用啟動腳本
./start_monitor.sh

# 方法 3: 雙擊 .command 文件（自動設置 Node 環境）
# claude_monitor.command
```

### 安裝依賴
```bash
pip3 install -r requirements.txt
```

### 測試關鍵功能
```bash
# 測試 ccusage 命令（基於 Token 計算模式）
npx ccusage@latest blocks --mode calculate

# 測試每日統計
npx ccusage@latest daily --mode calculate

# 更新 ccusage（自動恢復時使用）
npx --yes ccusage@latest --version
```

## 核心功能

### Claude 服務監控
- 使用 ping 測試網絡延遲
- HTTP 請求測試連接速度
- 實時顯示連接狀態（🟢/🔴）
- 連接狀態變化時發送 macOS 桌面通知

### Claude 對話監控
- 使用 `npx ccusage@latest blocks --mode calculate` 命令獲取使用統計
- 採用基於 Token 計算的費用模式，確保準確性
- 顯示當前對話狀態（活躍/已完成）
- 計算對話重置時間（開始後5小時）
- 實時顯示剩餘時間
- 追蹤 Token 使用量和費用（使用 LiteLLM 最新定價數據）

### 歷史帳單功能
- 使用 `npx ccusage@latest daily --mode calculate` 分析每日成本
- 優先使用 daily 命令，失敗時回退到 blocks 命令統計
- 最近7天趨勢圖表
- 彩色長條圖顯示（紅/黃/綠表示不同消費水平）
- 顯示累計總費用和日均費用
- 所有費用基於 Token 實時計算，非預存值

### 自動恢復機制
- 自動檢測 ccusage 命令失敗
- 連續失敗3次後自動更新 ccusage
- 更新成功後自動恢復監控
- 支持多種 npx 路徑查找

## 程序流程
```
初始化 NetworkMonitor
└── 主監控循環（3秒間隔）
    ├── 網絡測試（每秒）
    │   ├── ping google.com
    │   └── HTTP 請求測速
    ├── Claude 使用檢查
    │   ├── 執行 ccusage 命令
    │   ├── 解析會話數據
    │   └── 計算剩餘時間
    ├── 歷史分析
    │   └── analyze_daily_costs()
    └── 顯示更新
        └── display_status()
```

## 顯示信息說明
- **對話開始**: 完整的開始日期時間
- **開始時間**: 僅顯示時分秒
- **重置時間**: 對話開始後5小時的時分秒
- **剩餘時間**: 距離重置還有多少時間（格式：X時Y分）
- **Token數量**: 當前對話使用的 Token 數
- **花費**: 當前對話的費用（美元）

## 文件結構
```
Claude監控/
├── claude_monitor.py      # 主監控程序
├── start_monitor.sh       # Shell 啟動腳本
├── claude_monitor.command # macOS 啟動腳本
├── requirements.txt       # Python 依賴
├── CLAUDE.md             # 本文件
└── Network Monitor.app/   # macOS 應用（需更新）
```

## 依賴項
- Python 3.7+
- requests==2.31.0
- PyQt5==5.15.10（列在 requirements 但未使用）
- Claude Code CLI (`ccusage` 命令)
- Node.js/npx（運行 ccusage 需要）
- macOS（用於通知功能）

## 開發注意事項
- 需要已安裝並認證 Claude Code CLI
- macOS 可能需要在安全性設置中允許終端通知
- 監控間隔為3秒，可在 `monitor_loop()` 中調整
- ccusage 命令超時設為30秒（因 calculate 模式需要更多計算時間）
- npx 路徑查找包含常見安裝位置
- 費用計算使用 `--mode calculate` 確保基於實際 Token 計算而非預存值

## 關鍵函數說明
- `ping_google()`: 測試網絡延遲
- `check_connection()`: 測試連接速度
- `get_ccusage_info()`: 獲取 Claude 使用信息
- `analyze_daily_costs()`: 分析歷史成本
- `display_status()`: 更新終端顯示
- `show_notification()`: 發送 macOS 通知
- `update_ccusage()`: 自動更新 ccusage 工具

## 故障排查
- 如果 ccusage 命令失敗，檢查 Claude Code CLI 是否已安裝
- 如果找不到 npx，確保 Node.js 已安裝且在 PATH 中
- 使用 `claude_monitor.command` 可自動設置 Node 環境

## 重要指令提醒
- 僅維護一個主程序文件
- 保持代碼簡潔和專業風格
- 不創建額外的文檔文件
- 專注於核心功能的穩定性
- Network Monitor.app 當前指向錯誤路徑，需要更新 AppleScript