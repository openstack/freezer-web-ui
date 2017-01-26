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

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import forms
from horizon import workflows

import disaster_recovery.api.api as freezer_api


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
    success_url = "horizon:disaster_recovery:jobs:index"
    default_steps = (SessionConfiguration,)

    def handle(self, request, context):
        try:
            freezer_api.Session(request).add_job(context['session_id'],
                                                 context['job_id'])

            return reverse("horizon:disaster_recovery:jobs:index")
        except Exception:
            exceptions.handle(request)
            return False
