#!/usr/bin/env python3

import time
import sys
from lisa.node import Node

n = Node()

# if no peername is in argv, send a message to myself :'(
destination = n.NODE_ID if len(sys.argv) < 2 else sys.argv[1]

print('connecting...')
n.start(wait_for_connection=True)
print('OK')

n.send_message(destination, f'Hello, {destination}!')
print('message sent, waiting for response...')

try:
    rcv = n.recv_message(timeout_s=30)
    print(f'message received from {rcv[0].decode()}: {rcv[1].decode()}')
except Exception as ex:
    print(f'Exception: {ex}')

n.close()
