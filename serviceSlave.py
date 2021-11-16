import sys
import time
import socket
from enum import Enum

UDP_PORT = 4242
IP_BROADCAST = "255.255.255.255"

REQ_TO_CONNECT = "request to connect"
CONNECTION_DETAILS = "master reply"
END = "end"

class State(Enum):
    INIT = 1
    MASTER_KNOWN = 2
    CONNECTION_ESTABLISHED = 3

ip_master = None
state = State.INIT

def main():
    global ip_master, state

    while state != State.CONNECTION_ESTABLISHED:
        try:
            #here we cannot be sure the master knows us
            #so ensure that
            if state == State.INIT:
                #try to find master node
                #create a UDP socket
                broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #make sure this is sent as a broadcast
                broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                broadcast_sock.sendto(str.encode(REQ_TO_CONNECT, "utf-8"), (IP_BROADCAST, UDP_PORT))
                broadcast_sock.close()

                #if you try to use broadcast_sock for receiving that won't work because using SO_BROADCAST=1
                #to send - so just use a new socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(2)
                sock.bind(("0.0.0.0", UDP_PORT))

                data, addr = sock.recvfrom(1024)
                msg = data.decode("utf-8")
                ip_master = addr[0]
                if msg == CONNECTION_DETAILS:
                    print(f"[+] Found master: [{ip_master}].")
                else:
                    print(f"[!] Got some unintended message: {msg}")
                sock.close()
                state = State.MASTER_KNOWN

            #in this state it is sure the master knows us - and we know the master
            #but we cannot be sure the master knows that we know him
            #so both client and server have to send and receive an END packet
            if state == State.MASTER_KNOWN:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(2)
                sock.bind(("0.0.0.0", UDP_PORT))

                sock.sendto(str.encode(END), (ip_master, UDP_PORT))

                #now make sure the server received that by waiting for an ACK
                data, addr = sock.recvfrom(1024)
                msg = data.decode("utf-8")

                #this means the server has received our END packet and therefore
                #knows that we are ready
                if msg == END:
                    state = State.CONNECTION_ESTABLISHED
                    print(f"[+] Connection established.")
                    #we could also do a break directly here but I think it is a cleaner implementation of the state machine
                #should not occur
                else:
                    print(f"[!] Got some unintended message: {msg}")
                sock.close()

            #network discovery is over - both master and slave have the information they need for communication
            #AND they also know that their counterpart also does
            if state == State.CONNECTION_ESTABLISHED:
                break

        #in case UDP packet (either one of ours or the server) was lost:
        #we have to repeat this step of the network discovery
        except socket.timeout as e:
            #if broadcast connection request or connection details reply packet are lost, you have to repeat the request
            print("[*] Trying again ...")
            continue


if __name__ == "__main__":
    main()
