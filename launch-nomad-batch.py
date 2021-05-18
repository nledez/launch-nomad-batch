#!/home/ubuntu/venv/bin/python
import argparse
import json
import nomad
import os
import sys
import time

from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("job_name", help="Meta args to pass")
parser.add_argument("--meta", help="Meta args to pass")
parser.add_argument("--logs", action="store_true", help="Show logs")
args = parser.parse_args()

batch_name = args.job_name

n = nomad.Nomad(host="127.0.0.1", timeout=5)

# If launch with parameter look like:
if args.meta:
    print("Launch with meta")
    meta = json.loads(args.meta)
    result = n.job.dispatch_job(batch_name, meta=meta)
else:
    print("Launch without meta")
    result = n.job.dispatch_job(batch_name)

dispatched_jobid = result['DispatchedJobID']

print('{} launched'.format(dispatched_jobid))

job_done = 0
while job_done != 1:
    summary = n.job.get_summary(dispatched_jobid)
    key = list(summary['Summary'].keys())
    status = summary['Summary'][key[0]]
    if status['Complete'] == 1:
        job_done = 1
    if status['Failed'] == 1 or status['Lost'] == 1:
        print('Error')
        sys.exit(1)
    if status['Queued'] == 1:
        print('Q', end='', flush=True)
    if status['Running'] == 1:
        print('R', end='', flush=True)
    if status['Starting'] == 1:
        print('S', end='', flush=True)
    time.sleep(1)

print('\nDone')

if args.logs:
    allocations = n.job.get_allocations(dispatched_jobid)
    for alloc in allocations:
        print(alloc['ID'])
        command = "/usr/local/bin/nomad logs {}".format(alloc['ID'])
        os.system(command)
        command = "/usr/local/bin/nomad logs -stderr {}".format(alloc['ID'])
        os.system(command)
