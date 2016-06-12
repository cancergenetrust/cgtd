#!/usr/bin/python
import logging
import json
import cStringIO
import ipfsApi
from ethjsonrpc import EthJsonRpc
from flask import Flask, request, jsonify, g
from flask_restplus import Api, Resource

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.before_request
def connect_to_ipfs():
    g.ipfs = ipfsApi.Client("ipfs", 5001)
    g.eth = EthJsonRpc("ethereum", 8545)


@app.route("/")
def index():
    return app.send_static_file("index.html")


"""
RESTful API
"""
api = Api(app, version="v0", title="Cancer Gene Trust API", doc="/api",
          description="""
RESTful API for the Cancer Gene Trust Daemon (cgtd)
""")


@api.route("/v0/ipfs")
class IPFSAPI(Resource):
    def get(self):
        """ Return ipfs id. """
        return jsonify(g.ipfs.id())


@api.route("/v0/ethereum")
class EthereumAPI(Resource):
    def get(self):
        """ Return ethereum account. """
        return jsonify(accounts=g.eth.eth_accounts())


@api.route("/v0/submissions")
class SubmissionListAPI(Resource):

    def get(self):
        """
        Get a list of all submissions from this steward
        """
        steward = json.loads(g.ipfs.cat(g.ipfs.name_resolve()["Path"]))
        return jsonify(submissions=steward["submissions"])

    def post(self):
        """
        Add posted files and json manifest to ipfs.

        Add all posted files to ipfs along with a json manifest file which
        includes the ipfs path for each file as well as any form fields.

        Returns the submission manifest and its path in ipfs.
        """
        manifest = {"fields": {key: value for key, value in
                               request.form.items()}}
        manifest["files"] = [{"name": f.filename, "path":
                              "/ipfs/{}".format(g.ipfs.add(f)[1]["Hash"])}
                             for f in request.files.getlist("file")]
        logging.debug("Manifest:".format(manifest))
        path = "/ipfs/{}".format(
            g.ipfs.add(cStringIO.StringIO(json.dumps(manifest)))[1]["Hash"])
        logging.info("Path: {}".format(path))

        # Update steward submissions list and publish to ipns
        # steward = json.loads(g.ipfs.cat(g.ipfs.name_resolve()["Path"]))
        # if path not in steward["submissions"]:
        #     steward["submissions"].append(path)
        #     steward_path = g.ipfs.add(
        #         cStringIO.StringIO(json.dumps(steward)))[1]["Hash"]
        #     g.ipfs.name_publish(steward_path)
        #     logging.debug("{} added to submissions list".format(path))
        # else:
        #     logging.debug("{} already in submissions list".format(path))

        return jsonify(path=path, manifest=manifest)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
