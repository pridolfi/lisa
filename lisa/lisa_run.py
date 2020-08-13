#!/usr/bin/env python
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
        node = Node()
        time.sleep(10)
        node.lisa_close()


if __name__ == "__main__":
    main()
