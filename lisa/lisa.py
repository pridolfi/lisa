'''
LISA command line interface
'''

import sys

def main():
    if 'dispatcher' == sys.argv[1]:
        from dispatcher import Dispatcher
        d = Dispatcher()
        d.run_dispatcher()
    # todo client
    # todo register node (generate lisa_conf.c)
    elif 'node' == sys.argv[1]:
        import time
        from node import Node
        n = Node()
        n.start()
        while True:
            n.lisa_send(b'test')
            recv = n.lisa_recv()
            print(f'test recv: {recv}')
            time.sleep(10)

if __name__ == "__main__":
    main()
