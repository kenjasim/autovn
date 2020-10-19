# Automated Virtual Networks (AVN)

Pythonic application for automatically launching virtual networks using VirtualBox. 

* Command line based application 
* Automated network virtualisation with VirtualBox 
* YAML-defined network-host topology configuration
* Create, run and manage multiple deployment topologies
* Data persistence 
* RestApi server mode for remote connection with https support
* Remote client-only mode for connection to RestApi Server 
* User registration and authentication
* Automatically spawn SSH sessions in new Mac and Linux terminal windows
* Automatically distribute RSA keys for remote access and ansible support 
* SSH port forwarding for remote host SSH access 
* Log management 
* Supported on MacOS and Linux


## Requirements

Python 3.7: 
<https://www.python.org/downloads/>

VirtualBox 6.1.14:
<https://www.virtualbox.org/wiki/Downloads>

Nginx 1.18.0: 
<https://www.nginx.com/resources/wiki/start/topics/tutorials/install/>


## Installation 

```bash
# Clone repository
$ git clone https://github.com/Aresium/autovn.git
$ cd autovn 
# Build application binaries
$ make install
# Add avn application to PATH
$ mv bin/avn /usr/local/bin
``` 


## Development Environment 

```bash
# Clone repository
$ git clone https://github.com/Aresium/autovn.git
$ cd autovn 
# Create virtual python environment
$ python3 -m venv venv
$ source /venv/bin/activate 
$ pip3 install -r requirements.txt
# Start application
$ python3 /src/avn.py
```


## AVN Config File 
On initial launch of the avn application a configuration file `.avn` is built in the users home directory: `/Users/<username>/.avn`

```bash
~/.avn
├── certs
│   ├── cert.key
│   └── cert.pem
├── data.db
├── images
│   ├── Ubuntu_Server_20.04.ova
│   └── vm_setup.md
├── keys
│   ├── id_rsa_vb
│   └── id_rsa_vb.pub
├── logs
│   ├── access.log
│   ├── avn.log
│   └── error.log
├── proxy
│   ├── mime.types
│   └── nginx.conf
└── templates
    ├── default.yaml
    └── test.yaml
```


## YAML Topology Configuration 

Create custom topologies with yaml templates. To be located in `~/.avn/templates`.
Simply add networks, hosts and then assign networks to hosts as per the default.yaml example:

```yaml
---
# Deploymnet Configuration
deployment: 
  name: default

# Network Configuration
networks:
  hoif1:
    netaddr: "20.0.0.1"
    dhcplower: "20.0.0.2"
    dhcpupper: "20.0.0.254"
  hoif2:
    netaddr: "30.0.1.1"
    dhcplower: "30.0.1.2"
    dhcpupper: "30.0.1.254"

#Hosts Configuration
hosts:
  host1:
    image: "vm_templates/Ubuntu Server 20.04.ova"
    username: "dev"
    password: "ved"
    networks:
      - hoif1
    internet_adapter: bridged
  host2:
    image: "vm_templates/Ubuntu Server 20.04.ova"
    username: "dev"
    password: "ved"
    networks:
      - hoif1
      - hoif2    
    internet_adapter: bridged
  host3:
    image: "vm_templates/Ubuntu Server 20.04.ova"
    username: "dev"
    password: "ved"
    networks:
      - hoif2
    internet_adapter: bridged
```


## Example Usage 

### Create Default Network Topology
```python
>>> build # default.yaml
>>> build <template-name.yaml>
>>> build <template-name.yml>
```

### Start, Stop, Restart and Destroy Deployments
```python
>>> start <deployment-name>
>>> stop <deployment-name>
>>> restart <deployment-name>
>>> destroy <deployment-name>
```

### Display host configurations
```python 
show h
```

```bash
╒══════════╤═══════════╤═════════════════╤════════╤══════════╤══════════════╕
│ vmname   │ VMState   │ ostype          │   cpus │   memory │ deployment   │
╞══════════╪═══════════╪═════════════════╪════════╪══════════╪══════════════╡
│ host1    │ running   │ Ubuntu (64-bit) │      2 │     2048 │ default      │
├──────────┼───────────┼─────────────────┼────────┼──────────┼──────────────┤
│ host2    │ running   │ Ubuntu (64-bit) │      2 │     2048 │ default      │
├──────────┼───────────┼─────────────────┼────────┼──────────┼──────────────┤
│ host3    │ running   │ Ubuntu (64-bit) │      2 │     2048 │ default      │
╘══════════╧═══════════╧═════════════════╧════════╧══════════╧══════════════╛
```

### Display network configurations
```python 
show n
```

