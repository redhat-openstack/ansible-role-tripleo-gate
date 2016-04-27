ansible-role-tripleo-gate
=========================

An Ansible role for generating custom RPMSs from upstream Gerrit changes in the
TripleO project using DLRN. This repo then can be injected in the tested
environment, a repo file created and a yum update should start using the built
RPMs.

Requirements
------------

* [DLRN](https://github.com/openstack-packages/DLRN)

Role Variables
--------------

* `artg_dlrn_repo_url` -- the URL of the DLRN repository
* `artg_rdoinfo_repo_url` -- the URL of the rdoinfo repository that contains
  the project definitions for DLRN
* `artg_compressed_gating_repo` -- a full path to a compressed repository that contains all the generated rpms

The role also depends on these environment variables, that are set when the
[Gerrit Trigger plugin](https://wiki.jenkins-ci.org/display/JENKINS/Gerrit+Trigger)
is being used:

* `GERRIT_HOST` -- the hostname of the Gerrit server
* `GERRIT_PROJECT` -- the full project name of the change
* `GERRIT_REFSPEC` -- refspec of the project, can be found out by clicking on
  the "Download" link in the Gerrit interface, starts with `refs/...`

Example Playbook
----------------

```yaml
---
- name: Build custom RPMs
  hosts: virthost
  roles:
    - ansible-role-tripleo-gate
```

License
-------

Apache

Author Information
------------------

RDO-CI Team
