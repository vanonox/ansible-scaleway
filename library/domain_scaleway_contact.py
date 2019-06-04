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
- name: get contact
    domain_scaleway_contact:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        action: "get_contact"
        id: "abcd1234
```
'''

RETURN = '''
meta:
    status: The http code returned by the api
    data: The json error message
contents:
    the contact
'''


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    contact_args = dict(
        email=dict(type='str', required=False),
        phone_number=dict(type='str', required=False),
        fax_number=dict(type='str', required=False),
        address1=dict(type='str', required=False),
        address2=dict(type='str', required=False),
        zip=dict(type='str', required=False),
        city=dict(type='str', required=False),
        country=dict(type='str', required=False),
        vat=dict(type='str', required=False),
        siret=dict(type='str', required=False),
        lang=dict(type='str', required=False),
        resale=dict(type='str', required=False),
    )
    module_args = dict(
        endpoint=dict(type='str', required=False, default=DEFAULT_ENDPOINT),
        version=dict(type='str', required=False, default=DEFAULT_VERSION),
        action=dict(choices=['get_contact', 'update_contact'], required=True),
        id=dict(type='str', required=True),
        contact=dict(type='dict', options=contact_args),
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

    url_contact = "{}/domain/{}/contacts/{}" . format(module.params['endpoint'], module.params['version'], module.params['id'])

    contents = []
    if module.params['action'] == 'get_contact':
        result = requests.get(url_contact, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'update_contact':
        data = module.params['contact']
        result = requests.patch(url_contact, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results

    module.exit_json(meta= {"status": result.status_code}, contents=contents)

def main():
    run_module()

if __name__ == '__main__':
    main()