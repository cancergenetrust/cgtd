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


def test_submit(server):
    r = requests.post(url_for(server, "submissions"),
                      files=[
                          ("files[]", ("ALL-US__TARGET-10-PAIXPH-03A-01D.vcf",
                                       open("tests/ALL/ALL-US__TARGET-10-PAIXPH-03A-01D.vcf", "rb"))),
                          ("files[]", ("ALL-US__TARGET-10-PAKHZT-03A-01R.vcf",
                                       open("tests/ALL/ALL-US__TARGET-10-PAKHZT-03A-01R.vcf", "rb")))],
                      data={"a_key": "a_value"})
    assert(r.status_code == requests.codes.ok)
    submission = json.loads(r.text)
    assert submission['path'] == "/ipfs/QmQH59c9hfsb8rBjQ89tS9jRfzJ3GfbCsb319h4ANaq5bh"


def test_ipns(server):
    r = requests.get(url_for(server, "ipfs"))
    assert(r.status_code == requests.codes.ok)
    ipfs = json.loads(r.text)
    # REMIND: Should use publis ipfs.io for final build testing
    r = requests.get("http://ipfs:8080/ipns/{}".format(ipfs["ID"]))
    assert(r.status_code == requests.codes.ok)
    steward = json.loads(r.text)
    assert("/ipfs/QmQH59c9hfsb8rBjQ89tS9jRfzJ3GfbCsb319h4ANaq5bh" in steward["submissions"])
