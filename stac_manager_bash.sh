#!/bin/bash
set -a
source stac_envs &&
    docker-compose -f docker-compose.yml -f stac-bash.yml up --build --remove-orphans stac_manager
