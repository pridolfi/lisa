#!/usr/bin/env python
'''
LISA node configuration generator.
'''

from getpass import getpass

from Crypto.PublicKey import RSA
import sys
import os

from lisa.node import Node

class NodeConfigGenerator(Node):

    def __init__(self):
        super().__init__()


    def register_node(self):
        data_to_send = b'register:' + self.node_id.encode() + b':' + self.node_private_key.publickey().export_key()
        self.lisa_send(data_to_send)
        response = self.lisa_recv()
        if response != b'registered OK':
            self.logger.error('Error registering node to dispatcher.')
        else:
            self.logger.info(f'{self.node_id} registered successfully.')


    def get_user_input(self):
        self.node_private_key = RSA.generate(2048)
        self.node_id = input('Node ID: ')
        self.wifi_ssid = input('Wi-Fi SSID: ')
        self.wifi_passwd = getpass('Wi-Fi password: ')
        passwd2 = getpass('Wi-Fi password again: ')
        if self.wifi_passwd != passwd2:
            self.lisa_close()
            raise ValueError('Passwords do not match!')


    def lisa_conf(self):
        node_private_key = self.node_private_key.export_key()
        node_private_key = node_private_key.replace(b'\n', b'\\n\\\n').decode()
        dispatcher_key = self.get_peer_key(self.settings.get('dispatcher_name')).export_key()
        dispatcher_key = dispatcher_key.replace(b'\n', b'\\n\\\n').decode()
        owner_key = self.public_key.export_key().replace(b'\n', b'\\n\\\n').decode()
        return f'''/* AUTOMATICALLY GENERATED FILE - DO NOT EDIT */
const char node_id[] = "{self.node_id}";
const char dispatcher_ip[] = "{self.dispatcher_addr[0]}";
const short dispatcher_port = {self.dispatcher_addr[1]};
const unsigned char dispatcher_public_key[] = "{dispatcher_key}";
const unsigned char owner_public_key[] = "{owner_key}";
const unsigned char node_private_key[] = "{node_private_key}";
const char wifi_ssid[] = "{self.wifi_ssid}";
const char wifi_passwd[] = "{self.wifi_passwd}";
'''


    def generate(self, out_path):
        self.get_user_input()
        with open(out_path, 'w') as fd:
            self.logger.info('Writing configuration to %s', out_path)
            fd.write(self.lisa_conf())
        self.logger.info('Registering %s to %s...', self.node_id, self.settings.get('dispatcher_name'))
        self.register_node()
        self.lisa_close()
        self.logger.info('Configuration written to %s', os.path.abspath(out_path))


if __name__ == "__main__":
    conf = NodeConfigGenerator()
    if len(sys.argv) > 1:
        path = os.path.join(sys.argv[1], 'lisa_conf.c')
    else:
        path = './lisa_conf.c'
    conf.generate(path)
