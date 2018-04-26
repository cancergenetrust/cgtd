import json
import requests
import argparse

parser = argparse.ArgumentParser(
    description="Upload submission from submit.cancergenetrust.org")
parser.add_argument('file', nargs='?', default="submission.json",
                    help="Path to json file to submit")
args = parser.parse_args()

with open(args.file) as f:
    submission = json.loads(f.read())
submission["clinical"]["CGT Public ID"] = submission["patientId"]

if submission["genomic"]:
    print("Submitting clinical and genomic data")
    r = requests.post("http://localhost:5000/v0/submissions?publish=true",
                      files=[("files[]",
                              ("foundationone.json",
                               json.dumps(submission["genomic"], sort_keys=True)))],
                      data=submission["clinical"])
else:
    print("No genomic data, submitting only clinical")
    r = requests.post("http://localhost:5000/v0/submissions?publish=true",
                      data=submission["clinical"])
print(r.text)
assert(r.status_code == requests.codes.ok)