```bash
╒══════════╤════════╤═══════════════════════╤═══════════════════╤══════════╤══════════════╕
│ vmname   │   name │ netname               │ mac               │ ip       │ deployment   │
╞══════════╪════════╪═══════════════════════╪═══════════════════╪══════════╪══════════════╡
│ host1    │      1 │ en0: Wi-Fi (Wireless) │ 08:00:27:44:23:44 │          │ default      │
├──────────┼────────┼───────────────────────┼───────────────────┼──────────┼──────────────┤
│ host1    │      2 │ vboxnet1              │ 08:00:27:82:e6:ba │ 20.0.0.2 │ default      │
├──────────┼────────┼───────────────────────┼───────────────────┼──────────┼──────────────┤
│ host2    │      1 │ en0: Wi-Fi (Wireless) │ 08:00:27:d7:b9:ba │          │ default      │
├──────────┼────────┼───────────────────────┼───────────────────┼──────────┼──────────────┤
│ host2    │      2 │ vboxnet1              │ 08:00:27:f0:35:a4 │ 20.0.0.3 │ default      │
├──────────┼────────┼───────────────────────┼───────────────────┼──────────┼──────────────┤
│ host2    │      3 │ vboxnet2              │ 08:00:27:be:30:a7 │ 30.0.0.3 │ default      │
├──────────┼────────┼───────────────────────┼───────────────────┼──────────┼──────────────┤
│ host3    │      1 │ en0: Wi-Fi (Wireless) │ 08:00:27:88:44:de │          │ default      │
├──────────┼────────┼───────────────────────┼───────────────────┼──────────┼──────────────┤
│ host3    │      2 │ vboxnet2              │ 08:00:27:74:fd:83 │ 30.0.0.2 │ default      │
╘══════════╧════════╧═══════════════════════╧═══════════════════╧══════════╧══════════════╛
``` 

### Spawn SSH Shells (Mac and Linux) Automatically 
```python
>>> shell <hostname>
```
For remote client mode, see Server chapter.

### Automatically Generate and Distribute SSH Keys 
```python
>>> keys <deployment-id>
```

### Start/Stop SSH Forwarding
```python
>>> sshforward start <deployment-id>
>>> sshforward stop <deployment-id>
```

### Exit Application 
```python
>>> exit 
```
Or press, CTRL + C 


## Rest API Server 
The RestAPI Server enables remote access to the application either through AVN's client mode, or via direct http (localhost), https (remote) requests. 

### Server (Localhost mode with http) 

```python
>>> server
```

Response:
```python
[i] Starting RestAPI server...
[✓] Server avaliable at: http://127.0.0.1:5000/
```

The server can be run in headless mode by parsing in the the `-r` option only at the command line:
```bash
$ ./avn -r
```

### Server (Remote mode with https)

```python
>>> server r # remote
```

Response:
```python
[i] Starting RestAPI server...
[✓] Server avaliable at: https://<public-ip-address>:5000/
```

The server can be run in headless mode by parsing in the the `-r <public-up-address>` option only at the command line:
```bash
$ python avn.py -r 
```

Note: 
1. The https certificates are by default self-signed. A certification warning will therfore need to be accepted if accessing via a browser. If using `curl`, apply the `--insecure` option. 
2. The https termination is handle by an Nginx reverse proxy. In order to run with user-level priviledges the port must be greater than `1024` and the proxy config files must be assigned user-level permissions. This is the default configuration. 

### Client-only Mode 

The RestApi Server can be accessed via AVN's client-only mode. All functions and options avaliable to the standard CLI are avaliable; appearing identical to the standard cli mode. 

```bash
$ python avn.py -c <https://server-url:6001>
$ python avn.py -c <http://127.0.0.1:5000/>
```


## Authentication and Authorisation

When accessing the application via the RestApi Server all requests must be authorised for a given user. The RestApi, being stateless, provisions a session token upon login that is used to authenticate future Api calls.

### Default User

```python
[i] Creating admin user...
Enter admin Password:
```

If the database has no active users, when the user starts the rest API they must enter an admin password to create the default user.

### Register User 
```python
>>> register johndoe
Enter Password: 
```

### Remove User 
```python
>>> remove johndoe
[i] Removing user...
Enter Password: 
```

### Change user password
```python
>>> passwd johndoe
[i] Changing user password...
Enter old Password: 
Enter new Password: 
```

### Server Login (Client-mode) 
```python
>>> login <username>
# Returns a session token for future Api call authorisation
```

### Spawn SSH Shells (Mac and Linux) Automatically (Remote Client Mode)

In remote client mode it is possible to SSH into the Server side virtual machines. On the server-side, the application starts port forwarding servers for each host in the deployment. This allows SSH sessions to be generated for all hosts remotely (via the automated port-forwarding redirect), and to be locally accessible on the default SSH port `22`.

```python
>>> sshforward <deployment-id>
>>> shell <vmname> <server-ip> <username> <password>
```

## Template Management

Topology configurations are defined by a YAML Topology Configuration as demonstrated in the above chapter. Templates can be added either by manually saving the file to the `~/.avn/templates` configuration directory OR through AVN's cli (standard or Client modes):

### Create Template from Local YAML File

```python
>>> create -f <path/to/file-name.yaml>
>>> create -f <path/to/file-name.yml>
```

### Pull Template from GitHub

```python
>>> create -g <https://raw.githubusercontent.com/path/to/template.yaml>
```

Note: Github repository must be publicly avaliable. 


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

### Ubuntu 20.04 Dual Honed Virtual Machines Fail to Connect to Secondary Networks

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
$ sudo netplan apply
```
