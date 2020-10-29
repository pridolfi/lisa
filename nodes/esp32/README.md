# LISA ESP32 port

## Building

- Use [`esp-idf`](https://github.com/espressif/esp-idf).
- Before building, you need to set LISA configuration for the ESP32 node (its node ID, key pair, Wi-Fi credentials, dispatcher address).
- Generate key pairs for ESP32 node and register to dispatcher using `./lisa_esp32_generator.py`.
- See `lisa_esp32_generator.py -h` for help.

### Build example

- Use within LISA virtualenv:
```shell
$ lisa_esp32_generator.py my_esp32_node YOUR-WIFI-SSID nodes/esp32/main/ # folder where to store lisa_conf.c
Wi-Fi password: # enter wi-fi password
Wi-Fi password again: # enter wi-fi password again
2020-10-28 23:39:28,618 INFO lisa_esp32_generator.generate: Writing configuration to nodes/esp32/main/lisa_conf.c
2020-10-28 23:39:28,680 INFO lisa_esp32_generator.generate: Writing public key to /home/user/.lisa/peers/my_esp32_node.pub
2020-10-28 23:39:28,682 INFO lisa_esp32_generator.generate: Registering my_esp32_node to srv1.codenload.com...
2020-10-28 23:39:29,132 INFO node.register_new_node: my_esp32_node registered successfully.
2020-10-28 23:39:30,349 INFO lisa_esp32_generator.generate: Configuration written to /home/user/lisa/nodes/esp32/main/lisa_conf.c
# now you can build with esp-idf
$ idf.py build
```