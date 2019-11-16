This directory contains the Freezer Web UI DevStack plugin.

To configure the Freezer Web UI with DevStack, you will need to
enable this plugin by adding one line to the [[local|localrc]]
section of your local.conf file.

To enable the plugin, add a line of the form::

    enable_plugin freezer-web-ui <GITURL> [GITREF]

where::

    <GITURL> is the URL of a freezer-web-ui repository
    [GITREF] is an optional git ref (branch/ref/tag).  The default is master.

For example::

    enable_plugin freezer-web-ui https://github.com/openstack/freezer-web-ui master

This is a sample ``local.conf`` file for freezer developer::

    [[local|localrc]]
    ADMIN_PASSWORD=stack
    DATABASE_PASSWORD=stack
    RABBIT_PASSWORD=stack
    SERVICE_PASSWORD=$ADMIN_PASSWORD

    DEST=/opt/stack
    LOGFILE=$DEST/logs/stack.sh.log

    # only install keystone/horizon/swift in devstack
    # disable_all_services
    # enable_service key mysql s-proxy s-object s-container s-account horizon

    enable_plugin freezer http://git.openstack.org/openstack/freezer master
    enable_plugin freezer-api http://git.openstack.org/openstack/freezer-api.git master
    enable_plugin freezer-tempest-plugin http://git.openstack.org/openstack/freezer-tempest-plugin.git master
    enable_plugin freezer-web-ui http://git.openstack.org/openstack/freezer-web-ui.git master

    export FREEZER_BACKEND='sqlalchemy'

For more information, see:
 https://docs.openstack.org/devstack/latest/index.html
