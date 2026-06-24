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

from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from horizon import exceptions
from horizon import forms
from horizon import workflows

import freezer_ui.api.api as freezer_api


class SessionConfigurationAction(workflows.Action):
    session_id = forms.ChoiceField(
        help_text=_("Set a session to attach this job"),
        label=_("Session Name"))

    job_id = forms.CharField(
        widget=forms.HiddenInput())

    def populate_session_id_choices(self, request, context):
        sessions = []
        try:
            sessions = freezer_api.Session(request).list()
        except Exception:
            exceptions.handle(request, _('Error getting session list'))

        sessions = [(s.session_id, s.description) for s in sessions]
        sessions.insert(0, ('', _('Select A Session')))
        return sessions

    class Meta:
        name = _("Sessions")
        slug = "sessions"


class SessionConfiguration(workflows.Step):
    action_class = SessionConfigurationAction
    contributes = ('session_id',
                   'job_id')


class AttachJobToSession(workflows.Workflow):
    slug = "attach_job"
    name = _("Attach To Session")
    finalize_button_name = _("Attach")
    success_message = _('Job attached successfully.')
    failure_message = _('Unable to attach to session.')
    success_url = "horizon:project:freezer-jobs:index"
    default_steps = (SessionConfiguration,)

    def handle(self, request, context):
        try:
            freezer_api.Session(request).add_job(context['session_id'],
                                                 context['job_id'])

            return reverse("horizon:project:freezer-jobs:index")
        except Exception:
            exceptions.handle(request)
            return False


class JobConfigurationAction(workflows.Action):
    job_id = forms.ChoiceField(
        help_text=_("Select a job to attach to this session"),
        label=_("Job"))

    session_id = forms.CharField(
        widget=forms.HiddenInput())

    def populate_job_id_choices(self, request, context):
        jobs = []
        try:
            jobs = freezer_api.Job(request).list()
        except Exception:
            exceptions.handle(request, _('Error getting jobs list'))

        attached_job_ids = set(context.get('attached_job_ids') or [])
        choices = [
            (j.job_id, j.description) for j in jobs
            if j.job_id not in attached_job_ids
        ]
        choices.insert(0, ('', _('Select A Job')))
        return choices

    class Meta:
        name = _("Jobs")
        slug = "jobs"


class JobConfiguration(workflows.Step):
    action_class = JobConfigurationAction
    depends_on = ('attached_job_ids',)
    contributes = ('session_id',
                   'job_id')


class AttachJobWorkflow(workflows.Workflow):
    slug = "attach_job"
    name = _("Attach Job")
    finalize_button_name = _("Attach")
    success_message = _('Job attached successfully.')
    failure_message = _('Unable to attach job.')
    default_steps = (JobConfiguration,)

    def get_success_url(self):
        url = reverse("horizon:project:freezer-sessions:detail",
                      kwargs={'session_id': self.context['session_id']})
        return url + "?tab=associated_jobs"

    def handle(self, request, context):
        try:
            freezer_api.Session(request).add_job(context['session_id'],
                                                 context['job_id'])
            return True
        except Exception:
            exceptions.handle(request)
            return False
