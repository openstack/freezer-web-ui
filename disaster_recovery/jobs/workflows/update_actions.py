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

from django import shortcuts
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

import disaster_recovery.api.api as freezer_api


class ActionsConfigurationAction(workflows.Action):
    actions = forms.CharField(
        required=False)

    job_id = forms.CharField(
        required=False)

    class Meta(object):
        name = _("Actions")
        slug = "actions"
        help_text_template = "disaster_recovery/jobs" \
                             "/_actions.html"


class ActionsConfiguration(workflows.Step):
    action_class = ActionsConfigurationAction
    contributes = ('actions', 'job_id')


class UpdateActions(workflows.Workflow):
    slug = "update_actions"
    name = _("Update Actions")
    finalize_button_name = _("Save")
    success_message = _('Actions updated correctly.')
    failure_message = _('Unable to update actions.')
    success_url = "horizon:disaster_recovery:jobs:index"
    default_steps = (ActionsConfiguration,)

    def handle(self, request, context):
        try:
            if context['job_id'] != '':
                freezer_api.Job(request).update_actions(context['job_id'],
                                                        context['actions'])
            return shortcuts.redirect('horizon:disaster_recovery:jobs:index')
        except Exception:
            exceptions.handle(request)
            return False
