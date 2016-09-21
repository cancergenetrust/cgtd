# Cancer Gene Trust Daemon

Stores steward submissions in a distributed, replicated and decentralized
content addressable database.  Provides an HTML interface and RESTful API to
add, list and authenticate submissions as well as the peering relationship
between stewards.

Submissions consist of a JSON manifest with a list of fields and files. Fields
typically include de-identified clinical data (i.e. tumor type).  Files
typically consist of somatic variant vcf files.  Manifest's and files are
stored and referenced by the multihash (https://github.com/jbenet/multihash) of
their content.

Each steward has a public private key pair which is used to authenticate their
submissions. A steward's address is the multihash of their public key.

Eash steward has a top level JSON index file containing it's dns domain, list
of submissions by multihash and list of peers by address. A steward's address
resolves to the multihash of the latest version of its index.

Updates to a steward's index file are signed using their private key.  This
provides authentication and authorization for its contents as well as any other
content referenced via multihash within it including all submissions.

The current underlying implementation leverages ipfs (http://ipfs.io) for
storage and replication and ipns for address resolution and public/private key
operations.  The server is implemented using python and flask
(http://flask.pocoo.org/)

# Running a Production Instance

Note: The only dependencies for the following is make and docker.

Start the ipfs server and store in data/ and generate a default
configuration and public/private key pair in data/config:

    make ipfs 

Reset the steward's index to no submissions, no peers, and a domain of
lorem.edu:

    DOMAIN=lorem.edu make reset

Startup the cgtd container listening on port 80:

    make run

To verify both cgtd and ipfs are working you can query your steward's address:

    curl localhost/v0/address

# Making Submissions

To make a test submission:

    make submit

or via curl:

    docker exec -it cgtd curl -X POST localhost:5000/v0/submissions \
        -F "a_field_name=a_field_value" \
        -F files[]=@tests/ALL/ALL-US__TARGET-10-PAKMVD-09A-01D.vcf

To access the submission:

    curl localhost/v0/submissions/QmZwuc83iD64mvsf484aGcerUHJce1bJtf1y7AAzQDp234

Access control for mutable operations such as adding submissions or peers
is restricted to localhost as a poor mans authentication. As a result we curl
from within the cgtd container above.

To populate a server with a bunch of test data:

    make populate

Finally to see the index for you server including submissions:

    curl localhost/v0/submissions

# Build, Debug and Test Locally

Build a local cgtd docker container:

    make build

Start a cgtd container linked to the ipfs container:

    make debug

This runs the cgtd container listening on port 5000 out of the local folder so
you can make changes and it will live reload.

To run tests open another terminal window and:

    make test
