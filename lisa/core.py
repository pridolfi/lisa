'''
Light Implementation of Secure Automation protocol

Core class
'''

import os
import socket
import logging
import sys

from Crypto.PublicKey import RSA


class Core(object):

    def __init__(self):
        ''' Initialize class base members and load node keys. '''
        self.NODE_ID = os.getenv('LISA_NODE_ID', socket.gethostname())
        self.LISA_FOLDER = os.getenv('LISA_FOLDER', os.path.join(os.getenv('HOME'), '.lisa'))
        self.PEERS_FOLDER = os.path.join(self.LISA_FOLDER, 'peers')
        self.PRIVATE_KEY_FILE = os.path.join(self.LISA_FOLDER, self.NODE_ID)
        self.PUBLIC_KEY_FILE = os.path.join(self.LISA_FOLDER, f'{self.NODE_ID}.pub')
        self.LISA_PORT = os.getenv('LISA_PORT', 5432)
        self.TIMEOUT_S = 30
        self.PACKET_SIZE_B = 1024
        os.system('mkdir -p {}'.format(self.PEERS_FOLDER))
        self.logger = logging.getLogger('LISA')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s'))
        self.logger.addHandler(handler)
        self.load_keys()


    def load_keys(self):
        ''' Load RSA keys for this node. If they don't exist, create them. '''
        try:
            self.private_key = RSA.importKey(open(self.PRIVATE_KEY_FILE, 'rb').read())
            self.public_key = RSA.importKey(open(self.PUBLIC_KEY_FILE, 'rb').read())
        except FileNotFoundError:
            self.logger.info("Creating keys...")
            self.private_key = RSA.generate(2048)
            self.public_key = self.private_key.publickey()
            open(self.PRIVATE_KEY_FILE, 'wb').write(self.private_key.export_key())
            open(self.PUBLIC_KEY_FILE, 'wb').write(self.public_key.export_key())


    def parse_user_host_port(self, user_host_port):
        ''' Parse user@hostname:port string and return its components. '''
        remote = user_host_port.strip()
        if remote.find('@') != -1:
            user = remote.split('@')[0]
            host = remote.split('@')[1]
        else:
            user = None
            host = remote
        if host.find(':') != -1:
            port = int(host.split(':')[1])
            host = host.split(':')[0]
        else:
            port = None
        return host, port, user


    def resolve(self, hostname):
        ''' Try to obtain IP address for hostname. ''' 
        ip = None
        msg = ''
        for h in [hostname, hostname + '.local']:
            try:
                ip = socket.gethostbyname(h)
                break
            except Exception as e:
                msg += str(e)
        if ip == None:
            raise Exception('Could not resolve {}: {}'.format(hostname, msg))
        return ip


    def get_peer_key(self, peername):
        ''' Obtain peer public key to encrypt data. '''
        key = RSA.importKey(open(os.path.join(self.PEERS_FOLDER, '{}.pub'.format(peername)), 'rb').read())
        return key


    def scp_exchange_pubkeys(self, user_host_port):
        ''' register to peer in network: send my public key, receive its public key '''
        host, port, user = self.parse_user_host_port(user_host_port)
        port = 22 if port is None else port
        user = os.getenv('USER') if user is None else user
        ip = self.resolve(host)
        host = host.replace('.local', '')
        os.system(f'scp -P{port} {self.PUBLIC_KEY_FILE} {user}@{ip}:~/.lisa/peers/')
        os.system(f'scp -P{port} {user}@{ip}:~/.lisa/{host}.pub {self.PEERS_FOLDER}')

