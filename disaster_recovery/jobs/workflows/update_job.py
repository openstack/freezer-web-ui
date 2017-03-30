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

import datetime

from django import shortcuts
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

import disaster_recovery.api.api as freezer_api


class InfoConfigurationAction(workflows.Action):

    description = forms.CharField(
        label=_("Job Name"),
        help_text=_("Set a name for this job"))

    job_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    schedule_start_date = forms.CharField(
        label=_("Start Date and Time"),
        required=False)

    schedule_interval = forms.CharField(
        label=_("Interval"),
        required=False,
        help_text=_("""Set the interval in the following format:
                       continuous,
                       N weeks,
                       N days,
                       N hours,
                       N minutes,
                       N seconds,
                       If no start date is provided the job
                       will start immediately"""))

    schedule_end_date = forms.CharField(
        label=_("End Date and Time"),
        required=False)

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context
        super(InfoConfigurationAction, self).__init__(
            request, context, *args, **kwargs)

    def clean(self):
        cleaned_data = super(InfoConfigurationAction, self).clean()
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
        name = _("Job Info")
        slug = "info"
        help_text_template = "disaster_recovery/jobs" \
                             "/_info.html"


class InfoConfiguration(workflows.Step):
    action_class = InfoConfigurationAction
    contributes = ('description',
                   'job_id',
                   'actions',
                   'schedule_start_date',
                   'schedule_interval',
                   'schedule_end_date')


class UpdateJob(workflows.Workflow):
    slug = "update_job"
    name = _("Update Job")
    finalize_button_name = _("Save")
    success_message = _('Job updated correctly.')
    failure_message = _('Unable to update job.')
    success_url = "horizon:disaster_recovery:jobs:index"
    default_steps = (InfoConfiguration,)

    def handle(self, request, context):
        try:
            if context['job_id'] != '':
                freezer_api.Job(request).update(context['job_id'], context)
            return shortcuts.redirect('horizon:disaster_recovery:jobs:index')
        except Exception:
            exceptions.handle(request)
            return False
