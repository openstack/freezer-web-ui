# (c) Copyright 2014-2016 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket

import freezer_ui.enabled
from openstack_dashboard.test.settings import *  # noqa
from openstack_dashboard.test.settings import HORIZON_CONFIG
from openstack_dashboard import enabled as openstack_enabled
from openstack_dashboard.utils import settings as horizon_settings


SECRET_KEY = 'HELLA_SECRET!'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': 'test'}}


socket.setdefaulttimeout(1)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TESTSERVER = 'http://testserver'


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

OPENSTACK_ADDRESS = "localhost"
OPENSTACK_ADMIN_TOKEN = "openstack"
OPENSTACK_KEYSTONE_URL = "http://%s:5000/v2.0" % OPENSTACK_ADDRESS
OPENSTACK_KEYSTONE_ADMIN_URL = "http://%s:35357/v2.0" % OPENSTACK_ADDRESS
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "Member"
FREEZER_API_URL = "test"

# Silence logging output during tests.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler'
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
        },
        'horizon': {
            'handlers': ['null'],
            'propagate': False,
        },
        'novaclient': {
            'handlers': ['null'],
            'propagate': False,
        },
        'keystoneclient': {
            'handlers': ['null'],
            'propagate': False,
        },
        'quantum': {
            'handlers': ['null'],
            'propagate': False,
        },
        'nose.plugins.manager': {
            'handlers': ['null'],
            'propagate': False,
        }
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.humanize',
    'openstack_auth',
    'compressor',
    'horizon',
    'openstack_dashboard',
]
horizon_settings.update_dashboards([
    openstack_enabled, freezer_ui.enabled], HORIZON_CONFIG, INSTALLED_APPS)
INSTALLED_APPS = tuple(INSTALLED_APPS)
ALLOWED_HOSTS = ['*']
