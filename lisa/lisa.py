'''
LISA command line interface
'''

import sys

def main():
    if 'dispatcher' == sys.argv[1]:
        from lisa.dispatcher import Dispatcher
        d = Dispatcher()
        d.run_dispatcher()
    # todo client
    # todo register node (generate lisa_conf.c)
    elif 'node' == sys.argv[1]:
        import time
        from lisa.node import Node
        Node()
        time.sleep(10)

if __name__ == "__main__":
    main()
