# check for service enabled
if is_service_enabled freezer-web-ui; then
    if [[ "$1" == "source" || "`type -t install_freezer_web_ui`" != 'function' ]]; then
        # Initial source
        source $FREEZER_WEB_UI_DIR/devstack/lib/freezer-web-ui
    fi

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Freezer Web UI"
        install_freezer_client
        install_freezer_web_ui
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