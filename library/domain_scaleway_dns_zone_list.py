#!/usr/bin/env python
# encoding: utf-8

import requests
from ansible.module_utils.basic import AnsibleModule
import json

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

short_description: This is a little ansible module to update Scaleway dns zone

version_added: "0.1"

description:
    - "This is a little ansible module to update Scaleway dns zone"

options:
    token:
        description:
            - This is the secret key of Scaleway account
        required: true

    domain:
        description:
            - Filter dns zones for a domain
        required: false

    action:
        description:
            - This is action requested (list_dns_zones)
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
# To list the dns zones
- name: list dns zones
    domain_scaleway_dns_zone_list:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        action: "list_dns_zones"

# To list a domain dns zones
- name: list example.com dns zones
    domain_scaleway_dns_zone_list:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        domain: "example.com"
        action: "list_dns_zones"
```
'''

RETURN = '''
meta:
    status: The http code returned by the api
    data: The json error message
domain:
    the domain dns zones requested
contents:
    array of dns zone's records
total:
    total number of dns zones
'''


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        endpoint=dict(type='str', required=False, default=DEFAULT_ENDPOINT),
        version=dict(type='str', required=False, default=DEFAULT_VERSION),
        action=dict(choices=['list_dns_zones'], required=True),
        token=dict(type='str', required=True),
        domain=dict(type='str', required=False),
        verify_certs=dict(type='bool', required=False)
    )

    result = {}

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result

    if module.params['endpoint']=='':
        module.params['endpoint']=DEFAULT_ENDPOINT

    result['original_message'] = module.params['action']
    if module.params['domain']:
        result['original_message'] += module.params['domain']
    result['message'] = 'working'

    headers = {
        "x-auth-token": module.params['token']
    }

    url = "{}/domain/{}/dns-zones?" . format(module.params['endpoint'], module.params['version'])
    if module.params['domain']:
        url += "domain={}&" . format(module.params['domain'])
    url += "page=1&page_size=10000"

    total = 0
    contents = []
    if module.params['action']=='list_dns_zones':
        result = requests.get(url, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            total = results['total_count']
            contents = results['dns_zones']

    module.exit_json(meta= {"status": result.status_code}, domain=module.params['domain'], contents=contents, total=total)

def main():
    run_module()

if __name__ == '__main__':
    main()