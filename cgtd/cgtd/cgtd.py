#!/usr/bin/python
import logging
import json
import cStringIO
from functools import wraps
import uwsgi
import ipfsApi
from werkzeug.exceptions import BadRequest
from flask import Flask, request, g
from flask import Response, jsonify, render_template
import flask_restplus
from flask_restplus import Api, Resource, reqparse

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.before_request
def connect_to_ipfs():
    g.ipfs = ipfsApi.Client("ipfs", 5001)


@app.route("/")
@app.route("/stewards.html")
def stewards():
    return render_template("stewards.html", title="Stewards")


@app.route("/steward.html")
def steward():
    return render_template("steward.html", title="Steward")


@app.route("/submission.html")
def submission():
    return render_template("submission.html", title="Submission")


@app.route("/add.html")
def add():
    return render_template("add.html", title="Add")


@app.route("/data/<string:multihash>")
def ipfs(multihash):
    """
    Proxy requests for ipfs. This should only be used for debugging.
    In production a proper reverse proxy should pass ipfs requests directly
    to the ipfs daemon.
    """
    return Response(g.ipfs.cat(multihash))


"""
IPNS helpers to resolve, get and update steward index files

REMIND: Probably need to implement a lock so that only one process/thread
can update at a time.
"""


def resolve_steward(address=None):
    """
    Resolve ipns address to multihash. If address is None resolve this
    steward's address locally.
    """
    logging.debug("Resolving {}...".format(address if address else
                                           g.ipfs.id()["ID"]))
    # If resolving self use local so we get latest, otherwise will
    # use cache for other servers
    multihash = g.ipfs.name_resolve(address if address else g.ipfs.id()["ID"],
                                    opts={'local': address is None})["Path"].rsplit('/')[-1]
    logging.debug("... to {}".format(multihash))
    return multihash


def get_steward(address=None):
    """
    Return the steward's index. If address is None return this steward's index.
    """
    return json.loads(g.ipfs.cat(resolve_steward(address)))


def update_steward(steward):
    """
    Add steward record to ipfs and publish this multihash against the steward's
    address.
    """
    steward_multihash = g.ipfs.add(
        cStringIO.StringIO(json.dumps(steward, sort_keys=True)))['Hash']
    g.ipfs.name_publish(steward_multihash)
    logging.debug("Published {} to {}".format(steward_multihash,
                                              g.ipfs.id()["ID"]))


"""
Very simple api-key authorization
"""


def bad_request(message):
    e = BadRequest(message)
    e.data = {'error': message}
    return e


def requires_authorization(f):
    """
    Quick and dirty limit mutable api calls to only come from localhost.
    REMIND: Sort authorization via api key etc....
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.remote_addr != "127.0.0.1":
            e = BadRequest("Authorization required")
            raise e
        return f(*args, **kwargs)
    return decorated


"""
RESTful API
"""
api = Api(app, version="v0", title="Cancer Gene Trust API", doc="/api",
          description="""
RESTful API for the Cancer Gene Trust Daemon (cgtd)

Note that most operations involve validating public keys, signing, and
publishing the updated signature to other stewards. As a result some
operations can take several seconds if the cached resolution from pki
to multihash has expired.

