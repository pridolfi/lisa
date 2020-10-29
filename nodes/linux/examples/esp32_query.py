#!/usr/bin/env python3

import time
from datetime import datetime
from lisa.node import Node

n = Node()

while True:
    try:
        n.start(wait_for_connection=True)        
        while True:
            devices = n.list_devices()
            devices = [dev for dev in devices if 'esp32' in dev]       
            for device in devices:
                print(f'querying {device}...')
                n.send_message(device, 'hello')
                sender, message = n.recv_message(timeout_s=10)
                if sender:
                    print(f'message from {sender}: {message}')
                else:
                    print(f'timeout.')
    except Exception as ex:
        print(f'exception {str(ex)}')
    except KeyboardInterrupt:
        break
    n.close()
