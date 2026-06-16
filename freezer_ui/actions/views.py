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

from django.urls import reverse_lazy
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from horizon import tables
from horizon import workflows

import freezer_ui.api.api as freezer_api

from freezer_ui.actions import tables as freezer_tables
from freezer_ui.actions.workflows import action as action_workflow
from freezer_ui.utils import shield


class IndexView(tables.DataTableView):
    name = _("Actions")
    slug = "freezer-actions"
    table_class = freezer_tables.ActionsTable
    template_name = "project/freezer-actions/index.html"

    @shield("Unable to get actions", redirect="freezer-actions:index")
    def get_data(self):
        filters = self.table.get_filter_string() or None
        return freezer_api.Action(self.request).list(search=filters)


class ActionView(generic.TemplateView):
    template_name = 'project/freezer-actions/detail.html'

    @shield('Unable to get action', redirect='freezer-actions:index')
    def get_context_data(self, **kwargs):
        action_api = freezer_api.Action(self.request)
        action = action_api.get(kwargs['action_id'], json=True)
        action_obj = action_api.to_object(action)
        table = freezer_tables.ActionsTable(self.request)
        actions = table.render_row_actions(action_obj)
        return {
            'action': action,
            'page_title': action.get('action_id'),
            'actions': actions,
            'url': reverse('horizon:project:freezer-actions:index')
        }


class ActionWorkflowView(workflows.WorkflowView):
    workflow_class = action_workflow.ActionWorkflow
    success_url = reverse_lazy("horizon:project:freezer-actions:index")

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
