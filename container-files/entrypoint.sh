#!/usr/bin/env bash

readonly _conf_file_name=cfg.yml
readonly _dir="$(cd "$(dirname "${0}")" && pwd)"
readonly _home_path="$(cd "${_dir}/.." && pwd)"/"${_HOME_DIR_NAME}"

kafka_dns_resolution() {
    local -r __config_file="${1}"
    local __fba_enabled="$(cat "${__config_file}" | grep fba_risk_score_fetch_enable: | awk -F'fba_risk_score_fetch_enable: ' '{print $2}')"

    if [ ! -z ${__fba_enabled} ] && [ ${__fba_enabled,,} = true ]; then
        local __kafka_server_name="$(cat "${__config_file}" | grep kafka_server_name: | awk -F'kafka_server_name: ' '{print $2}')"
        local __kafka_server_ip="$(cat "${__config_file}" | grep kafka_server_ip: | awk -F'kafka_server_ip: ' '{print $2}')"
        if [ ! -z ${__kafka_server_name} ] && [ ! -z ${__kafka_server_ip} ]; then
            local __etc_content="${__kafka_server_ip} ${__kafka_server_name}"
            cat /etc/hosts | grep -q "${__etc_content}" || bash -c 'echo '"${__etc_content}"' >> /etc/hosts'
        else
            echo "Error - Please first configure kafka_server_name and kafka_server_ip in "${__config_file}" then run this script again"
            exit 1
        fi
    fi
}

main() {
    if [ ! -z ${CONFIG_FILE_URL_LOCATION} ]; then
        wget -O "${_home_path}"/"${_conf_file_name}" "${CONFIG_FILE_URL_LOCATION}"
    fi

    local __config_file="${_home_path}"/"${_conf_file_name}"
    kafka_dns_resolution "${__config_file}"

    "${_home_path}"/src/modules/main_run.py
}

main "$@"
