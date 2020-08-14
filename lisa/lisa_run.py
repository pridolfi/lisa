#!/usr/bin/env python
'''
LISA command line interface
'''

import sys
from argparse import ArgumentParser

def parse_arguments():
    parser = ArgumentParser(description='LISA command line interface')
    parser.add_argument('action', nargs='?', help='Action to perform.', choices=['node', 'dispatcher'], default='node')
    return parser.parse_args(sys.argv[1:])


def main():
    options = parse_arguments()
    if 'dispatcher' == options.action:
        from lisa.dispatcher import Dispatcher
        d = Dispatcher()
        d.run_dispatcher()
    elif 'node' == options.action:
        import time
        from lisa.node import Node
        node = Node()
        time.sleep(10)
        node.lisa_close()


if __name__ == "__main__":
    main()
