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

# Running

Initialize the ipfs data store and create a public private keypair:

    make stop clean init ipfs 

Reset the steward's index to a default cgt.lorem.edu:

    make reset

Startup the server:

    make run


# Build, Debug and Test Locally

Note: All of the following use docker containers so that the only required
dependency is make and docker.

Build a local cgtd docker container:

    make build

Start a cgtd container linked to the database container:

    make debug

NOTE: Assumes you have initialized and reset the database as above

Web interface: [http://localhost:5000/api]

Direct access to content via multihash:
[http://localhost:5000/data/<multihash>]

Note: make debug runs the cgtd daemon out of the current directory with
auto-reload so you can edit, test, and debug continuously.

Run pytest inside of the running cgtd container:

    make test

Note: Run in another terminal from the above make debug
