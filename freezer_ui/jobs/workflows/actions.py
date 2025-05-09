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

from django import shortcuts
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

import freezer_ui.api.api as freezer_api


class ActionsConfigurationAction(workflows.Action):
    pass

    class Meta(object):
        name = _("Actions")
        slug = "actions"
        help_text_template = "disaster_recovery/jobs" \
                             "/_actions.html"


class ActionsConfiguration(workflows.Step):
    action_class = ActionsConfigurationAction
    contributes = ()


class InfoAction(workflows.Action):
    job_id = forms.CharField(label=_("Job ID"), required=False,
                             widget=forms.HiddenInput(),)
    actions = forms.CharField(label=_("Actions"), required=False,
                              widget=forms.TextInput(
                                  attrs={'readonly': 'readonly'}))

    def __init__(self, request, *args, **kwargs):
        super(InfoAction, self).__init__(request, *args, **kwargs)

    class Meta(object):
        name = _("Info")
        # Unusable permission so this is always hidden. However, we
        # keep this step in the workflow for validation/verification purposes.
        permissions = ()


class Info(workflows.Step):
    action_class = InfoAction
    contributes = ("job_id", "actions")


class ConfigureActions(workflows.Workflow):
    slug = "job"
    name = _("Actions Configuration")
    finalize_button_name = _("Save")
    success_message = _('Actions saved correctly.')
    failure_message = _('Unable to save actions.')
    success_url = "horizon:disaster_recovery:jobs:index"
    default_steps = (ActionsConfiguration, Info)

    def handle(self, request, context):
        try:
            if context['job_id'] != '':
                freezer_api.Job(request).update_actions(context['job_id'],
                                                        context['actions'])
            return shortcuts.redirect('horizon:disaster_recovery:jobs:index')
        except Exception:
            exceptions.handle(request)
            return False
