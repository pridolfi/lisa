#!/usr/bin/env python3

import time
import logging
from datetime import datetime
from lisa.node import Node

n = Node()
#n.logger.setLevel(logging.DEBUG)

while True:
    try:
        i = 0
        n.start(wait_for_connection=True)        
        while True:
            devices = n.list_devices(timeout_s=5)
            devices = [dev for dev in devices if 'esp32' in dev]       
            for device in devices:
                message = f'message {i}'
                print(f'send "{message}" to {device}...')
                n.send_message(device, message, timeout_s=5)
            sender, message = n.recv_message(timeout_s=5)
            while sender:
                print(f'message from {sender}: {message}')
                sender, message = n.recv_message(timeout_s=5)
            i += 1
    except Exception as ex:
        print(f'exception {str(ex)}')
    except KeyboardInterrupt:
        break
    n.close()
