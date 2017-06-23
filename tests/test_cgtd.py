import json
import requests
import uuid
import hashlib
import ipfsapi

CGT_UCSF_ADDRESS = "QmY96gKPRbQNaSDB2cZCWBriz9n5Ryisygo8DCCuDxSFqs"


ipfs = ipfsapi.Client("ipfs", 5001)


def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))


def get_latest_index(server):
    """
    Return the latest steward's index forcing local resolution
    so we don't get a cached entry.
    """
    # multihash = ipfs.name_resolve(ipfs.id()["ID"], opts={'local': True})["Path"].rsplit('/')[-1]
    # return json.loads(ipfs.cat(multihash))
    r = requests.get(url_for(server, ""))
    assert(r.status_code == requests.codes.ok)
    return r.json()


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
    # Delete it to make sure its not there
    r = requests.delete(url_for(server, "peers/{}".format(CGT_UCSF_ADDRESS)))
    assert(CGT_UCSF_ADDRESS not in get_latest_index(server)["peers"])

    r = requests.post(url_for(server, "peers/{}".format(CGT_UCSF_ADDRESS)))
    assert(r.status_code == requests.codes.ok)
    assert(CGT_UCSF_ADDRESS in get_latest_index(server)["peers"])

    r = requests.delete(url_for(server, "peers/{}".format(CGT_UCSF_ADDRESS)))
    assert(CGT_UCSF_ADDRESS not in get_latest_index(server)["peers"])


def test_submit(server):
    TEST_SUBMISSION = "QmP6BDTNm3yTNdJQK4fJyVE91fiePovrJ8wX4ZHbh6qGjj"

    r = requests.post(url_for(server, "submissions"),
                      files=[("files[]",
                             ("SSM-PAIXPH-03A-01D.vcf",
                              open("tests/ALL/SSM-PAIXPH-03A-01D.vcf", "rb"))),
                             ("files[]", ("SSM-PAKHZT-03A-01R.vcf",
                              open("tests/ALL/SSM-PAKHZT-03A-01R.vcf", "rb")))],
                      data={"a_key": "a_value", "another_key": "another_value"})
    assert(r.status_code == requests.codes.ok)
    submission = json.loads(r.text)
    assert(submission['multihash'] == TEST_SUBMISSION)

    # Make sure order of files and/or fields doesn't matter
    r = requests.post(url_for(server, "submissions"),
                      files=[("files[]", ("SSM-PAKHZT-03A-01R.vcf",
                              open("tests/ALL/SSM-PAKHZT-03A-01R.vcf", "rb"))),
                             ("files[]", ("SSM-PAIXPH-03A-01D.vcf",
                              open("tests/ALL/SSM-PAIXPH-03A-01D.vcf", "rb")))],
                      data={"another_key": "another_value", "a_key": "a_value"})
    assert(r.status_code == requests.codes.ok)
    submission = json.loads(r.text)
    assert(submission['multihash'] == TEST_SUBMISSION)

    # Make sure it made it into our submissions list
    assert(submission["multihash"] in get_latest_index(server)["submissions"])

    # And finally remove it
    r = requests.delete(url_for(server,
                                "submissions/{}".format(TEST_SUBMISSION)))
    ipfs.pin_rm(TEST_SUBMISSION)
    ipfs.repo_gc()


def test_binary_file(server):
    r = requests.post(url_for(server, "submissions"),
                      files=[("files[]", ("DO52153_SA570901.tsv.gz",
                              open("tests/DO52153_SA570901.tsv.gz", "rb")))],
                      data={"another_key": "another_value", "a_key": "a_value"})
    assert(r.status_code == requests.codes.ok)
    r = requests.get("{}/ipfs/QmfDrcUmRbb1Uye4MDmRpHNMrAXoy8BEtJcUHHSY29h4vf".format(server))
    assert(r.status_code == requests.codes.ok)
    assert(hashlib.sha256(r.content).hexdigest() ==
           "f58e05d0e6e77697b9496c306bc7074306ebc2e072c0988328522daca9b3724c")


def test_bulk_submit(server):
    submissions = []
    # Make multiple submissions w/o publishing
    for i in range(3):
        r = requests.post(url_for(server, "submissions?publish=false"),
                          files=[("files[]",
                                  ("SSM-PAKHZT-03A-01R.vcf",
                                   open("tests/ALL/SSM-PAKHZT-03A-01R.vcf", "rb")))],
                          data={"id": str(uuid.uuid4())})
        assert(r.status_code == requests.codes.ok)
        submissions.append(json.loads(r.text)["multihash"])

    # Make sure none of the submissions were published
    index = get_latest_index(server)
    for s in submissions:
        assert(s not in index["submissions"])

    # Now publish them all in bulk
    r = requests.put(url_for(server, "submissions"), json={"submissions": submissions})
    assert(r.status_code == requests.codes.ok)

    # And verify they are now in the index for the steward
    index = get_latest_index(server)
    for s in submissions:
        assert(s in index["submissions"])
