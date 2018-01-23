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

# Some helper functions to use the disaster_recovery client functionality
# from horizon.

from oslo_log import log

from django.conf import settings
from horizon.utils.memoized import memoized  # noqa
from freezerclient.v1 import client as freezer_client

from disaster_recovery import utils


LOG = log.getLogger(__name__)


@memoized
def client(request):
    """Return a freezer client object"""
    api_url = _get_service_url(request)

    # get keystone version to connect to
    ks_version = getattr(settings,
                         'OPENSTACK_API_VERSIONS', {}).get('identity', 2.0)

    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)

    credentials = {
        'token': request.user.token.id,
        'auth_url': getattr(settings, 'OPENSTACK_KEYSTONE_URL'),
        'endpoint': api_url,
        'version': ks_version,
        'cacert': cacert
    }

    if ks_version == 3:
        credentials['project_name'] = request.user.project_name
        credentials['project_id'] = request.user.project_id
        credentials['project_domain_name'] = \
            request.user.domain_name or 'Default'

    return freezer_client.Client(**credentials)


@memoized
def _get_service_url(request):
    """Get freezer api url"""
    hardcoded_url = getattr(settings, 'FREEZER_API_URL', None)
    if hardcoded_url is not None:
        LOG.warning('Using hardcoded FREEZER_API_URL:{0}'
                    .format(hardcoded_url))
        return hardcoded_url

    e_type = getattr(settings, 'OPENSTACK_ENDPOINT_TYPE', '')
    endpoint_type_priority = [e_type, ['internal', 'internalURL'], ['public',
                              'publicURL']]

    try:
        catalog = (getattr(request.user, "service_catalog", []))
        for c in catalog:
            if c['name'] == 'freezer':
                for endpoint_type in endpoint_type_priority:
                    for e in c['endpoints']:
                        if e['interface'] in endpoint_type:
                            return e['url']
        raise ValueError('Could no get FREEZER_API_URL from config'
                         ' or Keystone')
    except Exception:
        LOG.warning('Could no get FREEZER_API_URL from config or Keystone')
        raise


def get_schedule_info(context):
    """Get schedule info from context
    """
    scheduling = {}
    try:
        if context['schedule_end_date'] != '':
            utils.assign_and_remove(context, scheduling, 'schedule_end_date')
        else:
            context.pop('schedule_end_date')
    except KeyError:
        pass
    try:
        if context['schedule_interval'] != '':
            utils.assign_and_remove(context, scheduling, 'schedule_interval')
        else:
            context.pop('schedule_interval')
    except KeyError:
        pass
    try:
        if context['schedule_start_date'] != '':
            utils.assign_and_remove(context, scheduling, 'schedule_start_date')
        else:
            context.pop('schedule_start_date')
    except KeyError:
        pass
    return scheduling


