#!/bin/sh
docker ps -a | grep 'test_' | awk '{print $1}' | xargs docker stop || true
docker ps -a | grep 'test_' | awk '{print $1}' | xargs docker rm || true

docker pull ipfs/go-ipfs:latest
docker pull robcurrie/cgtd:latest

for domain in cgt.ucsf.edu cgt.ucdavis.edu cgt.mskcc.org cgt.nki.nl cgt.singhealth.com.sg; do
    echo "Launching $domain"
    docker run -d --name test_ipfs_$domain ipfs/go-ipfs:latest
    sleep 10
    docker exec test_ipfs_$domain sh -c "echo '{\"domain\": \"$domain\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"
    docker run -d --name test_cgtd_$domain -p 5000 --link test_ipfs_$domain:ipfs robcurrie/cgtd:latest
done
