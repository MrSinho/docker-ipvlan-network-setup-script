# Docker IPvlan Network Setup Script

A simple Python script that reads the available network interfaces and easily creates an IPvlan docker network for your containers.

## Usage (Linux only)

To scan the available network interfaces just type `python3 setup.py`

```shell
python3 setup.py

----setup----cmd----------------
ls /sys/class/net
docker0
eth0
lo
--------------------------------


----setup----cmd----------------
ip -4 addr show eth0 | grep "inet" | awk '{print $2}'
172.21.148.216/20
--------------------------------


Selected network interface                  eth0
IPv4 address                                172.21.148.216
IPv4 prefix length                          20

Network                                     172.21.144.0/20
Network address                             172.21.144.0
Prefix len / Network prefix / Netmask bits  20
Network mask / subnet mask                  255.255.240.0
Gateway                                     172.21.144.1

```