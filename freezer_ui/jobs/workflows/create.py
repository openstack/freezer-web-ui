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

import json

from django import shortcuts
import logging

from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

import freezer_ui.api.api as freezer_api
from freezer_ui.utils import datetime_to_iso_string

LOG = logging.getLogger(__name__)


class ActionsConfigurationAction(workflows.Action):

    def __init__(self, request, context, *args, **kwargs):
        super().__init__(request, context, *args, **kwargs)
        self.available_actions = []
        self.clients_json = "[]"
        try:
            self.available_actions = freezer_api.Action(
                request).list(json=True)
        except Exception:
            LOG.exception('Unable to retrieve actions')
        try:
            clients = freezer_api.Client(request).list(json=True)
            self.clients_json = json.dumps(clients)
        except Exception:
            pass

    def get_help_text(self, extra_context=None):
        extra_context = extra_context or {}
        extra_context['available_actions'] = (
            self.available_actions)
        extra_context['selected_actions'] = []
        extra_context['clients_json'] = self.clients_json
        return super().get_help_text(extra_context)

    class Meta(object):
        name = _("Actions")
        slug = "actions"


class ActionsConfiguration(workflows.Step):
    action_class = ActionsConfigurationAction
    template_name = "project/freezer-jobs/_actions.html"
    contributes = ('actions',)


class ClientsConfigurationAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(ClientsConfigurationAction, self).__init__(request,
                                                         *args,
                                                         **kwargs)
        err_msg = _('Unable to retrieve client list.')

        job_id = args[0].get('job_id', None)

        default_role_name = self.get_default_role_field_name()
        self.fields[default_role_name] = forms.CharField(required=False)
        self.fields[default_role_name].initial = 'member'

        all_clients = []
        try:
            all_clients = freezer_api.Client(request).list()
        except Exception:
            exceptions.handle(request, err_msg)
        client_list = [(c.uuid, c.hostname)
                       for c in all_clients]

        field_name = self.get_member_field_name('member')
        if not job_id:
            self.fields[field_name] = forms.MultipleChoiceField()
            self.fields[field_name].choices = client_list

    class Meta:
        name = _("Clients")
        slug = 'selected_clients'


class ClientsConfiguration(workflows.UpdateMembersStep):
    action_class = ClientsConfigurationAction
    help_text = _("From here you can add and remove clients to "
                  "this job from the list of available clients")
    available_list_title = _("All Clients")
    members_list_title = _("Selected Clients")
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


class InfoConfigurationAction(workflows.Action):
    actions = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    description = forms.CharField(
        label=_("Job Name"),
        help_text=_("Set a name for this job"))

    job_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    schedule_start_date = forms.DateTimeField(
        label=_("Start Date and Time"),
        required=False,
        input_formats=['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
    )

    interval_uint = forms.ChoiceField(
        label=_("Interval Unit"),
        help_text=_("Set the unit for the Interval"),
        required=False)

    interval_value = forms.IntegerField(
        label=_("Interval Value"),
        initial=1,
        min_value=1,
        help_text=_("Set the interval value"),
        required=False)

    schedule_end_date = forms.DateTimeField(
        label=_("End Date and Time"),
        required=False,
        input_formats=['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
    )

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context
        super(InfoConfigurationAction, self).__init__(
            request, context, *args, **kwargs)

    def populate_interval_uint_choices(self, request, context):
        return [
            ('', _("Please choose a interval unit")),
            ('continuous', _("Continuous")),
            ('weeks', _("Weeks")),
            ('days', _("Days")),
            ('hours', _("Hours")),
            ('minutes', _("Minutes")),
            ('seconds', _("Seconds")),
        ]

    def clean_schedule_start_date(self):
        return datetime_to_iso_string(
            self.cleaned_data.get('schedule_start_date'))

    def clean_schedule_end_date(self):
        return datetime_to_iso_string(
            self.cleaned_data.get('schedule_end_date'))

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('schedule_start_date')
        end = cleaned_data.get('schedule_end_date')

        if start and end and not cleaned_data.get('interval_uint'):
            self._errors['interval_uint'] = self.error_class(
                [_("Please provide this value.")])

        if end and not start and not cleaned_data.get('interval_uint'):
            self._errors['schedule_start_date'] = self.error_class(
                [_("Please provide this value.")])

        return cleaned_data

    class Meta(object):
        name = _("Job Info")
        slug = "info"
        help_text_template = "project/freezer-jobs" \
                             "/_info.html"


class InfoConfiguration(workflows.Step):
    action_class = InfoConfigurationAction
    contributes = ('description',
                   'job_id',
                   'actions',
                   'schedule_start_date',
                   'interval_uint',
                   'interval_value',
                   'schedule_end_date')


class ConfigureJob(workflows.Workflow):
    slug = "job"
    name = _("Job Configuration")
    finalize_button_name = _("Save")
    success_message = _('Job queued correctly. It will appear soon.')
    failure_message = _('Unable to created job.')
    success_url = "horizon:project:freezer-jobs:index"
    default_steps = (InfoConfiguration,
                     ClientsConfiguration,
                     ActionsConfiguration)

    def handle(self, request, context):
        try:
            interval_unit = context['interval_uint']
            if not interval_unit or interval_unit == 'continuous':
                context['schedule_interval'] = interval_unit
            else:
                interval_value = context['interval_value']
                schedule_interval = "{0} {1}".format(interval_value,
                                                     interval_unit)

                context['schedule_interval'] = schedule_interval
            if context['job_id'] != '':
                freezer_api.Job(request).update(context['job_id'], context)
            else:
                freezer_api.Job(request).create(context)
            return shortcuts.redirect('horizon:project:freezer-jobs:index')
        except Exception:
            exceptions.handle(request)
            return False
