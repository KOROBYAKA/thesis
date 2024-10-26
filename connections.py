import asyncssh


res_path = "/sys/class/net/wg0/statistics/"
core_path = "/sys/devices/system/cpu/cpu"

class Host:
    def __init__(self, ip: str, usr: str, passwd: str,name: str):
        self.ip = ip
        self.usr = usr
        self.passwd = passwd
        self.cores = 16
        self.active_cores = 1
        self.name = name

    async def start(self, time, duration, iface):
        async with asyncssh.connect(self.ip, port=22, username=self.usr, password=self.passwd) as conn:
           result =  await conn.run(f"python3.11 /home/student/pudge/getter.py {time} {duration} {iface}",check=True)
           print(result.stdout)
           return result.stdout



    async def set_cores_down(self):
        async with asyncssh.connect(self.ip, port=22, username=self.usr, password=self.passwd) as conn:
            for x in range(1,self.cores):
                cmd = 'echo "0" > ' + core_path + str(x) +"/online"
                await conn.run(cmd, check=True)
                print(f"!# {cmd} |||{self.name}")

    async def core_up(self):
        if self.active_cores == 16:
            pass
        else:
            async with asyncssh.connect(self.ip, port=22, username=self.usr, password=self.passwd) as conn:
                cmd = f'echo "1" > {core_path}{self.active_cores}/online'
                await conn.run(cmd, check=True)
                print(f"!# {cmd}")
                self.active_cores+=1



