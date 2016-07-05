#!/bin/sh
docker ps -a | grep 'test_' | awk '{print $1}' | xargs docker stop || true
docker ps -a | grep 'test_' | awk '{print $1}' | xargs docker rm || true

domain=ucdavis.edu
for domain in cgt.lorem.edu cgt.ipsum.org cgt.dolor.com; do
    docker run -d --name test_ipfs_$domain -p 8080 -p 4001 ipfs/go-ipfs:latest
    sleep 10
    docker exec test_ipfs_$domain sh -c "echo '{\"domain\": \"cgt.$domain\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"
    docker run -d --name test_cgtd_$domain -p 5000 --link ipfs:test_ipfs_$domain robcurrie/cgtd:latest
done
