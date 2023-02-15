import argparse
import pickle
import socket

from engines import ENGINES
import messages


def serve(listen_addr, engine):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
    args = parser.parse_args()

    try:
        engine = ENGINES[args.engine]
    except KeyError:
        parser.exit(status=1, message='Invalid engine: "{}"'.format(args.engine))

    addr, port = args.listen_addr.split(':')

    serve((addr,int(port)), engine)
