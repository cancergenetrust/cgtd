import json
import requests
import argparse

parser = argparse.ArgumentParser(
    description="Upload multiple files to cgtd")
parser.add_argument('--fields', required=True,
                    help="Path to json file with fields")
parser.add_argument('--file', nargs=2, action='append',
                    metavar=('name', 'path'),
                    help="Name and path to file to submit")
args = parser.parse_args()

with open(args.fields) as f:
    fields = json.loads(f.read())

if args.file:
    print("Submitting fields and files")
    files = [("files[]", (f[0], open(f[1], "rb"))) for f in args.file]
    r = requests.post("http://localhost:5000/v0/submissions?publish=true",
                      files=files, data=fields)
else:
    print("No files, submitting only fields")
    r = requests.post("http://localhost:5000/v0/submissions?publish=true",
                      data=fields)
print(r.text)
assert(r.status_code == requests.codes.ok)
