#!/usr/bin/env python

DOCUMENTATION = '''
---
module: jenkins_deps
version_added: "2.0"
short_description: Parses the Gerrit commit message and identifies cross repo depenency changes
description:
    - Parses the Gerrit commit message and identifies cross repo depenency changes.
      The expected format in the commit message is:
      Depends-On: <change-id>[@<gerrit-instance-shorthand>]
      Where <change-id> is the gerrit Change-Id of the dependent change,
      <gerrit-instance> should be a part of a hostname in ALLOWED_HOSTS.
options:
  host:
    description:
      - The hostname of the Gerrit server
    required: True
  change_id:
    description:
      - The change-id of the Gerrit change, starting with I...
    required: True
  patchset_rev:
    description:
      - The sha hash of the patchset to be tested. Latest will be used if omitted.
    required: False
'''

EXAMPLES = '''
- jenkins-deps:
    host: review.openstack.org
    change_id: I387b6bfd763d2d86cad68a3119b0edd0caa237b0
    patchset_rev: d18f21853e2f3be7382a20d0f42232ff3a78b348
'''

import json
import logging
import re
import sys

import requests

# we ignore any other host reference
ALLOWED_HOSTS = ['review.openstack.org',
                 'review.gerrithub.io',
                 'review.rdoproject.org']


def parse_commit_msg(current_host, msg):
    '''Look for dependency links in the commit message.'''
    tags = []
    for line in iter(msg.splitlines()):
        # note: this regexp takes care of sanitizing the input
        tag = re.search(r'Depends-On: *(I[0-9a-f]+)@?([0-9a-z\.\-:]*)',
                        line, re.IGNORECASE)
        if tag:
            change_id = tag.group(1)
            target = tag.group(2)
            if target == '':
                host = current_host
            else:
                # match a shorthand hostname for our allowed list
                for hostname in ALLOWED_HOSTS:
                    if target in hostname:
                        host = hostname
                        break
                else:
                    logging.warning('Cannot resolve "%s" to a host from the '
                                'ALLOWED HOSTS list', target)
                    continue
            tags.append([host, change_id, None])
            logging.debug('Valid tag found. Change-Id: %s, host: %s',
                          change_id, host)
    return tags


def resolve_dep(to_resolve):
    '''
    Resolve the dependencies in the target commits until there are no more
    dependent changes. The to_resolve list is expected to have a list of of the
    following items: [hostname, change_id, patchset_id or None].

    The function avoids circular dependencies and only allows one change per
    project to be added to the output list.

    Returns a list of dictionaries with the dependent changes.
    '''
    resolved_ids = []
    deps = []
    while len(to_resolve) > 0:
        current_host, current_id, current_rev = to_resolve.pop()
        # avoid circular dependencies
        if current_id in resolved_ids:
            continue
        # NOTE: this won't work if there are multiple changes on a Gerrit
        # server with the same Change-Id on different branches.
        # If this becomes important, we need to first search for the
        # Change-IDs then select the change with the proper branch.
        url = ''.join(['https://', current_host, '/changes/', current_id,
                       '?o=ALL_REVISIONS&o=ALL_COMMITS'])
        try:
            req = requests.get(url)
            req.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.warning('Failed to fetch change details from %s', url)
            continue
        data = json.loads(req.text[4:])
        resolved_ids.append(data['change_id'])

        if current_rev is None:
            current_rev = data['current_revision']
        if current_rev not in data['revisions']:
            logging.warning('Could not find revision %s for change %s on %s',
                            current_rev, current_id, current_host)
            continue

        # allow only one of each project as a dependency
        if not any(d['project'] == data['project'] for d in deps):
            deps.append({'host': current_host,
                         'project': str(data['project']),
                         'branch': str(data['branch']),
                         'refspec': str(data['revisions'][current_rev]['ref'])})
        else:
            logging.warning('Skipping %s on %s because project "%s" is '
                            'already a dependency',
                            current_id, current_host, data['project'])
            continue
        message = data['revisions'][current_rev]['commit']['message']
        to_resolve.extend(parse_commit_msg(current_host, message))
    if len(deps) == 0:
        return {'failed': True, 'msg': 'Failed to resolve even the root change'}
    else:
        return {'changed': True, 'change_list': deps}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            change_id=dict(required=True),
            patchset_rev=dict(required=False, default=None)
        )
    )
    result = resolve_dep([[module.params['host'],
                          module.params['change_id'],
                          module.params['patchset_rev']]])
    module.exit_json(**result)


# see http://docs.ansible.com/developing_modules.html#common-module-boilerplate
from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()
