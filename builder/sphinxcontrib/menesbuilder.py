#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
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

    def getTitle(self, doctree):
        ''' return first text node as Title'''
        for node in doctree.traverse(Text):
            t = node.astext()
            if t:
                return t

    def write(self, docname, doctree, conf):
        title = self.getTitle(doctree)
        params = urllib.urlencode({
            'email': conf['email'],
            'lang': conf['lang'],
            })

        url = conf['server_url'] + '/' + conf['_index']
        ret = urllib.urlopen(url, params).read()

        result = simplejson.loads(ret)

        if 'ok' not in result or result['ok'] is not True:
            print "Error"
            print result


class MenesBuilder(Builder):
    name = 'menesbuilder'
    format = 'latexpdf'
    out_suffix = ''

    def get_outdated_docs(self):
        return 'pass'

    def get_target_uri(self, docname, typ=None):
        return ''

    def prepare_writing(self, docnames):
        self.writer = MenesWriter(self)

    def write_doc(self, docname, doctree):
        conf = {
            'server_url': self.config.menes_url,
            'email': self.config.menes_email,
            'lang': self.config.lang
            }

        self.writer.write(docname, doctree, conf)


def setup(app):
    app.add_config_value('menes_url', None, '')
    app.add_config_value('menes_command', None, '')
    app.add_config_value('menes_email', None, '')

    app.add_builder(MenesBuilder)
