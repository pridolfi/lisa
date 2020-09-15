# LISA :dog:

Light Implementation of Secure Automation

## TL;DR

LISA is a secure P2P data exchange library written in Python and C (for its ESP32 port). It allows two or more peers (`nodes`) to exchange information using a third peer as a `dispatcher`. Each `node` can act also as a `dispatcher` to prevent centralization of messages. It uses RSA and AES encryption standards to verify identity and encrypt exchanged data.

## Functional description

Let's say `node1` wants to send `hello!` to `node2` but they can't establish a direct TCP/IP connection, but they are both connected to the Internet and can access a server running a LISA `dispatcher` with the name `dispatcher1.example.org`. 

1. `node1` uses public RSA key from `node2` to encrypt the message `hello!`.

2. `node1` establishes a secure session with `dispatcher1.example.org`:
    1. `node1` encrypts its `node_id` with the public RSA key of the `dispatcher` and sends the information using a standard UDP connection.
    2. The `dispatcher` decrypts the message with its private RSA key and identifies an incoming connection request from `node1`.
    3. The `dispatcher` generates a random AES key and encrypts it with the RSA public key of `node1` and replies using the same UDP connection.
    4. `node1` receives and decrypts the AES key. Until the session ends, this random key and the AES scheme will be used for encryption and decryption of data between the `node` and the `dispatcher`.

3. `node1` sends the encrypted message to the `dispatcher` specifying that the recipient is `node2`. The `dispatcher` uses a Queue for each registered `node` to hold the message.

4. `node1` closes the session by sending a special `close` payload to the `dispatcher` who replies with the correspondent `close` response.

5. `node2` opens a session with the `dispatcher` in the way described in step 2.

6. `node2` asks the `dispatcher` for any message. `dispatcher` replies with the encrypted message from `node1`.

7. `node2` decrypts the message using its private RSA key.

8. `node2` closes the session in the same way described in step 4.

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

## TODOs

See [issues](https://github.com/pridolfi/lisa/issues).
