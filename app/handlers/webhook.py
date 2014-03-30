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
from raven.contrib.tornado import SentryMixin

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class WebHookHandler(tornado.web.RequestHandler, SentryMixin):
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

        print self.get_arguments()
        ret = {"ret": "ok", "token": "ss"}

        result_encoded = json.dumps(ret)
        self.write(result_encoded)
        self.finish()
        return
