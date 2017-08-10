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

from django.conf.urls import url
from disaster_recovery.jobs import views

urlpatterns = [
    url(r'^(?P<job_id>[^/]+)?$',
        views.JobsView.as_view(),
        name='index'),

    url(r'^create/$',
        views.JobWorkflowView.as_view(),
        name='create'),

    url(r'^configure/(?P<job_id>[^/]+)?$',
        views.JobWorkflowView.as_view(),
        name='configure'),

    url(r'^edit/(?P<job_id>[^/]+)?$',
        views.EditJobWorkflowView.as_view(),
        name='edit_job'),

    url(r'^edit_actions/(?P<job_id>[^/]+)?$',
        views.ActionsInJobView.as_view(),
        name='edit_action'),
]
