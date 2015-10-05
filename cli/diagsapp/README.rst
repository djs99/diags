===============================
cinderdiags
===============================

HP Storage OpenStack Cinder Diagnostic CLI

* Free software: Apache license

Overview
---------

This CLI tool can be used to validate a user cinder.conf file and also
to verify software installed on Cinder and Nova nodes.

Requirements
------------

cliff
cliff-tab
hp3parclient

Installation instructions
-------------------------

pip install configdiags

A cli.conf must exist and should contain the following format::

    [EXAMPLE-CINDER-NODE]
    service=cinder
    host_ip=15.125.224.1
    ssh_user=admin
    ssh_password=admin
    conf_source=/etc/cinder/cinder.conf

    [EXAMPLE-NOVA-NODE]
    service=nova
    host_ip=15.125.224.1
    ssh_user=admin

By default, this file needs to exist in /etc/cinderdiags/cli.conf. Alternatively, this file location
can be passed into the CLI using the -configfile option.

Starting the CLI
----------------

To view command options::

    cinderdiags --help
