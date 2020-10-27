'''
LISA Dispatcher (server) class.
'''

import socket
import threading
import os

from queue import Queue, Empty
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Random import get_random_bytes

from lisa.core import Core


class Dispatcher(Core):

    def __init__(self):
        super().__init__()
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.active_clients = {}
        self.messages = {}
        self.decipher_rsa = PKCS1_v1_5.new(self.private_key)


    def put_message(self, sender, receiver, message):
        if receiver not in self.messages:
            self.messages[receiver] = Queue()
        self.messages[receiver].put((sender, message))


    def get_message(self, receiver):
        self.logger.info(receiver)
        if receiver not in self.messages:
            return None
        try:
            sender, message = self.messages[receiver].get_nowait()
            self.logger.info('%s %s', sender, message)
            return b'msg:' + sender + b':' + message
        except Empty:
            return None


    def process_data(self, recv_data, peername):
        self.logger.debug('%s: %s', peername, recv_data)
        if recv_data.startswith(b'register:'):
            _, name, pubkey = recv_data.split(b':')
            name = name.decode()
            self.logger.info('registering %s', name)
            with open(os.path.join(self.PEERS_FOLDER, f'{name}.pub'), 'wb') as fd:
                fd.write(pubkey)
            return b'registered OK'

        if recv_data.startswith(b'msg:'):
            _, receiver, message = recv_data.split(b':')
            receiver = receiver.decode('utf-8')
            self.put_message(peername, receiver, message)
            return b'message queued'

        response = self.get_message(peername)

        if response == None:
            return recv_data
        else:
            return response


    def session_thread(self, address):
        sentinel = None
        peername = None
        queue = self.active_clients[address]['squeue']
        try:
            recv_data = queue.get(timeout=self.TIMEOUT_S)
            peername = self.decipher_rsa.decrypt(recv_data, sentinel).decode('utf-8')
            self.active_clients[address]['name'] = peername
            cipher_rsa = PKCS1_v1_5.new(self.get_peer_key(peername))
            aes_session_key = get_random_bytes(16)
            iv = get_random_bytes(16)
            self.s.sendto(cipher_rsa.encrypt(aes_session_key+iv), address)
            self.logger.info('new session: %s %s', peername, address)
            while True:
                recv_data = queue.get(timeout=self.TIMEOUT_S)
                decipher_aes = AES.new(aes_session_key, AES.MODE_CBC, iv)
                recv_data = decipher_aes.decrypt(recv_data)
                recv_data = recv_data[:-recv_data[-1]]
                response = self.process_data(recv_data, peername)
                padding_len = 16 - (len(response) % 16)
                response += bytes([padding_len])*padding_len
                cipher_aes = AES.new(aes_session_key, AES.MODE_CBC, iv)
                self.s.sendto(cipher_aes.encrypt(response), address)
                if recv_data == b'close':
                    break
        except ValueError as ex:
            self.logger.exception(str(ex))
            self.logger.warning('received data: %s', recv_data)
        except Empty as ex:
            self.logger.info('receive queue empty')
        except Exception as ex:
            self.logger.exception(str(ex))
        self.logger.info('end session: %s %s', peername, address)
        del self.active_clients[address]


    def run_dispatcher(self):
        self.s.bind(('', self.LISA_PORT))
        self.logger.info("Dispatcher up and listening on port %s", self.LISA_PORT)
        while True:
            recv_data, address = self.s.recvfrom(self.PACKET_SIZE_B)
            if address not in self.active_clients:
                t = threading.Thread(target=self.session_thread,
                                     args=[address])
                t.daemon = True
                self.active_clients[address] = dict(thread=t, squeue=Queue(), name='')
                t.start()
            self.active_clients[address]['squeue'].put(recv_data)