class Job(object):

    def __init__(self, request):
        self.request = request
        self.client = client(request)

    def list(self, json=False, limit=500, offset=0, search=None):
        if search:
            search = {"match": [{"_all": search}, ], }

        jobs = self.client.jobs.list_all(limit=limit,
                                         offset=offset,
                                         search=search)
        if json:
            return jobs

        return [utils.JobObject(
            job.get('job_id'),
            job.get('description'),
            job.get('job_schedule', {}).get('result'),
            job.get('job_schedule', {}).get('status'),
            job.get('client_id')
        ) for job in jobs]

    def get(self, job_id, json=False):
        job = self.client.jobs.get(job_id)

        if json:
            return job

        return utils.JobObject(
            job.get('job_id'),
            job.get('description'),
            job.get('job_schedule', {}).get('result'),
            job.get('job_schedule', {}).get('event'),
            job.get('client_id'))

    def create(self, job):
        return self._build(job)

    def update(self, job_id, job):
        scheduling = get_schedule_info(job)
        job.pop('job_actions', [])
        job.pop('clients', None)
        job.pop('actions', None)
        job.pop('job_id')
        job['job_schedule'] = scheduling
        return self.client.jobs.update(job_id, job)

    def update_actions(self, job_id, action_ids):
        ids = utils.get_action_ids(action_ids)
        job = self.get(job_id, json=True)
        job.pop('job_actions', None)
        actions = self._get_actions_in_job(ids)
        job['job_actions'] = actions
        return self.client.jobs.update(job_id, job)

    def delete(self, job_id):
        return self.client.jobs.delete(job_id)

    def actions(self, job_id, api=False):
        job = self.get(job_id, json=True)

        if not job:
            return []

        if api:
            return job.get('job_actions', [])

        return [utils.ActionObject(
            action_id=a.get('action_id'),
            action=a.get('freezer_action', {}).get('action'),
            backup_name=a.get('freezer_action', {}).get('backup_name'),
            job_id=job_id
        ) for a in job.get('job_actions')]

    def delete_action(self, ids):
        action_id, job_id = ids.split('===')
        job = self.get(job_id, json=True)
        for action in job['job_actions']:
            if action.get('action_id') == action_id:
                job.get('job_actions').remove(action)
        return self.client.jobs.update(job_id, job)

    def clone(self, job_id):
        job = self.get(job_id, json=True)
        job['description'] = '{0}_clone'.format(job['description'])
        job.pop('job_id', None)
        job.pop('_version', None)
        job_id = self.client.jobs.create(job)
        return self.stop(job_id)

    def stop(self, job_id):
        return self.client.jobs.stop_job(job_id)

    def start(self, job_id):
        return self.client.jobs.start_job(job_id)

    def _build(self, job):
        action_ids = utils.get_action_ids(job.pop('actions'))
        job = utils.create_dict(**job)
        clients = job.pop('clients', [])
        scheduling = {}
        new_job = {}
        utils.assign_and_remove(job, scheduling, 'schedule_start_date')
        utils.assign_and_remove(job, scheduling, 'schedule_interval')
        utils.assign_and_remove(job, scheduling, 'schedule_end_date')

        actions = self._get_actions_in_job(action_ids)

        new_job['description'] = job.get('description')
        new_job['job_actions'] = actions
        new_job['job_schedule'] = scheduling

        for client_id in clients:

            search = client_id
            client = Client(self.request).list(search=search)

            new_job['client_id'] = client[0].id
            job_id = self.client.jobs.create(new_job)
            self.stop(job_id)
        return True

    def _get_actions_in_job(self, action_ids):
        actions_in_job = []
        for action_id in action_ids:
            action = Action(self.request).get(action_id, json=True)
            actions_in_job.append(action)
        return actions_in_job


class Session(object):

    def __init__(self, request):
        self.request = request
        self.client = client(request)

    def list(self, json=False, limit=500, offset=0, search=None):
        if search:
            search = {"match": [{"_all": search}, ], }

        sessions = self.client.sessions.list_all(limit=limit,
                                                 offset=offset,
                                                 search=search)

        if json:
            return sessions

        return [utils.SessionObject(
            session.get('session_id'),
            session.get('description'),
            session.get('status'),
            session.get('jobs'),
            session.get('schedule', {}).get('schedule_start_date'),
            session.get('schedule', {}).get('schedule_interval'),
            session.get('schedule', {}).get('schedule_end_date')
        ) for session in sessions]

    def get(self, session_id, json=False):
        session = self.client.sessions.get(session_id)

        if json:
            return session

        return utils.SessionObject(
            session.get('session_id'),
            session.get('description'),
            session.get('status'),
            session.get('jobs'),
            session.get('schedule', {}).get('schedule_start_date'),
            session.get('schedule', {}).get('schedule_interval'),
            session.get('schedule', {}).get('schedule_end_date'))

    def create(self, session):
        return self._build(session)

    def update(self, session, session_id):
        new_session = {'schedule': get_schedule_info(session),
                       'description': session.pop('description')}
        return self.client.sessions.update(session_id, new_session)

    def delete(self, session_id):
        return self.client.sessions.delete(session_id)

    def remove_job(self, session_id, job_id):
        try:
            # even if the job is removed from the session the api returns an
            # error.
            return self.client.sessions.remove_job(session_id, job_id)
        except Exception:
            pass

    def add_job(self, session_id, job_id):
        return self.client.sessions.add_job(session_id, job_id)

    def jobs(self, session_id):
        session = self.get(session_id, json=True)
        jobs = []

        if session is None:
            return jobs

        try:
            jobs = [utils.JobsInSessionObject(k,
                                              session_id,
                                              v['client_id'],
                                              v['result'])
                    for k, v in session['jobs'].iteritems()]
        except AttributeError as error:
            LOG.error(error.message)
        return jobs

    def _build(self, session):
        session = utils.create_dict(**session)
        scheduling = {}
        utils.assign_and_remove(session, scheduling, 'schedule_start_date')
        utils.assign_and_remove(session, scheduling, 'schedule_interval')
        utils.assign_and_remove(session, scheduling, 'schedule_end_date')
        session['jobs'] = {}
        session['schedule'] = scheduling
        return self.client.sessions.create(session)


