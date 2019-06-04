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

short_description: This is a little ansible module to manage Scaleway domain

version_added: "0.1"

description:
    - "This is a little ansible module to manage Scaleway domain"

options:
    token:
        description:
            - This is the secret key of Scaleway account
        required: true

    action:
        description:
            - This is action requested (get_domain)
        required: true

    domain:
        description:
            - The domain to manage
        required: false

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
- name: list all user contacts
    domain_scaleway_contact_list:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        action: "list_contacts"
- name: list domain contacts
    domain_scaleway_contact_list:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        action: "list_contacts"
        domain: "domain.tld"
```
'''

RETURN = '''
meta:
    status: The http code returned by the api
    data: The json error message
contents:
    list of contacts
'''


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        endpoint=dict(type='str', required=False, default=DEFAULT_ENDPOINT),
        version=dict(type='str', required=False, default=DEFAULT_VERSION),
        action=dict(choices=['list_contacts'], required=True),
        domain=dict(type='str', required=False, default=''),
        token=dict(type='str', required=True),
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
    result['message'] = 'working'

    headers = {
        "x-auth-token": module.params['token']
    }

    url_list_contacts = "{}/domain/{}/contacts" . format(module.params['endpoint'], module.params['version'])
    if module.params['domain'] != '':
        url_list_contacts = "{}?domain={}" . format(url_list_contacts, module.params['domain'])

    contents = []
    if module.params['action'] == 'list_contacts':
        result = requests.get(url_list_contacts, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results['contacts']

    module.exit_json(meta= {"status": result.status_code}, contents=contents)

def main():
    run_module()

if __name__ == '__main__':
    main()