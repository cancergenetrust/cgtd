# Cancer Gene Trust Daemon

Manages steward submissions in an immutable content addressable database and
provides a web and RESTful api to add and browse stewards and their
submissions.

Submissions consist of a json manifest with a list of fields and files. Fields
typically include de-identified clinical data (i.e. tumor type).  Files
typically consist of somatic variant vcf files.  Manifest's and files are
stored and referenced via the by the multihash
(https://github.com/jbenet/multihash) of their content.

Steward's are identified by a unique id which is the multihash of their public
encryption key. Each steward has a top level mutable json file including its
domain, list of submissions, and list of peer stewards. Updates to this top
level steward information filed are signed using their private key.  This
provides authentication, authorization, and accounting for its contents as well
as any other content referenced via multihash within it including all
submissions.

The current underlying implementation leverages ipfs (http://ipfs.io) for
storage, replication and ipns for public/private key operations. The web and
api server are implemented using python and flask (http://flask.pocoo.org/)

# Build, Debug and Test Locally

Note: All of the following use docker containers so that the only required
dependency is make and docker.

Start and initialize an ipfs database

    make stop ipfs init

Build a local cgtd docker container:

    make build

Start a cgtd container linked to the database container:

    make debug

Web interface: [http://localhost:5000/api]

Direct access to content via multihash:
[http://localhost:5000/data/<multihash>]

Note: make debug runs the cgtd daemon out of the current directory with
auto-reload so you can edit, test, and debug continuously.

Run pytest inside of the running cgtd container:

    make test

Note: Run in another terminal from the above make debug

# Running

    make stop clean ipfs init run
