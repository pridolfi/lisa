#!/usr/bin/env python
'''
LISA node configuration generator.
'''
import sys
import os

from argparse import ArgumentParser
from getpass import getpass

from Crypto.PublicKey import RSA

from lisa.node import Node

class NodeConfigGenerator(Node):

    def __init__(self):
        super().__init__()
        self.start()


    def register_node(self):
        data_to_send = b'register:' + self.node_id.encode() + b':' + self.node_public_key.export_key()
        self.lisa_send(data_to_send)
        response = self.lisa_recv()
        if response != b'registered OK':
            self.logger.error('Error registering node to dispatcher.')
        else:
            self.logger.info(f'{self.node_id} registered successfully.')


    def get_user_input(self):
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


    def generate(self, node_id, ssid, out_path):
        self.node_id = node_id
        self.wifi_ssid = ssid
        self.node_private_key = RSA.generate(2048)
        self.node_public_key = self.node_private_key.publickey()
        self.get_user_input()
        with open(out_path, 'w') as fd:
            self.logger.info('Writing configuration to %s', out_path)
            fd.write(self.lisa_conf())
        with open(os.path.join(self.PEERS_FOLDER, f'{node_id}.pub'), 'wb') as fd:
            self.logger.info('Writing public key to %s', os.path.join(self.PEERS_FOLDER, f'{node_id}.pub'))
            fd.write(self.node_public_key.export_key())
        self.logger.info('Registering %s to %s...', self.node_id, self.settings.get('dispatcher_name'))
        self.register_node()
        self.lisa_close()
        self.logger.info('Configuration written to %s', os.path.abspath(out_path))


def parse_arguments():
    parser = ArgumentParser(description='LISA configuration generator for ESP32 nodes.')
    parser.add_argument('node_id', help='Node ID for ESP32 node.')
    parser.add_argument('ssid', help='Wi-Fi SSID for ESP32 to connect.')
    parser.add_argument('output_dir', help='Output folder for file lisa_conf.c.')
    return parser.parse_args(sys.argv[1:])

if __name__ == "__main__":
    opts = parse_arguments()
    conf = NodeConfigGenerator()
    conf.generate(opts.node_id, opts.ssid, os.path.join(opts.output_dir, 'lisa_conf.c'))
