#!/usr/bin/env python
# -*- coding: utf-8 -*-


# This test file is not used from test suite such as nose.
# just a snippet.


import os
import sys
import boto
from boto.sqs.message import Message

import ujson as json
import requests



def test_apply():
    url = "http://localhost:9000/apply"

    filename = os.path.join(os.path.dirname(__file__), "testfiles", "test.zip")
    p = {'email': "hamspam@example.jp"}


    files = {'file': open(filename, 'rb')}
    r = requests.post(url, files=files, params=p)

def test_sqs_connect():
    QUEUE_TIMEOUT = 120
    conf = {'sqs_region': "ap-northeast-1", "sqs_queue_name": "menes_queue"}

    conn = boto.sqs.connect_to_region(conf['sqs_region'])
    q = conn.create_queue(conf['sqs_queue_name'])
    # Long Polling Setting
    q.set_attribute('ReceiveMessageWaitTimeSeconds', 20)

def test_mkzip():
    import zipfile
    import tempfile

    fd, dstpath = tempfile.mkstemp(suffix=".zip")
    os.close(fd)

    fileroot = os.path.join(os.path.dirname(__file__), "testfiles", "sphinx_source")
    zf = zipfile.ZipFile(dstpath, "w", zipfile.ZIP_DEFLATED)

    for dirname, subdirs, files in os.walk(fileroot):
        # skip build directory
        if dirname == "_build" or dirname == "build":
            continue
        # remove top directory name
        zf.write(dirname, dirname.replace(fileroot, ""))
        for filename in files:
            fname = os.path.join(dirname, filename)
            zf.write(fname, fname.replace(fileroot, ""))

    zf.close()


if __name__ == '__main__':
    test_apply()
#    test_sqs_connect()
#    test_mkzip()
