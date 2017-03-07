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

import datetime
import pprint

from django.utils.translation import ugettext_lazy as _
from django.views import generic

from horizon import tables
from horizon import workflows

import disaster_recovery.api.api as freezer_api

from disaster_recovery.backups import tables as freezer_tables
from disaster_recovery.backups.workflows import restore as restore_workflow
from disaster_recovery.utils import shield


class IndexView(tables.DataTableView):
    name = _("Backups")
    slug = "backups"
    table_class = freezer_tables.BackupsTable
    template_name = "disaster_recovery/backups/index.html"

    @shield('Unable to retrieve backups.', redirect='backups:index')
    def get_data(self):
        filters = self.table.get_filter_string() or None
        return freezer_api.Backup(self.request).list(search=filters)


class DetailView(generic.TemplateView):
    template_name = 'disaster_recovery/backups/detail.html'

    @shield('Unable to get backup.', redirect='backups:index')
    def get_context_data(self, **kwargs):
        backup = freezer_api.Backup(self.request).get(kwargs['backup_id'],
                                                      json=True)
        return {'data': pprint.pformat(backup)}


class RestoreView(workflows.WorkflowView):
    workflow_class = restore_workflow.Restore

    @shield('Unable to get backup.', redirect='backups:index')
    def get_object(self, *args, **kwargs):
        return freezer_api.Backup(self.request).get(self.kwargs['backup_id'])

    def is_update(self):
        return 'name' in self.kwargs and bool(self.kwargs['name'])

    @shield('Unable to get backup.', redirect='backups:index')
    def get_workflow_name(self):
        backup = freezer_api.Backup(self.request).get(self.kwargs['backup_id'])
        backup_date_str = datetime.datetime.fromtimestamp(int(backup.time_stamp))\
            .strftime("%Y/%m/%d %H:%M")
        return "Restore '{}' from {}".format(backup.backup_name,
                                             backup_date_str)

    def get_initial(self):
        return {"backup_id": self.kwargs['backup_id']}

    @shield('Unable to get backup.', redirect='backups:index')
    def get_workflow(self, *args, **kwargs):
        workflow = super(RestoreView, self).get_workflow(*args, **kwargs)
        workflow.name = self.get_workflow_name()
        return workflow
