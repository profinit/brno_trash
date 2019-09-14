#! /bin/bash

# DISCLAIMER: Hackathon spaghetti code, use at your own risk.
# Launches Open Source Routing Machine on our docker
# Based on the tutorial from https://hub.docker.com/r/osrm/osrm-backend/

wget http://download.geofabrik.de/europe/czech-republic-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/czech-republic-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/czech-republic-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/czech-republic-latest.osrm
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/czech-republic-latest.osrm
