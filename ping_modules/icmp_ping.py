import os
import time
import statistics
from datetime import datetime

class ICMPPing:
    def __init__(self, ip, count, interval, callback, on_complete=None):
        self.ip = ip
        self.count = float('inf') if count == "无限" else int(count)
        self.interval = float(interval)
        self.callback = callback
        self.on_complete = on_complete
        self.running = False
        self.times = []
        
    def start(self):
        self.running = True
        sent = 0
        received = 0
        
        self.callback(f"开始 ICMP Ping {self.ip}...")
        self.callback("")  # 添加空行
        
        while self.running and (sent < self.count):
            if not self.running:
                break
                
            response = os.popen(f"ping -n 1 {self.ip}").read()
            sent += 1
            
            if "TTL=" in response:
                received += 1
                time_ms = float(response.split("时间=")[1].split("ms")[0])
                self.times.append(time_ms)
                self.callback(f"来自 {self.ip} 的回复: 时间={time_ms}ms")
            else:
                self.callback(f"请求超时")
                
            if sent < self.count and self.running:
                time.sleep(self.interval)
                
        if not self.running:
            self.callback("\n检测已被用户终止")
            
        if self.times:
            min_time = min(self.times)
            max_time = max(self.times)
            avg_time = statistics.mean(self.times)
            self.callback(f"\nPing 统计信息:")
            self.callback(f"    数据包: 已发送 = {sent}, 已接收 = {received}, 丢失 = {sent - received} ({((sent - received) / sent) * 100:.1f}% 丢失)")
            self.callback(f"往返行程的估计时间(以毫秒为单位):")
            self.callback(f"    最短 = {min_time:.1f}ms, 最长 = {max_time:.1f}ms, 平均 = {avg_time:.1f}ms")
        
        self.running = False
        if self.on_complete:
            self.on_complete()
            
    def stop(self):
        self.running = False