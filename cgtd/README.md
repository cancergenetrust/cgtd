# Cancer Gene Trust Daemon (Prototype)

A prototype Flask based web server allowing simple
drag and drop submission to ipfs and Ethereum.

# Build, Debug and Test Locally

Start an ipfs and test Ethereum chain locally in containers:

    make stop init ipfs ethereum

Build and start a cgtd container linked to the preceding containers:

    make build debug

Web submission form at [http://localhost:5000]

RESTful API doc at [http://localhost:5000]

Note: make debug runs the cgtd daemon out of the current
directory with auto-reload so you can edit, test, and debug
continuously.

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
examples.


