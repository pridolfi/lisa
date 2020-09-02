#!/usr/bin/env python
'''
LISA command line interface
'''

import os
import sys
import yaml
from argparse import ArgumentParser

def run_dispatcher(options):
    from lisa.dispatcher import Dispatcher
    d = Dispatcher()
    d.run_dispatcher()

def get_info(options):
    from lisa.node import Node
    node = Node()
    print(f'Node ID: {node.NODE_ID}')
    print(node.public_key.export_key().decode())
    print(f'Node settings:')
    print(yaml.dump(node.settings, indent=4, sort_keys=True))

def register_to_remote(options):
    from lisa.node import Node
    node = Node()
    node.scp_exchange_pubkeys(options.uri)

ACTIONS = {
    'dispatcher': run_dispatcher,
    'info': get_info,
    'register': register_to_remote
}

def parse_arguments():
    parser = ArgumentParser(description='LISA command line interface')
    parser.add_argument('action', nargs='?', help='Action to perform.', choices=ACTIONS.keys(), default='info')
    parser.add_argument('--uri', '-u', help='Remote URI.', default=None)
    return parser.parse_args(sys.argv[1:])

def main():
    options = parse_arguments()
    ACTIONS[options.action](options)

if __name__ == "__main__":
    main()
