===========================
Freezer - Horizon Dashboard
===========================

Requirements
============

Freezer Freezer Dashboard requires a freezer API client to be installed in the same environment as horizon::

    git clone https://github.com/stackforge/freezer
    cd freezer
    python setup.py install (is important that freezer is installed from source and not with pip)

Freezer Dashboard requires a freezer API endpoint which you can install following this steps::

    https://github.com/stackforge/freezer-api/blob/master/README.rst

API registration
================

Register freezer api endpoint::

    https://github.com/stackforge/freezer-api/blob/master/README.rst#3-api-registration

If keystone service-create and endpoint-create are not available you can set as a fallback the following on::

    # vim /opt/stack/horizon/openstack_dashboard/local/local_settings.py

    # add FREEZER_API_URL = http://<api_url>:<port>


Dev Installation
================

In the installation procedure we'll assume your main Horizon dashboard
directory is /opt/stack/horizon/openstack_dashboard/dashboards/.


To install freezer dashboard for development you need to do the following::

    # git clone https://github.com/stackforge/freezer-web-ui

    # cd freezer-web-ui

    # cp _50_freezer.py  /opt/stack/horizon/openstack_dashboard/enabled
    
    # modify _50_freezer.py (line 9) and point the path to the freezer repo.

    # cd /opt/stack/horizon/

    # pip install -r requirements.txt

    # make sure freezer is installed from source as detailed in the first step

    # ./run_tests.sh --runserver 0.0.0.0:8000

Production Installation
=======================

To deploy freezer dashboard in production you need to do the following::

    # git clone https://github.com/stackforge/freezer-web-ui

    # cd freezer-web-ui

    # cp _50_freezer.py  /opt/stack/horizon/openstack_dashboard/enabled/

    # modify _50_freezer.py (line 9) and point the path to the freezer repo.

    # restart apache2 service


A new tab called "Disaster Recovery" will be on your panels.


Running the unit tests
======================

1. Create a virtual environment::

    virtualenv --no-site-packages -p /usr/bin/python2.7 .venv

2. Activate the virtual environment::

    . ./.venv/bin/activate

3. Install the requirements::

    pip install -r test-requirements.txt

4. Run the tests::

    python manage.py test . --settings=freezer_ui.tests.settings

Test coverage
-------------

1. Collect coverage information::

    coverage run --source='.' --omit='.venv/*' manage.py test . --settings=freezer_ui.tests.settings

2. View coverage report::

    coverage report


Tox
---

1. Run tox::

    tox -v


Development under proxy
_______________________

If you are developing or deploying under proxies remember to set no_proxies for::

    freezer-api endpoint
    keystone endpoint
