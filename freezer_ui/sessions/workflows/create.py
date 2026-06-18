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
from django.utils.translation import gettext_lazy as _


from horizon import exceptions
from horizon import forms
from horizon import workflows

import freezer_ui.api.api as freezer_api
from freezer_ui.utils import datetime_to_iso_string


class SessionConfigurationAction(workflows.Action):
    description = forms.CharField(
        label=_("Session Name"),
        help_text=_("Define a name for this session"))

    session_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    schedule_start_date = forms.DateTimeField(
        label=_("Start Date and Time"),
        required=False,
        help_text=_(
            "Optional. Start time for the session. "
            "If not provided, the session will start immediately."
        ),
        input_formats=['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
    )

    interval_unit = forms.ChoiceField(
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
        help_text=_(
            "Optional. End time for the session. "
            "If not provided, the session will run indefinitely "
            "or until manually stopped."
        ),
        input_formats=['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
    )

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context
        super(SessionConfigurationAction, self).__init__(
            request, context, *args, **kwargs)

    def populate_interval_unit_choices(self, request, context):
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

        if start and end and not cleaned_data.get('interval_unit'):
            self._errors['interval_unit'] = self.error_class(
                [_("Please provide this value.")])

        if end and not start and not cleaned_data.get('interval_unit'):
            self._errors['schedule_start_date'] = self.error_class(
                [_("Please provide this value.")])

        return cleaned_data

    class Meta(object):
        name = _("Session Information")
        slug = "freezer-sessions"
        help_text_template = "project/freezer-sessions/_info.html"


class SessionConfiguration(workflows.Step):
    action_class = SessionConfigurationAction
    contributes = ('description',
                   'session_id',
                   'schedule_start_date',
                   'interval_unit',
                   'interval_value',
                   'schedule_end_date')


class CreateSession(workflows.Workflow):
    slug = "create_session"
    name = _("Create Session")
    finalize_button_name = _("Save")
    success_message = _('Session queued correctly. It will appear soon.')
    failure_message = _('Unable to create session.')
    success_url = "horizon:project:freezer-sessions:index"
    default_steps = (SessionConfiguration,)

    def handle(self, request, context):
        try:
            interval_unit = context['interval_unit']
            if not interval_unit or interval_unit == 'continuous':
                context['schedule_interval'] = interval_unit
            else:
                interval_value = context['interval_value']
                schedule_interval = "{0} {1}".format(interval_value,
                                                     interval_unit)
                context['schedule_interval'] = schedule_interval

            if context['session_id'] != '':
                freezer_api.Session(request).update(context,
                                                    context['session_id'])
            else:
                freezer_api.Session(request).create(context)

            return reverse("horizon:project:freezer-sessions:index")
        except Exception:
            exceptions.handle(request)
            return False
