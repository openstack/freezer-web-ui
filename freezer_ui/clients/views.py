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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables

from freezer_ui.clients import tables as freezer_tables
import freezer_ui.api.api as freezer_api

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    name = _("Backups")
    slug = "backups"
    table_class = freezer_tables.ClientsTable
    template_name = "freezer_ui/clients/index.html"

    def get_data(self):
        try:
            return freezer_api.client_list(self.request)
        except Exception:
            redirect = reverse("horizon:freezer_ui:clients:index")
            msg = _('Unable to retrieve details.')
            exceptions.handle(self.request, msg, redirect=redirect)
