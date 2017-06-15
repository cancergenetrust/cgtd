ifdef DOMAIN
	domain=$$DOMAIN
else
	domain="lorem.edu"
endif

build:
	docker-compose -f docker-compose-debug.yml build

up:
	docker-compose up

debug:
	docker-compose -f docker-compose-debug.yml up

down:
	docker-compose down

clean:
	docker volume rm -q cgtd_ipfs

test:
	docker exec cgtd_cgtd_1 py.test -p no:cacheprovider -s -x

reset:
	echo "Resetting steward to no submissions, no peers, and domain = $(domain)"
	docker exec cgtd_ipfs_1 sh -c "echo '{\"domain\": \"$(domain)\", \"submissions\": [], \"peers\": []}' | ipfs add -q | xargs ipfs name publish"
	echo "Installing private network ip filters so we don't get acccused of running netscan..."
	docker exec -it cgtd_ipfs_1 ipfs swarm filters add /ip4/10.0.0.0/ipcidr/8 /ip4/172.16.0.0/ipcidr/12 /ip4/192.168.0.0/ipcidr/16 /ip4/100.64.0.0/ipcidr/10

populate:
	# Populate with data from the tests folder
	docker exec -it cgtd_cgtd_1 python tests/populate.py

submit:
	# Make a single test submission
	docker exec -it cgtd_cgtd_1 curl -X POST localhost:5000/v0/submissions \
        -F "a_field_name=a_field_value" \
        -F files[]=@tests/ALL/SSM-PAKMVD-09A-01D.vcf
