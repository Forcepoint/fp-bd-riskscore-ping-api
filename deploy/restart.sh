#!/usr/bin/env bash

main() {
    sudo systemctl restart fp-risk-score-api.service
}

main "$@"
