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

For more information, see:
 https://docs.openstack.org/devstack/latest/plugins.html
