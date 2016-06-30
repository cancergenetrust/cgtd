#!/usr/bin/python
import logging
import json
import cStringIO
import requests
import ipfsApi
from flask import Flask, request, jsonify, render_template, g
from flask import Response, stream_with_context
from flask_restplus import Api, Resource

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.before_request
def connect_to_ipfs():
    g.ipfs = ipfsApi.Client("ipfs", 5001)


@app.route("/")
@app.route("/submissions.html")
def submissions():
    return render_template("submissions.html", title="Submissions")


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
    req = requests.get("http://ipfs:8080/ipfs/{}".format(multihash), stream=True)
    return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])


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
""")


def resolve(name):
    return g.ipfs.name_resolve(name)["Path"].rsplit('/')[-1]


def get_steward(name=None):
    return json.loads(g.ipfs.cat(resolve(name)))


def update_steward(steward):
    steward_multihash = g.ipfs.add(
        cStringIO.StringIO(json.dumps(steward)))[1]['Hash']
    g.ipfs.name_publish(steward_multihash)


@api.route("/v0/peers")
class PeerListAPI(Resource):

    def get(self):
        """
        Get a dereferenced list of all peers and submissions including
        this server.

        All references are multihashes vs. ids. The results may be cached
        or published back to cgt as the state of the entire network
        at this point in time. Also useful for DAPs as all content
        is statically walkable.
        """
        steward = get_steward()
        stewards = [steward(name) for name in steward["peers"]]
        stewards.append(steward)
        return jsonify(stewards=stewards)

    def post(self):
        """
        Add peer
        """
        new_id = request.form["id"]
        steward = get_steward()
        if new_id not in steward["peers"]:
            # Sort so adding in different order yields the same list
            steward["peers"].append(new_id)
            steward["peers"] = sorted(steward["peers"])
            update_steward(steward)
            logging.info("Added new peers: {}".format(new_id))
        else:
            logging.info("Peer {} already exists".format(new_id))
        return jsonify(steward=steward)


@api.route("/v0/submissions")
class SubmissionListAPI(Resource):

    def get(self):
        """
        Get list of all submissions.
        """
        steward = get_steward()
        return jsonify(submissions=steward["submissions"]
                       if "submissions" in steward else [])

    def post(self):
        """
        Add posted files and json manifest

        Add all posted files along with a json manifest file which
        includes the multihash for each file as well as any form fields.


        Returns the submission manifest and its multihash
        """
        manifest = {"fields": {key: value for key, value in
                               request.form.items()}}
        manifest["files"] = [{"name": f.filename, "multihash":
                              "{}".format(g.ipfs.add(f)[1]["Hash"])}
                             for f in request.files.getlist("files[]")]
        logging.debug("Manifest: {}".format(manifest))
        manifest_multihash = g.ipfs.add(cStringIO.StringIO(json.dumps(manifest)))[1]["Hash"]
        logging.info("Manifest multihash: {}".format(manifest_multihash))

        # Update steward submissions list and publish to ipns
        # REMIND: Do we need to synchronize this explicitly?
        steward = get_steward()
        if manifest_multihash not in steward["submissions"]:
            steward["submissions"].append(manifest_multihash)
            update_steward(steward)
            logging.debug("{} added to submissions list".format(manifest_multihash))
        else:
            logging.debug("{} already in submissions list".format(manifest_multihash))

        return jsonify(multihash=manifest_multihash, manifest=manifest)


if __name__ == "__main__":
    # Work around bug in flask where templates don't auto-reload
    app.jinja_env.auto_reload = True
    app.run(host="0.0.0.0", debug=True)
