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

from horizon import browsers
from horizon import workflows

import workflows.create as configure_workflow
import workflows.update_job as update_job_workflow
import workflows.update_actions as update_actions_workflow

import disaster_recovery.api.api as freezer_api
import disaster_recovery.jobs.browsers as project_browsers

from disaster_recovery.utils import shield


class JobsView(browsers.ResourceBrowserView):
    browser_class = project_browsers.ContainerBrowser
    template_name = "disaster_recovery/jobs/browser.html"

    @shield("Unable to get job", redirect='jobs:index')
    def get_jobs_data(self):
        return freezer_api.Job(self.request).list(limit=100)

    @shield("Unable to get actions for this job.", redirect='jobs:index')
    def get_actions_in_job_data(self):
        if self.kwargs['job_id']:
            return freezer_api.Job(self.request).actions(self.kwargs['job_id'])
        return []


class JobWorkflowView(workflows.WorkflowView):
    workflow_class = configure_workflow.ConfigureJob

    @shield("Unable to get job", redirect="jobs:index")
    def get_object(self):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and bool(self.kwargs['job_id'])

    @shield("Unable to get job", redirect="jobs:index")
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

    @shield("Unable to get job", redirect="jobs:index")
    def get_object(self):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and bool(self.kwargs['job_id'])

    @shield("Unable to get job", redirect="jobs:index")
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
    workflow_class = update_actions_workflow.UpdateActions

    @shield("Unable to get job", redirect="jobs:index")
    def get_object(self):
        return freezer_api.Job(self.request).get(self.kwargs['job_id'])

    def is_update(self):
        return 'job_id' in self.kwargs and bool(self.kwargs['job_id'])

    @shield("Unable to get job", redirect="jobs:index")
    def get_initial(self):
        initial = super(ActionsInJobView, self).get_initial()
        if self.is_update():
            job = freezer_api.Job(self.request).get(self.kwargs['job_id'])
            initial.update({'job_id': job.id})
        return initial
