stop:
	docker stop cgtd || true && docker rm cgtd || true
	docker stop ipfs || true && docker rm ipfs || true

clean:
	sudo rm -rf data/*
	mkdir -p data/ipfs/export
	mkdir -p data/ipfs/data
	mkdir -p data/ethereum
	sudo chmod -R 777 data

ipfs:
	mkdir -p data/ipfs/export
	mkdir -p data/ipfs/data
	docker pull ipfs/go-ipfs:latest
	docker run -d --name ipfs \
		-v `pwd`/data/ipfs/export:/export \
		-v `pwd`/data/ipfs/data:/data/ipfs \
		-p 8080:8080 \
		-p 5001:5001 \
		ipfs/go-ipfs:latest
	sleep 10
	docker exec ipfs ipfs config Datastore.StorageMax "512MB"

eth:
	docker run --rm -it \
		-v `pwd`/data/ethereum:/data \
		-v `pwd`/genesis.json:/genesis.json \
		ethereum/client-go:latest \
		--datadir /data \
		--networkid 93324 \
		--identity "Cancer Gene Trust" \
		init /genesis.json
	docker run --rm -it \
		-v `pwd`/data/ethereum:/data \
		-v `pwd`/password.txt:/password.txt \
		ethereum/client-go:latest \
		--datadir /data \
		--password password.txt \
		account new 
	docker run --rm -it \
		-v `pwd`/data/ethereum:/data \
		-v `pwd`/password.txt:/password.txt \
		ethereum/client-go:latest \
		--datadir /data \
		--rpc \
		--ipcapi  "admin,db,eth,debug,miner,net,shh,txpool,personal,web3" \
		--rpcapi "db,eth,net,web3" \
	    --nodiscover --maxpeers 0 \
		--password password.txt \
		--mine

init:
	# Initialize the ipns reference to a submission list - run AFTER ipfs is up
	docker exec ipfs sh -c "echo '{\"submissions\": []}' | ipfs add -q | ipfs name publish"

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
	docker stop cgtd || true && docker rm cgtd || true
	docker pull robcurrie/cgtd:latest
	docker run -d --name cgtd \
		--link ipfs:ipfs \
		-p 5000:5000 \
		-p 80:5000 \
		robcurrie/cgtd:latest

shell:
	docker exec -it cgtd /bin/sh

update_requirements:
	docker exec cgtd pip freeze > requirements.txt