Arrays are sorted by value and dictionaries by key so that
hashes are independent of the order the data is added.
""")


@api.route("/v0/")
class API(Resource):

    def get(self):
        """
        Get steward's index

        If address is missing return this stewards index.
        """
        return get_steward()


@api.route("/v0/address")
class AddressAPI(Resource):

    def get(self):
        """
        Get steward's address
        """
        return jsonify(address=g.ipfs.id()["ID"])


@api.route("/v0/peers/<string:address>")
class PeersAPI(Resource):

    @requires_authorization
    def post(self, address):
        """
        Add address to this steward's peer list
        """
        uwsgi.lock()  # make sure only one process does this at a time
        steward = get_steward()
        if address == g.ipfs.id()["ID"]:
            logging.warning("Attempt to add this steward's address to peer list")
        elif address in steward["peers"]:
            logging.info("{} already in peer list".format(address))
        else:
            # Sort so adding in different order yields the same list
            steward["peers"] = sorted(steward["peers"] + [address])
            update_steward(steward)
            logging.info("Added {} to peer list".format(address))
        uwsgi.unlock()
        return steward["peers"]

    @requires_authorization
    def delete(self, address):
        """
        Delete address from peer list
        """
        steward = get_steward()
        if address in steward["peers"]:
            # Sort so adding in different order yields the same list
            steward["peers"].remove(address)
            steward["peers"] = sorted(steward["peers"])
            update_steward(steward)
            logging.info("Removed {} from peer list".format(address))
        else:
            logging.warning("{} does not exist in peer list".format(address))

        return steward["peers"]


@api.route("/v0/stewards")
class StewardsListAPI(Resource):

    def get(self):
        """
        Get a list of all stewards including their peers and submissions.

        All submission references  are resolved so that the results may be
        cached or published back to cgt as the state of the entire network at
        this point in time. Also useful for DAPs as all content is statically
        walkable.

        Recurses one level deep into peers
        """
        us = get_steward()
        stewards = {}
        for address in us["peers"]:
            try:
                stewards[address] = get_steward(address)
            except Exception as e:
                logging.warning(
                    "Skipping peer {} problems resolving: {}".format(address, e.message))

        # Add ourselves
        stewards[g.ipfs.id()["ID"]] = us

        # One level of recursion
        for address in [peer for address, steward in stewards.iteritems()
                        for peer in steward["peers"]]:
            if address not in stewards:
                try:
                    # REMIND: We may end up trying and failing twice
                    stewards[address] = get_steward(address)
                except Exception as e:
                    logging.warning(
                        "Skipping peer {} problems resolving: {}".format(address, e.message))

        return stewards


@api.route("/v0/stewards/<string:address>")
class StewardsAPI(Resource):

    def get(self, address):
        """
        Get steward index
        """
        try:
            return get_steward(address)
        except Exception as e:
            logging.warning(
                "Skipping peer {} problems resolving: {}".format(address, e.message))
            return {'message': e.message}, 404


# Ceremony to document the publish flag nicely in swagger
submit_parser = reqparse.RequestParser()
submit_parser.add_argument("publish", type=flask_restplus.inputs.boolean,
                           default='true', location="args",
                           help="Whether to publish submission to index")


@api.route("/v0/submissions")
class SubmissionListAPI(Resource):

    def get(self):
        """
        Get list of all submissions.
        """
        steward = get_steward()
        return steward["submissions"] if "submissions" in steward else []

    @requires_authorization
    # @api.doc(params={"publish": "Publish submission to stewards index"})
    @api.expect(submit_parser)
    def post(self):
        """
        Make a submission

        Add all posted files to ipfs and then adds a json manifest
        consisting of a 'fields' dictionary made up of all the
        form fields in the POST and a 'files' array with the name
        and multihash of each posted file:

        {
            "fields": {"field_name": "field_value", ...}
            "files": [{"name": "file_name", "multihash": "ipfs_multihash of file"}...]
        }

        Passing publish=False will skip adding the submission to the
        stewards index. This is useful if you want to make a large number
        of submissions and need to avoid an ipns publish on every one.
        Note that the submission will essentially be 'dangling' and up
        to the client to keep track of and at some point add via PUT.

        Returns the multihash of the submission
        """
        manifest = {"fields": {key: value for key, value in
                               request.form.items()}}
        manifest["files"] = sorted([{"name": f.filename,
                                     "multihash": "{}".format(g.ipfs.add(f)["Hash"])}
                                    for f in request.files.getlist("files[]")],
                                   key=lambda k: k["name"])
        logging.debug("Manifest: {}".format(manifest))
        manifest_multihash = g.ipfs.add(cStringIO.StringIO(
            json.dumps(manifest, sort_keys=True)))["Hash"]
        logging.info("Manifest multihash: {}".format(manifest_multihash))

        # Update steward submissions list and publish to ipns
        args = submit_parser.parse_args()
        if args["publish"]:
            uwsgi.lock()  # make sure only one process does this at a time
            steward = get_steward()
            if manifest_multihash not in steward["submissions"]:
                steward["submissions"] = sorted(
                    steward["submissions"] + [manifest_multihash])
                update_steward(steward)
                logging.debug("{} added to submissions list".format(manifest_multihash))
            else:
                logging.debug("{} already in submissions list".format(manifest_multihash))
            uwsgi.unlock()
        else:
            logging.debug("{} NOT added to submissions list".format(manifest_multihash))

        return jsonify(multihash=manifest_multihash)

    @requires_authorization
    @api.doc(params={"submissions": "List of submission multihash's to publish"})
    def put(self):
        """
        Add a list of existing submissions

        Add the multihash of an existing submission to this server's index.
        Used with publish=False in POST to add multiple submissions
        to the index at once and therefore avoid the ipns publish on each.
        """
        uwsgi.lock()  # make sure only one process does this at a time
        steward = get_steward()
        for s in request.json["submissions"]:
            if s not in steward["submissions"]:
                logging.debug("{} added to submissions list".format(s))
                steward["submissions"] = sorted(steward["submissions"] + [s])
            else:
                logging.debug("{} already in submissions list".format(s))
        update_steward(steward)
        uwsgi.unlock()
        logging.debug("{} bulk published".format(request.json["submissions"]))
        return jsonify(request.json)


@api.route("/v0/submissions/<string:multihash>")
class SubmissionAPI(Resource):

    def get(self, multihash):
        """
        Get submission
        """
        return json.loads(g.ipfs.cat(multihash))

    @requires_authorization
    def delete(self, multihash):
        """
        Delete submission
        """
        steward = get_steward()
        if multihash in steward["submissions"]:
            steward["submissions"].remove(multihash)
            update_steward(steward)
            logging.info("{} removed from submissions".format(multihash))
            return {'message': "{} removed from submissions".format(multihash)}
        else:
            logging.warning("{} not in submissions".format(multihash))
            return {'message': "{} not in submissions".format(multihash)}

if __name__ == "__main__":
    # Work around bug in flask where templates don't auto-reload
    app.jinja_env.auto_reload = True
    app.run(host="0.0.0.0", debug=True)
