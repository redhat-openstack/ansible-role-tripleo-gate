#!/usr/bin/env python

DOCUMENTATION = '''
---
module: local_deps
version_added: "2.0"
short_description: Transforms the dependent changes variable hosted locally from Zuul format into a dictionary
description:
    - Transforms the dependent changes variable hosted locally from Zuul format into a dictionary
options:
  changes:
    description:
      - The content of the LOCAL_CHANGES variable
    required: True
'''

EXAMPLES = '''
- local_deps:
    changes: "openstack/tripleo-heat-templates:master:/workspace/local/repo/tht^openstack/instack-undercloud:master:/workspace/local/repo/instack"
'''

import sys

def process(host, changes):
    """Process the changes from Zuul format"""
    output = []

    for item in changes.split("^"):
        params = item.split(":")
        output.append({"project": params[0],
                       "branch": params[1],
                       "path": params[2]})
    return {'changed': True,
            'ansible_facts': {'artg_change_list': output}}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            changes=dict(required=True, type='str')
        )
    )
    result = process(module.params['changes'])
    module.exit_json(**result)


# see http://docs.ansible.com/developing_modules.html#common-module-boilerplate
from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()
