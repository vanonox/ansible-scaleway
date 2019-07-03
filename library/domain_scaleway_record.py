#!/usr/bin/env python
# encoding: utf-8

import requests
from ansible.module_utils.basic import AnsibleModule
import json

DEFAULT_TTL = 86400
DEFAULT_PRIORITY = 10
DEFAULT_ENDPOINT = 'https://api.scaleway.com'
DEFAULT_VERSION = 'v2alpha2'

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'domain-team@scaleway.com'
}

DOCUMENTATION = '''
---
module: scaleway-domain

short_description: This is a little ansible module to update Scaleway dns records for a dns zone

version_added: "0.1"

description:
    - "This is a little ansible module to update Scaleway dns records for a dns zone"

options:
    token:
        description:
            - This is the secret key of Scaleway account
        required: true

    dns_zone:
        description:
            - This is the dns zone requested
        required: true

    name:
        description:
            - This is the name of the record to update
        required: true
    type:
        description:
            - This is the type of the record to update
        choices:
            - A
            - AAAA
            - MX
            - CNAME
            - TXT
            - SRV
        required: true

    state:
        description:
            - This is state requested
        choice:
            - present,absent
        required: true

    content:
        description:
            - This is content requested
        required: false

    unique:
        description:
            - This allows or not multiple contents on same name
        required: false
        default: false

    priority:
        description:
            - This is priority requested (for MX)
        required: true

    endpoint:
        description:
            - This is the endpoint to use, will allow use of sandbox api
        required: false

    verify_certs:
        description:
            - Ignore ssl certificate verification
        required: false
        type: bool
        default: True

extends_documentation_fragment

author:
    - domain-team@scaleway.com
'''

EXAMPLES = '''
```
# To list the records of a dns zone
- name: list records of example.com
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "list_records"

# To clear a dns zone records. Restart from scratch
- name: clear records contents of example.com
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "clear"
```
'''

EXAMPLES = '''
# update a record with unique content
```yaml
- domain_scaleway_record:
    name: host01
    dns_zone: example.com
    type: A
    content: 192.168.1.234
    ttl: 1440
    state: present
    unique: true
```

# update a record with multiple contents
```yaml
- domain_scaleway_record:
    name: host01
    dns_zone: example.com
    type: A
    content: 192.168.1.234
    ttl: 1440
    state: present
- domain_scaleway_record:
    name: host01
    dns_zone: example.com
    type: A
    content: 192.168.1.235
    ttl: 1440
    state: present
```

# delete all record with same name and type
```yaml
- domain_scaleway_record:
    name: host01
    dns_zone: example.com
    type: A
    state: absent
```
'''

RETURN = '''
meta:
    status: The http code returned by the api
    data: The json error message
    serial: The new serial of the dns zone
'''

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        endpoint=dict(type='str', required=False, default=DEFAULT_ENDPOINT),
        version=dict(type='str', required=False, default=DEFAULT_VERSION),
        token=dict(type='str', required=True),
        dns_zone=dict(type='str', required=True),
        name=dict(type='str', required=True),
        type=dict(choices=['A','AAAA','MX','CNAME','TXT','SRV','TLSA','NS','PTR','CAA'], required=True),
        content=dict(type='str', required=False, default=''),
        ttl=dict(type='int', required=False, default=DEFAULT_TTL),
        priority=dict(type='int', required=False, default=DEFAULT_PRIORITY),
        comment=dict(type='str', required=False),
        state=dict(choices=['present','absent'], required=False, default='present'),
        unique=dict(type='bool', required=False, default=False),
        verify_certs=dict(type='bool', required=False)
    )

    result = {}

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json()

    if module.params['endpoint']=='':
        module.params['endpoint']=DEFAULT_ENDPOINT

    if module.params['version']=='':
        module.params['version']=DEFAULT_VERSION

    result['original_message'] = module.params['name']+' '+module.params['type']
    result['message'] = 'working'

    headers = {
        "x-auth-token": module.params['token']
    }

    url = "{}/domain/{}/dns-zones/{}/records" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'])

    data = {}

    action = ""
    if (module.params['state'] == 'present'):
        comment = None
        if module.params['comment']:
            comment = module.params['comment']
        data = {
            "records": [
                {
                    "name": module.params['name'],
                    "type": module.params['type'],
                    "ttl": module.params['ttl'],
                    "priority": module.params['priority'],
                    "data": module.params['content'],
                    "comment": comment,
                }
            ]
        }
        if (module.params['unique']):
            action = "set"
            data["name"] = module.params['name']
            data["type"] = module.params['type']
            if ((module.params['content'] == '') and (module.params['type'] != 'CNAME')):
                module.fail_json(msg = 'content empty')
        else:
            action = "add"
    else:
        action = "delete"
        data = {
            "name": module.params['name'],
            "type": module.params['type']
        }
        if module.params['content'] != '':
            data['data'] = module.params['content']

    data = {
        "return_all_records": False,
        "changes": [
            {
                action: data
            }
        ]
    }

    result = requests.patch(url, json.dumps(data), headers=headers, verify=module.params['verify_certs'])

    if result.status_code != 200:
       # if error
       module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})

    module.exit_json(meta= {"status": result.status_code})

def main():
    run_module()

if __name__ == '__main__':
    main()
