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
            - This is action requested (get_domain, buy_domain)
        required: true

    domain:
        description:
            - The domain to manage
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
# To get details about a domain
- name: get domain
    domain_scaleway_domain:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        domain: "domain.tld"
        action: "get_domain"

# To buy a domain
- name: get domain with a contact ID
    domain_scaleway_domain:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        domain: "domain.tld"
        action: "buy_domain"
        "organization_id": "YOUR_SCALEWAY_ORGANIZATION_ID",
        "period": 1,
        "contact_id": "abcd1234"
```
'''

RETURN = '''
meta:
    status: The http code returned by the api
    data: The json error message
domain:
    the domain requested
contents:
    domain details
'''


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    contact_args = dict(
        legal_form=dict(type='str', required=True),
        civility=dict(type='str', required=False),
        firstname=dict(type='str', required=True),
        lastname=dict(type='str', required=True),
        company_name=dict(type='str', required=False),
        email=dict(type='str', required=True),
        phone_number=dict(type='str', required=True),
        fax_number=dict(type='str', required=False),
        address1=dict(type='str', required=True),
        address2=dict(type='str', required=False),
        zip=dict(type='str', required=True),
        city=dict(type='str', required=True),
        country=dict(type='str', required=True),
        vat=dict(type='str', required=False),
        siret=dict(type='str', required=False),
        lang=dict(type='str', required=False),
        resale=dict(type='str', required=False),
    )
    module_args = dict(
        endpoint=dict(type='str', required=False, default=DEFAULT_ENDPOINT),
        version=dict(type='str', required=False, default=DEFAULT_VERSION),
        action=dict(choices=[
            'get_domain',
            'buy_domain',
            'renew_domain',
            'update_domain',
            'lock_domain_transfer',
            'unlock_domain_transfer',
            'enable_domain_auto_renew',
            'disable_domain_auto_renew',
            'get_domain_auth_code'
        ], required=True),
        domain=dict(type='str', required=True),
        organization_id=dict(type='str', required=False),
        period=dict(type='int', required=False),
        contact=dict(type='dict', options=contact_args),
        owner_contact=dict(type='dict', options=contact_args),
        administrative_contact=dict(type='dict', options=contact_args),
        technical_contact=dict(type='dict', options=contact_args),
        contact_id=dict(type='str', required=False),
        owner_contact_id=dict(type='str', required=False),
        administrative_contact_id=dict(type='str', required=False),
        technical_contact_id=dict(type='str', required=False),
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

    url_get_domain = "{}/domain/{}/domains/{}" . format(module.params['endpoint'], module.params['version'], module.params['domain'])
    url_buy_domain = "{}/domain/{}/domains" . format(module.params['endpoint'], module.params['version'])
    url_renew_domain = "{}/domain/{}/domains/{}/renew" . format(module.params['endpoint'], module.params['version'], module.params['domain'])
    url_update_domain = url_get_domain
    url_lock_domain_transfer = "{}/domain/{}/domains/{}/lock-transfer" . format(module.params['endpoint'], module.params['version'], module.params['domain'])
    url_unlock_domain_transfer = "{}/domain/{}/domains/{}/unlock-transfer" . format(module.params['endpoint'], module.params['version'], module.params['domain'])
    url_enable_domain_auto_renew = "{}/domain/{}/domains/{}/enable-auto-renew" . format(module.params['endpoint'], module.params['version'], module.params['domain'])
    url_disable_domain_auto_renew = "{}/domain/{}/domains/{}/disable-auto-renew" . format(module.params['endpoint'], module.params['version'], module.params['domain'])
    url_get_domain_auth_code = "{}/domain/{}/domains/{}/auth-code" . format(module.params['endpoint'], module.params['version'], module.params['domain'])

    contents = []
    data = {}
    if module.params['action'] == 'get_domain':
        result = requests.get(url_get_domain, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results['domain']
    elif module.params['action'] == 'buy_domain':
        data = {
            'domain': module.params['domain'],
            'organization_id': module.params['organization_id'],
            'period': module.params['period']
        }
        if module.params['contact'] != None:
            data['contact'] = module.params['contact']
        if module.params['contact_id'] != None:
            data['contact_id'] = module.params['contact_id']

        result = requests.post(url_buy_domain, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'renew_domain':
        data = {
            'domain': module.params['domain'],
            'period': module.params['period']
        }

        result = requests.post(url_renew_domain, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'update_domain':
        data = {}
        if module.params['owner_contact'] != None:
            data['owner_contact'] = module.params['owner_contact']
        if module.params['administrative_contact'] != None:
            data['administrative_contact'] = module.params['administrative_contact']
        if module.params['technical_contact'] != None:
            data['technical_contact'] = module.params['technical_contact']
        if module.params['owner_contact_id'] != None:
            data['owner_contact_id'] = module.params['owner_contact_id']
        if module.params['administrative_contact_id'] != None:
            data['administrative_contact_id'] = module.params['administrative_contact_id']
        if module.params['technical_contact_id'] != None:
            data['technical_contact_id'] = module.params['technical_contact_id']

        result = requests.patch(url_update_domain, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'lock_domain_transfer':
        data = {}
        result = requests.post(url_lock_domain_transfer, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'unlock_domain_transfer':
        data = {}
        result = requests.post(url_unlock_domain_transfer, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'enable_domain_auto_renew':
        data = {}
        result = requests.post(url_enable_domain_auto_renew, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'disable_domain_auto_renew':
        data = {}
        result = requests.post(url_disable_domain_auto_renew, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results
    elif module.params['action'] == 'get_domain_auth_code':
        result = requests.get(url_get_domain_auth_code, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            module.fail_json(msg = 'Your request failed', meta = {"status": result.status_code, "data": result.json()})
        else:
            results = result.json()
            contents = results

    module.exit_json(meta= {"status": result.status_code}, contents=contents, domain=module.params['domain'], data=data)

def main():
    run_module()

if __name__ == '__main__':
    main()