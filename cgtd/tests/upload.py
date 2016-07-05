import uuid
import json
import requests

with open("tests/ALL/ALL-US.json") as f:
    submissions = json.loads(f.read())

for name, fields in submissions.iteritems():
    print "Submitting {}".format(name)

    # Change raw_data_accession so each run adds new records
    fields["raw_data_accession"] = str(uuid.uuid4())
    print fields["raw_data_accession"]
    r = requests.post("http://localhost:5000/v0/submissions",
                      files=[
                          ("files[]", ("{}.vcf".format(name),
                                       open("tests/ALL/ALL-US__{}.vcf".format(name), "rb")))],
                      data=fields)
    assert(r.status_code == requests.codes.ok)
