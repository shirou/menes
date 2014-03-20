#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ujson as json
import urllib
import tornado.web
import ltsvlogger
import logging
import os
import datetime
import tempfile

import boto
from boto.ses.connection import SESConnection


class FinishedHandler(tornado.web.RequestHandler):
    def auth(self, email, token):
        return True

    def initialize(self, conf):
        self.ses = self.connect_ses(conf)

    def connect_ses(self, conf):
        conn = boto.ses.connect_to_region(conf['aws']['ses_region'])

        return conn

    def post(self):
        conf = self.application.settings['config']
        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())

        email = self.get_argument("email", None)
        token = self.get_argument("token", None)
        result = self.get_argument("result", None)

        m = {"email": email, "token": token, "result": result}
        log.info("finished accepted", **m)

        if email is None:
            self.send_error(400)
            return

        if self.auth(email, token) is False:
            self.send_error(403)
            return

        if result == "True":
            suffix = ".pdf"
        else:
            suffix = ".txt"

        # Saving to tempfile
        fileinfo = self.request.files['file'][0]
        path = os.path.join(conf['app']['download_root'], token + suffix)
        fh = open(path,  'wb')
        fh.write(fileinfo['body'])

        m = {"path": path}
        log.info("save to tempfile", **m)

        result_encoded = json.dumps((True, "success"))
        self.write(result_encoded)
        self.finish()
        return
