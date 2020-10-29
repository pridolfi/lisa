'''
LISA Node (client) class.
'''

import socket
import threading
import time
from queue import Queue
from ast import literal_eval

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
        self.is_connected = False
        self.UPTIME_BEACON_PERIOD_s = 1


    def __node_thread(self):
        self.logger.debug('starting node session')
        try:
            self.dispatcher_addr = (
                self.resolve(self.settings['dispatcher_name']),
                self.settings.get('dispatcher_port', self.LISA_PORT)
            )
            self.dispatcher_pubkey = self.get_peer_key(self.settings.get('dispatcher_name'))
        except Exception as ex:
            self.logger.warning('Error resolving dispatcher address, check your configuration! (%s)', str(ex))
            return
        self.running = True
        while self.running:
            try:
                self.__lisa_connect()
                start = time.monotonic()
                while self.running:
                    data_to_send = None
                    uptime_message = ''
                    if not self.send_queue.empty():
                        data_to_send = self.send_queue.get_nowait()
                    elif time.monotonic() >= (start + self.UPTIME_BEACON_PERIOD_s):
                        start = time.monotonic()
                        uptime_ms = int(start*1000)
                        uptime_message = f'uptime:{uptime_ms}'.encode()
                        data_to_send = uptime_message
                    if data_to_send:
                        self.__lisa_send(data_to_send)
                        response = self.__lisa_recv()
                        if response != uptime_message:
                            self.recv_queue.put(response)
                        else:
                            end = time.monotonic()
                            t = end - start
                            time.sleep(1-t if t < 1 else 1)
            except Exception as ex:
                self.logger.exception(str(ex))
                time.sleep(1)
        self.__lisa_close()
        self.logger.debug('ending node session')


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
        self.logger.debug('connected to %s:%s', self.settings.get('dispatcher_name'), self.dispatcher_addr[1])
        self.aes_session_key = session_data[0:16]
        self.aes_session_iv = session_data[16:32]
        self.is_connected = True


    def __lisa_close(self):
        self.__lisa_send(b'close')
        recv_data = self.__lisa_recv()
        if recv_data != b'close':
            self.logger.warning('received %s', recv_data)
        self.is_connected = False
        self.aes_session_key = None
        self.aes_session_iv = None
        self.running = False


    def __lisa_send(self, data_to_send):
        self.logger.debug('data_to_send: %s', data_to_send)
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
        self.logger.debug('recv_data: %s', recv_data)
        return recv_data


    def close(self):
        self.running = False
        self.thread.join()


    def start(self, wait_for_connection=False):
        self.thread = threading.Thread(target=self.__node_thread, daemon=True)
        self.thread.start()
        while wait_for_connection and not self.is_connected:
            self.logger.debug('waiting for connection...')
            time.sleep(1)


    def recv_message(self, timeout_s=None):
        if not self.is_connected:
            raise ConnectionError('Node is not connected!')
        response = self.recv_queue.get(timeout=timeout_s)
        header, sender, message = response.split(b':')
        if header != b'msg':
            raise ValueError(f'Bad response from dispatcher: {response}')
        return sender, message


    def send_message(self, receiver, message, timeout_s=None):
        if not self.is_connected:
            raise ConnectionError('Node is not connected!')
        data_to_send = b'msg:' + receiver.encode() + b':' + message.encode()
        self.send_queue.put(data_to_send)
        response = self.recv_queue.get(timeout=timeout_s)
        if response != b'message queued':
            raise ValueError(f'Bad response from dispatcher: {response}')


    def register_new_node(self, new_node_id, new_node_public_key, timeout_s=None):
        if not self.is_connected:
            raise ConnectionError('Node is not connected!')
        data_to_send = b'register:' + new_node_id.encode() + b':' + new_node_public_key.export_key()
        self.send_queue.put(data_to_send)
        response = self.recv_queue.get(timeout=timeout_s)
        if response != b'registered OK':
            raise ValueError(f'Bad response from dispatcher: {response}')
        else:
            self.logger.info(f'{new_node_id} registered successfully.')


    def set_dispatcher(self, uri):
        host, port, _ = self.parse_user_host_port(uri)
        self.settings['dispatcher_name'] = host
        if port:
            self.settings['dispatcher_port'] = port
        elif 'dispatcher_port' in self.settings:
            del self.settings['dispatcher_port']
        self.save_settings()


    def list_devices(self, timeout_s=None):
        if not self.is_connected:
            raise ConnectionError('Node is not connected!')
        self.send_queue.put(b'list_devices')
        response = self.recv_queue.get(timeout=timeout_s)
        response = response.decode()
        return literal_eval(response)
