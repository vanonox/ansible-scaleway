Scaleway Domain Ansible library
==========
- [Introduction](#introduction)
- [Usage](#usage)
  - [Records](#records)
  - [Examples](#examples)
  - [Makefille](#makefile)

# Introduction

This is a short module to update domain zone by Scaleway Api v2  
This module will follow the evolution of the Api

# Usage

Copy the directory libray and use the 2 modules to update your zone  
You need to fill your api private key available in Scaleway Console

example of command :

```
ansible-playbook --connection=local -i vars_example play_testxxxx.yml
```

example of command with python3 :

```
ansible-playbook --connection=local -e 'ansible_python_interpreter=/usr/bin/python3' -i vars_example play_testxxxx.yml
```

## Records

Ensure A record
```yaml
- domain_scaleway_record:
    token: SCALEWAY_PRIVATE_KEY
    dns_zone: team.internal.scaleway.com
    name: host01
    type: A
    content: 192.168.1.234
    ttl: 1440
    state: present
```

Ensure AAAA record
```yaml
- domain_scaleway_record:
    token: SCALEWAY_PRIVATE_KEY
    dns_zone: team.internal.scaleway.com
    name: host01
    type: AAAA
    content: 2001:cdba:0000:0000:0000:0000:3257:9652
    ttl: 1440
    state: present
    unique: true
```

Ensure CNAME record
```yaml
- domain_scaleway_record:
    token: SCALEWAY_PRIVATE_KEY
    dns_zone: team.internal.scaleway.com
    name: database
    type: CNAME
    content: host01.zone01.internal.example.com
    state: present
```

Ensure record is absent
```yaml
- domain_scaleway_record:
    token: SCALEWAY_PRIVATE_KEY
    dns_zone: team.internal.scaleway.com
    name: database
    type: CNAME
    state: absent
```

Ensure record is absent with filter on content
```yaml
- domain_scaleway_record:
    token: SCALEWAY_PRIVATE_KEY
    dns_zone: team.internal.scaleway.com
    name: database
    type: A
    content: 192.168.1.234    
    state: absent
```

## Examples

Fill vars_example with your credentials and you can test the examples files

## Makefille

* all : build the docker image for python2 and python3
* tests_python2 : execute the 3 `test` playbooks with python2
* shell_python2 : launch a shell in the docker container with volume mount locally to test playbook directly with python2
* tests_python3 : execute the 3 `test` playbooks with python3
* shell_python3 : launch a shell in the docker container with volume mount locally to test playbook directly with python3
