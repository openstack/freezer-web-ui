===========================
Freezer - Horizon Dashboard
===========================

freezer-web-ui is a horizon plugin based in django aimed at providing an interaction
with freezer.

* Issue tracking and feature specifications: https://launchpad.net/freezer

Requirements
============

Before start, please install git and pip in your Operation System.
If your use Ubuntu:

    apt install git python3-pip

If your use RHEL/CentOS:

    dnf install git python3-pip

Freezer Dashboard requires a freezer API client to be installed in the same
environment as Horizon:

    git clone https://opendev.org/openstack/python-freezerclient
    cd python-freezerclient
    python3 -m pip install .

Freezer Dashboard requires a freezer API endpoint which you can install
following this steps:

    `https://opendev.org/openstack/freezer-api
    <https://opendev.org/openstack/freezer-api>`_

API registration
================

If keystone service-create and endpoint-create are not available you can
set as a fallback the following on:

    vim /etc/horizon/openstack_dashboard/local/local_settings.py

    add FREEZER_API_URL = http://<api_url>:<port>

Installation
============

In the installation procedure we'll assume your main Horizon dashboard
directory is /etc/horizon/openstack_dashboard/dashboards/.

To install freezer dashboard for development you need to do the following:

    git clone https://opendev.org/openstack/freezer-web-ui
    cd freezer-web-ui
    cp freezer-web-ui/freezer_ui/enabled/_5050_freezer.py  /etc/horizon/openstack_dashboard/enabled/_5050_freezer.py

To disable the panel set `DISABLED = True` in /etc/horizon/openstack_dashboard/enabled/_5050_freezer.py

    cd /etc/horizon/
    python3 -m pip install -r requirements.txt

Make sure freezer is installed from source as detailed in the first step

    ./run_tests.sh --runserver 0.0.0.0:8000

A new tab called "Disaster Recovery" will appear on your panels.

Tox
===

Run tox:

    tox -v

Development under proxy
_______________________

If you are developing or deploying under proxies remember to set no_proxies for:

    freezer-api endpoint
    keystone endpoint

Source Code
===========

The project source code repository is located at:
https://opendev.org/openstack/freezer-web-ui/
