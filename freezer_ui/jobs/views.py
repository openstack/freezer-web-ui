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

from django.views import generic
from horizon import tables
from horizon import workflows

from freezer_ui.jobs import tables as freezer_tables
from freezer_ui.jobs.workflows import create as configure_workflow
from freezer_ui.jobs.workflows import update_job as update_job_workflow
from freezer_ui.jobs.workflows import update_actions as update_workflow

import freezer_ui.api.api as freezer_api

from freezer_ui.utils import shield
from freezer_ui.utils import timestamp_to_string


class JobsView(tables.DataTableView):
    table_class = freezer_tables.JobsTable
    template_name = "project/freezer-jobs/index.html"

    @shield("Unable to get job", redirect='freezer-jobs:index')
    def get_data(self):
        return freezer_api.Job(self.request).list(limit=100)


class DetailView(generic.TemplateView):
    template_name = 'project/freezer-jobs/detail.html'

    @shield('Unable to get job.', redirect='freezer-jobs:index')
    def get_context_data(self, **kwargs):
        job = freezer_api.Job(self.request).get(kwargs['job_id'],
                                                json=True)
        if '_version' in job:
            job['version'] = job['_version']
        schedule = job.get('job_schedule', {})
        for key in ['time_created', 'time_started', 'time_ended']:
            if key in schedule and schedule[key]:
                try:
                    schedule[key + '_formatted'] = (
                        timestamp_to_string(schedule[key]))
                except Exception:
                    schedule[key + '_formatted'] = schedule[key]
        return {
            'job': job,
            'page_title': job.get('description') or job.get('job_id')
        }


class JobWorkflowView(workflows.WorkflowView):
    workflow_class = configure_workflow.ConfigureJob

    @shield("Unable to get job", redirect="freezer-jobs:index")
    def get_object(self):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and bool(self.kwargs['job_id'])

    @shield("Unable to get job", redirect="freezer-jobs:index")
    def get_initial(self):
        initial = super(JobWorkflowView, self).get_initial()
        if self.is_update():
            initial.update({'job_id': None})
            job = freezer_api.Job(self.request).get(self.kwargs['job_id'],
                                                    json=True)
            initial.update(**job)
            initial.update(**job['job_schedule'])

        return initial


class EditJobWorkflowView(workflows.WorkflowView):
    workflow_class = update_job_workflow.UpdateJob

    @shield("Unable to get job", redirect="freezer-jobs:index")
    def get_object(self):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and bool(self.kwargs['job_id'])

    @shield("Unable to get job", redirect="freezer-jobs:index")
    def get_initial(self):
        initial = super(EditJobWorkflowView, self).get_initial()
        if self.is_update():
            initial.update({'job_id': None})
            job = freezer_api.Job(self.request).get(self.kwargs['job_id'],
                                                    json=True)
            initial.update(**job)
            initial.update(**job['job_schedule'])

        return initial


class ActionsInJobView(workflows.WorkflowView):
    workflow_class = update_workflow.UpdateActions

    @shield("Unable to get job", redirect="freezer-jobs:index")
    def get_object(self):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and bool(self.kwargs['job_id'])

    @shield("Unable to get job", redirect="freezer-jobs:index")
    def get_initial(self):
        initial = super(ActionsInJobView, self).get_initial()
        if self.is_update():
            job = freezer_api.Job(self.request).get(self.kwargs['job_id'])
            initial.update({'job_id': job.id})
        return initial
