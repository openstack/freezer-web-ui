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


def update_session_jobs(request, session_id, selected_job_ids):
    # Fetch current session jobs
    try:
        session = freezer_api.Session(request).get(session_id, json=True)
        current_job_ids = set(session.get('jobs', {}).keys())
    except Exception:
        current_job_ids = set()

    selected_job_ids = set(selected_job_ids or [])

    # Jobs to add
    for job_id in selected_job_ids - current_job_ids:
        try:
            freezer_api.Session(request).add_job(session_id, job_id)
        except Exception:
            pass

    # Jobs to remove
    for job_id in current_job_ids - selected_job_ids:
        try:
            freezer_api.Session(request).remove_job(session_id, job_id)
        except Exception:
            pass


class JobsConfigurationAction(workflows.MembershipAction):
    def __init__(self, request, context, *args, **kwargs):
        super(JobsConfigurationAction, self).__init__(request,
                                                      context,
                                                      *args,
                                                      **kwargs)
        err_msg = _('Unable to retrieve jobs list.')

        default_role_name = self.get_default_role_field_name()
        self.fields[default_role_name] = forms.CharField(required=False)
        self.fields[default_role_name].initial = 'member'

        all_jobs = []
        try:
            all_jobs = freezer_api.Job(request).list()
        except Exception:
            exceptions.handle(request, err_msg)

        job_list = [(j.job_id, j.description or j.job_id) for j in all_jobs]

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)
        self.fields[field_name].choices = job_list

        session_id = (context.get('session_id') or
                      self.initial.get('session_id'))
        initial_jobs = (context.get('jobs') or
                        self.initial.get('jobs') or [])
        if isinstance(initial_jobs, dict):
            self.fields[field_name].initial = list(initial_jobs.keys())
        elif isinstance(initial_jobs, list) and initial_jobs:
            self.fields[field_name].initial = initial_jobs
        elif session_id:
            try:
                session = freezer_api.Session(request).get(
                    session_id, json=True)
                self.fields[field_name].initial = list(
                    session.get('jobs', {}).keys())
            except Exception:
                pass

    class Meta:
        name = _("Jobs")
        slug = 'selected_jobs'


class JobsConfiguration(workflows.UpdateMembersStep):
    action_class = JobsConfigurationAction
    help_text = _("From here you can associate and disassociate jobs "
                  "to this session from the list of available jobs")
    available_list_title = _("All Jobs")
    members_list_title = _("Associated Jobs")
    no_available_text = _("No jobs found.")
    no_members_text = _("No jobs selected.")
    show_roles = False
    depends_on = ('session_id', 'jobs')
    contributes = ("jobs",)

    def contribute(self, data, context):
        request = self.workflow.request
        if data:
            field_name = self.get_member_field_name('member')
            context["jobs"] = request.POST.getlist(field_name)
        return context


class ManageJobsWorkflow(workflows.Workflow):
    slug = "manage_jobs"
    name = _("Manage Session Jobs")
    finalize_button_name = _("Save")
    success_message = _('Session jobs updated successfully.')
    failure_message = _('Unable to update session jobs.')
    default_steps = (JobsConfiguration,)

    def get_success_url(self):
        session_id = self.context.get('session_id')
        referer = self.request.META.get('HTTP_REFERER')
        if session_id and referer:
            from urllib.parse import urlparse
            path = urlparse(referer).path
            if ('/freezer-sessions/%s' % session_id) in path:
                url = reverse("horizon:project:freezer-sessions:detail",
                              kwargs={'session_id': session_id})
                return url + "?tab=associated_jobs"
        return reverse("horizon:project:freezer-sessions:index")

    def handle(self, request, context):
        try:
            update_session_jobs(request,
                                context['session_id'],
                                context.get('jobs', []))
            return True
        except Exception:
            exceptions.handle(request)
            return False


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
    default_steps = (SessionConfiguration,
                     JobsConfiguration)

    def get_success_url(self):
        session_id = self.context.get('session_id')
        referer = self.request.META.get('HTTP_REFERER')
        if session_id and referer:
            from urllib.parse import urlparse
            path = urlparse(referer).path
            if ('/freezer-sessions/%s' % session_id) in path:
                return reverse("horizon:project:freezer-sessions:detail",
                               kwargs={'session_id': session_id})
        return reverse("horizon:project:freezer-sessions:index")

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
                session_id = context['session_id']
                freezer_api.Session(request).update(context, session_id)
            else:
                session_id = freezer_api.Session(request).create(context)

            update_session_jobs(request, session_id, context.get('jobs', []))

            return True
        except Exception:
            exceptions.handle(request)
            return False
