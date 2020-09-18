# LISA :dog:

Light Implementation of Secure Automation

## TL;DR

LISA is a secure P2P data exchange library written in Python and C (for its ESP32 port). It allows two or more peers (`nodes`) to exchange information using a third peer as a `dispatcher`. Each `node` can act also as a `dispatcher` to prevent centralization of messages. It uses RSA and AES encryption standards to verify identity and encrypt exchanged data.

## Functional description

The communication beteween each `node` and a `dispatcher` is established following these steps:

1. `node1` establishes a secure session with `dispatcher1.example.org`:
    1. `node1` encrypts its `node_id` with the public RSA key of the `dispatcher` and sends the information using a standard UDP connection.
    2. The `dispatcher` decrypts the message with its private RSA key and identifies an incoming connection request from `node1`.
    3. The `dispatcher` generates a random AES key and encrypts it with the RSA public key of `node1` and replies using the same UDP connection.
    4. `node1` receives and decrypts the AES key. Until the session ends, this random key and the AES scheme will be used for encryption and decryption of data between the `node` and the `dispatcher`.

2. The `node` sends periodic `uptime` messages to keep the connection alive.

## Installation

```bash
git clone git@github.com:pridolfi/lisa.git
cd lisa
python3.7 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
pip install .
```
```bash
# dispatcher example
lisa_run.py dispatcher
```

## Supported platforms

- [ESP32](./nodes/esp32)
- [Linux](./nodes/linux)

## TODOs

See [issues](https://github.com/pridolfi/lisa/issues).
