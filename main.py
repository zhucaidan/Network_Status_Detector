import tkinter as tk
from tkinter import ttk
import threading
from ping_modules.icmp_ping import ICMPPing
from ping_modules.traceroute import Traceroute
from ping_modules.mtr_trace import MTRTrace
from ping_modules.tcp_ping import TCPPing
from ping_modules.udp_ping import UDPPing
from ping_modules.http_status import HTTPStatus
from ping_modules.https_status import HTTPSStatus

class PingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("多种Ping检测工具")
        self.root.geometry("800x600")
        
        # 将窗口居中显示
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算窗口位置
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建变量
        self.ip_var = tk.StringVar()
        self.count_var = tk.StringVar(value="10")
        self.interval_var = tk.StringVar(value="1")
        self.ping_type = tk.StringVar(value="ICMP")
        self.tcp_port_var = tk.StringVar(value="80")
        self.udp_port_var = tk.StringVar(value="53")
        self.is_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部框架
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(fill=tk.X)
        
        # IP地址输入
        ttk.Label(top_frame, text="IP地址:").pack(side=tk.LEFT)
        ttk.Entry(top_frame, textvariable=self.ip_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # 请求次数选择
        ttk.Label(top_frame, text="请求次数:").pack(side=tk.LEFT)
        counts = ["无限"] + [str(x) for x in range(10, 101, 10)]
        ttk.Combobox(top_frame, textvariable=self.count_var, values=counts, width=10).pack(side=tk.LEFT, padx=5)
        
        # 发送间隔选择
        ttk.Label(top_frame, text="发送间隔(秒):").pack(side=tk.LEFT)
        intervals = [str(x/2) for x in range(1, 21)]
        ttk.Combobox(top_frame, textvariable=self.interval_var, values=intervals, width=10).pack(side=tk.LEFT, padx=5)
        
        # 开始/停止按钮
        self.start_btn = ttk.Button(top_frame, text="开始", command=self.toggle_ping)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 检测类型框架
        type_frame = ttk.LabelFrame(self.root, text="检测类型", padding="5")
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ICMP检测
        ttk.Radiobutton(type_frame, text="ICMP检测", variable=self.ping_type, value="ICMP").pack(side=tk.LEFT, padx=5)
        
        # Traceroute跟踪
        ttk.Radiobutton(type_frame, text="路由追踪", variable=self.ping_type, value="Traceroute").pack(side=tk.LEFT, padx=5)
        
        # MTR跟踪
        ttk.Radiobutton(type_frame, text="MTR检测", variable=self.ping_type, value="MTR").pack(side=tk.LEFT, padx=5)
        
        # TCP检测
        tcp_frame = ttk.Frame(type_frame)
        tcp_frame.pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tcp_frame, text="TCP检测", variable=self.ping_type, value="TCP").pack(side=tk.LEFT)
        ttk.Entry(tcp_frame, textvariable=self.tcp_port_var, width=6).pack(side=tk.LEFT)
        
        # UDP检测
        udp_frame = ttk.Frame(type_frame)
        udp_frame.pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(udp_frame, text="UDP检测", variable=self.ping_type, value="UDP").pack(side=tk.LEFT)
        ttk.Entry(udp_frame, textvariable=self.udp_port_var, width=6).pack(side=tk.LEFT)
        
        # HTTP状态检测
        ttk.Radiobutton(type_frame, text="HTTP状态检测", variable=self.ping_type, value="HTTP").pack(side=tk.LEFT, padx=5)
        
        # HTTPS状态检测
        ttk.Radiobutton(type_frame, text="HTTPS状态检测", variable=self.ping_type, value="HTTPS").pack(side=tk.LEFT, padx=5)
        
        # 日志输出区域
        self.log_text = tk.Text(self.root, height=20, padx=10, pady=10)  # 添加 padx 和 pady 参数
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def toggle_ping(self):
        if not self.is_running:
            self.start_ping()
        else:
            self.stop_ping()
            
    def start_ping(self):
        self.is_running = True
        self.start_btn.configure(text="停止")
        self.log_text.delete(1.0, tk.END)
        
        ping_type = self.ping_type.get()
        ip = self.ip_var.get()
        count = self.count_var.get()
        interval = float(self.interval_var.get())
        
        def on_complete():
            self.is_running = False
            self.start_btn.configure(text="开始")
        
        if ping_type == "ICMP":
            self.current_ping = ICMPPing(ip, count, interval, self.log_callback, on_complete)
        elif ping_type == "Traceroute":
            self.current_ping = Traceroute(ip, self.log_callback, on_complete)
        elif ping_type == "MTR":
            self.current_ping = MTRTrace(ip, count, interval, self.log_callback, on_complete)
        elif ping_type == "TCP":
            port = int(self.tcp_port_var.get())
            self.current_ping = TCPPing(ip, port, count, interval, self.log_callback, on_complete)
        elif ping_type == "UDP":
            port = int(self.udp_port_var.get())
            self.current_ping = UDPPing(ip, port, count, interval, self.log_callback, on_complete)
            
        elif ping_type == "HTTP":
            self.current_ping = HTTPStatus(ip, count, interval, self.log_callback, on_complete)
        elif ping_type == "HTTPS":
            self.current_ping = HTTPSStatus(ip, count, interval, self.log_callback, on_complete)
            
        threading.Thread(target=self.current_ping.start, daemon=True).start()
        
    def stop_ping(self):
        if hasattr(self, 'current_ping'):
            self.current_ping.stop()
            self.is_running = False
            self.start_btn.configure(text="开始")
            # 删除这行，因为在各个ping模块中已经有了终止提示
            # self.log_text.insert(tk.END, "\n检测已手动停止\n")
            self.log_text.see(tk.END)
        self.is_running = False
        self.start_btn.configure(text="开始")
        
    def log_callback(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PingGUI(root)
    root.mainloop()