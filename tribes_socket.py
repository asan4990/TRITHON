import socket, sys, time
from threading import Thread
from unidecode import unidecode

# Listening socket
HOST = ""
PORT = 31223

# Telnet socket
HOST_TEL = "127.0.0.1"
PORT_TEL = 31337

class TribesSocket:

    def __init__(self):
        self.sock_tel_try = 1
        self.connection_found = False
        self.check_sock_alive = Thread(target=self.check_if_alive).start()
        self.check_first_retry = False

    def create_telnet_socket(self):
        try:
            self.sock_tel = socket.socket()
            self.sock_tel.connect((HOST_TEL, PORT_TEL))
            self.sock_tel.send("change".encode("ascii") + b"\n")
            print("[TRITHON] Telnet socket has connected successfully.")
            self.connection_found = True
        except ConnectionRefusedError:
            if not self.check_first_retry:
                print(
                    "[TRITHON] Did not find a telnet connection. Retrying until found.."
                )
                self.check_first_retry = True
            self.create_telnet_socket()

    def create_tribes_socket(self):
        try:
            print(f"[TRITHON] Listening on port {PORT}..")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((HOST, PORT))
        except socket.error as e:
            print(e)
            sys.exit()

    def check_if_alive(self):
        while True:
            if self.connection_found == True:
                self.send_to_tribes(
                    f'eval("Trithon::HeartBeat(pong);");'
                )
                
            time.sleep(1)


    def check_incoming_conns(self):
        while True:
            pass

    def close_socket(self):
        if self.sock:
            self.sock.close()

    def send_to_tribes(self, cmd: str):
        try:
            cmd = unidecode(cmd)
            self.sock_tel.send(cmd.encode("ascii") + b"\n")
        except socket.error:
            print("[TRITHON] Client disconnected.")
            self.connection_found = False
            self.check_first_retry = False
            self.sock_tel.close()
            self.create_telnet_socket()


tribes_socket = TribesSocket()

# This order is important!
tribes_socket.create_tribes_socket()
tribes_socket.create_telnet_socket()
