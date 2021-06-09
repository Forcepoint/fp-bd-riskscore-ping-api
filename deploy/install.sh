#!/usr/bin/env bash

readonly _dir="$(cd "$(dirname "${0}")" && pwd)"
readonly _home_folder="$(cd "${_dir}/.." && pwd)"

install_prerequisite_centos() {
    echo "install_prerequisite_centos"
    sudo yum update -y
    sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
    sudo yum install -y python36u epel-release python-pip
}

install_prerequisite_debian() {
    echo "install_prerequisite_debian"
    sudo apt update
    sleep 5
    sudo apt install -y python3-pip python3-venv
}

# this only made to cater for centos7 and ubuntu18
main() {
    hostnamectl | grep -qi centos && install_prerequisite_centos || install_prerequisite_debian
    sleep 2
    sudo -H pip3 install -U pipenv
    sudo chmod ugo+rw "${_home_folder}"/*.yml
    sudo chmod +x "${_dir}"/*.sh
}

# main "$@"

echo "Traditional way is not supported anymore, only docker implementation is available"
