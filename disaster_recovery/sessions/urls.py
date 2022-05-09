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

from django.urls import re_path

from disaster_recovery.sessions import views

urlpatterns = [
    re_path(r'^(?P<session_id>[^/]+)?$',
            views.SessionsView.as_view(),
            name='index'),

    re_path(r'^attach_to_session/(?P<job_id>[^/]+)?$',
            views.AttachToSessionWorkflow.as_view(),
            name='attach'),

    re_path(r'^create/$',
            views.CreateSessionWorkflow.as_view(),
            name='create'),

    re_path(r'^edit/(?P<session_id>[^/]+)?$',
            views.CreateSessionWorkflow.as_view(),
            name='edit'),

]
