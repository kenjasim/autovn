# Automated Virtual Networks (AVN)

Pythonic application for automatically launching virtual networks using VirtualBox. 

* Command line based application 
* YAML-defined network-host topology configuration
* Data persistence 
* RestApi server 
* Log management 
* Automated virtualisation with VirtualBox 
* Automatically spawn SSH sessions in new Mac and Linux terminal windows
* Automatically distribute RSA keys for remote access and ansible support 


## Installation 

```bash
pip3 install -r requirements.txt
```

## YAML Topology Configuration 

Create custom topologies by simply adding networks, hosts and relationships between the two. 

```yaml
---
# Network Configuration
networks:
  hoif1:
    netaddr: "20.0.0.1"
    dhcplower: "20.0.0.2"
    dhcpupper: "20.0.0.254"
  hoif2:
    netaddr: "20.0.1.1"
    dhcplower: "20.0.1.2"
    dhcpupper: "20.0.1.254"

#Hosts Configuration
hosts:
  host1:
    image: "vm_templates/Ubuntu Server 20.04.ova"
    username: "dev"
    password: "ved"
    networks:
      - hoif1
    internet_access: True
  host2:
    image: "vm_templates/Ubuntu Server 20.04.ova"
    username: "dev"
    password: "ved"
    networks:
      - hoif1
      - hoif2    
    internet_access: True
  host3:
    image: "vm_templates/Ubuntu Server 20.04.ova"
    username: "dev"
    password: "ved"
    networks:
      - hoif1
    internet_access: True
```

## Example Usage 

### Quick Start
```bash 
$ python3 avn.py
```

### Create Default Network Topology
```python
>>> build
>>> build <path-to-image-template>
```

### Start Virtual Machines 
```python
>>> start 
```

### Display host configs 
```python 
show h
```

```bash
╒══════════╤═══════════╤═════════════════╤════════╤══════════╕
│ vmname   │ VMState   │ ostype          │   cpus │   memory │
╞══════════╪═══════════╪═════════════════╪════════╪══════════╡
│ master   │ running   │ Ubuntu (64-bit) │      1 │     2048 │
├──────────┼───────────┼─────────────────┼────────┼──────────┤
│ slave1   │ running   │ Ubuntu (64-bit) │      1 │     2048 │
├──────────┼───────────┼─────────────────┼────────┼──────────┤
│ slave2   │ running   │ Ubuntu (64-bit) │      1 │     2048 │
╘══════════╧═══════════╧═════════════════╧════════╧══════════╛
```

### Display network configs 
```python 
show n
```

```bash
╒══════════╤═══════╤═══════════╤═══════════════════╤═══════════╕
│ vmname   │   nic │ netname   │ mac               │ ip        │
╞══════════╪═══════╪═══════════╪═══════════════════╪═══════════╡
│ master   │     1 │ nat       │ 08:00:27:67:c2:a1 │           │
├──────────┼───────┼───────────┼───────────────────┼───────────┤
│ master   │     2 │ vboxnet0  │ 08:00:27:21:9a:98 │ 20.0.0.33 │
├──────────┼───────┼───────────┼───────────────────┼───────────┤
│ slave1   │     1 │ nat       │ 08:00:27:32:eb:53 │           │
├──────────┼───────┼───────────┼───────────────────┼───────────┤
│ slave1   │     2 │ vboxnet0  │ 08:00:27:ab:ec:0b │ 20.0.0.34 │
├──────────┼───────┼───────────┼───────────────────┼───────────┤
│ slave2   │     1 │ nat       │ 08:00:27:ab:5e:dd │           │
├──────────┼───────┼───────────┼───────────────────┼───────────┤
│ slave2   │     2 │ vboxnet0  │ 08:00:27:4e:15:78 │ 20.0.0.32 │
╘══════════╧═══════╧═══════════╧═══════════════════╧═══════════╛
``` 

### Spawn SSH Shells (Mac and Linux) Automatically 
```python
>>> shell
>>> shell <hostname>
```

### Generate and Distribute SSH Keys 
```python
>>> keys
```

### Cleanup 
```python
>>> destroy
```

### Exit Application 
```python
>>> exit 
```
Or press, CTRL + C 

### Rest API 
```python
>>> server

```
Or press, CTRL + C 
Response:
```python
[i] Starting RestAPI server...
[✓] Server avaliable at: http://127.0.0.1:5000/
```


## Troubleshooting 

### Virtual Machines aborts on Mac OS Catalina 

1. Modify GUI settings
```bash 
$ VBoxManage setextradata global GUI/HidLedsSync 0
$ VBoxManage setextradata global "GUI/HidLedsSync"
```
2. Disable audio in virtual machine settings via VirtualBox GUI

### Cloned Virtual Machines assigned duplicated IP's by DHCP Server 
On Linux Ubuntu 18.x and up, by default, systemd-networkd supplies an "opaque" client-ID that was generated from the contents of /etc/machine-id.

The DHCP protocol leases are chosen by client ID first (as long as the client supplies a "client ID" option, which may or may not be MAC-based), then by the MAC address only if the client didn't send an ID.

To ensure a unique IP addresses assignment the machine-id must be unique. Solution is to create a base imagine without a preset machine-id as follows: 

```bash
$ sudo rm /etc/machine-id /var/lib/dbus/machine-id
$ sudo touch /etc/machine-id
$ sudo chmod 444 /etc/machine-id
$ sudo shutdown -h now
``` 
Opening the VM will re-allocate a machine-id. 

## Dual Honed Virtual Machines Fail to Connect to Secondary Networks
Additional interaces must be configured for each network. Edit 00-installer-config.yaml as follows:

```bash
$ sudo nano /etc/netplan/00-installer-config.yaml
```
```yaml
	#####
	network:
	  ethernets:
	    enp0s3:
	    	dhcp4: true
	    enp0s8:
	    	dhcp4: true
	  version: 2
```
```bash
$ sudo netplan apply```
```
