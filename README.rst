===========================
Freezer - Horizon Dashboard
===========================

freezer-web-ui is a horizon plugin based in django aimed at providing an interaction
with freezer

* Release management: https://launchpad.net/freezer
* Blueprints and feature specifications: https://blueprints.launchpad.net/freezer
* Issue tracking: https://bugs.launchpad.net/freezer

Requirements
============

Freezer Freezer Dashboard requires a freezer API client to be installed in the same environment as horizon::

    git clone https://github.com/openstack/freezer
    cd freezer
    python setup.py install (is important that freezer is installed from source and not with pip and
                             is installed on horizon virtual environment)

Freezer Dashboard requires a freezer API endpoint which you can install following this steps::

    https://github.com/openstack/freezer-api/blob/master/README.rst

API registration
================

Register freezer api endpoint::

    https://github.com/openstack/freezer-api/blob/master/README.rst#3-api-registration

If keystone service-create and endpoint-create are not available you can set as a fallback the following on::

    # vim /opt/stack/horizon/openstack_dashboard/local/local_settings.py

    # add FREEZER_API_URL = http://<api_url>:<port>


Dev Installation
================

In the installation procedure we'll assume your main Horizon dashboard
directory is /opt/stack/horizon/openstack_dashboard/dashboards/.


To install freezer dashboard for development you need to do the following::

    # git clone https://github.com/openstack/freezer-web-ui

    # cd freezer-web-ui

    # cp freezer-web-ui/disaster_recovery/enabled/_5050_freezer.py  /opt/stack/horizon/openstack_dashboard/enabled/_5050_freezer.py

    # to disable the panel just copy the following file

    # cp freezer-web-ui/disaster_recovery/enabled/_7050_freezer.py  /opt/stack/horizon/openstack_dashboard/enabled/_7050_freezer.py

    # cd /opt/stack/horizon/

    # pip install -r requirements.txt

    # make sure freezer is installed from source as detailed in the first step

    # ./run_tests.sh --runserver 0.0.0.0:8000

Production Installation
=======================

To deploy freezer dashboard in production you need to do the following::

    # git clone https://github.com/openstack/freezer-web-ui

    # cd freezer-web-ui

    # cp freezer-web-ui/disaster_recovery/enabled/_5050_freezer.py  /opt/stack/horizon/openstack_dashboard/enabled/_5050_freezer.py

    # to disable the panel just copy the following file

    # cp freezer-web-ui/disaster_recovery/enabled/_7050_freezer.py  /opt/stack/horizon/openstack_dashboard/enabled/_7050_freezer.py

    # make sure freezer is installed from source as detailed in the first step

    # restart apache2 service


A new tab called "Disaster Recovery" will appear on your panels.


Tox
===

1. Run tox::

    tox -v


Development under proxy
_______________________

If you are developing or deploying under proxies remember to set no_proxies for::

    freezer-api endpoint
    keystone endpoint
