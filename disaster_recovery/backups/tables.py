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

from django.core.urlresolvers import reverse
from django.utils import safestring
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.utils import functions as utils

from disaster_recovery.utils import timestamp_to_string


class Restore(tables.LinkAction):
    name = "restore"
    verbose_name = _("Restore")
    classes = ("ajax-modal", "btn-launch")
    ajax = True

    def get_link_url(self, datum=None):
        return reverse("horizon:disaster_recovery:backups:restore",
                       kwargs={'backup_id': datum.id})


class Filter(tables.FilterAction):
    filter_type = "server"
    filter_choices = (("exact", "Exact text", True),)


def icons(backup):
    result = []

    placeholder = '<i class="fa fa-fw"></i>'

    try:
        level_txt = "Level: {} ({} backup)".format(
            backup.curr_backup_level, "Full"
            if backup.curr_backup_level == 0 else "Incremental")
        result.append(
            '<i class="fa fa-fw fa-custom-number" title="{}">{}</i>'.format(
                level_txt, backup.curr_backup_level))
    except Exception:
        result.append("Level: {}".format("Full"))

    try:
        if backup.encrypted:
            result.append(
                '<i class="fa fa-lock fa-fw" title="Backup is encrypted"></i>')
    except Exception:
        result.append(placeholder)

    try:
        if int(backup.total_broken_links) > 0:
            result.append(
                '<i class="fa fa-chain-broken fa-fw" title="There are {} '
                'broken links in this backup"></i>'.format(
                    backup.total_broken_links))
    except Exception:
        result.append(placeholder)

    try:
        if backup.excluded_files:
            result.append(
                '<i class="fa fa-minus-square fa-fw" title="{} files have been'
                ' excluded from this backup"></i>'.format(
                    len(backup.excluded_files)))
    except Exception:
        result.append(placeholder)

    return safestring.mark_safe("".join(result))


def backup_detail_view(backup):
    return reverse("horizon:disaster_recovery:backups:detail",
                   kwargs={'backup_id': backup.id})


class BackupsTable(tables.DataTable):
    backup_name = tables.Column('backup_name',
                                verbose_name=_("Backup Name"),
                                link=backup_detail_view)
    hostname = tables.Column('hostname', verbose_name=_("Hostname"))
    created = tables.Column("time_stamp",
                            verbose_name=_("Created At"),
                            filters=[timestamp_to_string])
    icons = tables.Column(icons, verbose_name='Info')

    def get_pagination_string(self):
        page_size = utils.get_page_size(self.request)
        return "=".join(['offset', str(self.offset + page_size)])

    class Meta:
        name = "backups"
        verbose_name = _("Backup History")
        row_actions = (Restore,)
        table_actions = (Filter,)
        multi_select = False
