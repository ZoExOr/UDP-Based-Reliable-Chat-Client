import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5382  
BUFFER_SIZE = 1024  

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_HOST, SERVER_PORT))

users = {}  

print(f"UDP 服务器正在运行 {SERVER_HOST}:{SERVER_PORT}...")

def handle_client():
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = data.decode().strip()

            if message.startswith("HELLO-FROM"):
                username = message.split(" ", 1)[1]
                if username in users:
                    response = "IN-USE\n"
                else:
                    users[username] = addr
                    response = f"HELLO {username}\n"
                    print(f"{username} log in, current online users: {list(users.keys())}")
            
            elif message == "LIST":
                response = "LIST-OK " + " ".join(users.keys()) + "\n"

            elif message.startswith("SEND"):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    response = "BAD-RQST-BODY\n"
                else:
                    sender = [u for u, a in users.items() if a == addr]
                    if not sender:
                        response = "BAD-RQST-HDR\n"
                    else:
                        sender = sender[0]
                        receiver, msg = parts[1], parts[2]
                        if receiver not in users:
                            response = "BAD-DEST-USER\n"
                        else:
                            delivery_msg = f"DELIVERY {sender} {msg}\n"
                            sock.sendto(delivery_msg.encode(), users[receiver])
                            response = "SEND-OK\n"
            
            elif message.startswith("ACK"):
                print(f"Receive ACK: {message} from {users}")
                response = ""

            elif message.startswith("NACK"):
                print(f"Receive NACK: {message} from {users}")
                response = ""

            elif message == "!quit":
                user_to_remove = [u for u, a in users.items() if a == addr]
                if user_to_remove:
                    del users[user_to_remove[0]]
                    print(f"{user_to_remove[0]} quit, current online users: {list(users.keys())}")
                response = "BYE\n"

            else:
                response = "BAD-RQST-HDR\n"

            if response:
                sock.sendto(response.encode(), addr)

        except Exception as e:
            print(f"ERROR: {e}")

threading.Thread(target=handle_client, daemon=True).start()

while True:
    pass
