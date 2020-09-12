# Mac SSH Shell 

Automated Pythonic SSH Agent for: 
* Opening SSH sessions with a host in a new terminal on Apple Mac
* Distribute SSH keys to a host

## Prerequisites
[Python 3.x](https://www.python.org/downloads/)

## Usage

### Open SSH Session
```python 
from ssh_shell import Shell
s = Shell() 
s.connect(hostname, hostaddr, password) 
```

### Generate and distribute SSH keys
```python 
from ssh_shell import Shell
s = Shell() 
s.copy(hostname, hostaddr, password, keypath):
```
