# Cancer Gene Trust Daemon (Prototype)

A prototype web server allowing simple drag and drop submission

# Build, Debug and Test Locally

Note: All of the following use docker containers so that
the only required dependency is make and docker.

Start and initialize an ipfs database

    make stop ipfs init

Build a local cgtd docker container:

    make build

Start a cgtd container linked to the database container:

    make debug

Note: make debug runs the cgtd daemon out of the current
directory with auto-reload so you can edit, test, and debug
continuously.

Web submission form at [http://localhost:5000]

RESTful API doc at [http://localhost:5000/api]

Run pytest inside of the running cgtd container:

    make test

Note: Run in another terminal from the above make debug

# Running

Start an ipfs database, initialize the submission list, and 
start up the cgt web server:

    docker run -d --name ipfs ipfs/go-ipfs:latest
	docker exec ipfs sh -c "echo '{\"submissions\": []}' | ipfs add -q | ipfs name publish"
    docker run -d --name cgtd --link ipfs:ipfs -p 80:5000 robcurrie/cgtd:latest
