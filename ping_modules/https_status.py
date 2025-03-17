import requests
import time

class HTTPSStatus:
    def __init__(self, ip, count, interval, callback, on_complete=None):
        self.ip = ip if ip.startswith('https://') else f'https://{ip}'
        self.count = float('inf') if count == "无限" else int(count)
        self.interval = float(interval)
        self.callback = callback
        self.on_complete = on_complete
        self.running = False
        self.times = []
        self.sent = 0
        self.received = 0
        
    def start(self):
        self.running = True
        self.sent = 0
        self.received = 0
        
        self.callback(f"开始 HTTPS 状态检测 {self.ip}...")
        self.callback("")  # 添加空行
        
        while self.running and (self.sent < self.count):
            try:
                start_time = time.time()
                response = requests.get(self.ip, timeout=5, verify=True)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                self.times.append(response_time)
                self.sent += 1
                
                if response.status_code == 200:
                    self.received += 1
                    self.callback(f"状态码: {response.status_code}, 时间={response_time:.1f}ms")
                else:
                    self.callback(f"异常状态码: {response.status_code}, 时间={response_time:.1f}ms")
                    
                if self.sent < self.count and self.running:
                    time.sleep(self.interval)
                    
            except requests.RequestException as e:
                self.callback(f"请求失败: {str(e)}")
                self.sent += 1
                
                if self.sent < self.count and self.running:
                    time.sleep(self.interval)
        
        if not self.running:
            self.callback("\n检测已被用户终止")
            
        if self.times:
            min_time = min(self.times)
            max_time = max(self.times)
            avg_time = sum(self.times) / len(self.times)
            success_rate = (self.received / self.sent) * 100
            
            self.callback(f"\nHTTPS状态检测统计:")
            self.callback(f"    请求: 已发送 = {self.sent}, 成功(200) = {self.received}, "
                        f"失败 = {self.sent - self.received} ({100 - success_rate:.1f}% 失败)")
            self.callback(f"响应时间(毫秒):")
            self.callback(f"    最短 = {min_time:.1f}ms, 最长 = {max_time:.1f}ms, 平均 = {avg_time:.1f}ms")
            
        self.running = False
        if self.on_complete:
            self.on_complete()
            
    def stop(self):
        self.running = False