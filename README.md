# AutoVBox

Pythonic application for automatically launching virtual networks using VirtualBox. 

* Operates on a models pattern, Networks and Hosts are initialisable from a single command. 
* Overide the Topology class to create custom topologies. 
* Automatically spawns SSH sessions in new Mac terminal windows. 

## Installation 

### ssh-copy-id
```bash
brew install ssh-copy-id
```

## Use case

### Quick Start
```bash 
$ python3 cli.py
```

### Create Default Network Topology
```python
>>> build
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

### Spawn SSH shells (Mac terminal) automatically 
```python
>>> shell
```
or individually:
```python
>>> shell <hostname>
```

### Cleanup 
```python
>>> destroy
```

# Troubleshooting 

## Virtual Machines abort on Mac OS Catalina 

```bash 
$ VBoxManage setextradata global GUI/HidLedsSync 0
$ VBoxManage setextradata global "GUI/HidLedsSync"
```

## Cloned Virtual Machines assigned duplicated IP's by DHCP Server 
On Linux Ubuntu 18.x and up, the DHCP server assigns IP addresses by the machine-id not the MAC address. Solution is to create a base imagine without a preset machine-id as follows: 

```bash
sudo rm /etc/machine-id /var/lib/dbus/machine-id
sudo touch /etc/machine-id
sudo chmod 444 /etc/machine-id
sudo shutdown -h now
``` 
