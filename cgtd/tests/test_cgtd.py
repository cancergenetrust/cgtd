import json
import requests


def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))


def test_root(server):
    r = requests.get(server)
    assert(r.status_code == requests.codes.ok)


def test_ipfs(server):
    r = requests.get(url_for(server, "ipfs"))
    assert(r.status_code == requests.codes.ok)
    ipfs = json.loads(r.text)
    assert "Addresses" in ipfs


def test_ethereum(server):
    r = requests.get(url_for(server, "ethereum"))
    assert(r.status_code == requests.codes.ok)
    ethereum = json.loads(r.text)
    assert "accounts" in ethereum


def test_submit(server):
    r = requests.post(url_for(server, "submissions"),
                      files=[
                          ("file", ("ALL-US__TARGET-10-PAIXPH-03A-01D.vcf",
                                    open("tests/ALL/ALL-US__TARGET-10-PAIXPH-03A-01D.vcf", "rb"))),
                          ("file", ("ALL-US__TARGET-10-PAKHZT-03A-01R.vcf",
                                    open("tests/ALL/ALL-US__TARGET-10-PAKHZT-03A-01R.vcf", "rb")))],
                      data={"a_key": "a_value"})
    assert r.status_code == 200
    submission = json.loads(r.text)
    assert submission['path'] == "/ipfs/QmQH59c9hfsb8rBjQ89tS9jRfzJ3GfbCsb319h4ANaq5bh"


# Return when ethereum implimentaiton is up and running
# def test_get_submissions(server):
#     r = requests.get(url_for(server, "submissions"))
#     assert(r.status_code == requests.codes.ok)
#     submissions = json.loads(r.text)["submissions"]
#     assert(len(submissions) > 0)
#     assert("/ipfs/QmQH59c9hfsb8rBjQ89tS9jRfzJ3GfbCsb319h4ANaq5bh" in submissions)
