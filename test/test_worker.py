#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__),
                             "..", "worker"))
import pytest

from worker import Worker, parse_configfile

class TestWorker(object):

    def get_conf(self):
        return parse_configfile(os.path.join(os.path.dirname(__file__),
                               "..", "conf", "menes.ini"))

    def test_getzipfile(self):
        conf = self.get_conf()
        w = Worker(conf)
        p = w.get_zipfile("http://localhost:9000/download/test.zip",
                        conf['app']['internaltoken'],
                        "/tmp/")
        assert p == "/tmp/test.zip"
        assert os.path.exists("/tmp/test.zip")

    def test_extract(self):
        conf = self.get_conf()
        w = Worker(conf)
        p = w.get_zipfile("http://localhost:9000/download/test.zip",
                        conf['app']['internaltoken'],
                        "/tmp/")

        d = w.extract(p, "/tmp/")
        assert d.startswith("/tmp/")
        assert os.path.isdir(d)

        shutil.rmtree(d)

    def test_do_sphinx(self):
        conf = self.get_conf()
        w = Worker(conf)
        p = w.get_zipfile("http://localhost:9000/download/test.zip",
                        conf['app']['internaltoken'],
                        "/tmp/")

        d = w.extract(p, "/tmp/")
        req = {}
        print w.do_sphinx(d, req, conf)

if __name__ == '__main__':
    pass
