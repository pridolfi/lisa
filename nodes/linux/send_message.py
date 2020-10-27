#!/usr/bin/env python3

import time

from lisa.node import Node

n = Node()

n.start(wait_for_connection=True)

print('list devices:')
print(n.list_devices())

n.send_message('esp32-01', 'Hello, ESP!')
print('message sent, waiting for response ...')

rcv = n.recv_message()
print(f'message received from {rcv[0].decode()}: {rcv[1].decode()}')

n.close()
