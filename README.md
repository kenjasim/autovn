# AutoVBox

Pythonic application for automatically launching virtual networks using VirtualBox. 

* Operates on a models pattern, Networks and Hosts are initialisable from a single command. 
* Overide the Topology class to create custom topologies. 
* Automatically spawns SSH sessions in new Mac terminal windows. 

## Use case

### Quick Start
```bash 
$ python3 topo.py
```

### Display host configs 
```python
t = Topology()
t.start() 
```
### Display host configs 
```python 
t.show_hosts() 
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
t.show_networks()
```
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

### Spawn SSH shells (Mac terminal) automatically 
```python
>>> t.shells() 
```
or individually:
```python
>>> host.shell() 
```

### Cleaup 
```python
>>> t.destroy() 
```
