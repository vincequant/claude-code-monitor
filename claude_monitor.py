#!/usr/bin/env python3
import threading
import time
import subprocess
import platform
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import os
import re
from collections import defaultdict


class NetworkMonitor:
    def __init__(self):
        self.is_monitoring = True
        self.last_status = None
        self.ccusage_data = {
            'latest_session': '--',
            'session_start': '--',
            'session_end': '--',
            'remaining_time': '--',
            'tokens': '--',
            'cost': '--',
            'status': '--'
        }
        self.daily_costs = {}
        self.total_cost = 0
        self.ccusage_failed_count = 0
        self.max_ccusage_failures = 3
        self.npx_path = None
        self.debug_mode = False  # 可以設為 True 來顯示調試信息
        self.session_count = 0
        self.active_sessions = 0
        
    def ping_google(self):
        """測試網絡連接延遲"""
        try:
            param = '-c' if platform.system().lower() != 'windows' else '-n'
            command = ['ping', param, '1', 'google.com']
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                output = result.stdout
                for line in output.split('\n'):
                    if 'avg' in line.lower():
                        try:
                            latency = line.split('/')[4] + 'ms'
                            return True, latency
                        except:
                            pass
                return True, "< 5ms"
            return False, None
        except:
            return False, None
    
    def check_connection(self):
        """檢查網絡連接速度"""
        try:
            start_time = time.time()
            with urllib.request.urlopen('https://www.google.com', timeout=5) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                speed = "良好" if response_time < 200 else "一般" if response_time < 500 else "較慢"
                return True, speed, response_time
        except:
            return False, None, None
    
    def clean_ansi_codes(self, text):
        """移除 ANSI 顏色代碼"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text).strip()
    
    def calculate_session_times(self, session_start_str):
        """計算對話開始時間、結束時間和剩餘時間"""
        try:
            # 支援多種日期格式
            # 先嘗試 AM/PM 格式
            try:
                start_time = datetime.strptime(session_start_str, '%m/%d/%Y, %I:%M:%S %p')
            except:
                # 如果失敗，嘗試 24 小時格式
                start_time = datetime.strptime(session_start_str, "%Y/%m/%d %H:%M:%S")
            end_time = start_time + timedelta(hours=5)
            
            now = datetime.now()
            if end_time > now:
                remaining = end_time - now
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                remaining_time = f"{hours}時{minutes}分"
            else:
                remaining_time = "已過期"
            
            return {
                'session_start': start_time.strftime("%H:%M:%S"),
                'session_end': end_time.strftime("%H:%M:%S"),
                'remaining_time': remaining_time
            }
        except:
            return {
                'session_start': '--',
                'session_end': '--',
                'remaining_time': '--'
            }
    
    def get_ccusage_info(self):
        try:
            # 尋找 npx 的完整路徑
            npx_path = self.find_npx_path()
            if not npx_path:
                print("⚠️  找不到 npx 命令，請確保已安裝 Node.js")
                print("📍 當前 PATH:", os.environ.get('PATH', '未設置'))
                return False
            
            # print(f"🔍 使用 npx 路徑: {npx_path}")  # 減少輸出
            
            # 設置環境變量，確保 npx 可以正常運行
            env = os.environ.copy()
            env['PATH'] = f"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:{env.get('PATH', '')}"
            
            result = subprocess.run([npx_path, 'ccusage@latest', 'blocks', '--mode', 'calculate'], 
                                  capture_output=True, text=True, timeout=30, env=env)
            
            if result.returncode == 0:
                output = result.stdout
                lines = output.split('\n')
                
                if self.debug_mode:
                    print(f"\n=== DEBUG: 找到 {len(lines)} 行輸出 ===")
                    for i, line in enumerate(lines):
                        if 'ACTIVE' in line or 'elapsed' in line:
                            print(f"行 {i}: {repr(line[:100])}...")
                
                # 先檢查是否有 ACTIVE 狀態的對話
                for i, line in enumerate(lines):
                    if 'ACTIVE' in line or ('elapsed' in line and 'remaining' in line):
                        if self.debug_mode:
                            print(f"\n=== DEBUG: 找到 ACTIVE 行 {i}: {repr(line[:100])} ===")
                        parts = line.split('│')
                        if len(parts) >= 6:
                            session_info = self.clean_ansi_codes(parts[1])
                            status = self.clean_ansi_codes(parts[2])
                            tokens = self.clean_ansi_codes(parts[4])
                            cost = self.clean_ansi_codes(parts[5])
                            
                            # 嘗試多種日期格式
                            # 格式1: 6/21/2025, 11:52:17 AM
                            # 格式2: 2025/6/21 11:52:17
                            session_match = re.search(r'(\d+/\d+/\d{4},\s+\d+:\d+:\d+\s+[AP]M)', session_info)
                            if not session_match:
                                session_match = re.search(r'(\d{4}/\d+/\d+\s+\d+:\d+:\d+)', session_info)
                            
                            if self.debug_mode:
                                print(f"  session_info: {repr(session_info[:50])}")
                                print(f"  status: {repr(status)}")
                                print(f"  tokens: {repr(tokens)}")
                                print(f"  cost: {repr(cost)}")
                                print(f"  session_match: {session_match}")
                            
                            if session_match:
                                session_start_str = session_match.group(1)
                                times = self.calculate_session_times(session_start_str)
                                
                                self.ccusage_data = {
                                    'latest_session': session_start_str,
                                    'session_start': times['session_start'],
                                    'session_end': times['session_end'],
                                    'remaining_time': times['remaining_time'],
                                    'tokens': tokens if tokens and tokens != '-' else '--',
                                    'cost': cost if cost and cost != '-' else '--',
                                    'status': 'ACTIVE'
                                }
                                self.ccusage_failed_count = 0  # 成功時重置計數器
                                return True
                
                # 如果沒有 ACTIVE 狀態，找最近的已完成對話
                for line in reversed(lines):
                    if '│' in line and not ('gap' in line or 'ACTIVE' in line or 'PROJECTED' in line):
                        parts = line.split('│')
                        if len(parts) >= 6:
                            session_info = self.clean_ansi_codes(parts[1])
                            tokens = self.clean_ansi_codes(parts[4])
                            cost = self.clean_ansi_codes(parts[5])
                            
                            if tokens and tokens != '-':
                                # 嘗試多種日期格式
                                session_match = re.search(r'(\d+/\d+/\d{4},\s+\d+:\d+:\d+\s+[AP]M)', session_info)
                                if not session_match:
                                    session_match = re.search(r'(\d{4}/\d+/\d+\s+\d+:\d+:\d+)', session_info)
                                
                                if session_match:
                                    session_start_str = session_match.group(1)
                                    times = self.calculate_session_times(session_start_str)
                                    
                                    self.ccusage_data = {
                                        'latest_session': session_start_str,
                                        'session_start': times['session_start'],
                                        'session_end': times['session_end'],
                                        'remaining_time': '已完成',
                                        'tokens': tokens,
                                        'cost': cost,
                                        'status': 'COMPLETED'
                                    }
                                    self.ccusage_failed_count = 0  # 成功時重置計數器
                                    return True
                
                # 如果沒有找到任何數據，可能是因為沒有活躍的對話
                # 不顯示警告，保持界面清潔
                return False
            else:
                print(f"❌ ccusage 命令執行失敗 (返回碼: {result.returncode})")
                if result.stderr:
                    print(f"錯誤輸出: {result.stderr}")
                if result.stdout:
                    print(f"標準輸出: {result.stdout}")
                return False
        except subprocess.TimeoutExpired:
            print("⏰ ccusage 命令執行超時")
            self.ccusage_failed_count += 1
            return False
        except Exception as e:
            print(f"CCUsage 錯誤: {type(e).__name__}: {e}")
            self.ccusage_failed_count += 1
            
            # 如果連續失敗次數達到上限，嘗試更新 ccusage
            if self.ccusage_failed_count >= self.max_ccusage_failures:
                print("🔄 連續失敗次數過多，正在嘗試更新 ccusage...")
                if self.update_ccusage():
                    print("✅ ccusage 更新成功，重置失敗計數器")
                    self.ccusage_failed_count = 0
                else:
                    print("❌ ccusage 更新失敗")
            
            return False
    
    def find_npx_path(self):
        """尋找 npx 命令的完整路徑"""
        if self.npx_path:
            return self.npx_path
            
        # 嘗試常見的 npx 位置
        possible_paths = [
            '/usr/local/bin/npx',
            '/usr/bin/npx',
            '/opt/homebrew/bin/npx',
            os.path.expanduser('~/.nvm/versions/node/*/bin/npx'),
            os.path.expanduser('~/n/*/bin/npx'),
        ]
        
        # 使用 which 命令尋找
        try:
            result = subprocess.run(['which', 'npx'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                self.npx_path = result.stdout.strip()
                return self.npx_path
        except:
            pass
        
        # 檢查可能的路徑
        import glob
        for path in possible_paths:
            if '*' in path:
                matches = glob.glob(path)
                if matches:
                    for match in matches:
                        if os.path.exists(match) and os.access(match, os.X_OK):
                            self.npx_path = match
                            return self.npx_path
            elif os.path.exists(path) and os.access(path, os.X_OK):
                self.npx_path = path
                return self.npx_path
        
        return None
    
    def update_ccusage(self):
        """更新 ccusage 到最新版本"""
        try:
            print("📦 正在更新 ccusage...")
            
            # 尋找 npx 路徑
            npx_path = self.find_npx_path()
            if not npx_path:
                print("❌ 找不到 npx 命令")
                return False
            
            # 使用 --yes 強制更新到最新版本
            result = subprocess.run([npx_path, '--yes', 'ccusage@latest', '--version'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"🎉 ccusage 已更新到版本: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ 更新失敗: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ 更新超時")
            return False
        except Exception as e:
            print(f"❌ 更新過程出錯: {e}")
            return False
    
    def analyze_daily_costs(self):
        """分析每日花費並生成圖表數據"""
        try:
            # 尋找 npx 路徑
            npx_path = self.find_npx_path()
            if not npx_path:
                return False
                
            # 設置環境變量
            env = os.environ.copy()
            env['PATH'] = f"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:{env.get('PATH', '')}"
            
            # 使用 ccusage daily 命令來獲取每日費用，使用 calculate 模式確保準確性
            result = subprocess.run([npx_path, 'ccusage@latest', 'daily', '--mode', 'calculate', '--order', 'asc'], 
                                  capture_output=True, text=True, timeout=30, env=env)
            
            if result.returncode != 0:
                return False
            
            output = result.stdout
            lines = output.split('\n')
            
            daily_costs = defaultdict(float)
            session_count = 0
            active_sessions = 0
            
            # 解析 daily 命令的輸出格式
            # 格式範例: │ 2025     │ - opus-4        │    9,760 │  170,645 │ 11,697,588 │ 153,763,… │ 165,641,8… │   $460.77 │
            for line in lines:
                if '│' in line and not ('Date' in line or 'Total' in line or '─' in line or '═' in line):
                    parts = line.split('│')
                    if len(parts) >= 9:  # daily 格式有9個欄位
                        date_str = self.clean_ansi_codes(parts[1])
                        cost_str = self.clean_ansi_codes(parts[8])
                        
                        # 解析日期 (格式: 2025 06-21)
                        date_match = re.search(r'(\d{4})\s+(\d{2}-\d{2})', date_str)
                        if not date_match:
                            # 嘗試其他格式
                            date_match = re.search(r'(\d{2}-\d{2})', date_str)
                        
                        # 解析費用
                        cost_match = re.search(r'\$?(\d+\.?\d*)', cost_str)
                        
                        if date_match and cost_match:
                            if date_match.lastindex == 2:
                                # 格式: 2025 06-21
                                month_day = date_match.group(2)
                            else:
                                # 格式: 06-21
                                month_day = date_match.group(1)
                            
                            cost_value = float(cost_match.group(1))
                            daily_costs[month_day] = cost_value
            
            # 如果 daily 命令沒有返回數據，使用 blocks 命令作為備用
            if not daily_costs:
                result = subprocess.run([npx_path, 'ccusage@latest', 'blocks', '--mode', 'calculate'], 
                                      capture_output=True, text=True, timeout=30, env=env)
                
                if result.returncode == 0:
                    output = result.stdout
                    lines = output.split('\n')
                    
                    for line in lines:
                        if '│' in line and not ('gap' in line or 'PROJECTED' in line or 'Block Start' in line):
                            parts = line.split('│')
                            if len(parts) >= 6:
                                session_info = self.clean_ansi_codes(parts[1])
                                status_info = self.clean_ansi_codes(parts[2])
                                cost_str = self.clean_ansi_codes(parts[5])
                                
                                # 統計會話數量
                                if 'ACTIVE' in status_info:
                                    active_sessions += 1
                                session_count += 1
                                
                                # 解析日期
                                date_match = re.search(r'(\d+/\d+/\d{4})', session_info)
                                if not date_match:
                                    date_match = re.search(r'(\d{4}/\d+/\d+)', session_info)
                                
                                # 解析費用
                                cost_match = re.search(r'\$?(\d+\.?\d*)', cost_str)
                                
                                if date_match and cost_match and cost_str != '-':
                                    date_str = date_match.group(1)
                                    cost_value = float(cost_match.group(1))
                                    
                                    # 轉換為標準日期格式
                                    try:
                                        try:
                                            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                                        except:
                                            date_obj = datetime.strptime(date_str, "%Y/%m/%d")
                                            
                                        formatted_date = date_obj.strftime("%m/%d")
                                        daily_costs[formatted_date] += cost_value
                                    except:
                                        continue
            
            self.daily_costs = dict(daily_costs)
            self.total_cost = sum(daily_costs.values())
            self.session_count = session_count if session_count > 0 else len(daily_costs)
            self.active_sessions = active_sessions
            return True
            
        except Exception as e:
            # analyze_daily_costs 失敗不影響主功能，只是沒有圖表顯示
            return False
    
    def create_bar_chart(self, width=40):
        """創建美觀的長條圖表"""
        if not self.daily_costs:
            return ["  📊 暫無歷史數據"]
        
        # 獲取最近7天的數據並按日期排序
        all_dates = sorted(self.daily_costs.keys())
        sorted_dates = all_dates[-7:] if len(all_dates) >= 7 else all_dates
        
        if not sorted_dates:
            return ["  📊 暫無歷史數據"]
        
        chart_lines = []
        chart_lines.append("  📊 歷史帳單統計 (最近7天)")
        chart_lines.append("  " + "─" * 48)
        
        max_cost = max(self.daily_costs[date] for date in sorted_dates)
        
        for date in sorted_dates:
            cost = self.daily_costs[date]
            
            # 計算長條長度
            if max_cost > 0:
                bar_length = int((cost / max_cost) * 25)
            else:
                bar_length = 0
            
            # 根據金額選擇顏色和圖標
            if cost >= 50:
                bar_chars = "█"  # 實心方塊
                cost_indicator = "💸"  # 高消費
            elif cost >= 30:
                bar_chars = "▓"  # 深色方塊
                cost_indicator = "💵"  # 中高消費
            elif cost >= 10:
                bar_chars = "▒"  # 中等方塊
                cost_indicator = "💰"  # 中等消費
            elif cost > 0:
                bar_chars = "░"  # 淺色方塊
                cost_indicator = "💲"  # 低消費
            else:
                bar_chars = "·"  # 點
                cost_indicator = "🪙"  # 極少消費
            
            # 創建長條
            bar = bar_chars * max(1, bar_length) if bar_length > 0 else "·"
            
            # 格式化輸出
            chart_lines.append(f"  {cost_indicator} {date}: {bar:<25} ${cost:>7.2f}")
        
        chart_lines.append("  " + "─" * 48)
        
        # 添加統計信息
        avg_cost = self.total_cost / len(self.daily_costs) if self.daily_costs else 0
        chart_lines.append(f"  💳 總計: ${self.total_cost:>7.2f}  |  📊 平均: ${avg_cost:>7.2f}/天")
        
        # 添加會話統計
        if self.session_count > 0:
            chart_lines.append(f"  🔢 總會話數: {self.session_count}  |  ⚡ 活躍會話: {self.active_sessions}")
        
        return chart_lines
    
    def show_notification(self, message):
        system = platform.system().lower()
        try:
            if system == 'darwin':  # macOS
                subprocess.run([
                    'osascript', '-e', 
                    f'display notification "{message}" with title "Claude Code 監測器" sound name "Glass"'
                ])
            elif system == 'linux':
                subprocess.run(['notify-send', 'Claude Code 監測器', message])
            elif system == 'windows':
                subprocess.run(['msg', '*', message])
        except:
            print(f"🔔 系統提醒: {message}")
    
    def clear_screen(self):
        # 使用標準 clear 命令
        os.system('clear' if platform.system() != 'Windows' else 'cls')
    
    def format_line(self, content, width=50):
        """輔助函數: 格式化一行內容以確保寬度一致"""
        # 計算實際顯示寬度（考慮 emoji 和中文）
        display_len = 0
        for char in content:
            if ord(char) > 0x1F000:  # Emoji 範圍
                display_len += 2
            elif ord(char) > 0x4E00:  # 中文範圍
                display_len += 2
            else:
                display_len += 1
        
        padding_needed = width - display_len
        return content + ' ' * max(0, padding_needed)
    
    def display_status(self, connected, speed, latency, current_time):
        self.clear_screen()
        
        # 使用簡潔的設計
        print("\n" + "=" * 54)
        print("         Claude Code 網絡監測器 v2.0")
        print("=" * 54)
        print()
        
        # 網絡狀態
        print("[🌐 網絡連接狀態]")
        if connected:
            # 根據延遲選擇顏色圖標
            try:
                latency_ms = float(latency.replace('ms', ''))
                if latency_ms < 50:
                    latency_icon = "🟢"
                elif latency_ms < 150:
                    latency_icon = "🟡"
                else:
                    latency_icon = "🔴"
            except:
                latency_icon = "🟢"
                
            print(f"  🟢 狀態: 已連接")
            print(f"  🚀 網速: {speed}")
            print(f"  {latency_icon} 延遲: {latency}")
        else:
            print("  🔴 狀態: 連接失敗")
            print("  💔 無法連接到網絡")
        
        print("\n[🤖 Claude Code 使用狀態]")
        
        # 對話開始時間
        if self.ccusage_data['latest_session'] != '--':
            print(f"  📅 對話開始: {self.ccusage_data['latest_session']}")
        else:
            print("  📅 對話開始: --")
        
        # 時間信息
        if self.ccusage_data['session_start'] != '--':
            print(f"  ⏱️  時間: {self.ccusage_data['session_start']} → {self.ccusage_data['session_end']} (重置)")
            print(f"  ⏰ 剩餘: {self.ccusage_data['remaining_time']}")
        
        # Token 和費用
        if self.ccusage_data['tokens'] != '--':
            try:
                token_num = int(self.ccusage_data['tokens'].replace(',', ''))
                formatted_tokens = f"{token_num:,}"
            except:
                formatted_tokens = self.ccusage_data['tokens']
                
            print(f"  🎫 Tokens: {formatted_tokens}")
            print(f"  💰 費用: {self.ccusage_data['cost']}")
        
        # 狀態
        status_text = {
            'ACTIVE': '⚡ 活躍中',
            'COMPLETED': '✅ 已完成',
            'RUNNING': '🔄 運行中',
            '--': '⏸️  未活動'
        }
        current_status = status_text.get(self.ccusage_data['status'], f"❓ {self.ccusage_data['status']}")
        print(f"  📍 狀態: {current_status}")
        
        # 歷史帳單
        print("\n[📊 歷史帳單統計 (基於 Token 計算)]")
        if self.daily_costs:
            # 獲取最近7天的數據
            all_dates = sorted(self.daily_costs.keys())
            recent_dates = all_dates[-7:] if len(all_dates) >= 7 else all_dates
            
            for date in recent_dates:
                cost = self.daily_costs[date]
                # 根據金額選擇顯示符號
                if cost >= 50:
                    indicator = "💸"  # 高消費
                elif cost >= 30:
                    indicator = "💵"  # 中高消費  
                elif cost >= 10:
                    indicator = "💰"  # 中等消費
                else:
                    indicator = "💲"  # 低消費
                    
                # 簡單的長條圖
                bar_length = int((cost / 100) * 20) if cost < 100 else 20
                bar = "█" * bar_length if bar_length > 0 else "│"
                
                print(f"  {indicator} {date}: {bar} ${cost:.2f}")
            
            # 統計信息
            avg_cost = self.total_cost / len(self.daily_costs) if self.daily_costs else 0
            print(f"\n  💳 總計: ${self.total_cost:.2f}")
            print(f"  📊 平均: ${avg_cost:.2f}/天")
            
            if self.session_count > 0:
                print(f"  🔢 總會話數: {self.session_count}")
                print(f"  ⚡ 活躍會話: {self.active_sessions}")
        else:
            print("  暫無歷史數據")
        
        print(f"\n🕐 最後更新: {current_time}")
        print("\n按 Ctrl+C 停止監控")
        print("=" * 54)
    
    def monitor_loop(self):
        while self.is_monitoring:
            try:
                ping_success, latency = self.ping_google()
                conn_success, speed, _ = self.check_connection()
                ccusage_success = self.get_ccusage_info()
                self.analyze_daily_costs()
                
                connected = ping_success and conn_success
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.display_status(connected, speed or "--", latency or "--", current_time)
                
                if not connected and self.last_status != False:
                    self.show_notification("🚨 網絡連接中斷")
                elif connected and self.last_status == False:
                    self.show_notification("🎉 網絡連接已恢復")
                
                self.last_status = connected
                
            except Exception as e:
                print(f"監測錯誤: {e}")
            
            # 每3秒刷新一次
            time.sleep(3)
    
    def start(self):
        print("\n🚀 Claude Code 監測器 v2.0 啟動中...")
        print("🔍 正在檢查網絡和 Claude 狀態...")
        print("🔄 具備自動更新 ccusage 功能")
        print("📊 包含歷史帳單統計功能 (使用 Token 計算模式)")
        print("💡 費用計算採用 ccusage --mode calculate 確保準確性")
        print("🔄 刷新頻率: 3秒")
        print("✅ 準備就緒，開始監測\n")
        time.sleep(2)
        
        try:
            self.monitor_loop()
        except KeyboardInterrupt:
            print("\n\n👋 Claude Code 監測器已停止")
            print("🌙 監測服務已關閉")
            self.is_monitoring = False


if __name__ == "__main__":
    monitor = NetworkMonitor()
    monitor.start()