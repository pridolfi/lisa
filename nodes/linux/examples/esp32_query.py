#!/usr/bin/env python3

import time
from datetime import datetime
from lisa.node import Node

n = Node()

while True:
    try:
        print('connecting...')
        n.start(wait_for_connection=True)        
        print('OK')
        while True:
            devices = n.list_devices()
            devices = [dev for dev in devices if 'esp32' in dev]       
            for device in devices:
                print(f'querying {device}...')
                n.send_message(device, 'hello')
                sender, message = n.recv_message(timeout_s=5)
                if sender:
                    print(f'message from {sender}: {message}')
                else:
                    print(f'timeout.')
            print('checking for other messages:')
            sender, message = n.recv_message(timeout_s=5)
            while sender:
                print(f'message from {sender}: {message}')
                sender, message = n.recv_message(timeout_s=1)

    except Exception as ex:
        print(f'exception {str(ex)}')
    except KeyboardInterrupt:
        break
    n.close()