class Action(object):

    def __init__(self, request):
        self.request = request
        self.client = client(request)

    def list(self, json=False, limit=500, offset=0, search=None):
        if search:
            search = {"match": [{"_all": search}, ], }

        actions = self.client.actions.list(limit=limit,
                                           offset=offset,
                                           search=search)

        if json:
            return actions

        return [utils.ActionObjectDetail(
            action.get('action_id'),
            action['freezer_action'].get('action'),
            action['freezer_action'].get('backup_name'),
            action['freezer_action'].get('path_to_backup') or
            action['freezer_action'].get('restore_abs_path'),
            action['freezer_action'].get('storage'),
            mode=action['freezer_action'].get('mode')
        ) for action in actions]

    def get(self, job_id, json=False):

        action = self.client.actions.get(job_id)

        if json:
            return action

        return utils.ActionObjectDetail(
            action.get('action_id'),
            action['freezer_action'].get('action'),
            action['freezer_action'].get('backup_name'),
            action['freezer_action'].get('path_to_backup'),
            action['freezer_action'].get('storage'))

    def create(self, action):
        return self._build(action)

    def update(self, action, action_id):
        updated_action = {}
        updated_action['freezer_action'] = utils.create_dict(**action)
        try:
            if action['mandatory'] != '':
                updated_action['mandatory'] = action['mandatory']
        except KeyError:
            pass

        try:
            if action['max_retries'] != '':
                updated_action['max_retries'] = action['max_retries']
        except KeyError:
            pass

        try:
            if action['max_retries_interval'] != '':
                updated_action['max_retries_interval'] =\
                    action['max_retries_interval']
        except KeyError:
            pass
        return self.client.actions.update(action_id, updated_action)

    def delete(self, action_id):
        return self.client.actions.delete(action_id)

    def _build(self, action):
        """Get a flat action dict and convert it to a freezer action format
        """
        action_rules = {}

        utils.assign_and_remove(action, action_rules, 'max_retries')
        utils.assign_and_remove(action, action_rules, 'max_retries_interval')
        utils.assign_and_remove(action, action_rules, 'mandatory')
        action = utils.create_dict(**action)
        action.pop('action_id', None)
        # if the backup name has spaces the tar metadata file cannot be found
        # so we replace " " for "_"
        backup_name = action.pop('backup_name', None)
        action['backup_name'] = backup_name.replace(' ', '_')
        action = {'freezer_action': action}
        action.update(action_rules)
        return self.client.actions.create(action)


class Client(object):

    def __init__(self, request):
        self.request = request
        self.client = client(request)

    def list(self, json=False, limit=500, offset=0, search=None):
        if search:
            search = {"match": [{"_all": search}, ], }

        clients = self.client.clients.list(limit=limit,
                                           offset=offset,
                                           search=search)

        if json:
            return clients

        return [utils.ClientObject(
            c.get('client', {}).get('hostname'),
            c.get('client', {}).get('client_id'),
            c.get('client', {}).get('uuid')
        ) for c in clients]

    def get(self, client_id, json=False):
        c = self.client.clients.get(client_id)

        if json:
            return c

        return utils.ClientObject(
            c.get('client', {}).get('hostname'),
            c.get('client', {}).get('client_id'),
            c.get('uuid'))

    def delete(self, client_id):
        return self.client.clients.delete(client_id)


