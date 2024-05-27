import socket

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.socket.connect((self.ip, self.port))
            print(f"Connected to server at {self.ip}:{self.port}")
            while True:
                print("Commands:")
                print("1. start <node> <service>")
                print("2. stop <node> <service>")
                print("3. query <node>")
                print("4. exit")
                choice = input("Enter your choice: ")
                if choice.lower() == "exit":
                    break
                elif choice.lower().startswith("query") or choice.lower().startswith("start") or choice.lower().startswith("stop"):
                    self.socket.sendall(choice.encode())
                    data = self.socket.recv(1024)
                    print(f"Received data from server:\n{data.decode()}")
                else:
                    print("Invalid command.")
        finally:
            self.socket.close()

if __name__ == "__main__":
    client = Client("127.0.0.1", 12345)
    client.connect_to_server()
