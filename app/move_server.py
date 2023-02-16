import argparse
import pickle
import socket

from engines import ENGINES
from util import LOOPBACK_DEVICE, get_ipmreqn

import messages


def serve(listen_addr, engine, multicast_ip=None):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # do we bind to the local interface + port
    # or to the multicast interface + port
    if multicast_ip:
        listen_ip, listen_port = listen_addr
        sock.bind((multicast_ip, listen_port))

        ipmreqn = get_ipmreqn(multicast_ip, listen_ip, LOOPBACK_DEVICE)
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, ipmreqn)
    else:
        sock.bind(listen_addr)

    while True:
        data, from_addr = sock.recvfrom(65565)
        message = pickle.loads(data)

        print('Got message: {}'.format(message))

        move = engine(message.fen)
        response = messages.MoveResponse(
            message.transaction_id,
            move
        )

        reply_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        reply_sock.sendto(pickle.dumps(response), from_addr)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a process that listens for move requests and responds based on the configured engine')
    parser.add_argument('listen_addr')
    parser.add_argument('--engine', default='random')
    parser.add_argument('--multicast_group_ip')
    args = parser.parse_args()

    try:
        engine = ENGINES[args.engine]
    except KeyError:
        parser.exit(status=1, message='Invalid engine: "{}"'.format(args.engine))

    addr, port = args.listen_addr.split(':')

    serve((addr,int(port)), engine, args.multicast_group_ip)
