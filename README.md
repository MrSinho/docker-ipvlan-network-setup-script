# Docker IPvlan Network Setup Script

A simple Python script that reads the available network interfaces and easily creates an IPvlan docker network for your containers.

## Usage (Linux only)

* To scan the available network interfaces just type `python3 setup.py`

```shell
python3 setup.py
```

```shell
----setup----cmd----------------
ls /sys/class/net
docker0
enp0s3
lo
--------------------------------


----setup----cmd----------------
ip -4 addr show enp0s3 | grep "inet" | awk '{print $2}'
192.168.1.70/24
--------------------------------


Selected network interface                  enp0s3
IPv4 address                                192.168.1.70
IPv4 prefix length                          24

Network                                     192.168.1.0/24
Network address                             192.168.1.0
Prefix len / Network prefix / Netmask bits  24
Network mask / subnet mask                  255.255.255.0
Gateway                                     192.168.1.1

```

* To automatically create a Docker IPvlan network type `python3 setup.py --create-docker-network --docker-network-name ipvlan_network`. If you don't specify the docker network name it will be named `ipvlan_network`.

```shell
python3 setup.py --create-docker-network --docker-network-name ipvlan_network
```

```shell
----setup----cmd----------------
ls /sys/class/net
docker0
enp0s3
lo
--------------------------------


----setup----cmd----------------
ip -4 addr show enp0s3 | grep "inet" | awk '{print $2}'
192.168.1.70/24
--------------------------------


Selected network interface                  enp0s3
IPv4 address                                192.168.1.70
IPv4 prefix length                          24

Network                                     192.168.1.0/24
Network address                             192.168.1.0
Prefix len / Network prefix / Netmask bits  24
Network mask / subnet mask                  255.255.255.0
Gateway                                     192.168.1.1


----setup----cmd----------------
docker network create -d ipvlan --subnet 192.168.1.0/24 --gateway 192.168.1.1 -o ipvlan_mode=l2 -o parent=enp0s3 ipvlan_network
5c979b9229a34b15e3b4a2e05cf214f41fc595eaf90a5f0b19b110a536e689c8
--------------------------------

```

## Testing with a container

Now you can create and run a docker container with the newly created network:

```shell
docker run -d --network ipvlan_network --name test ubuntu:latest sleep infinity
docker exec -it test bash
```

## Important notes when using Virtual Machines

If you are running this script on a Linux virtual machine you should consider that your docker container will have assigned the following ranges of addresses instead of the most common `192.168.0.0 - 192.168.255.255`:

| Private IP Range                   | Subnet Mask (Default)            | CIDR            | Common Use Case                  |
|------------------------------------|----------------------------------|-----------------|----------------------------------|
| **10.0.0.0 - 10.255.255.255**      | `255.0.0.0`                      | `/8` - `/30`    | Large corporate networks, VMs    |
| **172.16.0.0 - 172.31.255.255**    | `255.240.0.0`                    | `/12`           | Enterprise networks              |
| **192.168.0.0 - 192.168.255.255**  | `255.255.0.0` or `255.255.255.0` | `/16` - `/24`   | Home and small business networks |


With VirtualBox you can assign the `192.168.0.0 - 192.168.255.255` ip range by _selecting VM → Settings → Network → Advanced → Port Forwarding_, or alternatively switch from _NAT mode_ to _Bridged Adapter_ or _Host-Only Networking_ to change how the VM interacts with your real network.