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

* `local_working_dir` -- the directory where tripleo-quickstart is located
* `artg_mode` -- either `dlrn` (the default, gating upstream tripleo packages)
   or `roles` (gating ansible-role-tripleo repos like this one)
* `artg_dlrn_repo_url` -- the URL of the DLRN repository
* `artg_rdoinfo_repo_url` -- the URL of the rdoinfo repository that contains
  the project definitions for DLRN
* `artg_compressed_gating_repo` -- a full path to a compressed repository that
  contains all the generated rpms
* `artg_change_list` -- a list of changes to gate. Only needed when not running
  in Zuul or Gerrit (see below). The format is:
* `artg_requirements` -- used in roles mode, the requirements file to use for
  replacing the gated roles
* `artg_skipped_projects` -- a list of projects that are not going to be gated.
  This is useful if the project is directly checked out by the gate job as this
  retains "Depends-On" functionality for the rest of the projects. Also useful
  to skip projects that DLRN cannot build.

```yaml
artg_change_list:
    - host: "review.openstack.org"
      project: "openstack/tripleo-heat-templates"
      branch: "master"
      refspec: "refs/changes/1/123456/1"
      path: "/workspace/repos/tht/" # for local changes only
    - host: ...
```

Gating with Zuul or Jenkins
---------------------------

The role can also work with Zuul and Jenkins based gating jobs.

In case of Zuul, the role uses `ZUUL_HOST` and `ZUUL_CHANGES` vars to parse the
full set of dependent changes that were previously
[resolved by Zuul](http://docs.openstack.org/infra/zuul/gating.html#cross-repository-dependencies).

If we're running in a Jenkins environment with the
[Gerrit Trigger plugin](https://wiki.jenkins-ci.org/display/JENKINS/Gerrit+Trigger),
`GERRIT_HOST`, `GERRIT_CHANGE_ID`, `GERRIT_BRANCH` and
`GERRIT_PATCHSET_REVISION` are used to detect the gated change. The role then
searches for "Depends-On:" lines in the commit message (and recursively in the
commit messages of the dependent changes) and adds all of them to the gating
list. This happens through Gerrit server's public REST API.

Gating Local Changes
--------------------

The role is able to work with changes from a local copy of a repo. In this case
project name and branches in changes list are still mandatory, as they cannot be
desumed by the local repo, but path field is used instead of the refspec, that contains
the path to the top-level dir of the repo that should be gated.
The branch parameters still refers to the upstream branch, not the local repo branch. Local
branch needed to be gated should be manually checked out before deploying.
A `LOCAL_CHANGES` environment variables can be used, and the format is the same as
the `ZUUL_CHANGES` variable, with again the exception of specifying the path instead of
the refspec.

Example Playbook
----------------

```yaml
---
- name: Build custom RPMs
  hosts: virthost
  roles:
    - tripleo-gate
```

License
-------

Apache

Author Information
------------------

RDO-CI Team
