# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import datetime

from openstack_dashboard.test import helpers as test

from freezer_ui.utils import datetime_to_iso_string


class UtilsTestCase(test.TestCase):

    def test_datetime_to_iso_string_with_none(self):
        self.assertEqual(datetime_to_iso_string(None), '')

    def test_datetime_to_iso_string_with_datetime(self):
        dt = datetime.datetime(2026, 6, 18, 12, 34, 56)
        self.assertEqual(datetime_to_iso_string(dt), '2026-06-18T12:34:56')
