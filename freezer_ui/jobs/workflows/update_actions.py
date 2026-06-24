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

import json
import logging

from django import shortcuts
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

import freezer_ui.api.api as freezer_api

LOG = logging.getLogger(__name__)


class ActionsConfigurationAction(workflows.Action):
    actions = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    job_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    def __init__(self, request, context, *args, **kwargs):
        super().__init__(request, context, *args, **kwargs)
        self.available_actions = []
        self.selected_actions = []
        self.clients_json = "[]"
        try:
            clients = freezer_api.Client(request).list(json=True)
            self.clients_json = json.dumps(clients)
        except Exception:
            pass

        job_id = (context.get('job_id') or
                  self.initial.get('job_id', ''))
        if job_id:
            try:
                all_actions = freezer_api.Action(
                    request).list(json=True)
                actions_in_job = freezer_api.Job(
                    request).actions(job_id, api=True) or []
                in_job_ids = {
                    a['action_id'] for a in actions_in_job
                    if a and isinstance(a, dict) and 'action_id' in a
                }
                self.available_actions = [
                    a for a in all_actions
                    if (a and isinstance(a, dict) and
                        a.get('action_id') not in in_job_ids)
                ]
                self.selected_actions = actions_in_job

                # Server-side capability filtering
                job = freezer_api.Job(request).get(job_id, json=True)
                if job:
                    client_id = job.get('client_id')
                    if client_id:
                        self.available_actions = self._filter_by_capabilities(
                            request, client_id, self.available_actions)
            except Exception:
                LOG.exception(
                    'Unable to retrieve actions for job %s',
                    job_id)
        else:
            try:
                self.available_actions = freezer_api.Action(
                    request).list(json=True)
            except Exception:
                LOG.exception('Unable to retrieve actions')

    def _filter_by_capabilities(self, request, client_id, actions):
        try:
            client_info = freezer_api.Client(request).get(client_id, json=True)
            if not client_info:
                return actions
        except Exception:
            return actions

        client_props = client_info.get('client', {})
        supported_actions = client_props.get('supported_actions')
        supported_modes = client_props.get('supported_modes')
        supported_storages = client_props.get('supported_storages')
        supported_engines = client_props.get('supported_engines')

        filtered_actions = []
        for a in actions:
            freezer_action = a.get('freezer_action', {})
            act = freezer_action.get('action')
            mode = freezer_action.get('mode')
            storage = freezer_action.get('storage')
            engine = (
                freezer_action.get('engine_name') or
                freezer_action.get('engine'))

            is_compatible = True

            if act and supported_actions:
                if act not in supported_actions:
                    is_compatible = False
            if mode and supported_modes:
                if mode not in supported_modes:
                    is_compatible = False
            if storage and supported_storages:
                if storage not in supported_storages:
                    is_compatible = False
            if engine and supported_engines:
                if engine not in supported_engines:
                    is_compatible = False

            if is_compatible:
                filtered_actions.append(a)

        return filtered_actions

    def get_help_text(self, extra_context=None):
        extra_context = extra_context or {}
        extra_context['available_actions'] = self.available_actions
        extra_context['selected_actions'] = self.selected_actions
        extra_context['clients_json'] = self.clients_json
        return super().get_help_text(extra_context)

    class Meta(object):
        name = _("Actions")
        slug = "actions"


class ActionsConfiguration(workflows.Step):
    action_class = ActionsConfigurationAction
    template_name = "project/freezer-jobs/_actions.html"
    contributes = ('actions', 'job_id')


class UpdateActions(workflows.Workflow):
    slug = "update_actions"
    name = _("Update Actions")
    finalize_button_name = _("Save")
    success_message = _('Actions updated correctly.')
    failure_message = _('Unable to update actions.')
    success_url = "horizon:project:freezer-jobs:index"
    default_steps = (ActionsConfiguration,)

    def handle(self, request, context):
        try:
            if context['job_id'] != '':
                freezer_api.Job(request).update_actions(
                    context['job_id'],
                    context['actions'])
            return shortcuts.redirect(
                'horizon:project:freezer-jobs:index')
        except Exception:
            exceptions.handle(request)
            return False
