'''
LISA node configuration generator.
'''

from getpass import getpass

from Crypto.PublicKey import RSA
import cbor

from node import Node

class NodeConfigGenerator(Node):

    def __init__(self):
        super().__init__()


    def register_node(self):
        data_to_send = b'register:' + self.node_id.encode() + b':' + self.node_private_key.publickey().export_key()
        print(data_to_send)
        self.lisa_send(data_to_send)
        response = self.lisa_recv()
        if response != b'registered OK':
            self.logger.error('Error registering node to dispatcher.')
        else:
            self.logger.info(f'{self.node_id} registered successfully.')


    def get_user_input(self):
        self.node_private_key = RSA.generate(2048)
        self.node_id = input('Node ID? ')
        self.wifi_ssid = input('WiFi SSID? ')
        self.wifi_passwd = getpass('WiFi password? ')


    def print_lisa_conf(self):
        node_private_key = self.node_private_key.export_key()
        node_private_key = node_private_key.replace(b'\n', b'\\n\\\n').decode()
        dispatcher_key = self.get_peer_key(self.settings.get('dispatcher_name')).export_key()
        dispatcher_key = dispatcher_key.replace(b'\n', b'\\n\\\n').decode()
        out = f'''/* AUTOMATICALLY GENERATED FILE - DO NOT EDIT */
const char node_id[] = "{self.node_id}";
const char dispatcher_ip[] = "{self.dispatcher_addr[0]}";
const short dispatcher_port = {self.dispatcher_addr[1]};
const unsigned char dispatcher_public_key[] = "{dispatcher_key}";
const unsigned char node_private_key[] = "{node_private_key}";
const char wifi_ssid[] = "{self.wifi_ssid}";
const char wifi_passwd[] = "{self.wifi_passwd}";
'''
        print(out)


if __name__ == "__main__":
    conf = NodeConfigGenerator()
    conf.get_user_input()
    conf.print_lisa_conf()
    conf.register_node()
    conf.lisa_close()
