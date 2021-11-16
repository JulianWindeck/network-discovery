# network-discovery
A simple foundation for the network discovery of devices running your distributed application.

## Example
You want that your application directly recognizes a device (running a client version of the application) as soon as the device joins the network (e.g. is connected via Wi-Fi).

This way, you don't have to manually configure IP addresses within your application. 
Devices running your application can be dynamically added by simply being part of the same network.

This works by sending a UDP broadcast datagram as soon as a new device is connected.
Then, there will be a reliable exchange of IP addresses for further communication.

After that, you can use the IP addresses on both ends for further communication (via TCP sockets/REST/...)
