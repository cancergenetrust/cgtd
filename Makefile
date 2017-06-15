IPFS_VERSION := release

ifdef DOMAIN
	domain=$$DOMAIN
else
	domain="lorem.edu"
endif

up:
	docker-compose up

debug:
	docker-compose -f docker-compose-debug.yml up

down:
	docker-compose down

test:
	docker exec cgtd_cgtd_1 py.test -p no:cacheprovider -s -x

clean:
	sudo rm -rf data/*

ipfs:
	# Initializing local IPFS daemon and data directory (if not present already)..."
	if [ -d "data" ]; then \
        docker run -d --name ipfs \
            -v `pwd`/data:/data/ipfs \
            -p 8080:8080 \
            -p 4001:4001 \
            ipfs/go-ipfs:$(IPFS_VERSION) --migrate=true; \
    else \
        mkdir -p data/ipfs && chmod -R 777 data && \
        docker run -d --name ipfs \
            -v `pwd`/data:/data/ipfs \
            -p 8080:8080 \
            -p 4001:4001 \
            ipfs/go-ipfs:$(IPFS_VERSION) --init; \
	fi

reset:
	# Reset steward to no submissions and no peers and then gc
	echo "Resetting steward to no submissions, no peers, and domain = $(domain)"
	docker exec cgtd_ipfs_1 sh -c "echo '{\"domain\": \"$(domain)\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"
	# Install private network ip filters so we don't get acccused of running netscan...
	docker exec -it cgtd_ipfs_1 ipfs swarm filters add /ip4/10.0.0.0/ipcidr/8 /ip4/172.16.0.0/ipcidr/12 /ip4/192.168.0.0/ipcidr/16 /ip4/100.64.0.0/ipcidr/10

build:
	docker build -t ga4gh/cgtd .

# debug:
# 	# Run cgtd out of the current directory with reloading after code change
# 	docker stop cgtd || true && docker rm cgtd || true
# 	docker run --name cgtd --rm -it \
# 		-v `pwd`:/app:ro \
# 		--link ipfs:ipfs \
# 		-p 5000:5000 \
# 		ga4gh/cgtd uwsgi --ini uwsgi.ini --python-autoreload=1 --processes=1 --threads=1


run:
	# Run the latest version from docker hub
	# docker run -d --name cgtd --link ipfs:ipfs -p 80:5000 ga4gh/cgtd
	docker-compose up

pull:
	git pull
	docker pull ipfs/go-ipfs:$(IPFS_VERSION)
	docker pull ga4gh/cgtd:latest

populate:
	# Populate with data from the tests folder
	docker exec -it cgtd python tests/populate.py

submit:
	# Make a single test submission
	docker exec -it cgtd curl -X POST localhost:5000/v0/submissions \
        -F "a_field_name=a_field_value" \
        -F files[]=@tests/ALL/SSM-PAKMVD-09A-01D.vcf
