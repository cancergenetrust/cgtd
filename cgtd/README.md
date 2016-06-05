# Cancer Gene Trust Daemon (Prototype)

A prototype Flask based web server with a RESTful API 
and simple drag and drop web page to submit files
to the ipfs based CGT database.

# Running

Start a cgtd linked to a local ipfs node:

	docker run -d --name ipfs ipfs/go-ipfs:latest
	docker run -d --name cgtd --link ipfs:ipfs -p 5000:5000 robcurrie/cgtd:latest

Web submission form at [http://localhost:5000]

RESTful API doc at [http://localhost:5000]

# Build, Debug and Test Locally

Start an ipfs node in a container:

    make ipfs

Build and start a cgtd container linked to the ipfs container.

    make build debug

Run pytest inside of the running cgtd container:

    make test

Note: make debug runs the cgtd daemon out of the current
directory with auto-reload so you can edit, test, and debug
continuously.
