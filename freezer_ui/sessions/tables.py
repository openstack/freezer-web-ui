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

from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django.urls import reverse

from horizon import tables

import freezer_ui.api.api as freezer_api
from freezer_ui.utils import shield


class SessionFilterAction(tables.FilterAction):
    def allowed(self, request, datum):
        return bool(self.table.kwargs.get('session_id'))


def session_detail_view(session):
    return reverse("horizon:project:freezer-sessions:detail",
                   kwargs={'session_id': session.id})


class CreateJob(tables.LinkAction):
    name = "create_session"
    verbose_name = _("Create Session")
    url = "horizon:project:freezer-sessions:create"
    classes = ("ajax-modal",)
    icon = "plus"


class DeleteSession(tables.DeleteAction):
    help_text = _("Deleted Sessions is not recoverable.")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            "Delete Session",
            "Delete Sessions",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            "Deleted Session",
            "Deleted Sessions",
            count
        )

    @shield("Unable to delete session", redirect="freezer-sessions:index")
    def delete(self, request, session_id):
        return freezer_api.Session(request).delete(session_id)


class EditSession(tables.LinkAction):
    name = "edit_session"
    verbose_name = _("Edit Session")
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, datum=None):
        return reverse("horizon:project:freezer-sessions:edit",
                       kwargs={'session_id': datum.session_id})


class DeleteMultipleActions(DeleteSession):
    name = "delete_multiple_actions"


class DeleteJobFromSession(tables.DeleteAction):
    name = "delete_job_from_session"
    help_text = _(
        "Disassociating a job removes it from the session, "
        "but does not delete the job itself."
    )

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            "Disassociate Job",
            "Disassociate Jobs",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            "Disassociated Job",
            "Disassociated Jobs",
            count
        )

    @shield("Unable to disassociate job.", redirect="freezer-sessions:index")
    def delete(self, request, session):
        job_id, session_id = session.split('===')
        return freezer_api.Session(request).remove_job(session_id, job_id)

    def get_success_url(self, request=None):
        session_id = self.table.kwargs.get('session_id')
        url = reverse("horizon:project:freezer-sessions:detail",
                      kwargs={'session_id': session_id})
        return url + "?tab=associated_jobs"


class AttachJob(tables.LinkAction):
    name = "attach_job"
    verbose_name = _("Attach Job")
    classes = ("ajax-modal",)
    icon = "plus"

    def get_link_url(self, datum=None):
        session_id = self.table.kwargs.get('session_id')
        return reverse("horizon:project:freezer-sessions:attach_job",
                       kwargs={'session_id': session_id})


def get_job_link(job):
    return reverse("horizon:project:freezer-jobs:detail",
                   kwargs={'job_id': job.job_id})


def get_client_link(job):
    if job.client_id:
        return reverse("horizon:project:freezer-clients:client",
                       kwargs={'client_id': job.client_id})
    return None


class JobsTable(tables.DataTable):
    job_id = tables.Column(
        'job_id',
        link=get_job_link,
        verbose_name=_("Job ID"))

    client_id = tables.Column(
        'client_id',
        link=get_client_link,
        verbose_name=_("Client ID"))

    result = tables.Column(
        'result',
        verbose_name=_("Status"))

    def get_object_id(self, job):
        # this is used to pass to values as an url
        # TODO(m3m0): look for a way to improve this
        ids = '{0}==={1}'.format(job.job_id, job.session_id)
        return ids

    class Meta(object):
        name = "jobs"
        verbose_name = _("Jobs")
        table_actions = (SessionFilterAction, AttachJob, DeleteJobFromSession)
        row_actions = (DeleteJobFromSession,)
        footer = False
        multi_select = True


class UpdateRow(tables.Row):
    ajax = True


class SessionsTable(tables.DataTable):
    description = tables.Column('description',
                                link=session_detail_view,
                                verbose_name=_("Session"))

    status = tables.Column('status',
                           verbose_name=_("Status"))

    def get_object_display(self, session):
        return session.description

    class Meta(object):
        name = "sessions"
        verbose_name = _("Sessions")
        table_actions = (SessionFilterAction,
                         CreateJob,
                         DeleteMultipleActions)
        row_actions = (EditSession,
                       DeleteSession,)
        footer = False
        multi_select = True
        row_class = UpdateRow
