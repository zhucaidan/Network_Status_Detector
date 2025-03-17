import socket
import time
import statistics

class TCPPing:
    def __init__(self, ip, port, count, interval, callback, on_complete=None):
        self.ip = ip
        self.port = port
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
        
        self.callback(f"开始 TCP Ping {self.ip}:{self.port}...")
        self.callback("")  # 添加空行
        
        while self.running and (self.sent < self.count):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                start_time = time.time()
                result = sock.connect_ex((self.ip, self.port))
                end_time = time.time()
                
                self.sent += 1
                
                if result == 0:
                    self.received += 1
                    response_time = (end_time - start_time) * 1000
                    self.times.append(response_time)
                    self.callback(f"连接到 {self.ip}:{self.port} 成功: 时间={response_time:.1f}ms")
                else:
                    self.callback(f"连接到 {self.ip}:{self.port} 失败")
                    
                sock.close()
                
                if self.sent < self.count and self.running:
                    time.sleep(self.interval)
                    
            except Exception as e:
                self.callback(f"错误: {str(e)}")
                self.sent += 1
                
        if not self.running:
            self.callback("\n检测已被用户终止")
            
        loss_rate = ((self.sent - self.received) / self.sent) * 100 if self.sent > 0 else 0
        
        if self.times:
            min_time = min(self.times)
            max_time = max(self.times)
            avg_time = statistics.mean(self.times)
            self.callback(f"\nTCP Ping 统计信息:")
            self.callback(f"    连接尝试: 已发送 = {self.sent}, 已成功 = {self.received}, 失败 = {self.sent - self.received} ({loss_rate:.1f}% 失败)")
            self.callback(f"连接时间(以毫秒为单位):")
            self.callback(f"    最短 = {min_time:.1f}ms, 最长 = {max_time:.1f}ms, 平均 = {avg_time:.1f}ms")
        
        self.running = False
        if self.on_complete:
            self.on_complete()
            
    def stop(self):
        self.running = False