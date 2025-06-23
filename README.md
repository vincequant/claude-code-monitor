# Claude Code Monitor 🚀

<div align="center">
  
  ![Claude Code](https://img.shields.io/badge/Claude_Code-Monitor-blue?style=for-the-badge&logo=anthropic&logoColor=white)
  ![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python&logoColor=white)
  ![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
  ![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?style=for-the-badge&logo=apple&logoColor=white)
  
  <h3>實時監控您的 Claude Code CLI 使用狀態和網絡連接</h3>
  
  [English](#english) | [中文](#中文)
  
</div>

---

## 🌟 功能特色

### 🔍 實時監控
- **網絡狀態檢測**: 即時顯示 Claude 服務連接狀態
- **對話追蹤**: 監控當前對話狀態、Token 使用量和費用
- **智能提醒**: 連接狀態變化時自動發送 macOS 桌面通知
- **自動恢復**: 工具失敗時自動更新並恢復監控

### 📊 數據分析
- **歷史統計**: 查看最近 7 天的使用趨勢
- **費用計算**: 基於實際 Token 使用量精確計算費用
- **視覺化圖表**: 彩色長條圖直觀顯示消費水平
- **日均分析**: 自動計算日均使用量和費用

### ⚡ 技術優勢
- **高效能**: 3 秒更新間隔，實時響應
- **準確計費**: 採用 `--mode calculate` 確保費用計算準確性
- **多重啟動**: 支持命令行、腳本和 macOS 應用多種啟動方式
- **自動環境配置**: `.command` 腳本自動設置 Node.js 環境

## 📸 預覽

<div align="center">
  <img src="https://user-images.githubusercontent.com/placeholder/demo.gif" alt="Claude Monitor Demo" width="800">
  
  *實時監控介面展示*
</div>

## 🚀 快速開始

### 系統要求
- macOS (用於桌面通知功能)
- Python 3.7+
- Node.js/npm (用於 ccusage 命令)
- Claude Code CLI (已安裝並認證)

### 安裝步驟

1. **克隆倉庫**
   ```bash
   git clone https://github.com/yourusername/claude-code-monitor.git
   cd claude-code-monitor
   ```

2. **安裝依賴**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **確保 Claude Code CLI 已安裝**
   ```bash
   # 測試 ccusage 命令
   npx ccusage@latest --version
   ```

### 運行方式

#### 方法 1: 直接運行 Python
```bash
python3 claude_monitor.py
```

#### 方法 2: 使用啟動腳本
```bash
./start_monitor.sh
```

#### 方法 3: macOS 雙擊啟動
雙擊 `claude_monitor.command` 文件即可啟動（自動配置環境）

## 📖 使用指南

### 監控界面說明

```
===========================================
         Claude Code 監測器
===========================================

服務狀態:
  Claude 服務: 🟢 正常 (延遲: 45ms)
  連接速度: 156 KB/s
  
當前對話:
  狀態: 活躍
  開始時間: 14:30:45
  重置時間: 19:30:45
  剩餘時間: 3時25分
  Token: 15,234
  花費: $0.45

歷史帳單 (最近7天):
  2025-06-17: ████████ $2.35
  2025-06-18: ██████ $1.89
  2025-06-19: █████████ $2.78
  2025-06-20: ███ $0.95
  2025-06-21: ███████ $2.12
  2025-06-22: ████ $1.23
  2025-06-23: ██ $0.67
  
  累計總費用: $11.99
  日均費用: $1.71
```

### 狀態指示器
- 🟢 **綠燈**: 服務正常連接
- 🔴 **紅燈**: 服務連接異常
- 📊 **長條圖顏色**:
  - 🟥 紅色: 高消費 (>$3)
  - 🟨 黃色: 中等消費 ($1.5-$3)
  - 🟩 綠色: 低消費 (<$1.5)

## 🛠️ 配置選項

### 調整監控間隔
在 `claude_monitor.py` 中修改:
```python
time.sleep(3)  # 改為您想要的秒數
```

### 自定義通知
macOS 通知功能在 `show_notification()` 函數中配置

### 費用閾值
修改 `analyze_daily_costs()` 中的顏色閾值:
```python
if cost > 3.0:      # 高消費閾值
elif cost > 1.5:    # 中等消費閾值
```

## 🔧 故障排除

### ccusage 命令失敗
- 確保 Claude Code CLI 已安裝: `npm install -g @anthropic-ai/claude-code`
- 檢查是否已認證: `claude auth login`

### 找不到 npx
- 確保 Node.js 已安裝: `brew install node`
- 使用 `.command` 腳本自動配置環境

### 通知權限
- 前往 系統偏好設置 > 通知
- 允許終端應用發送通知

## 📁 項目結構

```
claude-code-monitor/
├── claude_monitor.py      # 主監控程序
├── start_monitor.sh       # Shell 啟動腳本
├── claude_monitor.command # macOS 啟動腳本
├── requirements.txt       # Python 依賴
├── README.md             # 項目說明
├── CLAUDE.md             # Claude Code 指引
└── .gitignore            # Git 忽略文件
```

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 本倉庫
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- [Claude Code CLI](https://claude.ai/code) - Anthropic 官方 CLI 工具
- [LiteLLM](https://github.com/BerriAI/litellm) - Token 計費數據來源

---

<div id="english"></div>

## English

### 🌟 Features

- **Real-time Monitoring**: Track Claude service connection status
- **Session Tracking**: Monitor current conversation status, token usage, and costs
- **Smart Notifications**: Automatic macOS desktop notifications on connection changes
- **Auto-recovery**: Automatically updates and recovers when tools fail

### 📊 Data Analysis

- **Historical Statistics**: View usage trends for the last 7 days
- **Cost Calculation**: Accurate cost calculation based on actual token usage
- **Visual Charts**: Colorful bar charts showing consumption levels
- **Daily Analysis**: Automatic calculation of daily average usage and costs

### 🚀 Quick Start

1. Clone the repository
2. Install dependencies: `pip3 install -r requirements.txt`
3. Run: `python3 claude_monitor.py`

For detailed instructions, please refer to the Chinese documentation above.

---

<div align="center">
  
  Made with ❤️ for Claude Code users
  
  ⭐ Star this repo if you find it helpful!
  
</div>