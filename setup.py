import subprocess
import ipaddress
import sys


G_network_interfaces :list = []

G_network_interface   :str = ''
G_ipv4_address        :str = ''
G_ipv4_prefix_length  :str = ''


G_network               :any 
G_network_address       :str = ''
G_network_prefix_length :str = ''
G_network_mask          :str = ''
G_gateway               :str = ''

G_create_docker_network :bool = False
G_docker_network_name   :str  = 'workstations_network'


def cmd(cmd:str, print_log:bool) -> str:

    log :str = subprocess.getoutput(cmd)

    if print_log:
        print(f"""
----setup----cmd----------------
{cmd}
{log}
--------------------------------
""")

    return log

def get_network_interfaces():

    log :str = cmd("ls /sys/class/net", True)
    
    global G_network_interfaces

    G_network_interfaces = log.split()

    return

def get_gateway(network_address: str) -> str:
    parts = network_address.split(".")
    parts[-1] = "1"
    return ".".join(parts)

def select_network_interface():

    if len(G_network_interfaces) == 0:
        raise Exception("No network interfaces found.")
    
    selected_interface:str = ''

    for interface in G_network_interfaces:
        s_interface = str(interface)

        #ethernet interfaces either start with eth (eth0, en1) or with en (enp0s, ens)
        if (s_interface.startswith("eth") or s_interface.startswith("en")):
            selected_interface = s_interface
            break

        
    if (selected_interface == ''):

        for interface in G_network_interfaces:
            s_interface = str(interface)
            
            #wireless interfaces start with wl (wlan, wlp)
            if (s_interface.startswith("wlan") or s_interface.startswith("wl")):
                selected_interface = s_interface

    if (selected_interface == ''):
        raise Exception("Could not find an ethernet or wireless interface")

    log :str = cmd(f"ip -4 addr show {selected_interface} | grep \"inet\" | awk '{{print $2}}'", True)

    log_list :list = log.split('/')



    global G_network_interface
    global G_ipv4_address
    global G_ipv4_prefix_length

    G_network_interface     = selected_interface
    G_ipv4_address          = log_list[0]
    G_ipv4_prefix_length    = log_list[1]
    
    global G_network
    global G_network_address
    global G_network_prefix_length
    global G_network_mask
    global G_gateway

    G_network = ipaddress.ip_network(f"{G_ipv4_address}/{G_ipv4_prefix_length}", strict = False)
    
    G_network_address       = G_network.network_address
    G_network_prefix_length = G_network._prefixlen
    G_network_mask          = G_network.netmask

    G_gateway =  get_gateway(str(G_network.network_address))

    print(f"""
Selected network interface                  {G_network_interface}
IPv4 address                                {G_ipv4_address}
IPv4 prefix length                          {G_ipv4_prefix_length}

Network                                     {G_network}
Network address                             {G_network_address}
Prefix len / Network prefix / Netmask bits  {G_network_prefix_length}
Network mask / subnet mask                  {G_network_mask}
Gateway                                     {G_gateway}
""")
    
    #Prefix length / network prefix / Netmask bits:
    #    20 bits for network, 12 bits for host addresses (ipv4 addresses are 32 bits)

    # Network mask / subnet mask
    # is calculated based on the prefix length
    # 20 bits set to 1 (network portion) + 12 bits set to 0 (host portion) = 11111111.11111111.11110000.00000000
    # = in decimal 255.255.240.0

    return

def create_docker_network(network_name :str):
    
    cmd(f"docker network create -d ipvlan --subnet {G_network_address}/{G_network_prefix_length} --gateway {G_gateway} -o ipvlan_mode=l2 -o parent={G_network_interface} {network_name}", True)

    return    

def read_args():

    global G_docker_network_name
    global G_create_docker_network

    for arg in sys.argv:
        if arg == "--create-docker-network":
            G_create_docker_network = True

        elif arg == "--docker-network-name":
            G_docker_network_name = sys.argv[sys.argv.index(arg) + 1]

    return

def main():

    read_args()

    get_network_interfaces()

    select_network_interface()

    if (G_create_docker_network):
        create_docker_network(G_docker_network_name)

    return



if __name__ == '__main__':
    main()
