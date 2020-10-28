#!/usr/bin/env python3

import time
from lisa.node import Node

n = Node()

print('connecting...')
n.start(wait_for_connection=True)
print('OK')

sender, message = n.recv_message()
sender = sender.decode()
message = message.decode()
print(f'message received from {sender}: {message}')

n.send_message(sender, f'Hi, {sender}, how are you?')

n.close()
