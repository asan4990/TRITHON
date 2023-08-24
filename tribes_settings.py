import socket, sys, time
from threading import Thread
from registered_functions import trithon_functions, trithon
from unidecode import unidecode

HOST = ""
PORT = 31223

HOST_TEL = "127.0.0.1"
PORT_TEL = 31337

TRIBES_DIR = r"C:\retro_141_tribes_bak - TEST\config\Modules"

class TribesSocket:
    def __init__(self):
        self.sock_tel_try = 1
        self.connection_not_found = True
        self.check_sock_alive = Thread(target=self.check_if_alive, daemon=True)

    def create_telnet_socket(self):
        try:
            self.sock_tel = socket.socket()
            self.sock_tel.connect((HOST_TEL, PORT_TEL))
            self.sock_tel.send("change".encode("ascii") + b"\n")
            if not self.check_sock_alive.is_alive():
                self.check_sock_alive.start()
            self.connection_not_found = False
            print("[TRITHON] Telnet socket has connected successfully.")
        except ConnectionRefusedError:
            if self.connection_not_found == True and self.sock_tel_try == 1:
                self.sock_tel_try += 1
                print(
                    "[TRITHON] Did not find a telnet connection. Retrying until found.."
                )
            if self.sock_tel.connect_ex(("127.0.0.1", 31337)):
                self.create_telnet_socket()
                time.sleep(1)

    def create_tribes_socket(self):
        try:
            print(f"[TRITHON] Listening on port {PORT}..")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((HOST, PORT))
        except socket.error as msg:
            print(f"Bind failed. Error Code: {str(msg[0])} Message {str(msg[1])}")
            sys.exit()

    def check_if_alive(self):
        while True:
            try:
                if self.connection_not_found == False:
                    self.send_to_tribes(
                        f'eval("Trithon::HeartBeat(pong);");'
                    )
                    #self.sock_tel.send("change".encode("ascii") + b"\n")
            except socket.error:
                if self.connection_not_found == False:
                    self.connection_not_found = True
                    self.sock_tel_try = 1
                    self.sock_tel.close()
                    self.create_telnet_socket()
                
            time.sleep(2)

    def close_socket(self):
        if self.sock:
            self.sock.close()

    def send_to_tribes(self, cmd: str):
        try:
            cmd = unidecode(cmd)
            self.sock_tel.send(cmd.encode("ascii") + b"\n")
        except socket.error:
            self.sock_tel.close()
            print("[TRITHON] Client disconnected.")
            self.create_telnet_socket()
            time.sleep(1)


tribes_socket = TribesSocket()

# This order is important!
tribes_socket.create_tribes_socket()
tribes_socket.create_telnet_socket()
