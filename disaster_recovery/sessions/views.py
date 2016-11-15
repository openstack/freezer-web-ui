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

from horizon import browsers
from horizon import workflows

import disaster_recovery.api.api as freezer_api
import disaster_recovery.sessions.browsers as project_browsers

from disaster_recovery.sessions.workflows import attach
from disaster_recovery.sessions.workflows import create
from disaster_recovery.utils import shield


class SessionsView(browsers.ResourceBrowserView):
    browser_class = project_browsers.SessionBrowser
    template_name = "disaster_recovery/sessions/browser.html"

    @shield('Unable to get sessions list.', redirect='sessions:index')
    def get_sessions_data(self):
        return freezer_api.Session(self.request).list(limit=100)

    @shield('Unable to get job list.', redirect='sessions:index')
    def get_jobs_data(self):
        if self.kwargs['session_id']:
            return freezer_api.Session(self.request).jobs(
                self.kwargs['session_id'])
        return []


class AttachToSessionWorkflow(workflows.WorkflowView):
    workflow_class = attach.AttachJobToSession

    @shield('Unable to get job', redirect='jobs:index')
    def get_object(self, *args, **kwargs):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and \
               bool(self.kwargs['job_id'])

    @shield('Unable to get job', redirect='jobs:index')
    def get_initial(self):
        initial = super(AttachToSessionWorkflow, self).get_initial()
        job = self.get_object()
        initial.update({'job_id': job.id})
        return initial


class CreateSessionWorkflow(workflows.WorkflowView):
    workflow_class = create.CreateSession

    @shield('Unable to get session', redirect='sessions:index')
    def get_object(self, *args, **kwargs):
        return freezer_api.Session(self.request).get(self.kwargs['session_id'])

    @shield('Unable to get session', redirect='sessions:index')
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
