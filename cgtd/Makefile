stop:
	docker stop cgtd || true && docker rm cgtd || true
	docker stop ipfs || true && docker rm ipfs || true

clean:
	sudo rm -rf data/*

init:
	# Create a new ipfs database including public/private key
	mkdir -p data/export
	mkdir -p data/ipfs
	sudo chmod -R 777 data
	docker run -it --rm --name ipfs \
		-v `pwd`/data/ipfs:/data/ipfs \
		--entrypoint=ipfs \
		ipfs/go-ipfs:release init
	# Default config file only listens on 127.0.0.1
	docker run -it --rm --name ipfs \
		-v `pwd`/data/ipfs:/data/ipfs \
		--entrypoint=ipfs \
		ipfs/go-ipfs:release config Addresses.API /ip4/0.0.0.0/tcp/5001
	docker run -it --rm --name ipfs \
		-v `pwd`/data/ipfs:/data/ipfs \
		--entrypoint=ipfs \
		ipfs/go-ipfs:release config Addresses.Gateway /ip4/0.0.0.0/tcp/8080

ipfs:
	# Start ipfs daemon (assumes database is already initialized)
	docker run -d --name ipfs \
		-v `pwd`/data/export:/export \
		-v `pwd`/data/ipfs:/data/ipfs \
		-p 8080:8080 \
		-p 4001:4001 \
		-p 4002:4002/udp \
		ipfs/go-ipfs:release

reset:
	# Reset steward to no submissions and no peers and then gc
	docker exec ipfs sh -c "echo '{\"domain\": \"cgt.lorem.edu\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"

build:
	docker build -t cgtd .

debug:
	# Run cgtd out of the current directory with reloading after code change
	docker stop cgtd || true && docker rm cgtd || true
	docker run --name cgtd --rm -it \
		-v `pwd`:/app:ro \
		--link ipfs:ipfs \
		-p 5000:5000 \
		cgtd uwsgi --ini uwsgi.ini --python-autoreload=1 --processes=1 --threads=1

test:
	docker exec cgtd py.test -p no:cacheprovider -s -x

push:
	# Update docker hub (requires authentication)
	docker tag cgtd:latest robcurrie/cgtd:latest
	docker images | grep cgtd
	docker push robcurrie/cgtd:latest

run:
	# Run the latest version from docker hub
	docker stop cgtd || true && docker rm cgtd || true
	docker run -d --name cgtd --link ipfs:ipfs -p 80:5000 robcurrie/cgtd:latest

pull:
	git pull
	docker pull ipfs/go-ipfs:latest
	docker pull robcurrie/cgtd:latest

populate:
	# Populate with data from the tests folder
	docker exec -it cgtd python tests/demo_data.py

submit:
	# Make a single test submission
	docker exec -it cgtd curl -X POST localhost:5000/v0/submissions \
		-F "field_one=field_value_one" \
		-F "field_two=field_value_one" \
		-F files[]=@tests/ALL/ALL-US__TARGET-10-PAKHZT-03A-01R.vcf \
		-F files[]=@tests/ALL/ALL-US__TARGET-10-PAKMVD-09A-01D.vcf
	curl localhost:5000/v0/submissions/QmW6LTMSVZbMBRedZvivWcw3XnhuU4Z5ojn12FiJrG9ezx

shell:
	docker exec -it cgtd /bin/sh

update_pip_packages:
	docker exec cgtd "pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U"

update_requirements:
	docker exec cgtd pip freeze > requirements.txt
