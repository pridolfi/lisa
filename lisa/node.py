'''
LISA Node (client) class.
'''

import socket
import threading
import time
from queue import Queue

from Crypto.Cipher import AES, PKCS1_v1_5

from lisa.core import Core


class Node(Core):

    def __init__(self):
        super().__init__()
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.aes_session_key = None
        self.send_queue = Queue()
        self.recv_queue = Queue()
        self.running = False
        try:
            self.dispatcher_addr = (
                self.resolve(self.settings['dispatcher_name']),
                self.settings.get('dispatcher_port', self.LISA_PORT)
            )
            self.dispatcher_pubkey = self.get_peer_key(self.settings.get('dispatcher_name'))
        except Exception as ex:
            self.logger.exception('exception setting dispatcher access, check your configuration! (%s)', str(ex))
            return
        self.thread = threading.Thread(target=self.__node_thread)


    def __node_thread(self):
        self.logger.info('starting node session')
        self.running = True
        while self.running:
            try:
                self.__lisa_connect()
                while self.running:
                    if self.send_queue.empty():
                        uptime_ms = int(time.monotonic()*1000)
                        start = time.monotonic()
                        self.__lisa_send(f'uptime:{uptime_ms}'.encode())
                        uptime_response = self.__lisa_recv()
                        self.logger.debug(f'uptime response: {uptime_response}')
                        end = time.monotonic()
                        t = end - start
                        time.sleep(1-t if t < 1 else 1)
                    else:
                        data_to_send = self.send_queue.get()
                        self.__lisa_send(data_to_send)
                        self.recv_queue.put(self.__lisa_recv())
            except Exception as ex:
                self.logger.exception(str(ex))
                time.sleep(1)
        self.__lisa_close()
        self.logger.info('ending node thread')


    def __lisa_connect(self):
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
        self.logger.info('connected to %s:%s', self.settings.get('dispatcher_name'), self.dispatcher_addr[1])
        self.aes_session_key = session_data[0:16]
        self.aes_session_iv = session_data[16:32]


    def __lisa_close(self):
        self.__lisa_send(b'close')
        recv_data = self.__lisa_recv()
        if recv_data != b'close':
            self.logger.warning('received %s', recv_data)
        self.aes_session_key = None
        self.aes_session_iv = None
        self.running = False


    def __lisa_send(self, data_to_send):
        cipher_aes = AES.new(self.aes_session_key, AES.MODE_CBC, self.aes_session_iv)
        length = 16 - (len(data_to_send) % 16)
        data_to_send += bytes([length])*length
        aes_payload = cipher_aes.encrypt(data_to_send)
        self.s.sendto(aes_payload, self.dispatcher_addr)


    def __lisa_recv(self):
        recv_data, remote_addr = self.s.recvfrom(self.PACKET_SIZE_B)
        if remote_addr != self.dispatcher_addr:
            self.logger.exception("%s != %s", remote_addr, self.dispatcher_addr)
        decipher_aes = AES.new(self.aes_session_key, AES.MODE_CBC, self.aes_session_iv)
        recv_data = decipher_aes.decrypt(recv_data)
        recv_data = recv_data[:-recv_data[-1]]
        return recv_data


    def __lisa_send(self, data_to_send):
        self.send_queue.put(data_to_send)
    

    def __lisa_recv(self, timeout_s=None):
        return self.recv_queue.get(timeout=timeout_s)


    def __lisa_close(self):
        self.running = False
        self.thread.join()


    def start(self):
        return self.thread.start()


    def register_command(self, command, handler):
        pass


    def send_command(self, command, handler):
        pass
