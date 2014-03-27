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
from jinja2 import Template

MAX_BUILD_LOG_SIZE = 1024


class FinishedHandler(tornado.web.RequestHandler):
    def auth(self, email, token):
        return True

    def initialize(self, conf):
        self.ses = self.connect_ses(conf)

    def create_mail_body(self, email, url, path, language="en", result="True"):
        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())
        build_log = ""
        if result == "True":
            fname = language + ".success.j2"
        else:
            fname = language + ".failed.j2"
            with open(path) as f:
                build_log = f.read(MAX_BUILD_LOG_SIZE)

        t = os.path.join(os.path.dirname(__file__), "..", "mailtmpl", fname)

        with open(t) as f:
            t_str = f.read()
        template = Template(t_str)

        return template.render(url=url, build_log=build_log)

    def send_email(self, conn, fromaddr, toaddr, body):
        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())
        m = {"from": fromaddr, "to": toaddr}
        log.info("sending email", **m)

        subject = "menes result"
        conn.send_email(fromaddr,
                        subject,
                        body,
                        [toaddr],
                        [fromaddr])

    def connect_ses(self, conf):
        conn = boto.ses.connect_to_region(conf['aws']['ses_region'])

        return conn

    def post(self):
        conf = self.application.settings['config']
        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())

        email = self.get_argument("email", None)
        token = self.get_argument("token", None)
        language = self.get_argument("language", "en")
        result = self.get_argument("result", None)

        m = {"email": email, "token": token, "result": result}
        log.info("finished accepted", **m)

        if email is None:
            self.send_error(400)
            return

        if self.auth(email, token) is False:
            self.send_error(403)
            return

        conn = self.connect_ses(conf)

        if result == "True":
            suffix = ".pdf"
        else:
            suffix = ".txt"

        # Saving to tempfile
        fileinfo = self.request.files['file'][0]
        path = os.path.join(conf['app']['download_root'], token + suffix)
        fh = open(path,  'wb')
        fh.write(fileinfo['body'])
        fh.close()

        m = {"path": path}
        log.info("save to tempfile", **m)

        url = os.path.join(conf['worker']['menes_url'], "download", token + suffix)

        body = self.create_mail_body(email, url, path, language, result)

        fromaddr = conf['app']['from_addr']
        self.send_email(conn, fromaddr, email, body)

        m = {"email": email}
        log.info("sendmail done", **m)

        result_encoded = json.dumps((True, "success"))
        self.write(result_encoded)
        self.finish()
        return
