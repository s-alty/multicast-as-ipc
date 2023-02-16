import argparse
import datetime
import pickle
import socket

from util import LOOPBACK_DEVICE, get_ipmreqn
import messages

MESSAGE_WAIT_TIME = datetime.timedelta(milliseconds=500)


class GameClient:
    transaction_id = 0
    game_state = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, addr):
        self.move_servers = addr
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        ip, _ = addr
        if is_multicast(ip):
            # don't send multicast packets outside of local network
            self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 1)
            # make sure the multicast packets are sent over the loopback device
            ipmreqn = get_ipmreqn(ip, '127.0.0.1', LOOPBACK_DEVICE)
            self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, ipmreqn)


    def get_moves(self):
        move_request = messages.MoveRequest(
            self.transaction_id,
            self.game_state
        )
        self.sock.sendto(pickle.dumps(move_request), self.move_servers)

        # wait a fixed amount of time for any replies
        moves = []
        deadline = datetime.datetime.utcnow() + MESSAGE_WAIT_TIME
        while True:
            now = datetime.datetime.utcnow()
            if now > deadline:
                break

            timeout = (deadline - now).total_seconds()
            self.sock.settimeout(timeout)
            try:
                resp_data, _ = self.sock.recvfrom(65565)
            except TimeoutError:
                break

            resp = pickle.loads(resp_data)
            if resp.transaction_id == self.transaction_id:
                moves.append(resp.move)
            # todo: else?? we got an old move so we should just discard it but maybe log
        return moves


def is_multicast(ip):
    parts = [int(b) for b in ip.split('.')]
    return 224 <= parts[0] <= 239


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a game state to one or more engines and return the list of proposed moves')
    parser.add_argument('server_addr')
    args = parser.parse_args()


    addr, port = args.server_addr.split(':')

    client = GameClient((addr, int(port)))
    moves = client.get_moves()
    print("got back: {}".format(moves))
