stop:
	docker stop cgtd || true && docker rm cgtd || true
	docker stop ipfs || true && docker rm ipfs || true

clean:
	sudo rm -rf data/*
	mkdir -p data/export
	mkdir -p data/ipfs
	sudo chmod -R 777 data

init:
	# Create a new ipfs database including public/private key
	docker run -it --rm --name ipfs \
		-v `pwd`/data/export:/export \
		-v `pwd`/data/ipfs:/data/ipfs \
		--entrypoint=ipfs \
		ipfs/go-ipfs:release init

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
	docker stop cgtd || true && docker rm cgtd || true
	docker run --name cgtd --rm -it \
		-v `pwd`:/app:ro \
		--link ipfs:ipfs \
		-p 5000:5000 \
		cgtd uwsgi --ini uwsgi.ini --python-autoreload=1 --processes=1 --threads=1

test:
	docker exec cgtd py.test -p no:cacheprovider -s -x

push:
	docker tag cgtd:latest robcurrie/cgtd:latest
	docker images | grep cgtd
	docker push robcurrie/cgtd:latest

run:
	docker stop cgtd || true && docker rm cgtd || true
	docker run -d --name cgtd --link ipfs:ipfs -p 80:5000 robcurrie/cgtd:latest

pull:
	git pull
	docker pull ipfs/go-ipfs:latest
	docker pull robcurrie/cgtd:latest

shell:
	docker exec -it cgtd /bin/sh

update_pip_packages:
	docker exec cgtd "pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U"

update_requirements:
	docker exec cgtd pip freeze > requirements.txt

