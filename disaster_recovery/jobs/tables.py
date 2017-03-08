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

from django import shortcuts
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from horizon import messages
from django.core.urlresolvers import reverse

import disaster_recovery.api.api as freezer_api
from disaster_recovery.utils import shield


class ObjectFilterAction(tables.FilterAction):
    def allowed(self, request, datum):
        return bool(self.table.kwargs['job_id'])


class AttachJobToSession(tables.LinkAction):
    name = "attach_job_to_session"
    verbose_name = _("Attach To Session")
    classes = ("ajax-modal",)
    url = "horizon:disaster_recovery:sessions:attach"

    def allowed(self, request, instance):
        return True

    def get_link_url(self, datum):
        return reverse("horizon:disaster_recovery:sessions:attach",
                       kwargs={'job_id': datum.job_id})


class DeleteJob(tables.DeleteAction):
    name = "delete"
    classes = ("btn-danger",)
    icon = "remove"
    help_text = _("Delete jobs is not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Job File",
            u"Delete Job Files",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Job File",
            u"Deleted Job Files",
            count
        )

    @shield("Unable to delete job", redirect="jobs:index")
    def delete(self, request, job_id):
        return freezer_api.Job(request).delete(job_id)


class DeleteMultipleJobs(DeleteJob):
    name = "delete_multiple_jobs"


class CloneJob(tables.Action):
    name = "clone"
    verbose_name = _("Clone Job")
    help_text = _("Clone and edit a job file")

    @shield("Unable to clone job", redirect="jobs:index")
    def single(self, table, request, job_id):
        freezer_api.Job(request).clone(job_id)
        return shortcuts.redirect('horizon:disaster_recovery:jobs:index')


class EditJob(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Job")
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, datum=None):
        return reverse("horizon:disaster_recovery:jobs:edit_job",
                       kwargs={'job_id': datum.job_id})


class EditActionsInJob(tables.LinkAction):
    name = "edit_actions_in_job"
    verbose_name = _("Edit Actions")
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, datum=None):
        return reverse("horizon:disaster_recovery:jobs:edit_action",
                       kwargs={'job_id': datum.job_id})


class StartJob(tables.Action):
    name = "start_job"
    verbose_name = _("Start Job")

    @shield("Unable to start job", redirect="jobs:index")
    def single(self, table, request, job_id):
        freezer_api.Job(request).start(job_id)
        messages.success(request, _("Job has started"))
        return shortcuts.redirect('horizon:disaster_recovery:jobs:index')

    def allowed(self, request, job=None):
        return True


class StopJob(tables.Action):
    name = "stop_job"
    verbose_name = _("Stop Job")

    @shield("Unable to stop job", redirect="jobs:index")
    def single(self, table, request, job_id):
        freezer_api.Job(request).stop(job_id)
        messages.success(request, _("Job has stopped"))
        return shortcuts.redirect('horizon:disaster_recovery:jobs:index')

    def allowed(self, request, job=None):
        if job.event == 'stop':
            return False
        return True


def get_link(row):
    return reverse('horizon:disaster_recovery:jobs:index',
                   kwargs={'job_id': row.job_id})


class CreateJob(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Job")
    url = "horizon:disaster_recovery:jobs:create"
    classes = ("ajax-modal",)
    icon = "plus"


class UpdateRow(tables.Row):
    ajax = True


class JobsTable(tables.DataTable):
    job_name = tables.Column("description",
                             link=get_link,
                             verbose_name=_("Name"))

    client_id = tables.Column("client_id",
                              verbose_name=_("Host"))

    event = tables.Column("event",
                          verbose_name=_("Status"))

    result = tables.Column("result",
                           verbose_name=_("Result"))

    def get_object_id(self, row):
        return row.id

    def get_object_display(self, job):
        return job.description

    class Meta(object):
        name = "jobs"
        verbose_name = _("Jobs")
        table_actions = (ObjectFilterAction,
                         CreateJob,
                         DeleteMultipleJobs)
        row_actions = (StartJob,
                       StopJob,
                       EditActionsInJob,
                       EditJob,
                       AttachJobToSession,
                       CloneJob,
                       DeleteJob)
        footer = False
        multi_select = True
        row_class = UpdateRow


class DeleteAction(tables.DeleteAction):
    name = "delete"
    classes = ("btn-danger",)
    icon = "remove"
    help_text = _("Delete actions is not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Action",
            u"Delete Action",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted action File",
            u"Deleted action Files",
            count
        )

    @shield("Unable to delete action", redirect="jobs:index")
    def delete(self, request, obj_id):
        freezer_api.Job(request).delete_action(obj_id)
        return reverse("horizon:disaster_recovery:jobs:index")


class DeleteMultipleActions(DeleteAction):
    name = "delete_multiple_actions"


class ActionsTable(tables.DataTable):
    action = tables.Column('action', verbose_name=_("Action Type"))

    name = tables.Column('backup_name', verbose_name=_("Action Name"))

    def get_object_id(self, container):
        # TODO(m3m0): we should't send the ids in this way
        ids = '{0}==={1}'.format(container.action_id, container.job_id)
        return ids

    class Meta(object):
        name = "actions_in_job"
        verbose_name = _("Actions")
        table_actions = (ObjectFilterAction,
                         DeleteMultipleActions)
        row_actions = (DeleteAction,)
        footer = False
        multi_select = True
