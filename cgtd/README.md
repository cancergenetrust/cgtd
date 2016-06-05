# Cancer Gene Trust Daemon (Prototype)

Flask based web server with RESTful API and simple drag and drop
web page to submit files to the CGT.

Web submission form at localhost:5000

RESTful API doc at localhost:5000/api

# Build, Debug and Test Locally

Start an ipfs node in a container:

    make ipfs

Build and start a cgtd container linked to the ipfs
container.

    make build debug

Run pytest inside of the running cgtd container:

    make test

Note: make debug runs the cgtd daemon out of the current
directory with auto-reload so you can edit, test, and debug
continuously.

# Running

Start an ipfs and cgtd container from docker hub:

    make ipfs run
