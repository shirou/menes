#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import zipfile
import tempfile

from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, os_path
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import bold, darkgreen, brown
from sphinx.errors import SphinxError

from docutils import nodes, writers
from docutils.nodes import Text

import requests


class MenesBuilder(Builder):
    name = 'menesbuilder'
    format = 'latexpdf'

    def makezip(self, fileroot):
        fd, dstpath = tempfile.mkstemp(prefix="menes_zip-", suffix=".zip")
        os.close(fd)

        zf = zipfile.ZipFile(dstpath, "w", zipfile.ZIP_DEFLATED)

        for dirname, subdirs, files in os.walk(fileroot):
            # skip build directory
            if "_build" in dirname or "build" in dirname:
                continue
            # remove top directory name
            zf.write(dirname, dirname.replace(fileroot, ""))
            for filename in files:
                fname = os.path.join(dirname, filename)
                zf.write(fname, fname.replace(fileroot, ""))

        zf.close()
        return dstpath

    def post(self, conf):
        zipfile = self.makezip(conf['root'])
        self.info("making zipfile of {}".format(conf['root']))

        params = {
            'email': conf['email'],
            'language': conf['language'],
            'command': conf['command'],
            }

        url = conf['menes_url'].rstrip("/") + "/api/apply"

        self.info("Posting to {}".format(url))

        files = {'file': open(zipfile, 'rb')}
        r = requests.post(url, files=files, params=params)

        os.remove(zipfile)

    def build(self, docnames, summary=None, method='update'):
        if self.config.menes_email is None:
            self.warn("you must set menes_email in conf.py")
            sys.exit(1)

        root = os.path.abspath(self.app.outdir)

        files = os.listdir(root)
        if "Makefile" not in files:
            self.warn("Please specify directory root where Makefile exists. \n  ex: sphinx-build -b menesbuilder source ."
            )
            sys.exit(1)

        conf = {
            'menes_url': self.config.menes_url,
            'command': self.config.menes_command,
            'email': self.config.menes_email,
            'language': self.config.language,
            'root': root
            }

        self.post(conf)

    def get_outdated_docs(self):
        return self.env.found_docs
    def get_target_uri(self, docname, typ=None):
        return ''


def setup(app):
    app.add_config_value('menes_url', 'http://menes-pdf.info', '')
    app.add_config_value('menes_command', 'latexpdf', '')
    app.add_config_value('menes_email', None, '')

    app.add_builder(MenesBuilder)
