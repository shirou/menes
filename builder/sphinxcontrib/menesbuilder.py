#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import zipfile
import tempfile
import os

from sphinx.builders import Builder
from sphinx.util.osutil import ensuredir, os_path
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import bold, darkgreen, brown
from sphinx.errors import SphinxError

from docutils import nodes, writers
from docutils.nodes import Text

import requests

class MenesWriter(writers.Writer):
    def __init__(self, builder):
        self.builder = builder
        writers.Writer.__init__(self)

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

    def write(self, docname, doctree, conf):
        zipfile = self.makezip(conf['root'])

        params = urllib.urlencode({
            'email': conf['email'],
            'language': conf['language'],
            'command': conf['command'],
            })

        url = conf['menes_url']

        files = {'file': open(zipfile, 'rb')}
        r = requests.post(url, files=files, params=params)

        os.remove(zipfile)

class MenesBuilder(Builder):
    name = 'menesbuilder'
    format = 'latexpdf'

    def get_outdated_docs(self):
        return self.env.found_docs

    def get_target_uri(self, docname, typ=None):
        return ''

    def prepare_writing(self, docnames):
        self.writer = MenesWriter(self)

    def write_doc(self, docname, doctree):
        # use 2 level upper from outdir as root dir
        root = os.path.abspath(os.path.join(self.app.outdir,
                                            "..",
                                            ".."))
        conf = {
            'menes_url': self.config.menes_url,
            'command': self.config.menes_command,
            'email': self.config.menes_email,
            'language': self.config.language,
            'root': root
            }

        self.writer.write(docname, doctree, conf)


def setup(app):
    app.add_config_value('menes_url', None, '')
    app.add_config_value('menes_command', None, 'latexpdfja')
    app.add_config_value('menes_email', None, '')

    app.add_builder(MenesBuilder)
