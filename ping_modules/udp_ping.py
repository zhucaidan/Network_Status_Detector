import socket
import time
import statistics

class UDPPing:
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
        
        self.callback(f"开始 UDP Ping {self.ip}:{self.port}...")
        self.callback("")  # 添加空行
        
        while self.running and (self.sent < self.count):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                
                start_time = time.time()
                sock.sendto(b"Ping", (self.ip, self.port))
                
                try:
                    data, addr = sock.recvfrom(1024)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    self.times.append(response_time)
                    self.received += 1
                    self.callback(f"来自 {self.ip}:{self.port} 的回复: 时间={response_time:.1f}ms")
                except socket.timeout:
                    self.callback(f"请求超时")
                    
                self.sent += 1
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
            self.callback(f"\nUDP Ping 统计信息:")
            self.callback(f"    数据包: 已发送 = {self.sent}, 已接收 = {self.received}, 丢失 = {self.sent - self.received} ({loss_rate:.1f}% 丢失)")
            self.callback(f"往返行程的估计时间(以毫秒为单位):")
            self.callback(f"    最短 = {min_time:.1f}ms, 最长 = {max_time:.1f}ms, 平均 = {avg_time:.1f}ms")
        
        self.running = False
        if self.on_complete:
            self.on_complete()
            
    def stop(self):
        self.running = False