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

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.core.urlresolvers import reverse

from horizon import tables

import disaster_recovery.api.api as freezer_api
from disaster_recovery.utils import shield


class ObjectFilterAction(tables.FilterAction):
    def allowed(self, request, datum):
        return bool(self.table.kwargs['session_id'])


def get_link(session):
    return reverse('horizon:disaster_recovery:sessions:index',
                   kwargs={'session_id': session.session_id})


class CreateJob(tables.LinkAction):
    name = "create_session"
    verbose_name = _("Create Session")
    url = "horizon:disaster_recovery:sessions:create"
    classes = ("ajax-modal",)
    icon = "plus"


class DeleteSession(tables.DeleteAction):
    name = "delete"
    classes = ("btn-danger",)
    icon = "remove"
    help_text = _("Delete sessions is not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Session",
            u"Delete Sessions",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Session",
            u"Deleted Sessions",
            count
        )

    @shield("Unable to delete session", redirect="sessions:index")
    def delete(self, request, session_id):
        return freezer_api.Session(request).delete(session_id)


class EditSession(tables.LinkAction):
    name = "edit_session"
    verbose_name = _("Edit Session")
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, datum=None):
        return reverse("horizon:disaster_recovery:sessions:edit",
                       kwargs={'session_id': datum.session_id})


class DeleteMultipleActions(DeleteSession):
    name = "delete_multiple_actions"


class DeleteJobFromSession(tables.DeleteAction):
    name = "delete_job_from_session"
    classes = ("btn-danger",)
    icon = "remove"
    help_text = _("Delete jobs is not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Job",
            u"Delete Jobs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Job",
            u"Deleted Jobs",
            count
        )

    @shield("Unable to delete session", redirect="sessions:index")
    def delete(self, request, session):
        job_id, session_id = session.split('===')
        return freezer_api.Session(request).remove_job(session_id, job_id)


class JobsTable(tables.DataTable):
    client_id = tables.Column(
        'client_id',
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
        table_actions = (ObjectFilterAction,)
        row_actions = (DeleteJobFromSession,)
        footer = False
        multi_select = True


class UpdateRow(tables.Row):
    ajax = True


class SessionsTable(tables.DataTable):
    description = tables.Column('description',
                                link=get_link,
                                verbose_name=_("Session"))

    status = tables.Column('status',
                           verbose_name=_("Status"))

    def get_object_display(self, session):
        return session.description

    class Meta(object):
        name = "sessions"
        verbose_name = _("Sessions")
        table_actions = (ObjectFilterAction,
                         CreateJob,
                         DeleteMultipleActions)
        row_actions = (EditSession,
                       DeleteSession,)
        footer = False
        multi_select = True
        row_class = UpdateRow
