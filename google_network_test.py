#!/usr/bin/env python3
import os
import time
import subprocess
import requests
from datetime import datetime
import sys
import threading
from queue import Queue
import io

class NetworkTester:
    def __init__(self):
        self.last_status = None
        self.fail_count = 0
        self.latest_ping = None
        self.latest_http = None
        self.data_queue = Queue()
        self.first_run = True
        
    def clear_screen(self):
        # 使用 ANSI escape codes 更平滑地清屏
        print("\033[H\033[J", end='')
        
    def ping_google(self):
        """測試到 google.com 的延遲"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', 'google.com'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        latency = float(line.split('time=')[1].split(' ')[0])
                        return latency
            return None
        except Exception:
            return None
            
    def check_connection(self):
        """測試網絡連接速度"""
        try:
            start_time = time.time()
            response = requests.get('https://www.google.com', timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000
                return response_time
            return None
        except:
            return None
            
    def get_status_icon(self, status):
        """根據狀態返回圖標"""
        return "🟢" if status else "🔴"
        
    def network_test_worker(self):
        """後台線程執行網絡測試"""
        while True:
            ping_result = self.ping_google()
            http_result = self.check_connection()
            self.data_queue.put((ping_result, http_result))
            time.sleep(3)
            
    def build_display_buffer(self, current_time, latency, response_time):
        """構建顯示緩衝區"""
        buffer = io.StringIO()
        
        # 標題
        buffer.write("=" * 50 + "\n")
        buffer.write("🌐 Google 網絡測試工具\n")
        buffer.write("=" * 50 + "\n")
        
        # 當前時間
        buffer.write(f"\n📅 當前時間: {current_time}\n")
        
        # 網絡測試
        buffer.write("\n" + "=" * 50 + "\n")
        buffer.write("📡 網絡連接測試\n")
        buffer.write("=" * 50 + "\n")
        
        # Ping 測試
        ping_status = latency is not None
        ping_icon = self.get_status_icon(ping_status)
        
        if latency:
            color = "\033[32m" if latency < 50 else "\033[33m" if latency < 100 else "\033[31m"
            buffer.write(f"{ping_icon} Ping延遲: {color}{latency:.1f}ms\033[0m\n")
        else:
            buffer.write(f"{ping_icon} Ping延遲: \033[31m無法連接\033[0m\n")
            
        # HTTP 測試
        http_status = response_time is not None
        http_icon = self.get_status_icon(http_status)
        
        if response_time:
            color = "\033[32m" if response_time < 500 else "\033[33m" if response_time < 1000 else "\033[31m"
            buffer.write(f"{http_icon} HTTP響應: {color}{response_time:.0f}ms\033[0m\n")
        else:
            buffer.write(f"{http_icon} HTTP響應: \033[31m無法連接\033[0m\n")
            
        # 整體狀態
        overall_status = ping_status and http_status
        overall_icon = self.get_status_icon(overall_status)
        
        buffer.write("\n" + "=" * 50 + "\n")
        buffer.write(f"{overall_icon} 整體狀態: {'正常' if overall_status else '異常'}\n")
        
        # 狀態變化通知
        if self.last_status is not None and self.last_status != overall_status:
            if overall_status:
                buffer.write("\n✅ 網絡已恢復正常！\n")
                self.show_notification("網絡恢復", "Google 網絡連接已恢復正常")
            else:
                buffer.write("\n❌ 網絡連接異常！\n")
                self.show_notification("網絡異常", "無法連接到 Google")
                
        self.last_status = overall_status
        
        # 統計信息
        if not overall_status:
            self.fail_count += 1
        else:
            self.fail_count = 0
            
        if self.fail_count > 0:
            buffer.write(f"\n⚠️  連續失敗次數: {self.fail_count}\n")
            
        buffer.write("\n" + "=" * 50 + "\n")
        buffer.write("按 Ctrl+C 退出\n")
        
        return buffer.getvalue()
        
    def display_status(self):
        """顯示網絡狀態"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 構建完整的顯示內容
        content = self.build_display_buffer(current_time, self.latest_ping, self.latest_http)
        
        # 一次性輸出所有內容
        self.clear_screen()
        print(content, end='', flush=True)
        
    def show_notification(self, title, message):
        """發送 macOS 通知"""
        try:
            subprocess.run([
                'osascript',
                '-e',
                f'display notification "{message}" with title "{title}"'
            ])
        except:
            pass
            
    def run(self):
        """主循環"""
        print("🚀 正在啟動 Google 網絡測試工具...")
        
        # 啟動後台測試線程
        test_thread = threading.Thread(target=self.network_test_worker, daemon=True)
        test_thread.start()
        
        try:
            while True:
                # 獲取最新測試結果
                if not self.data_queue.empty():
                    self.latest_ping, self.latest_http = self.data_queue.get()
                
                # 如果有數據就顯示
                if self.latest_ping is not None or self.latest_http is not None or self.first_run:
                    self.display_status()
                    self.first_run = False
                    
                time.sleep(0.1)  # 更短的主循環間隔，更流暢的顯示
                
        except KeyboardInterrupt:
            print("\n\n👋 測試已停止")
            sys.exit(0)

if __name__ == "__main__":
    tester = NetworkTester()
    tester.run()