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

Data (vcf files, submission manifests etc...) are all stored by the
multihash (https://github.com/jbenet/multihash) of their content.

Steward's are identified by a unique id which is the multihash
of their public encryption key. Their submission list is signed
using their private key thereby providing authentication, authorization,
and accounting.
""")


@api.route("/v0/submissions")
class SubmissionListAPI(Resource):

    def get(self):
        """
        Get list of all submissions.
        """
        steward = json.loads(g.ipfs.cat(g.ipfs.name_resolve()["Path"]))
        return jsonify(submissions=steward["submissions"])

    def post(self):
        """
        Add posted files and json manifest

        Add all posted files along with a json manifest file which
        includes the multihash for each file as well as any form fields.

        Note: May take several seconds to return as each update involves
        signing the submission list using a private key and publishing
        the new id to the rest of the steward servers.

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
        steward = json.loads(g.ipfs.cat(g.ipfs.name_resolve()["Path"]))
        if manifest_multihash not in steward["submissions"]:
            steward["submissions"].append(manifest_multihash)
            steward_multihash = g.ipfs.add(
                cStringIO.StringIO(json.dumps(steward)))[1]['Hash']
            g.ipfs.name_publish(steward_multihash)
            logging.debug("{} added to submissions list".format(manifest_multihash))
        else:
            logging.debug("{} already in submissions list".format(manifest_multihash))

        return jsonify(multihash=manifest_multihash, manifest=manifest)


if __name__ == "__main__":
    # Work around bug in flask where templates don't auto-reload
    app.jinja_env.auto_reload = True
    app.run(host="0.0.0.0", debug=True)
