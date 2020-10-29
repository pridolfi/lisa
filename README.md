# LISA :dog:

Light Implementation of Secure Automation

## TL;DR

LISA is a secure P2P data exchange library written in Python and C (for its ESP32 port). It allows two or more peers (`nodes`) to exchange messages using a third peer as a `dispatcher`. Each `node` can act also as a `dispatcher` to prevent centralization of messages. It uses RSA and AES encryption standards to verify identity and encrypt exchanged data.

## Functional description

The communication beteween each `node` and a `dispatcher` is established following these steps:

1. `node1` establishes a secure session with `dispatcher1.example.org`:
    1. `node1` encrypts its `node_id` with the public RSA key of the `dispatcher` and sends the information using a standard UDP connection.
    2. The `dispatcher` decrypts the message with its private RSA key and identifies an incoming connection request from `node1`.
    3. The `dispatcher` generates a random AES key and encrypts it with the RSA public key of `node1` and replies using the same UDP connection.
    4. `node1` receives and decrypts the AES key. Until the session ends, this random key and the AES scheme will be used for encryption and decryption of data between the `node` and the `dispatcher`.

2. The `node` sends periodic `uptime` messages to keep the connection alive.

## Installation

### Linux

```shell
git clone git@github.com:pridolfi/lisa.git
cd lisa
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
pip install .
```

## Usage

### Linux - dispatcher

- Use within created virtualenv.

```shell
lisa_run.py dispatcher
```

### Linux - node

- Set dispatcher to communicate to, just for the first time.
```shell
lisa_run.py set_dispatcher --uri dispatcher.example.org:5432 # port is optional
```

- Register to dispatcher using `scp` for public keys exchange, just for the first time.
```shell
lisa_run.py register --uri user@dispatcher.example.org:5432 # set user and port if required for SSH access
```

- Test
```shell
./nodes/linux/examples/list_devices.py # lists devices seen by dispatcher
```

## Supported platforms

- [ESP32](./nodes/esp32)
- [Linux](./nodes/linux)

## TODOs

See [issues](https://github.com/pridolfi/lisa/issues).
