import subprocess

class Traceroute:
    def __init__(self, ip, callback, on_complete=None):
        self.ip = ip
        self.callback = callback
        self.on_complete = on_complete
        self.running = False
        self.process = None  # 添加进程引用
        
    def start(self):
        self.running = True
        self.callback(f"开始路由追踪到 {self.ip}...")
        
        try:
            self.process = subprocess.Popen(
                ["tracert", self.ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            while self.running:
                # 使用更短的超时时间来读取输出
                try:
                    output = self.process.stdout.readline()
                    if output == '' and self.process.poll() is not None:
                        break
                    if output and self.running:
                        self.callback(output.strip())
                except:
                    break
            
            if not self.running:
                self.process.terminate()  # 终止进程
                self.process.wait(timeout=1)  # 等待进程结束，最多等待1秒
                self.callback("\n追踪已被用户终止")
                
        except Exception as e:
            self.callback(f"错误: {str(e)}")
            
        self.running = False
        if self.on_complete:
            self.on_complete()
        
    def stop(self):
        self.running = False
        if self.process:  # 如果进程存在，立即终止它
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                pass  # 忽略任何终止过程中的错误