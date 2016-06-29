stop:
	docker stop cgtd || true && docker rm cgtd || true
	docker stop ipfs || true && docker rm ipfs || true

clean:
	sudo rm -rf data/*
	mkdir -p data/ipfs/export
	mkdir -p data/ipfs/data
	sudo chmod -R 777 data

ipfs:
	docker run -d --name ipfs \
		-v `pwd`/data/ipfs/export:/export \
		-v `pwd`/data/ipfs/data:/data/ipfs \
		-p 8080:8080 \
		-p 4001:4001 \
		ipfs/go-ipfs:latest
	sleep 10
	# Limit size of db for testing
	docker exec ipfs ipfs config Datastore.StorageMax "512MB"

init:
	# Initialize and empty steward information file
	docker exec ipfs sh -c "echo '{\"domain\": \"lorem.edu\", \"submissions\": [], \"stewards\": []}' | ipfs add -q | ipfs name publish"

build:
	docker build -t cgtd .

debug:
	docker stop cgtd || true && docker rm cgtd || true
	docker run --name cgtd --rm -it \
		-v `pwd`:/app:ro \
		--link ipfs:ipfs \
		-p 5000:5000 \
		cgtd python cgtd/cgtd.py

test:
	docker exec cgtd py.test -p no:cacheprovider -s -x

push:
	docker tag cgtd:latest robcurrie/cgtd:latest
	docker images | grep cgtd
	docker push robcurrie/cgtd:latest

run:
	docker run -d --name cgtd --link ipfs:ipfs -p 80:5000 robcurrie/cgtd:latest

shell:
	docker exec -it cgtd /bin/sh

update_requirements:
	docker exec cgtd pip freeze > requirements.txt
