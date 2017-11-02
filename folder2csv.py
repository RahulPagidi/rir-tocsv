#!/usr/bin/env python3
#

from __future__ import print_function, division

import csv
from collections import defaultdict
import io
import json
import magic
import os
import requests
import sys
import time


class RIRAPI(object):
    """ RIR API wrapper """
    def __init__(self, secret_key, url='https://us.api.rossum.ai'):
        self.secret_key = secret_key
        self.url = url
        self.headers = {'Authorization': 'secret_key ' + self.secret_key}

        r = requests.get(self.url + '/fields')
        self._fields = json.loads(r.text)['names']
        self._titles = json.loads(r.text)['titles']

    def post_document(self, fp):
        """ Post a new document for processing; returns a dict with 'id' mapping to the job id. """
        r = requests.post(self.url + '/document', files={'file': fp}, headers=self.headers)
        # TODO retry on 5xx
        return json.loads(r.text)

    def poll_document(self, job_id):
        """ Wait until a document with given job id is processed, then return the results dict. """
        while True:
            r = requests.get(self.url + '/document/%s' % (job_id,), headers=self.headers)
            # TODO retry on 5xx
            res = json.loads(r.text)
            if res['status'] == 'processing':
                time.sleep(1)
                continue
            else:
                return res

    def fields(self):
        return self._fields

    def field_title(self, field):
        return self._titles[field]


if __name__ == "__main__":
    ofname = sys.argv[1]
    secret_key = sys.argv[2]
    try:
        api_url = sys.argv[3]
    except:
        api_url = 'https://us.api.rossum.ai'

    api = RIRAPI(secret_key=secret_key, url=api_url)

    fieldnames = ['filename', 'status', 'preview'] + [api.field_title(f) for f in api.fields()]
    csv_fp = open(ofname, 'w')
    writer = csv.DictWriter(csv_fp, fieldnames)
    writer.writeheader()

    for path in sys.stdin:
        path = path.rstrip()
        print(path)
        fname = os.path.basename(path)

        with open(path, 'rb') as fp:
            finfo = (fname, fp, magic.detect_from_filename(path).mime_type)
            did = api.post_document(finfo)['id']
        r = api.poll_document(did)

        fstr = defaultdict(list)
        for f in r.get('fields', []):
            if isinstance(f['content'], str):
                fstr[f['title']].append(f['content'])
            else:
                fstr[f['title']].append('\n'.join('%s: %s' % (sf['title'], sf['content']) for sf in f['content']))
        print(fstr)

        row = dict(filename=fname, status=r['status'], preview=r.get('preview', ''))
        for k, vl in fstr.items():
            row[k] = '\n'.join(vl)
        writer.writerow(row)
