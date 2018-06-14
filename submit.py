import os
import json
import requests
import argparse

parser = argparse.ArgumentParser(
    description="Make a submission to a CGT server via REST API")
parser.add_argument('--fields', required=True,
                    help="Path to json file with fields")
parser.add_argument('--files', nargs='+', action='append',
                    metavar=('name', 'path'),
                    help="Name and path to files to submit")
args = parser.parse_args()

with open(args.fields) as f:
    fields = json.loads(f.read())

if args.files:
    paths = [f for l in args.files for f in l]
    files = [("files[]", (os.path.basename(p), open(p, "rb"))) for p in paths]
    print("Submitting fields and {} files".format(len(files)))
    # for f in files:
    #     assert(f[1][0].endswith(".dcm"))
    #     print("|{}|".format(f[1][0]))
    # exit()
    r = requests.post("http://localhost:5000/v0/submissions?publish=true",
                      files=files, data=fields)
else:
    print("No files, submitting only fields")
    r = requests.post("http://localhost:5000/v0/submissions?publish=true",
                      data=fields)
print(r.text)
assert(r.status_code == requests.codes.ok)
