3
# Ansible

## Installation 
```bash
$ pip install --user ansible
```
Add ansible to PATH
```bash
$ export PATH=$PATH:/Users/danielcrouch/Library/Python/3.8/bin
```
Permanently add ansible to path 
Add: /Users/<username>/Library/Python/3.8/bin/
```python
nano /etc/paths
```

Validate installation 
```bash
ansible --version
```
Install SSHPass
```bash

$brew install hudochenkov/sshpass/sshpass
```

## Architecture 

### Inventories: 
Lists of host/targets requiring automated configuration.

### Playbooks: 
YAML files that describe the desired state.
Contains plays, plays contain tasks, tasks call modules. 
Tasks run sequentially. 
Handlers are triggered by tasks, running once at the end of plays.

```bash 
ansible-playbook <options> 
ansible-playbook my-playbook.yml 
```

https://docs.ansible.com/ansible/latest/user_guide/playbooks.html#working-with-playbooks

### Check mode 
Dry-run for ad-hoc commands and playbooks. Validates before making state changes on the target system. 
```bash
ansible web -C -m yum -a "name=httpd state=latest"
ansible-playbook -C my-playbook.yml
```

## Command Line (AD-HOC)
Ensure system is up and accesible 
```bash 
ansible web -m ping
```
Ensure a package is updated 
Ensure system is up and accesible 
```bash 
ansible web -s -m yum -a "name=openssl state=latest"
```

https://docs.ansible.com/ansible/latest/user_guide/intro_adhoc.html#intro-adhoc

### Default/Example Files 
https://github.com/ansible/ansible/tree/devel/examples


## Method
1. Update ansible.cfg *inventory* to point to hosts
2. Update hosts to include ip addresses of target machines
   20.0.0.2 ansible_user=dev
3. Run test 
    ```bash
    $ ansible -m ping all
    ``` 
4. Get hostname 
   ```bash
    $ ansible -m shell -a 'hostname' all
    ``` 