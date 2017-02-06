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

import functools
import json

from django import http
from django.views import generic

from openstack_dashboard.api.rest import utils as rest_utils
from openstack_dashboard.api.rest import utils

import disaster_recovery.api.api as freezer_api


# https://github.com/tornadoweb/tornado/issues/1009
# http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx/
def prevent_json_hijacking(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        response = function(*args, **kwargs)
        if isinstance(response, utils.JSONResponse) and response.content:
            response.content = ")]}',\n" + response.content
        return response

    return wrapper


class Clients(generic.View):
    """API for nova limits."""

    @prevent_json_hijacking
    @rest_utils.ajax()
    def get(self, request, job_id=None):
        """Get all registered freezer clients"""

        # we don't have a "get all clients" api (probably for good reason) so
        # we need to resort to getting a very high number.
        clients = freezer_api.Client(request).list(json=True)
        clients = json.dumps(clients)
        return http.HttpResponse(clients, content_type="application/json")


class ActionList(generic.View):
    @prevent_json_hijacking
    @rest_utils.ajax()
    def get(self, request):
        """Get all registered freezer actions"""

        actions = freezer_api.Action(request).list(json=True)
        actions = json.dumps(actions)
        return http.HttpResponse(actions, content_type="application/json")


class Actions(generic.View):
    @prevent_json_hijacking
    @rest_utils.ajax()
    def get(self, request, job_id=None):
        actions = freezer_api.Action(request).list(json=True)
        actions_in_job = freezer_api.Job(request).actions(job_id, api=True)

        action_ids = [a['action_id'] for a in actions]
        actions_in_job_ids = [a['action_id'] for a in actions_in_job]

        available = set.difference(set(action_ids), set(actions_in_job_ids))
        selected = set.intersection(set(action_ids), set(actions_in_job_ids))

        available_actions = []
        for action in actions:
            if action['action_id'] in available:
                available_actions.append(action)

        selected_actions = []
        for action in actions_in_job:
            if action['action_id'] in selected:
                selected_actions.append(action)

        actions = {'available': available_actions,
                   'selected': selected_actions}

        actions = json.dumps(actions)
        return http.HttpResponse(actions, content_type="application/json")
