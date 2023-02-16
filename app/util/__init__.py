import socket

LOOPBACK_DEVICE = 'lo'

def get_ipmreqn(multicast_ip, interface_ip, interface_name):
           # struct ip_mreqn {
           #     struct in_addr imr_multiaddr; /* IP multicast group
           #                                      address */
           #     struct in_addr imr_address;   /* IP address of local
           #                                      interface */
           #     int            imr_ifindex;   /* interface index */
           # };

    multicast_ip_bytes = socket.inet_aton(multicast_ip)
    interface_ip_bytes = socket.inet_aton(interface_ip)

    ifindex = socket.if_nametoindex(interface_name)
    ifindex_bytes = ifindex.to_bytes(length=4, byteorder='little', signed=True)
    return multicast_ip_bytes + interface_ip_bytes + ifindex_bytes
