# Cancer Gene Trust Daemon (Prototype)

A prototype Flask based web server allowing simple
drag and drop submission to ipfs and ethereum.

# Build, Debug and Test Locally

Note: All of the following use docker containers so that
the only required dependency is make and docker.

Start an ipfs and test ethereum chain locally in containers:

    make stop init ipfs ethereum

Build a local cgtd docker container:

    make build

Compile the ethereum contract and add it to the test chain:

    make compile

Now wait a bit for geth to mine the contract. You can see ethereum
logs by:

    docker logs -f ethereum

Start a cgtd container linked to the preceding containers:

    make debug

Note: make debug runs the cgtd daemon out of the current
directory with auto-reload so you can edit, test, and debug
continuously.

Web submission form at [http://localhost:5000/add.html]

List of transactions at [http://localhost:5000/transactions.html]

RESTful API doc at [http://localhost:5000/api]

Run pytest inside of the running cgtd container:

    make test

Note: Run in another terminal from the above make debug

# Running

Start a cgtd container linked to a local ipfs container:

    docker run -d --name ipfs ipfs/go-ipfs:latest
    docker run -d --name ethereum ethereum/client-go:latest
    docker run -d --name cgtd --link ipfs:ipfs -p 5000:5000 robcurrie/cgtd:latest

Note: You'll need to do some configuration on the ethereum container
depending on which block chain you want to use. See Makefile for some
examples. If running locally you'll need to compile and add
the contract to the block chain as above.


