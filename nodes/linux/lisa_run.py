#!/usr/bin/env python
'''
LISA command line interface
'''

import sys
import yaml
from argparse import ArgumentParser

def run_dispatcher():
    from lisa.dispatcher import Dispatcher
    d = Dispatcher()
    d.run_dispatcher()

def get_info():
    from lisa.node import Node
    node = Node()
    print(node.NODE_ID)
    print(node.public_key.export_key().decode())
    print(yaml.dump(node.settings, indent=4, sort_keys=True))

ACTIONS = {
    'dispatcher': run_dispatcher,
    'info': get_info
}

def parse_arguments():
    parser = ArgumentParser(description='LISA command line interface')
    parser.add_argument('action', nargs='?', help='Action to perform.', choices=ACTIONS.keys(), default='node')
    return parser.parse_args(sys.argv[1:])

def main():
    options = parse_arguments()
    ACTIONS[options.action]()

if __name__ == "__main__":
    main()
