'''
LISA command line interface
'''

import sys

from dispatcher import Dispatcher

def main():
    if 'dispatcher' == sys.argv[1]:
        d = Dispatcher()
        d.run_dispatcher()
    # todo client
    # todo register node (generate lisa_conf.c)

if __name__ == "__main__":
    main()
