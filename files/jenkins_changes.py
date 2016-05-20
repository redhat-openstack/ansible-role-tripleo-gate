#!/usr/bin/env python

'''
Parse the Gerrit commit message and identify the cross repo depenency changes
for a specific Gerrit change.

The expected format in the commit message is:

Depends-On: <change-id>[@<gerrit-instance-shorthand>]

Where <change-id> is the gerrit Change-Id of the dependent change,
<gerrit-instance> should be a part of a hostname in ALLOWED_HOSTS.
'''

import json
import logging
import re
import sys

import requests

# we ignore any other host reference
ALLOWED_HOSTS = ['review.openstack.org',
                 'review.gerrithub.io']


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
                    if hostname.find(target) != -1:
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
    return deps


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) == 3:
        print resolve_dep([[sys.argv[1], sys.argv[2], None]])
    elif len(sys.argv) == 4:
        print resolve_dep([[sys.argv[1], sys.argv[2], sys.argv[3]]])
    else:
        print []
