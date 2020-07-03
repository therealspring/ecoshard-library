#!/bin/bash
set -a
source stac_envs &&
    docker-compose -f compose-stac-manager.yml up --remove-orphans --build expand_drive_service geoserver $@
