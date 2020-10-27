#!/usr/bin/env python3

import time

from lisa.node import Node

n = Node()

n.start()

while not n.is_connected:
    print('waiting for connection...')
    time.sleep(1)

if n.send_message(n.NODE_ID, 'hola mundo!'):
    print('message sent')

rcv = n.recv_message()

print(rcv)

n.close()

