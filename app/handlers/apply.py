#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import logging
import os
import datetime
import re
import tempfile
import hashlib
import random

import ltsvlogger
import ujson as json
import tornado.web
import boto
from boto.sqs.message import Message

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class ApplyHandler(tornado.web.RequestHandler):
    def auth(self, user, password):
        '''Not implemented yet'''
        return True

    def initialize(self, conf):
        self.queue = self.connect_sqs(conf)

    def connect_sqs(self, conf):
        conn = boto.sqs.connect_to_region(conf['aws']['sqs_region'])
        q = conn.create_queue(conf['aws']['sqs_queue_name'])
        # Long Polling Setting
        q.set_attribute('ReceiveMessageWaitTimeSeconds', 20)

        return q

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        conf = self.application.settings['config']
        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())

        email = self.get_argument("email", None)
        token = self.get_argument("token", "")
        language = self.get_argument("language", "")
        command = self.get_argument("command", "latexpdf")

        if email is None or not EMAIL_REGEX.match(email):
            m = {"email": email}
            log.info("email is null or invalid", **m)
            self.send_error(400)
            return

        if self.auth(email, token) is False:
            m = {"email": email, 'token': token}
            log.info("auth failed", **m)
            self.send_error(403)
            return


        # Saving to tempfile
        try:
            fileinfo = self.request.files['file'][0]

            m = hashlib.md5()
            m.update("".join([datetime.datetime.now().isoformat(),
                              email,
                              str(random.random())]))
            md5 = m.hexdigest()

            fd, path = tempfile.mkstemp(dir=conf['app']['download_root'],
                                        suffix=".zip",
                                        prefix=md5)
            fp = os.fdopen(fd, 'w')
            fp.write(fileinfo['body'])
            fp.close()
        except Exception, e:  # TODO: specify exception
            import traceback
            m = {"e": str(e),
                 "trace": traceback.format_exc().replace("\n", "|")}
            log.error("saving file exception occured", **m)
            self.send_error(500)
            return

        # post task to SQS
        try:
            q = self.connect_sqs(conf)
            m = Message()

            req = {'url': os.path.basename(path), 'email': email, 'token': md5, 'language': language}
            m.set_body(json.dumps(req))
            q.write(m)
        except Exception, e:  # TODO: specify exception
            import traceback
            m = {"e": str(e),
                 "trace": traceback.format_exc().replace("\n", "|")}
            log.error("SQS exception occured", **m)
            self.send_error(500)
            return

        ret = {"ret": "ok", "token": "ss"}

        result_encoded = json.dumps(ret)
        self.write(result_encoded)
        self.finish()
        return
