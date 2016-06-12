stop:
	docker stop cgtd || true && docker rm cgtd || true
	docker stop ipfs || true && docker rm ipfs || true
	docker stop ethereum || true && docker rm ethereum || true

init:
	sudo rm -rf data/*
	mkdir -p data/ipfs/export
	mkdir -p data/ipfs/data
	mkdir -p data/ethereum
	sudo chmod -R 777 data

	# Initialize an isolated test dev node and account
	sudo rm -rf data/ethereum/*
	docker run --rm -it \
		-v `pwd`/data/ethereum:/data \
		-v `pwd`/password.txt:/password.txt \
		ethereum/client-go:latest \
		--dev \
		--datadir /data \
		--password password.txt \
		account new

ipfs:
	docker run -d --name ipfs \
		-v `pwd`/data/ipfs/export:/export \
		-v `pwd`/data/ipfs/data:/data/ipfs \
		-p 8080:8080 \
		ipfs/go-ipfs:latest
	sleep 10
	docker exec ipfs ipfs config Datastore.StorageMax "512MB"

ethereum:
	# Start isolated test dev node and start mining
	# Note static solc generated from https://github.com/rainbeam/solidity-static
	docker run -d --name ethereum \
		-v `pwd`/data/ethereum:/data \
		-v `pwd`/password.txt:/password.txt \
		-v `pwd`/solc:/usr/local/bin/solc \
		ethereum/client-go:latest \
		--rpc --rpcport 8545 --rpcaddr "0.0.0.0" --rpccorsdomain "*" \
		--datadir /data \
		--dev --nat none --nodiscover --maxpeers 0 \
		--verbosity 6 --pprof --pprofport 6110 \
		--password /password.txt \
		--unlock 0 \
		--lightkdf \
		--mine 1

build:
	docker build -t cgtd .

debug:
	docker stop cgtd || true && docker rm cgtd || true
	docker run --name cgtd --rm -it \
		-v `pwd`:/app:ro \
		--link ipfs:ipfs \
		--link ethereum:ethereum \
		-p 5000:5000 \
		cgtd python cgtd/cgtd.py

test:
	docker exec cgtd py.test -p no:cacheprovider -s -x

push:
	docker tag cgtd:latest robcurrie/cgtd:latest
	docker images | grep cgtd
	docker push robcurrie/cgtd:latest

run:
	# Start up geth connected to the test network
	docker run -d --name ethereum \
		-v `pwd`/data/ethereum:/data \
		-v ~/.cgtpassword:/password.txt \
		ethereum/client-go:latest \
		--password /password.txt \
		--rpc --rpcport 8545 --rpcaddr "0.0.0.0" --rpccorsdomain "*" \
		--testnet
	docker run -d --name cgtd \
		--link ipfs:ipfs --link ethereum:ethereum -p 80:5000
		robcurrie/cgtd:latest

shell:
	docker exec -it cgtd /bin/sh

compile:
	# Compile and submit contract to test ethereum
	docker exec cgtd python compile.py

update_requirements:
	docker exec cgtd pip freeze > requirements.txt
