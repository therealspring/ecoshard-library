#!/bin/bash
# Startup script for GeoServer Node

docker pull us.gcr.io/salo-api/stac-geoserver-container:latest
mkdir -p /mnt/geoserver_data
cd /home/rich/stac-geoserver-api/
git pull
nohup python3 resize_and_flush_service.py --mem_size 12G --snapshot-pattern geoserver-data-disk* --image_name us.gcr.io/salo-api/stac-geoserver-container:latest --check_time 300 --container_name geoserver_node --app_port 8081 --disk_pattern geoserver-data-disk* --mount_point /mnt/geoserver_data > /home/rich/resize_and_flush_service_log.txt &
