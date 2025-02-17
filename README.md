# UDP-Based Reliable Chat Client  
A lightweight, **multi-user chat system** built on **UDP**, featuring **reliable message delivery** using **ACK/NACK confirmation** and **CRC error detection**. This project aims to enhance UDP communication by adding a reliability layer that mitigates packet loss and corruption.

##  Features  
**Multi-user chat over UDP**  
**Automatic message retransmission with ACK/NACK**  
**Error detection using 16-bit CRC (Cyclic Redundancy Check)**  
**Real-time messaging with simple commands**  
**Multithreading for concurrent message handling**  

## Technologies Used  
- **Python**  
- **Socket Programming (UDP)**  
- **Multithreading**  
- **CRC (Error Detection & Correction)**  

## Installation & Setup  
### 1️. Clone the Repository  
```bash
git clone https://github.com/ZoExOr/UDP-Reliable-Chat.git
cd UDP-Reliable-Chat
```

### 2️. Run the Server  
```bash
python udp_server.py
```
The server will start listening for incoming connections.

### 3️. Run the Client  
```bash
python udp_chat.py
```
Log in with a username and start chatting with other users.

---

##  How It Works  
🔹 **Message Transmission:** Messages are sent over **UDP**, converted to **binary**, and a **CRC checksum** is appended for error detection.  
🔹 **Error Handling:** The receiver verifies the checksum, sending **ACK** for valid messages or **NACK** for corrupted ones.  
🔹 **Reliable Delivery:** If no ACK is received, the message will be **retransmitted automatically**.  

---

##  Commands  
| Command | Description |
|---------|------------|
| `!who` | List online users |
| `@user [message]` | Send a private message |
| `!quit` | Exit the chat |
| `!set [setting] [value]` | Configure client settings |
| `!get [setting]` | Retrieve current settings |

