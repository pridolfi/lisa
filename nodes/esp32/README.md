# LISA ESP32 port

## Building

Remember to create file `lisa_conf.c` declaring the following variables:

- `const char node_id[]` hostname or node FQDN.
- `const char server_ip[]` dispatcher IP address.
- `const short server_port` dispatcher port.
- `const unsigned char server_public_key[]` dispatcher public key.
- `const unsigned char node_private_key[]` node private key.
- `const char wifi_ssid[]` Wi-Fi SSID.
- `const char wifi_passwd[]` Wi-Fi password.

You can run `lisa.py register node_name` for an automated process.
