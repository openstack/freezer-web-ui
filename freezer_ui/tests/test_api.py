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
from openstack_dashboard.api.rest import utils as rest_utils


class SetterProperty(object):
    def __init__(self, prop):
        self.prop = prop

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if 'json_value' in obj.__dict__:
            return obj.__dict__['json_value']
        return self.prop.__get__(obj, objtype)

    def __set__(self, obj, value):
        obj.__dict__['json_value'] = value


rest_utils.JSONResponse.json = SetterProperty(rest_utils.JSONResponse.json)


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

    @mock.patch('freezer_ui.api.api.Job')
    def test_job_detail_view_get_none_schedule(self, mock_job_class):
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.get.return_value = {
            'job_id': 'job-123',
            'description': 'test-job-desc',
            'job_schedule': None,
            'client_id': 'client-1'
        }

        url = reverse('horizon:project:freezer-jobs:detail',
                      kwargs={'job_id': 'job-123'})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

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
            'jobs': {
                'job-1': {
                    'client_id': 'client-1',
                    'result': 'success'
                }
            }
        }

        url = reverse('horizon:project:freezer-sessions:detail',
                      kwargs={'session_id': 'session-123'})
        res = self.client.get(url)
        self.assertTemplateUsed(res, 'project/freezer-sessions/detail.html')
        self.assertContains(res, 'test-session-desc')
        self.assertContains(res, 'job-1')
        self.assertContains(res, 'client-1')
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
    def test_job_to_object_none_schedule(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        job_data = {
            'job_id': 'job-123',
            'description': 'test-job-desc',
            'job_schedule': None,
            'client_id': 'client-1'
        }
        api_job = freezer_api.Job(None)
        obj = api_job.to_object(job_data)
        self.assertEqual(obj.job_id, 'job-123')
        self.assertEqual(obj.description, 'test-job-desc')
        self.assertEqual(obj.client_id, 'client-1')
        self.assertEqual(obj.result, 'pending')
        self.assertEqual(obj.event, 'stop')

    @mock.patch('freezer_ui.api.api.client')
    def test_session_to_object(self, mock_client_factory):
        import freezer_ui.api.api as freezer_api
        session_data = {
            'session_id': 'session-123',
            'description': 'test-session-desc',
            'status': 'active',
            'jobs': {},
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

    def test_delete_client_allowed(self):
        from freezer_ui.clients.tables import DeleteClient
        from freezer_ui.utils import ClientObject

        request = mock.Mock()
        request.user.project_id = 'project-123'

        action = DeleteClient()

        # Central client should NOT be allowed
        client_central = ClientObject('host1', 'id1', 'uuid1',
                                      is_central=True,
                                      project_id='project-123')
        self.assertFalse(action.allowed(request, client_central))

        # Client from mismatched project should NOT be allowed
        client_mismatched = ClientObject('host1', 'id1', 'uuid1',
                                         is_central=False,
                                         project_id='project-other')
        self.assertFalse(action.allowed(request, client_mismatched))

        # Valid client should be allowed
        client_valid = ClientObject('host1', 'id1', 'uuid1',
                                    is_central=False,
                                    project_id='project-123')
        self.assertTrue(action.allowed(request, client_valid))

    @mock.patch('freezer_ui.api.api.Action')
    @mock.patch('freezer_ui.api.api.Job')
    def test_api_actions_in_job(self, mock_job_class, mock_action_class):
        mock_action_inst = mock_action_class.return_value
        mock_job_inst = mock_job_class.return_value

        mock_action_inst.list.return_value = [
            {'action_id': 'action-1', 'freezer_action': {'action': 'backup'}},
            {'action_id': 'action-2', 'freezer_action': {'action': 'backup'}},
            {'action_id': 'action-3', 'freezer_action': {'action': 'restore'}},
        ]

        mock_job_inst.actions.return_value = [
            {'action_id': 'action-2', 'freezer_action': {'action': 'backup'}},
            {'action_id': 'action-4', 'freezer_action': {'action': 'admin'}},
        ]

        url = reverse('horizon:project:freezer-api:api_actions_in_job',
                      kwargs={'job_id': 'job-123'})
        res = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)

        import json
        data = json.loads(res.content)

        selected_ids = [a['action_id'] for a in data['selected']]
        self.assertIn('action-2', selected_ids)
        self.assertIn('action-4', selected_ids)
        self.assertEqual(len(selected_ids), 2)

        available_ids = [a['action_id'] for a in data['available']]
        self.assertIn('action-1', available_ids)
        self.assertIn('action-3', available_ids)
        self.assertNotIn('action-2', available_ids)
        self.assertEqual(len(available_ids), 2)

    @mock.patch('freezer_ui.api.api.Client')
    @mock.patch('freezer_ui.api.api.Job')
    @mock.patch('freezer_ui.api.api.Action')
    def test_actions_configuration_action_capability_filtering(
            self, mock_action, mock_job, mock_client):
        mock_action.return_value.list.return_value = [
            {
                'action_id': 'action-swift',
                'freezer_action': {
                    'action': 'backup',
                    'mode': 'fs',
                    'storage': 'swift',
                    'engine': 'tar'
                }
            },
            {
                'action_id': 'action-local',
                'freezer_action': {
                    'action': 'backup',
                    'mode': 'fs',
                    'storage': 'local',
                    'engine': 'tar'
                }
            },
            {
                'action_id': 'action-cindernative',
                'freezer_action': {
                    'action': 'backup',
                    'mode': 'cindernative',
                }
            }
        ]

        mock_job.return_value.get.return_value = {
            'job_id': 'job-123',
            'client_id': 'client-1'
        }
        mock_job.return_value.actions.return_value = []

        mock_client.return_value.get.return_value = {
            'client': {
                'client_id': 'client-1',
                'supported_actions': ['backup', 'restore'],
                'supported_modes': ['fs', 'cindernative'],
                'supported_storages': ['swift'],
                'supported_engines': ['tar']
            }
        }

        from freezer_ui.jobs.workflows.update_actions import (
            ActionsConfigurationAction)
        request = mock.Mock()
        context = {'job_id': 'job-123'}

        form_action = ActionsConfigurationAction(request, context)

        available_ids = [
            a['action_id'] for a in form_action.available_actions
        ]
        self.assertIn('action-swift', available_ids)
        self.assertIn('action-cindernative', available_ids)
        self.assertNotIn('action-local', available_ids)

    @mock.patch('freezer_ui.api.api.Client')
    def test_restore_destination_action_init(self, mock_client):
        mock_client.return_value.list.return_value = [
            mock.Mock(id='client-1', hostname='host1'),
            mock.Mock(id='client-2', hostname='host2')
        ]

        from freezer_ui.backups.workflows.restore import DestinationAction
        request = mock.Mock()
        context = {'backup_id': 'backup-123'}

        action = DestinationAction(request, context)
        self.assertEqual(len(action.available_clients), 2)

    @mock.patch('freezer_ui.api.api.Client')
    @mock.patch('freezer_ui.api.api.Job')
    @mock.patch('freezer_ui.api.api.Action')
    def test_edit_actions_view_get(self, mock_action, mock_job, mock_client):
        mock_action.return_value.list.return_value = []
        mock_job.return_value.get.return_value = mock.Mock(
            id='job-123',
            job_id='job-123',
            client_id='client-1'
        )
        mock_job.return_value.actions.return_value = []
        mock_client.return_value.get.return_value = {
            'client': {
                'client_id': 'client-1',
                'supported_actions': ['backup', 'restore'],
            }
        }
        mock_client.return_value.list.return_value = []

        url = reverse('horizon:project:freezer-jobs:edit_action',
                      kwargs={'job_id': 'job-123'})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    @mock.patch('freezer_ui.api.api.Job')
    @mock.patch('freezer_ui.api.api.Session')
    def test_attach_job_view_get(self, mock_session_class, mock_job_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.get.return_value = {
            'session_id': 'session-123',
            'jobs': {'job-1': {}}
        }
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.list.return_value = [
            mock.Mock(job_id='job-1', description='job 1'),
            mock.Mock(job_id='job-2', description='job 2'),
        ]

        url = reverse('horizon:project:freezer-sessions:attach_job',
                      kwargs={'session_id': 'session-123'})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        mock_session_inst.get.assert_called_once_with('session-123', json=True)
        mock_job_inst.list.assert_called_once()

        workflow = res.context['workflow']
        choices = dict(workflow.steps[0].action.fields['job_id'].choices)
        self.assertNotIn('job-1', choices)
        self.assertIn('job-2', choices)

    @mock.patch('freezer_ui.api.api.Session')
    def test_attach_job_workflow_handle(self, mock_session_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.add_job.return_value = {}

        from freezer_ui.sessions.workflows.attach import AttachJobWorkflow
        request = mock.Mock()
        workflow = AttachJobWorkflow(request)
        context = {
            'session_id': 'session-123',
            'job_id': 'job-2'
        }
        success = workflow.handle(request, context)
        self.assertTrue(success)
        mock_session_inst.add_job.assert_called_once_with(
            'session-123', 'job-2')

    @mock.patch('freezer_ui.api.api.Job')
    @mock.patch('freezer_ui.api.api.Session')
    def test_create_session_view_get(self, mock_session_class, mock_job_class):
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.list.return_value = [
            mock.Mock(job_id='job-1', description='job 1'),
        ]

        url = reverse('horizon:project:freezer-sessions:create')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'horizon/common/_workflow.html')
        mock_job_inst.list.assert_called_once()

        workflow = res.context['workflow']
        steps = [s.slug for s in workflow.steps]
        self.assertIn('freezer-sessions', steps)
        self.assertIn('selected_jobs', steps)

    @mock.patch('freezer_ui.api.api.Session')
    def test_create_session_workflow_handle(self, mock_session_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.create.return_value = 'session-123'
        mock_session_inst.get.return_value = {
            'session_id': 'session-123',
            'jobs': {}
        }
        mock_session_inst.add_job.return_value = {}

        from freezer_ui.sessions.workflows.create import CreateSession
        request = mock.Mock()
        workflow = CreateSession(request)
        context = {
            'session_id': '',
            'description': 'test-session',
            'interval_unit': 'days',
            'interval_value': 2,
            'schedule_start_date': '',
            'schedule_end_date': '',
            'jobs': ['job-1', 'job-2']
        }
        res = workflow.handle(request, context)
        self.assertTrue(res)
        mock_session_inst.create.assert_called_once()
        mock_session_inst.add_job.assert_has_calls([
            mock.call('session-123', 'job-1'),
            mock.call('session-123', 'job-2')
        ], any_order=True)

    @mock.patch('freezer_ui.api.api.Job')
    @mock.patch('freezer_ui.api.api.Session')
    def test_edit_session_view_get(self, mock_session_class, mock_job_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.get.return_value = {
            'session_id': 'session-123',
            'description': 'test-session-desc',
            'status': 'active',
            'jobs': {
                'job-1': {
                    'client_id': 'client-1',
                    'result': 'success'
                }
            },
            'schedule': {}
        }
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.list.return_value = [
            mock.Mock(job_id='job-1', description='job 1'),
            mock.Mock(job_id='job-2', description='job 2'),
        ]

        url = reverse('horizon:project:freezer-sessions:edit',
                      kwargs={'session_id': 'session-123'})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'horizon/common/_workflow.html')

        workflow = res.context['workflow']
        steps = [s.slug for s in workflow.steps]
        self.assertIn('freezer-sessions', steps)
        self.assertIn('selected_jobs', steps)

        step = workflow.steps[1]
        choices = dict(step.action.fields['selected_jobs_role_member'].choices)
        self.assertIn('job-1', choices)
        initial_selected = (
            step.action.fields['selected_jobs_role_member'].initial)
        self.assertEqual(initial_selected, ['job-1'])

    @mock.patch('freezer_ui.api.api.Job')
    @mock.patch('freezer_ui.api.api.Session')
    def test_manage_jobs_view_get(self, mock_session_class, mock_job_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.get.return_value = {
            'session_id': 'session-123',
            'description': 'test-session-desc',
            'status': 'active',
            'jobs': {
                'job-1': {
                    'client_id': 'client-1',
                    'result': 'success'
                }
            },
            'schedule': {}
        }
        mock_job_inst = mock_job_class.return_value
        mock_job_inst.list.return_value = [
            mock.Mock(job_id='job-1', description='job 1'),
            mock.Mock(job_id='job-2', description='job 2'),
        ]

        url = reverse('horizon:project:freezer-sessions:manage_jobs',
                      kwargs={'session_id': 'session-123'})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'horizon/common/_workflow.html')

        workflow = res.context['workflow']
        steps = [s.slug for s in workflow.steps]
        self.assertIn('selected_jobs', steps)

        step = workflow.steps[0]
        choices = dict(step.action.fields['selected_jobs_role_member'].choices)
        self.assertIn('job-1', choices)
        initial_selected = (
            step.action.fields['selected_jobs_role_member'].initial)
        self.assertEqual(initial_selected, ['job-1'])

    @mock.patch('freezer_ui.api.api.Session')
    def test_manage_jobs_workflow_handle(self, mock_session_class):
        mock_session_inst = mock_session_class.return_value
        mock_session_inst.get.return_value = {
            'session_id': 'session-123',
            'jobs': {
                'job-1': {},
                'job-2': {}
            }
        }
        mock_session_inst.add_job.return_value = {}
        mock_session_inst.remove_job.return_value = {}

        from freezer_ui.sessions.workflows.create import (
            ManageJobsWorkflow)
        request = mock.Mock()
        workflow = ManageJobsWorkflow(request)
        context = {
            'session_id': 'session-123',
            'jobs': ['job-2', 'job-3']
        }
        res = workflow.handle(request, context)
        self.assertTrue(res)
        mock_session_inst.get.assert_called_once_with('session-123', json=True)
        mock_session_inst.add_job.assert_called_once_with(
            'session-123', 'job-3')
        mock_session_inst.remove_job.assert_called_once_with(
            'session-123', 'job-1')
