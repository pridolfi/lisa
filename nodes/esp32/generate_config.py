#!/usr/bin/env python3

import socket

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA

from core import Core

h = input('hostname: ')

private_key = RSA.generate(2048)
public_key = private_key.publickey()
open(f'{h}.pub', 'wb').write(public_key.export_key())

