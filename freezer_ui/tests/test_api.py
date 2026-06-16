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

    @mock.patch('freezer_ui.api.api.Backup')
    def test_backup_detail_view_get(self, mock_backup_class):
        mock_backup_inst = mock_backup_class.return_value
        mock_backup_inst.get.return_value = {
            'backup_id': 'backup-123',
            'backup_metadata': {
                'backup_name': 'test-backup-name',
                'action': 'backup',
                'storage': 'swift',
            }
        }

        url = reverse('horizon:project:freezer-backups:detail',
                      kwargs={'backup_id': 'backup-123'})
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-backups/detail.html')
        self.assertContains(res, 'test-backup-name')
        mock_backup_inst.get.assert_called_once_with('backup-123', json=True)

    @mock.patch('freezer_ui.api.api.Action')
    def test_action_detail_view_get(self, mock_action_class):
        mock_action_inst = mock_action_class.return_value
        mock_action_inst.get.return_value = {
            'action_id': 'action-123',
            'freezer_action': {
                'backup_name': 'test-action-backup-name',
                'action': 'backup',
            }
        }

        url = reverse('horizon:project:freezer-actions:action',
                      kwargs={'action_id': 'action-123'})
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-actions/detail.html')
        self.assertContains(res, 'test-action-backup-name')
        mock_action_inst.get.assert_called_once_with('action-123', json=True)

    @mock.patch('freezer_ui.api.api.Client')
    def test_client_detail_view_get(self, mock_client_class):
        mock_client_inst = mock_client_class.return_value
        mock_client_inst.get.return_value = {
            'client': {
                'client_id': 'client-123',
                'hostname': 'test-client-hostname',
            }
        }

        url = reverse('horizon:project:freezer-clients:client',
                      kwargs={'client_id': 'client-123'})
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-clients/detail.html')
        self.assertContains(res, 'test-client-hostname')
        mock_client_inst.get.assert_called_once_with('client-123', json=True)

    @mock.patch('freezer_ui.api.api.client')
    def test_job_to_object(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        job_data = {
            'job_id': 'job-123',
            'description': 'test-job-desc',
            'job_schedule': {'result': 'success', 'event': 'stop'},
            'client_id': 'client-1'
        }
        api_job = freezer_api.Job(None)
        obj = api_job.to_object(job_data)
        self.assertEqual(obj.job_id, 'job-123')
        self.assertEqual(obj.description, 'test-job-desc')
        self.assertEqual(obj.client_id, 'client-1')
        self.assertEqual(obj.result, 'success')
        self.assertEqual(obj.event, 'stop')

    @mock.patch('freezer_ui.api.api.client')
    def test_session_to_object(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        session_data = {
            'session_id': 'session-123',
            'description': 'test-session-desc',
            'status': 'active',
            'jobs': [],
            'schedule': {
                'schedule_start_date': '2026-06-16',
                'schedule_interval': 'daily',
                'schedule_end_date': '2026-06-17'
            }
        }
        api_session = freezer_api.Session(None)
        obj = api_session.to_object(session_data)
        self.assertEqual(obj.session_id, 'session-123')
        self.assertEqual(obj.description, 'test-session-desc')
        self.assertEqual(obj.status, 'active')
        self.assertEqual(obj.schedule_start_date, '2026-06-16')
        self.assertEqual(obj.schedule_interval, 'daily')
        self.assertEqual(obj.schedule_end_date, '2026-06-17')

    @mock.patch('freezer_ui.api.api.client')
    def test_action_to_object(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        action_data = {
            'action_id': 'action-123',
            'freezer_action': {
                'action': 'backup',
                'backup_name': 'test-backup-name',
                'path_to_backup': '/tmp/backup',
                'storage': 'swift',
                'mode': 'fs',
                'container': 'test-container'
            },
            'mandatory': True,
            'max_retries': 3,
            'max_retries_interval': 60
        }
        api_action = freezer_api.Action(None)
        obj = api_action.to_object(action_data)
        self.assertEqual(obj.action_id, 'action-123')
        self.assertEqual(obj.action, 'backup')
        self.assertEqual(obj.backup_name, 'test-backup-name')
        self.assertEqual(obj.path_to_backup, '/tmp/backup')
        self.assertEqual(obj.storage, 'swift')
        self.assertEqual(obj.mode, 'fs')
        self.assertEqual(obj.container, 'test-container')
        self.assertEqual(obj.mandatory, True)
        self.assertEqual(obj.max_retries, 3)
        self.assertEqual(obj.max_retries_interval, 60)

    @mock.patch('freezer_ui.api.api.client')
    def test_client_to_object(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        client_data = {
            'client': {
                'client_id': 'client-123',
                'hostname': 'test-client-hostname',
            },
            'uuid': 'uuid-123'
        }
        api_client = freezer_api.Client(None)
        obj = api_client.to_object(client_data)
        self.assertEqual(obj.client_id, 'client-123')
        self.assertEqual(obj.hostname, 'test-client-hostname')
        self.assertEqual(obj.uuid, 'uuid-123')

    @mock.patch('freezer_ui.api.api.client')
    def test_backup_to_object(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        backup_data = {
            'backup_id': 'backup-123',
            'backup_metadata': {
                'backup_name': 'test-backup-name',
                'action': 'backup',
                'storage': 'swift',
                'time_stamp': 1234567890
            }
        }
        api_backup = freezer_api.Backup(None)
        obj = api_backup.to_object(backup_data)
        self.assertEqual(obj.backup_id, 'backup-123')
        self.assertEqual(obj.backup_name, 'test-backup-name')
        self.assertEqual(obj.action, 'backup')
        self.assertEqual(obj.storage, 'swift')
        self.assertEqual(obj.time_stamp, 1234567890)
