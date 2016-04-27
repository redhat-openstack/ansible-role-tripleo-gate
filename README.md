ansible-role-tripleo-gate
=========================

An Ansible role for gating upstream repositories using
[DLRN](https://github.com/openstack-packages/DLRN).

Requirements
------------

* DLRN

Role Variables
--------------

* `artg_dlrn_repo` -- dlrn repo url
* `artg_rpm_dir` -- path where the built and tarballed rpms should be fetched

Example Playbook
----------------

```yaml
---
- name: Build gated RPMs
  hosts: virthost
  roles:
    - { role: ansible-role-tripleo-gate, tags: ['artg_build_rpms'] }

- name: Install gated RPMs
  hosts: undercloud
  roles:
    - { role: ansible-role-tripleo-gate, tags: ['artg_install_rpms'] }
```

License
-------

Apache

Author Information
------------------

RDO-CI Team
