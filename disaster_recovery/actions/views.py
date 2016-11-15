# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import pprint

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from horizon import tables
from horizon import workflows

import disaster_recovery.api.api as freezer_api

from disaster_recovery.actions import tables as freezer_tables
from disaster_recovery.actions.workflows import action as action_workflow
from disaster_recovery.utils import shield


class IndexView(tables.DataTableView):
    name = _("Actions")
    slug = "actions"
    table_class = freezer_tables.ActionsTable
    template_name = "disaster_recovery/actions/index.html"

    @shield("Unable to get actions", redirect="actions:index")
    def get_data(self):
        filters = self.table.get_filter_string() or None
        return freezer_api.Action(self.request).list(search=filters)


class ActionView(generic.TemplateView):
    template_name = 'disaster_recovery/actions/detail.html'

    @shield('Unable to get action', redirect='actions:index')
    def get_context_data(self, **kwargs):
        action = freezer_api.Action(self.request).get(kwargs['action_id'],
                                                      json=True)
        return {'data': pprint.pformat(action)}


class ActionWorkflowView(workflows.WorkflowView):
    workflow_class = action_workflow.ActionWorkflow
    success_url = reverse_lazy("horizon:disaster_recovery:actions:index")

    def is_update(self):
        return 'action_id' in self.kwargs and bool(self.kwargs['action_id'])

    @shield("Unable to get job", redirect="jobs:index")
    def get_initial(self):
        initial = super(ActionWorkflowView, self).get_initial()
        if self.is_update():
            initial.update({'action_id': None})
            action = freezer_api.Action(self.request).get(
                self.kwargs['action_id'], json=True)
            initial.update(**action['freezer_action'])
            initial.update({
                "mandatory": action.get('mandatory', None),
                "max_retries": action.get('max_retries', None),
                "max_retries_interval":
                    action.get('max_retries_interval', None)
            })
            initial.update({'action_id': action['action_id']})
        return initial
