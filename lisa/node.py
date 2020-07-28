'''
LISA Node (client) class.
'''

import socket

from queue import Queue
from Crypto.Cipher import AES, PKCS1_v1_5

from core import Core

class Node(Core):

    def __init__(self):
        super().__init__()
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.aes_session_key = None


    def set_dispatcher(self, peername, port=None):
        ''' Set dispatcher to communicate with. '''
        p = self.LISA_PORT if port is None else port
        self.dispatcher_addr = (self.resolve(peername), p)
        self.dispatcher_name = peername
        self.dispatcher_pubkey = self.get_peer_key(self.dispatcher_name)

    def lisa_connect(self):
        sentinel = None
        cipher_rsa = PKCS1_v1_5.new(self.dispatcher_pubkey)
        decipher_rsa = PKCS1_v1_5.new(self.private_key)
        self.s.settimeout(self.TIMEOUT_S)
        rsa_payload = cipher_rsa.encrypt(self.NODE_ID.encode())
        self.s.sendto(rsa_payload, self.dispatcher_addr)
        recv_data, remote_addr = self.s.recvfrom(self.PACKET_SIZE_B)
        if remote_addr != self.dispatcher_addr:
            self.logger.warning("%s != %s", remote_addr, self.dispatcher_addr)
        session_data = decipher_rsa.decrypt(recv_data, sentinel)
        if len(session_data) != 32:
            raise ConnectionError("error receiving session key")
        self.aes_session_key = session_data[0:16]
        self.aes_session_iv = session_data[16:32]


    def lisa_close(self):
        self.lisa_send('close')
        recv_data = self.session_recv()
        if recv_data != 'close':
            self.logger.warning('received %s', recv_data)
        self.aes_session_key = None
        self.aes_session_iv = None


    def lisa_send(self, data_to_send):
        cipher_aes = AES.new(self.aes_session_key, AES.MODE_CBC, self.aes_session_iv)
        aes_payload = cipher_aes.encrypt(data_to_send)
        self.s.sendto(aes_payload, self.dispatcher_addr)


    def lisa_recv(self):
        recv_data, remote_addr = self.s.recvfrom(self.DEFAULT_PACKET_SIZE_B)
        if remote_addr != self.dispatcher_addr:
            self.logger.exception("%s != %s", remote_addr, self.dispatcher_addr)
        decipher_aes = AES.new(self.aes_session_key, AES.MODE_CBC, self.aes_session_iv)
        recv_data = decipher_aes.decrypt(recv_data)
        return recv_data
