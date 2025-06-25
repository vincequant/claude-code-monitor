# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview
A real-time terminal application that monitors Claude service connection status and usage statistics, providing clear visual display of service status, conversation information, and historical usage trends.

## Architecture
- **Main Program**: `claude_monitor.py` - Contains `NetworkMonitor` class
- **Launch Scripts**: 
  - `start_monitor.sh` - Basic shell launcher
  - `claude_monitor.command` - macOS launcher with Node environment setup
- **macOS App**: `Network Monitor.app` - AppleScript wrapper (currently points to wrong path: network_monitor.py instead of claude_monitor.py)

## Commands

### Run Monitor
```bash
# Direct execution
python3 claude_monitor.py

# Using shell script
./start_monitor.sh

# macOS double-click (auto-configures Node environment)
open claude_monitor.command
```

### Dependencies
```bash
pip3 install -r requirements.txt
```

### Test ccusage Commands
```bash
# Token-based usage calculation
npx ccusage@latest blocks --mode calculate

# Daily statistics  
npx ccusage@latest daily --mode calculate

# Update ccusage (used for auto-recovery)
npx --yes ccusage@latest --version
```

## Core Features

### Network Monitoring
- Pings google.com for latency testing
- HTTP request speed testing
- Real-time connection status indicators (🟢/🔴)
- macOS desktop notifications on connection state changes

### Claude Usage Monitoring
- Uses `ccusage blocks --mode calculate` for token-based statistics
- Displays active/completed conversation status
- Calculates 5-hour conversation reset timer
- Real-time remaining time display
- Token usage and cost tracking (uses LiteLLM pricing data)

### Historical Billing
- Primary: `ccusage daily --mode calculate` for daily cost analysis
- Fallback: `ccusage blocks` aggregation if daily fails
- 7-day trend visualization with colored bars (red/yellow/green)
- Cumulative total and daily average costs
- All costs calculated from actual tokens, not cached values

### Auto-Recovery
- Detects ccusage command failures
- Auto-updates ccusage after 3 consecutive failures
- Resumes monitoring after successful update
- Searches multiple npx installation paths

## Key Functions
- `ping_google()`: Network latency test
- `check_connection()`: Connection speed test  
- `get_ccusage_info()`: Fetch Claude usage data
- `analyze_daily_costs()`: Historical cost analysis
- `display_status()`: Terminal UI update
- `show_notification()`: macOS notifications
- `update_ccusage()`: Auto-update recovery
- `find_npx_path()`: Locate npx in common paths

## Display Elements
- **對話開始** (Session Start): Full datetime of conversation start
- **開始時間** (Start Time): Time only (HH:MM:SS)
- **重置時間** (Reset Time): 5 hours after start
- **剩餘時間** (Remaining): Time until reset (X時Y分 format)
- **Token數量** (Tokens): Current conversation token count
- **花費** (Cost): Current conversation cost in USD

## Technical Details
- 3-second refresh interval (adjustable in `monitor_loop()`)
- 30-second timeout for ccusage commands (calculate mode needs more time)
- Supports multiple datetime formats:
  - `6/21/2025, 11:52:17 AM` (US format)
  - `2025/6/21 11:52:17` (ISO-like format)
- ANSI color code stripping for clean parsing
- PyQt5 listed in requirements but not used in current version

## Known Issues
- Network Monitor.app AppleScript points to wrong Python file (network_monitor.py instead of claude_monitor.py)
- Requires authenticated Claude Code CLI installation
- macOS may require Terminal notification permissions

## Development Guidelines
- Maintain single main program file structure
- Focus on core functionality stability
- Keep code clean and professional
- Don't create additional documentation files
- Ensure accurate token-based cost calculations