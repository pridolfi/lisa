#!/usr/bin/env python3

import time
from lisa.node import Node

destination = 'Inspiron15'

n = Node()

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
