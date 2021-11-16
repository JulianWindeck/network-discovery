import sys
import time
import socket


UDP_PORT = 4242
IP_BROADCAST = "255.255.255.255"

REQ_TO_CONNECT = "request to connect"
CONNECTION_DETAILS = "master reply"
END = "end"

#IP addresses of clients that want to become a slave
#but that do not know the master's IP address yet
clients_waiting = []

#IP adresses of all fully connected clients
clients_established = []

def main():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", UDP_PORT))

        #receive messages till user disables network discovery
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode("utf-8")
            ip_client = addr[0]

            #client wants to connect - but does not know the IP address of the master
            if msg == REQ_TO_CONNECT:
                #new client
                if ip_client not in clients_waiting:
                    clients_waiting.append(ip_client)
                    print(f"[*] {ip_client} requested to become a slave.")

                #client already made request, but CONNECTION DETAIL reply packet got lost (so he asked again)
                else:
                    #just resend connection details reply packet
                    pass

                #send connection detials reply to connect with IP of master
                sock.sendto(str.encode(CONNECTION_DETAILS), (ip_client, UDP_PORT))


            #ACK that client received connection details packet (including IP address of server)
            #this means both participants can now communicate directly with each other
            elif msg == END:
                #first time we receive this from the client - we have his information
                #and now we know he also has our information
                if ip_client in clients_waiting:
                    #move client to list of slaves (with which a conenction has been established)
                    clients_waiting.remove(ip_client)

                    #this should normally be the case
                    if ip_client not in clients_established:
                        clients_established.append(ip_client)
                    #the only exception would be a client that executes a network discovery a second time
                    #meaning he is already in the list of slaves - then prevent duplicates
                    else:
                        pass
                    print(f"[+] Connection established with [{ip_client}]")
                    for client in clients_established:
                        print(client)

                #this means we already received one of his END packets in the past
                #so our END (the ACK of his END packet) got lost
                #that means we just need to resend it to tell him we got it
                else:
                    pass

                sock.sendto(str.encode(END, "utf-8"), (ip_client, UDP_PORT))

            #other msg - should not occur
            else:
                print(f"[!] Received message from [{ip_client}]: {msg}")


        sock.close()
        print("[*] Server ended network discovery")


if __name__ == "__main__":
    main()
