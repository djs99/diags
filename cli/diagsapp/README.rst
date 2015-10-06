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

Running the CLI
---------------

To view command options::

    cinderdiags --help

Example commands::

    cinderdiags help options-check
    cinderdiags options-check -v
    cinderdiags help software-check
    cinderdiags software-check --log-file tmp.txt
    cinderdiags software-check -software hplefthandclient --package-min-version 1.0.2

Configuration File
------------------

Before executing cinderdiags, the user must create a cli.conf configuration file. The following
example shows the required fields and format::

    [MY-CINDER-NODE]                         # required section name - must be unique
    service=cinder                           # service type = cinder or nova
    host_ip=15.125.224.1                     # host system where service is running
    ssh_user=admin                           # SSH credentials for host system
    ssh_password=admin
    conf_source=/etc/cinder/cinder.conf      # if cinder node, location of cinder config file

    [MY-NOVA-NODE]
    service=nova
    host_ip=15.125.224.1
    ssh_user=admin

By default, this file needs to exist in the /etc/cinderdiags/ directory. Alternatively, this file
path can be passed into the CLI command using the argument '-conf-file <file path>'.
