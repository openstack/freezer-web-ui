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

from django.core import exceptions as d_exceptions
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

import disaster_recovery.api.api as freezer_api


class DestinationAction(workflows.MembershipAction):
    path = forms.CharField(label=_("Destination Path"),
                           help_text=_("The path in which the backup should be"
                                       " restored"))
    backup_id = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        if 'client' in self.request.POST:
            self.cleaned_data['client'] = self.request.POST['client']
        else:
            raise d_exceptions.ValidationError(_('Client is required'))

        return self.cleaned_data

    class Meta(object):
        name = _("Destination")
        slug = "destination"


class Destination(workflows.Step):
    template_name = 'disaster_recovery/backups/restore.html'
    action_class = DestinationAction
    contributes = ('client', 'path', 'backup_id')

    def has_required_fields(self):
        return True


class Restore(workflows.Workflow):
    slug = "restore"
    name = _("Restore")
    finalize_button_name = _("Restore")
    success_url = "horizon:disaster_recovery:backups:index"
    success_message = _("Restore job successfully queued. It will get "
                        "executed soon.")
    wizard = False
    default_steps = (Destination,)

    def handle(self, request, data):
        try:
            return freezer_api.Backup(request).restore(data)
        except Exception:
            exceptions.handle(request)
            return False
