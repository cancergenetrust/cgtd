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

with open("VarStore.json", "r") as f:
    eth = EthJsonRpc("ethereum", 8545)
    contract = json.loads(f.read())
    # REMIND: Move this into the compile step external to the server
    contract["address"] = eth.get_contract_address(contract["transaction"])
    logging.debug("Contract at {}".format(contract["address"]))


@app.before_request
def connect_to_ipfs():
    g.ipfs = ipfsApi.Client("ipfs", 5001)
    g.eth = EthJsonRpc("ethereum", 8545)


@app.route("/")
def index():
    return app.send_static_file("transactions.html")


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
        return jsonify(accounts=g.eth.eth_accounts(),
                       coinbase=g.eth.eth_coinbase())


@api.route("/v0/submissions")
class SubmissionListAPI(Resource):

    def get(self):
        """
        Get a list of all submissions

        Returns all transactions including account and transaction
        information from the ethereum blockchain.

        Note: DApps should use the ipns list updated below in PUT
        """
        eth_filter = g.eth.eth_newFilter(from_block=0, address=contract["address"])
        submissions = [{"transaction": t['transactionHash'],
                        "account": t['data'][26:66],
                        "path": t['data'][194:-24].decode("hex")}
                       for t in g.eth.eth_getFilterLogs(eth_filter)]
        eth_filter = g.eth.eth_uninstallFilter(eth_filter)
        return jsonify(submissions=submissions)

    def post(self):
        """
        Add posted files and json manifest to ipfs and ethereum.

        Add all posted files to ipfs along with a json manifest file which
        includes the ipfs path for each file as well as any form fields.

        Then send a transaction to an ethereum contract referencing
        the ipfs path of the manifest so that the entire list of
        submissions can be assembled via an ethereum event filter.

        Returns the submission manifest, its path in ipfs and
        the ethereum transaction hash.
        """
        manifest = {"fields": {key: value for key, value in
                               request.form.items()}}
        manifest["files"] = [{"name": f.filename, "path":
                              "/ipfs/{}".format(g.ipfs.add(f)[1]["Hash"])}
                             for f in request.files.getlist("files[]")]
        logging.debug("Manifest:".format(manifest))
        path = "/ipfs/{}".format(
            g.ipfs.add(cStringIO.StringIO(json.dumps(manifest)))[1]["Hash"])
        logging.info("Path: {}".format(path))

        # REMIND: Should see if path already in ipfs or transaction
        # referencing already in block chain to avoid duplicate transactions
        logging.debug("Adding to Ethereum block chain")
        transaction = g.eth.call_with_transaction(g.eth.eth_coinbase(),
                                                  contract["address"],
                                                  'saveVar(bytes)', [path])
        logging.debug("Transaction: {}".format(transaction))
        logging.debug("Transaction on blockchain: {}".format(g.eth.eth_getTransactionByHash(transaction)))

        # NOTE: Catch 22 here in that we can't add the transaction hash
        # to the manifest as that would change the ipfs address of the
        # manifest...

        return jsonify(path=path, manifest=manifest, transaction=transaction)

    def put(self):
        """
        Update the ipns list of submissions.

        Collect all submission hashes from the ethereum event log, de-dupe,
        and publish to ipns for easy consumption by DApps.

        This uses an Ethereum filter and therefore recent
        submissions may not show up until sufficient mining has
        occurred.

        Note that the ipns update is relatively slow (multiple seconds)
        and therefore this should be called after multiple submissions
        have been made vs. per submission.
        """
        eth_filter = g.eth.eth_newFilter(from_block=0, address=contract["address"])
        transactions = [(t['transactionHash'], t['data'][26:66], t['data'][194:-24].decode("hex"))
                        for t in g.eth.eth_getFilterLogs(eth_filter)]
        eth_filter = g.eth.eth_uninstallFilter(eth_filter)
        submissions = [s for s in set(submission for transaction, account,
                                      submission in transactions)]
        logging.debug("Submissions: {}".format(submissions))
        path = g.ipfs.add(cStringIO.StringIO(json.dumps(submissions)))[1]["Hash"]
        logging.debug("Publishing {} to ipns...".format(path))
        g.ipfs.name_publish(path)
        logging.debug("Done.")
        return jsonify(submissions=submissions)


@api.route("/v0/transactions/<string:transactionHash>")
class TransactionsAPI(Resource):
    def get(self, transactionHash):
        """
        Get details on the given ethereum transaction
        """
        return jsonify(transaction=g.eth.eth_getTransactionByHash(transactionHash))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
