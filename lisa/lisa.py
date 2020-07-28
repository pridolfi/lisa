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
        n.set_dispatcher('srv1.codenload.com')
        n.lisa_connect()
        i=0
        while True:
            n.lisa_send(str(i).encode())
            i+=1
            print(n.lisa_recv())

if __name__ == "__main__":
    main()
