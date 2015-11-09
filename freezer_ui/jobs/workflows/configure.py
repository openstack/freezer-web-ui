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

import logging

from collections import namedtuple
import datetime

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import workflows

import freezer_ui.api.api as freezer_api
from freezer_ui.utils import actions_in_job


LOG = logging.getLogger(__name__)


class ActionsConfigurationAction(workflows.Action):
    pass

    class Meta(object):
        name = _("Actions")
        slug = "actions"
        help_text_template = "freezer_ui/jobs" \
                             "/_actions.html"


class ActionsConfiguration(workflows.Step):
    action_class = ActionsConfigurationAction
    contributes = ('actions',)


class ClientsConfigurationAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(ClientsConfigurationAction, self).__init__(request,
                                                         *args,
                                                         **kwargs)
        err_msg = _('Unable to retrieve client list.')

        original_name = args[0].get('original_name', None)

        default_role_name = self.get_default_role_field_name()
        self.fields[default_role_name] = forms.CharField(required=False)
        self.fields[default_role_name].initial = 'member'

        all_clients = []
        try:
            all_clients = freezer_api.client_list(request)
        except Exception:
            exceptions.handle(request, err_msg)
        client_list = [(c.uuid, c.hostname)
                       for c in all_clients]

        field_name = self.get_member_field_name('member')
        if not original_name:
            self.fields[field_name] = forms.MultipleChoiceField(required=False)
            self.fields[field_name].choices = client_list

    class Meta:
        name = _("Clients")
        slug = 'selected_clients'


class ClientsConfiguration(workflows.UpdateMembersStep):
    action_class = ClientsConfigurationAction
    help_text = _("From here you can add and remove clients to "
                  "this job from the list of available clients")
    available_list_title = _("All Clients")
    members_list_title = _("Available clients")
    no_available_text = _("No clients found.")
    no_members_text = _("No clients selected.")
    show_roles = False
    contributes = ("clients",)

    def contribute(self, data, context):
        request = self.workflow.request
        if data:
            field_name = self.get_member_field_name('member')
            context["clients"] = request.POST.getlist(field_name)
        return context


class SchedulingConfigurationAction(workflows.Action):
    schedule_start_date = forms.CharField(
        label=_("Start Date and Time"),
        required=False,
        help_text=_(""))

    schedule_interval = forms.CharField(
        label=_("Interval"),
        required=False,
        help_text=_("Repeat this configuration in a minutes interval."))

    schedule_end_date = forms.CharField(
        label=_("End Date and Time"),
        required=False,
        help_text=_(""))

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context
        super(SchedulingConfigurationAction, self).__init__(
            request, context, *args, **kwargs)

    def clean(self):
        cleaned_data = super(SchedulingConfigurationAction, self).clean()
        self._check_start_datetime(cleaned_data)
        self._check_end_datetime(cleaned_data)
        return cleaned_data

    def _validate_iso_format(self, start_date):
        try:
            return datetime.datetime.strptime(
                start_date, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return False

    def _check_start_datetime(self, cleaned_data):
        if cleaned_data.get('start_datetime') and not \
                self._validate_iso_format(
                    cleaned_data.get('schedule_start_date')):
            msg = _("Start date time is not in ISO format.")
            self._errors['schedule_start_date'] = self.error_class([msg])

    def _check_end_datetime(self, cleaned_data):
        if cleaned_data.get('end_datetime') and not \
                self._validate_iso_format(
                    cleaned_data.get('schedule_end_date')):
            msg = _("End date time is not in ISO format.")
            self._errors['schedule_end_date'] = self.error_class([msg])

    class Meta(object):
        name = _("Scheduling")
        slug = "scheduling"
        help_text_template = "freezer_ui/jobs" \
                             "/_scheduling.html"


class SchedulingConfiguration(workflows.Step):
    action_class = SchedulingConfigurationAction
    contributes = ('schedule_start_date',
                   'schedule_interval',
                   'schedule_end_date')


class InfoConfigurationAction(workflows.Action):
    actions = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    description = forms.CharField(
        label=_("Job Name"),
        help_text=_("Set a short description for this job"),
        required=True)

    original_name = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    class Meta(object):
        name = _("Job Info")
        slug = "info"
        help_text_template = "freezer_ui/jobs" \
                             "/_info.html"


class InfoConfiguration(workflows.Step):
    action_class = InfoConfigurationAction
    contributes = ('description',
                   'original_name',
                   'actions')


class ConfigureJob(workflows.Workflow):
    slug = "job"
    name = _("Job Configuration")
    finalize_button_name = _("Save")
    success_message = _('Job created correctly.')
    failure_message = _('Unable to created job.')
    success_url = "horizon:freezer_ui:jobs:index"
    default_steps = (InfoConfiguration,
                     ClientsConfiguration,
                     SchedulingConfiguration,
                     ActionsConfiguration)

    def handle(self, request, context):
        try:
            is_edit = False
            if not context['original_name'] == '':
                is_edit = True

            actions = actions_in_job(context.pop('actions', []))
            actions_for_job = []

            if is_edit:
                # if this is a edit get the job and delete the action list
                # TODO(m3m0) improve this to not recreate the action list
                job_id = context['original_name']
                job = freezer_api.job_get(request, job_id)
                del job[0].data_dict['job_actions']

            for action in actions:
                a = freezer_api.action_get(request, action)
                a = {
                    'action_id': a['action_id'],
                    'freezer_action': a['freezer_action']
                }
                actions_for_job.append(a)

            context['job_actions'] = actions_for_job

            if is_edit:
                return freezer_api.job_edit(request, context)
            else:
                if context['clients']:
                    # we have to query the api to get the list of clients
                    # because MembershipAction for clients works with uuid's
                    # and we need to send the client_id instead of the uuid
                    # for the job creation
                    clients = freezer_api.client_list(request)
                    ClientIDS = namedtuple('Client', ['client_id', 'uuid'])

                    client_list = [ClientIDS(c.client_id, c.uuid)
                                   for c in clients]

                    for client_uuid in context['clients']:
                        for client_id, uuid in client_list:
                            if client_uuid == uuid:
                                context['client_id'] = client_id
                                freezer_api.job_create(request, context)
                else:
                    messages.warning(request, _("At least one client is "
                                                "required to create a job"))
                    return False
            return True
        except Exception:
            exceptions.handle(request)
            return False
