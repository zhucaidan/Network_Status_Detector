import socket
import struct
import time
import statistics
from threading import Lock

class MTRTrace:
    def __init__(self, ip, count, interval, callback, on_complete=None):
        self.ip = ip
        self.count = float('inf') if count == "无限" else int(count)
        self.interval = float(interval)
        self.callback = callback
        self.on_complete = on_complete
        self.running = False
        self.hops = {}
        self.lock = Lock()
        
    def create_icmp_packet(self, ttl):
        # ICMP Echo Request
        icmp_type = 8
        icmp_code = 0
        icmp_checksum = 0
        icmp_id = 12345
        icmp_seq = 1
        
        header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
        data = b'Q' * 36
        
        checksum = 0
        for i in range(0, len(header + data), 2):
            if i + 1 < len(header + data):
                checksum += (header + data)[i] + ((header + data)[i+1] << 8)
            else:
                checksum += (header + data)[i]
        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum = ~checksum & 0xffff
        
        header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, icmp_id, icmp_seq)
        return header + data

    def send_probe(self, ttl):
        try:
            icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            icmp_socket.settimeout(2)
            
            packet = self.create_icmp_packet(ttl)
            start_time = time.time()
            icmp_socket.sendto(packet, (self.ip, 0))
            
            try:
                data, addr = icmp_socket.recvfrom(1024)
                end_time = time.time()
                return addr[0], (end_time - start_time) * 1000
            except socket.timeout:
                return None, None
            finally:
                icmp_socket.close()
        except Exception as e:
            return None, None

    def update_hop_stats(self, ttl, addr, rtt):
        with self.lock:
            if ttl not in self.hops:
                self.hops[ttl] = {'addr': addr, 'rtts': [], 'loss': 0, 'sent': 0}
            
            self.hops[ttl]['sent'] += 1
            if addr and rtt:
                self.hops[ttl]['rtts'].append(rtt)
            else:
                self.hops[ttl]['loss'] += 1

    def print_hop_stats(self, ttl):
        hop = self.hops[ttl]
        addr = hop['addr'] or '*'
        sent = hop['sent']
        loss = hop['loss']
        rtts = hop['rtts']
        
        if rtts:
            avg_rtt = statistics.mean(rtts)
            loss_rate = (loss / sent) * 100
            self.callback(f"{ttl:2d}  {addr:15s}  {avg_rtt:5.1f}ms  {loss_rate:5.1f}% 丢失")
        else:
            self.callback(f"{ttl:2d}  {'*':15s}  请求超时")

    def start(self):
        self.running = True
        max_ttl = 30
        current_round = 0
        
        self.callback("开始 MTR 检测...")
        self.callback("")  # 添加空行
        self.callback("跳数  地址            延迟     丢包率")
        self.callback("-" * 40)
        
        while self.running and (current_round < self.count):
            for ttl in range(1, max_ttl + 1):
                if not self.running:
                    break
                    
                addr, rtt = self.send_probe(ttl)
                self.update_hop_stats(ttl, addr, rtt)
                self.print_hop_stats(ttl)
                
                if addr == self.ip:
                    break
                    
            current_round += 1
            if current_round < self.count and self.running:
                time.sleep(self.interval)
                self.callback("\n" + "-" * 40)
        
        if not self.running:
            self.callback("\n检测已被用户终止")
        
        self.running = False
        if self.on_complete:
            self.on_complete()
    
    def stop(self):
        self.running = False