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

# check for service enabled
if is_service_enabled freezer-web-ui; then
    if [[ "$1" == "source" || "`type -t install_freezer_web_ui`" != 'function' ]]; then
        # Initial source
        . $FREEZER_WEB_UI_DIR/devstack/lib/freezer-web-ui
    fi

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Freezer Web UI"
        install_freezer_web_ui
        install_freezerclient
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Freezer Web UI"
        configure_freezer_web_ui
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Freezer Web UI"
        init_freezer_web_ui
        start_freezer_web_ui
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_freezer_web_ui
    fi

    if [[ "$1" == "clean" ]]; then
        cleanup_freezer_web_ui
    fi
fi
