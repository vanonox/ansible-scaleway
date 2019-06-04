#!/usr/bin/env python
# encoding: utf-8

import requests
from ansible.module_utils.basic import AnsibleModule
import json
import base64

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

    dns_zone:
        description:
            - This is the dns zone requested
        required: true
    
    refresh_recreate_dns_zone:
        description:
            - Recreate the dns zone records after refresh
        required: false
    
    refresh_recreate_sub_dns_zone:
        description:
            - Recreate the sub dns zone records after refresh
        required: false
    
    export_format:
        description:
            - Format use to export the dns zone (ex: bind)
        required: false
    
    import_format:
        description:
            - Format use to import the dns zone (ex: bind)
        required: false
    
    import_content:
        description:
            - Import raw string content
        required: false

    action:
        description:
            - This is action requested (list_records, refresh, clear, delete, import_raw, export_raw)
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

# To clear a dns zone records. Restart from scratch with default scaleway NS
- name: clear records of example.com
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "clear"

# To refresh a SOA dns zone.
- name: refresh SOA of example.com
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "refresh"

# To refresh a SOA dns zone and recreate the dns zone and it's sub dns zones.
- name: refresh SOA of example.com and recreate dns zones
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "refresh"
        refresh_recreate_dns_zone: True
        refresh_recreate_sub_dns_zone: True

# To export the content of a dns zone.
- name: export with BIND format
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "export_raw"
        export_format: "bind"

# To import the content of a dns zone.
- name: import with BIND format
    domain_scaleway_record:
        token: "ZETZEGERHG35ERHGERHERSDGDSGS"
        dns_zone: "example.com"
        action: "import_raw"
        import_format: "bind"
        import_content: ""
```
'''

RETURN = '''
meta:
    status: The http code returned by the api
    data: The json error message
dns_zone:
    the dns zone name requested
contents:
    array of dns zone's records
'''


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        endpoint=dict(type='str', required=False, default=DEFAULT_ENDPOINT),
        version=dict(type='str', required=False, default=DEFAULT_VERSION),
        action=dict(choices=['list_records', 'refresh', 'clear', 'delete', 'export_raw', 'import_raw'], required=True),
        token=dict(type='str', required=True),
        dns_zone=dict(type='str', required=True),
        refresh_recreate_dns_zone=dict(type='bool', required=False, default=False),
        refresh_recreate_sub_dns_zone=dict(type='bool', required=False, default=False),
        export_format=dict(type='str', required=False, default="bind"),
        import_format=dict(type='str', required=False, default="bind"),
        import_content=dict(type='str', required=False),
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

    result['original_message'] = module.params['action']+' '+module.params['dns_zone']
    result['message'] = 'working'

    headers = {
        "x-auth-token": module.params['token']
    }

    url_get_records = "{}/domain/{}/dns-zones/{}/records?page=1&page_size=10000" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'])
    url_clear_records = "{}/domain/{}/dns-zones/{}/records" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'])
    url_refresh = "{}/domain/{}/dns-zones/{}/refresh" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'])
    url_export_raw = "{}/domain/{}/dns-zones/{}/raw?format={}" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'], module.params['export_format'])
    url_import_raw = "{}/domain/{}/dns-zones/{}/raw" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'])
    url = "{}/domain/{}/dns-zones/{}" . format(module.params['endpoint'], module.params['version'], module.params['dns_zone'])

    contents = []
    if module.params['action']=='refresh':
        data = {
            "recreate_dns_zone": module.params['refresh_recreate_dns_zone'],
	        "recreate_sub_dns_zone": module.params['refresh_recreate_sub_dns_zone']
        }
        result = requests.post(url_refresh, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})

    if module.params['action']=='export_raw':
        data = {
            "format": module.params['export_format']
        }
        result = requests.get(url_export_raw, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})

        contents.append(
            base64.b64decode(result.json()["content"])
        )

    if module.params['action']=='import_raw':
        data = {
            "format": module.params['import_format'],
            "content": module.params['import_content']
        }
        result = requests.post(url_import_raw, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})

    if module.params['action']=='clear':
        data = {
            "return_all_records": True,
            "changes": [
                {
                    "clear": {}
                }
            ]
        }
        result = requests.patch(url_clear_records, json.dumps(data), headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})

    if module.params['action']=='delete':
        result = requests.delete(url, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})

    if module.params['action']=='list_records':
        result = requests.get(url_get_records, headers=headers, verify=module.params['verify_certs'])
        if result.status_code != 200:
            # if error
            module.fail_json(msg='Your request failed', meta= {"status": result.status_code, "data": result.json()})
        else:
            dns_zones = result.json()['records']
            for z in range(len(dns_zones)):
                dns_zone = {
                    "name":dns_zones[z]['name'],
                    "ttl":dns_zones[z]['ttl'],
                    "type":dns_zones[z]['type'],
                    "data":dns_zones[z]['data'],
                    "comment":dns_zones[z]['comment'],
                }
                
                if dns_zone['type'] == 'MX':
                    dns_zone['priority'] = dns_zones[z]['priority']

                contents.append(
                    dns_zone
                )

    module.exit_json(meta= {"status": result.status_code}, dns_zone=module.params['dns_zone'], contents=contents)

def main():
    run_module()

if __name__ == '__main__':
    main()