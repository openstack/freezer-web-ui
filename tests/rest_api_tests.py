# (c) Copyright 2014,2015 Hewlett-Packard Development Company, L.P.
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

import json
from mock import patch

from django.core.urlresolvers import reverse
import openstack_dashboard.test.helpers as helpers


@patch('freezer.apiclient.client')
class TestRestApi(helpers.TestCase):
    CLIENT_1 = {u'client': {u'hostname': u'jonas',
                            u'description': u'client description',
                            u'client_id': u'test-client',
                            u'config_ids': [u'fdaf2fwf2', u'fdsfdsfdsfs']},
                u'user_id': u'13c2b15308c04cdf86989ee7335eb504'}

    JSON_PREFIX = ')]}\',\n'

    def test_clients_get(self, client_mock):
        client_mock.Client().registration.list.return_value = [self.CLIENT_1]
        url = reverse("horizon:freezer_ui:api_clients")

        res = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res['content-type'])
        self.assertEqual(self.JSON_PREFIX + json.dumps([self.CLIENT_1]),
                         res.content)
        # there is no get ALL api at the moment, so we just fetch a big number
        client_mock.Client().registration.list.assert_called_once_with(
            limit=9999)