class Backup(object):

    def __init__(self, request):
        self.request = request
        self.client = client(request)

    def list(self, json=False, limit=500, offset=0, search={}):
        if search:
            search = {"match": [{"_all": search}, ], }

        backups = self.client.backups.list(limit=limit,
                                           offset=offset,
                                           search=search)

        if json:
            return backups

        return [utils.BackupObject(
            backup_id=b.get('backup_id'),
            action=b.get('backup_metadata', {}).get('action'),
            time_stamp=b.get('backup_metadata', {}).get('time_stamp'),
            backup_name=b.get('backup_metadata', {}).get('backup_name'),
            backup_media=b.get('backup_metadata', {}).get('backup_media'),
            path_to_backup=b.get('backup_metadata', {}).get('path_to_backup'),
            hostname=b.get('backup_metadata', {}).get('hostname'),
            container=b.get('backup_metadata', {}).get('container'),
            level=b.get('backup_metadata', {}).get('level'),
            curr_backup_level=b.get('backup_metadata', {}).get(
                'curr_backup_level'),
            encrypted=b.get('backup_metadata', {}).get('encrypted'),
            total_broken_links=b.get('backup_metadata', {}).get(
                'total_broken_links'),
            excluded_files=b.get('backup_metadata', {}).get('excluded_files'),
            storage=b.get('backup_metadata', {}).get('storage'),
            ssh_host=b.get('backup_metadata', {}).get('ssh_host'),
            ssh_key=b.get('backup_metadata', {}).get('ssh_key'),
            ssh_username=b.get('backup_metadata', {}).get('ssh_username'),
            ssh_port=b.get('backup_metadata', {}).get('ssh_port'),
            mode=b.get('backup_metadata', {}).get('ssh_mode'),
        ) for b in backups]

    def get(self, backup_id, json=False):

        search = {"match": [{"backup_id": backup_id}, ], }

        b = self.client.backups.list(limit=1, search=search)
        b = b[0]

        if json:
            return b

        return utils.BackupObject(
            backup_id=b.get('backup_id'),
            action=b.get('backup_metadata', {}).get('action'),
            time_stamp=b.get('backup_metadata', {}).get('time_stamp'),
            backup_name=b.get('backup_metadata', {}).get('backup_name'),
            backup_media=b.get('backup_metadata', {}).get('backup_media'),
            path_to_backup=b.get('backup_metadata', {}).get('path_to_backup'),
            hostname=b.get('backup_metadata', {}).get('hostname'),
            container=b.get('backup_metadata', {}).get('container'),
            level=b.get('backup_metadata', {}).get('level'),
            curr_backup_level=b.get('backup_metadata', {}).get(
                'curr_backup_level'),
            encrypted=b.get('backup_metadata', {}).get('encrypted'),
            total_broken_links=b.get('backup_metadata', {}).get(
                'total_broken_links'),
            excluded_files=b.get('backup_metadata', {}).get('excluded_files'),
            storage=b.get('backup_metadata', {}).get('storage'),
            ssh_host=b.get('backup_metadata', {}).get('ssh_host'),
            ssh_key=b.get('backup_metadata', {}).get('ssh_key'),
            ssh_username=b.get('backup_metadata', {}).get('ssh_username'),
            ssh_port=b.get('backup_metadata', {}).get('ssh_port'),
            mode=b.get('backup_metadata', {}).get('ssh_mode'),
        )

    def restore(self, data):
        backup = self.get(data['backup_id'])
        client_id = data['client']
        name = "Restore {0} for {1}".format(backup.backup_name, client_id)

        iso_date = utils.timestamp_to_iso(backup.time_stamp)

        action = {
            'action': 'restore',
            'backup_name': backup.backup_name,
            'restore_abs_path': data['path'],
            'container': backup.container,
            'restore_from_host': backup.hostname,
            'storage': backup.storage,
            'restore_from_date': iso_date
        }

        if backup.storage == 'ssh':
            action['ssh_host'] = backup.ssh_host
            action['ssh_key'] = backup.ssh_key
            action['ssh_username'] = backup.ssh_username
            action['ssh_port'] = backup.ssh_port

        action_id = Action(self.request).create(action)

        job = {
            'job_actions': [{
                'action_id': action_id,
                'freezer_action': action
            }],
            'client_id': client_id,
            'description': name,
            'job_schedule': {}
        }
        job_id = self.client.jobs.create(job)
        return Job(self.request).start(job_id)
