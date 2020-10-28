#!/usr/bin/env python3

import time
from datetime import datetime
from lisa.node import Node

n = Node()

print('connecting...')
n.start(wait_for_connection=True)
print('OK')

devices = n.list_devices()

print('Devices in dispatcher {}:'.format(n.settings['dispatcher_name']))
for device in devices:
    print(f'Name: {device}')
    print('* uptime:    {}'.format(devices[device]['uptime']))
    last_seen = datetime.fromtimestamp(devices[device]['last_seen'])
    print('* last seen: {}'.format(last_seen.strftime('%Y-%m-%d %H:%M:%S')))

n.close()
