#!/usr/bin/env bash
#
# The module name is determined by the repo directory.
#
MODULE_NAME="${1}" && \
echo "Fixing server file for module ${MODULE_NAME}" && \
SOURCE_FILE="${PWD}/lib/${MODULE_NAME}/${MODULE_NAME}Server.py" && \
SERVICE_IMPORT_SNIPPET="${PWD}/widget/scripts/service-server-snippet-0.txt" && \
SERVICE_PATH_HANDLER_SNIPPET="${PWD}/widget/scripts/service-server-snippet-1.txt" && \
sed -i.bak-$(date "+%Y-%m-%d-%H-%M-%S") \
    -e "/from configparser import ConfigParser/ r ${SERVICE_IMPORT_SNIPPET}" \
    -e "/status = '500 Internal Server Error'/ r ${SERVICE_PATH_HANDLER_SNIPPET}" \
    ${SOURCE_FILE}