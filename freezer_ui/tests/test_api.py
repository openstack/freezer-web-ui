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

from unittest import mock
from django.urls import reverse
from openstack_dashboard.test import helpers as test


class FreezerTestCase(test.TestCase):

    @mock.patch('freezer_ui.api.api.Job')
    def test_jobs_view_get(self, mock_job_class):
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.list.return_value = []

        url = reverse('horizon:project:freezer-jobs:index')
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-jobs/index.html')
        mock_job_inst.list.assert_called_once_with(limit=100)

    @mock.patch('freezer_ui.api.api.Job')
    def test_job_detail_view_get(self, mock_job_class):
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.get.return_value = {
            'job_id': 'job-123',
            'description': 'test-job-desc',
            'job_schedule': {'result': 'success', 'status': 'completed'},
            'client_id': 'client-1'
        }

        url = reverse('horizon:project:freezer-jobs:detail',
                      kwargs={'job_id': 'job-123'})
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-jobs/detail.html')
        self.assertContains(res, 'test-job-desc')
        mock_job_inst.get.assert_called_once_with('job-123', json=True)

    @mock.patch('freezer_ui.api.api.Session')
    def test_sessions_view_get(self, mock_session_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.list.return_value = []

        url = reverse('horizon:project:freezer-sessions:index')
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-sessions/index.html')
        mock_session_inst.list.assert_called_once_with(limit=100)

    @mock.patch('freezer_ui.api.api.Session')
    def test_session_detail_view_get(self, mock_session_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.get.return_value = {
            'session_id': 'session-123',
            'description': 'test-session-desc',
            'status': 'active',
            'jobs': []
        }

        url = reverse('horizon:project:freezer-sessions:detail',
                      kwargs={'session_id': 'session-123'})
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-sessions/detail.html')
        self.assertContains(res, 'test-session-desc')
        mock_session_inst.get.assert_called_once_with('session-123', json=True)
