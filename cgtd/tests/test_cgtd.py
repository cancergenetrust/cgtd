import json
import requests
import uuid
import ipfsApi

CGT_UCSC_ADDRESS = "QmaWcGneeMEx6unN8iJCVCxP7Qcv4T91pjuZj9drJrdih1"


ipfs = ipfsApi.Client("ipfs", 5001)


def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))


def test_root(server):
    r = requests.get(server)
    assert(r.status_code == requests.codes.ok)


def test_steward(server):
    r = requests.get(url_for(server, "address"))
    assert(r.status_code == requests.codes.ok)
    us = r.json()["address"]
    r = requests.get(url_for(server, "stewards/{}".format(us)))
    assert(r.status_code == requests.codes.ok)
    r = requests.get(url_for(server, "stewards/QmaWcGneeMEx6unN8iJCVCxP7Qcv4T91pjuZj9drJXXXXX"))
    assert(r.status_code != requests.codes.ok)


def test_peers(server):
    # Add UCSC if it isn't already there, delete it, and add it
    r = requests.post(url_for(server, "peers/{}".format(CGT_UCSC_ADDRESS)))
    assert(r.status_code == requests.codes.ok)

    r = requests.delete(url_for(server, "peers/{}".format(CGT_UCSC_ADDRESS)))
    assert(r.status_code == requests.codes.ok)

    r = requests.get(url_for(server, ""))
    assert(r.status_code == requests.codes.ok)
    assert(CGT_UCSC_ADDRESS not in r.json()["peers"])

    r = requests.post(url_for(server, "peers/{}".format(CGT_UCSC_ADDRESS)))
    assert(r.status_code == requests.codes.ok)

    r = requests.get(url_for(server, ""))
    assert(r.status_code == requests.codes.ok)
    assert(CGT_UCSC_ADDRESS in r.json()["peers"])


def test_submit(server):
    TEST_SUBMISSION = "QmdkAk56NgAnrgTLVBeqwofCu48m2EK5t6eaLG2u1RaaFu"

    r = requests.post(url_for(server, "submissions"),
                      files=[
                          ("files[]", ("ALL-US__TARGET-10-PAIXPH-03A-01D.vcf",
                                       open("tests/ALL/ALL-US__TARGET-10-PAIXPH-03A-01D.vcf", "rb"))),
                          ("files[]", ("ALL-US__TARGET-10-PAKHZT-03A-01R.vcf",
                                       open("tests/ALL/ALL-US__TARGET-10-PAKHZT-03A-01R.vcf", "rb")))],
                      data={"a_key": "a_value", "another_key": "another_value"})
    assert(r.status_code == requests.codes.ok)
    submission = json.loads(r.text)
    assert(submission['multihash'] == TEST_SUBMISSION)

    # Make sure order of files and/or fields doesn't matter
    r = requests.post(url_for(server, "submissions"),
                      files=[
                          ("files[]", ("ALL-US__TARGET-10-PAKHZT-03A-01R.vcf",
                                       open("tests/ALL/ALL-US__TARGET-10-PAKHZT-03A-01R.vcf", "rb"))),
                          ("files[]", ("ALL-US__TARGET-10-PAIXPH-03A-01D.vcf",
                                       open("tests/ALL/ALL-US__TARGET-10-PAIXPH-03A-01D.vcf", "rb")))],
                      data={"another_key": "another_value", "a_key": "a_value"})
    assert(r.status_code == requests.codes.ok)
    submission = json.loads(r.text)
    assert(submission['multihash'] == TEST_SUBMISSION)

    # Make sure it made it into our submissions list
    r = requests.get(url_for(server, ""))
    assert(r.status_code == requests.codes.ok)
    assert(submission["multihash"] in r.json()["submissions"])

    # And finally remove it
    r = requests.delete(url_for(server,
                                "submissions/{}".format(TEST_SUBMISSION)))
    ipfs.pin_rm(TEST_SUBMISSION)
    ipfs.repo_gc()


def test_bulk_submit(server):
    submissions = []
    # Make multiple submissions w/o publishing
    for i in range(3):
        r = requests.post(url_for(server, "submissions?publish=false"),
                          files=[
                              ("files[]", ("ALL-US__TARGET-10-PAKHZT-03A-01R.vcf",
                                           open("tests/ALL/ALL-US__TARGET-10-PAKHZT-03A-01R.vcf", "rb")))],
                          data={"id": str(uuid.uuid4())})
        assert(r.status_code == requests.codes.ok)
        submissions.append(json.loads(r.text)["multihash"])

    # Make sure none of the submissions were published
    r = requests.get(url_for(server, ""))
    assert(r.status_code == requests.codes.ok)
    for s in submissions:
        assert(s not in r.json()["submissions"])

    # Now publish them all in bulk
    r = requests.put(url_for(server, "submissions"), json={"submissions": submissions})
    assert(r.status_code == requests.codes.ok)

    # And verify they are now in the index for the steward
    r = requests.get(url_for(server, ""))
    assert(r.status_code == requests.codes.ok)
    for s in submissions:
        assert(s in r.json()["submissions"])
