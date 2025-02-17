import socket
import threading
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5382  
BUF_SIZE = 1024  

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
polynomial = "11111111111111111"
users, msg_list, msg_count, ack_count, completed_ack = [], [], [], [], []
exit_flag = False


def xor(data, polynomial):
    return ''.join('1' if data[i] != polynomial[i] else '0' for i in range(len(polynomial)))

def crc_add(data_bits, polynomial):
    data_bits += "0" * (len(polynomial) - 1)
    while len(data_bits) >= len(polynomial):
        data_bits = xor(data_bits[:len(polynomial)], polynomial) + data_bits[len(polynomial):]
        data_bits = data_bits.lstrip("0")
    return data_bits.zfill(len(polynomial) - 1)


def crc_check(data_bits, polynomial):
    while len(data_bits) >= len(polynomial):
        data_bits = xor(data_bits[:len(polynomial)], polynomial) + data_bits[len(polynomial):]
        data_bits = data_bits.lstrip("0")
    return 0 if data_bits == "" else 1


def recv_part():
    global msg_list
    while True:
        data, addr = sock.recvfrom(BUF_SIZE)
        data = data.decode("utf-8", errors="ignore").rstrip("\n")

        if data.startswith("SEND-OK") or data.startswith("SET-OK"):
            continue

        if data.startswith("VALUE"):
            print(f"The value of {data.split()[1]} is {' '.join(data.split()[2:])}")
            continue

        if data.startswith("DELIVERY"):
            parts = data.split(" ", 2)
            if len(parts) < 3:
                continue
            sender, msg = parts[1], parts[2]
            data_bits = ''.join(format(ord(c), '08b') for c in msg)

            if sender not in users:
                users.append(sender)
                msg_count.append(0)
                ack_count.append(0)
                completed_ack.append(0)
                msg_list.append([])

            if crc_check(data_bits, polynomial) == 0:
                message = ''.join(chr(int(data_bits[i:i+8], 2)) for i in range(0, len(data_bits)-16, 8))
                msg_num, message = map(str, message.split("!", 1))
                index = users.index(sender)
                msg_num = int(msg_num)

                if message.startswith("ACK") and msg_num == completed_ack[index]:
                    completed_ack[index] += 1
                elif message.startswith("NACK"):
                    for i in range(msg_num, msg_count[index] + 1):
                        send_msg(msg_list[index][i], True, sender)
                elif msg_num != ack_count[index]:
                    send_msg(f"{ack_count[index]}!NACK", True, sender)
                else:
                    ack_count[index] += 1
                    send_msg(f"{msg_num}!ACK", True, sender)
                    print(f"From {sender}: {message}")
            continue

        if data.startswith("LIST-OK"):
            users_online = data.split(" ")[1:]
            print(f"There are {len(users_online)} online: {' '.join(users_online)}")

        elif data.startswith("BAD-DEST-USER"):
            print("The destination user does not exist")


def send_msg(message, to_client=False, receiver=""):
    if to_client:
        message = ''.join(format(ord(c), '08b') for c in message) + crc_add(message, polynomial)
        message = ''.join(chr(int(message[i:i+8], 2)) for i in range(0, len(message), 8))
        message = f"SEND {receiver} {message}\n"
    sock.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))


def timer():
    while True:
        time.sleep(1)
        for i, user in enumerate(users):
            if completed_ack[i] <= msg_count[i]:
                for msg in msg_list[i]:
                    send_msg(msg, True, user)


print('Welcome to Chat Client. Enter your login:')
while True:
    username = input()
    if username == "!quit":
        exit_flag = True
        sock.close()
        break
    if any(c in "!@#$%^&* " for c in username):
        print(f"Invalid username: {username}")
        continue
    send_msg(f"HELLO-FROM {username}\n", False)
    response, _ = sock.recvfrom(BUF_SIZE)
    response = response.decode()

    if response == "BUSY\n":
        print("Server full. Try again later.")
        break
    if response == "IN-USE\n":
        print(f"Username {username} is already taken.")
    elif response == f"HELLO {username}\n":
        print(f"Logged in as {username}")
        break

t = threading.Thread(target=recv_part, daemon=True)
t.start()
while not exit_flag:
    user_input = input(">>> ")
    if user_input == "!quit":
        exit_flag = True
        sock.close()
        break
    elif user_input == "!who":
        send_msg("LIST\n", False)
    elif user_input.startswith("!set"):
        send_msg(f"SET {user_input[5:]}\n", False)
    elif user_input.startswith("!get"):
        send_msg(f"GET {user_input[5:]}\n", False)
    elif user_input.startswith("@"):  
        parts = user_input.split(" ", 1)
        if len(parts) == 2:
            name, msg = parts[0][1:], parts[1]
            if name not in users:
                users.append(name)
                msg_count.append(0)
                ack_count.append(0)
                completed_ack.append(0)
                msg_list.append([])
            msg_id = msg_count[users.index(name)]
            formatted_msg = f"{msg_id}!{msg}"
            msg_list[users.index(name)].append(formatted_msg)
            send_msg(formatted_msg, True, name)
    else:
        print("Invalid input.")