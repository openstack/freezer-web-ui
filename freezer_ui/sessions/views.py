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

from django.urls import reverse
from django.views import generic
from horizon import tables
from horizon import workflows

import freezer_ui.api.api as freezer_api
from freezer_ui.sessions import tables as freezer_tables

from freezer_ui.sessions.workflows import attach
from freezer_ui.sessions.workflows import create
from freezer_ui.utils import shield
from freezer_ui.utils import timestamp_to_string


class SessionsView(tables.DataTableView):
    table_class = freezer_tables.SessionsTable
    template_name = "project/freezer-sessions/index.html"

    @shield('Unable to get sessions list.', redirect='freezer-sessions:index')
    def get_data(self):
        return freezer_api.Session(self.request).list(limit=100)


class DetailView(generic.TemplateView):
    template_name = 'project/freezer-sessions/detail.html'

    @shield('Unable to get session.', redirect='freezer-sessions:index')
    def get_context_data(self, **kwargs):
        session_api = freezer_api.Session(self.request)
        session = session_api.get(kwargs['session_id'], json=True)
        for key in ['time_started', 'time_ended']:
            if key in session and session[key]:
                try:
                    session[key + '_formatted'] = (
                        timestamp_to_string(session[key]))
                except Exception:
                    session[key + '_formatted'] = session[key]
        session_obj = session_api.to_object(session)
        table = freezer_tables.SessionsTable(self.request)
        actions = table.render_row_actions(session_obj)
        return {
            'session': session,
            'page_title': (session.get('session_tag') or
                           session.get('session_id')),
            'actions': actions,
            'url': reverse('horizon:project:freezer-sessions:index')
        }


class AttachToSessionWorkflow(workflows.WorkflowView):
    workflow_class = attach.AttachJobToSession

    @shield('Unable to get job', redirect='freezer-jobs:index')
    def get_object(self, *args, **kwargs):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and \
               bool(self.kwargs['job_id'])

    @shield('Unable to get job', redirect='freezer-jobs:index')
    def get_initial(self):
        initial = super(AttachToSessionWorkflow, self).get_initial()
        job = self.get_object()
        initial.update({'job_id': job.id})
        return initial


class CreateSessionWorkflow(workflows.WorkflowView):
    workflow_class = create.CreateSession

    @shield('Unable to get session', redirect='freezer-sessions:index')
    def get_object(self, *args, **kwargs):
        return freezer_api.Session(self.request).get(self.kwargs['session_id'])

    @shield('Unable to get session', redirect='freezer-sessions:index')
    def get_initial(self):
        initial = super(CreateSessionWorkflow, self).get_initial()
        if self.is_update():
            initial.update({'job_id': None})
            session = freezer_api.Session(self.request).get(
                self.kwargs['session_id'], json=True)
            initial.update(**session)
            initial.update(**session['schedule'])
        return initial

    def is_update(self):
        return 'session_id' in self.kwargs and \
               bool(self.kwargs['session_id'])
