#!/usr/bin/python
import logging
import json
import cStringIO
import ipfsApi
from flask import Flask, request, jsonify, g
from flask_restplus import Api, Resource

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.before_request
def connect_to_ipfs():
    g.ipfs = ipfsApi.Client('ipfs', 5001)


@app.route('/')
def index():
    return app.send_static_file('index.html')


"""
RESTful API
"""
api = Api(app, version='v0', title='CGTD API', doc='/api',
          description="""
RESTful API for the CGT daemon
""")


@api.route('/v0/ipfs')
class IPFSAPI(Resource):
    def get(self):
        """ Return various information about ipfs """
        return jsonify(g.ipfs.id())


@api.route('/v0/submissions')
class SubmissionListAPI(Resource):

    def post(self):
        """
        Add all posted files to ipfs along with a json manifest file which
        includes the ipfs hash for each file as well as any form fields.
        Returns the ipfs hash for the manifest file.
        """
        submission = {key: value for key, value in request.form.items()}
        submission["files"] = [{"name": f.filename, "hash":
                                g.ipfs.add(f)[1]['Hash']}
                               for f in request.files.getlist("file")]
        logging.debug(submission)
        submission_hash = g.ipfs.add(
            cStringIO.StringIO(json.dumps(submission)))[1]['Hash']
        logging.info("Submitted: {}".format(submission_hash))
        return jsonify(hash=submission_hash, submission=submission)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
