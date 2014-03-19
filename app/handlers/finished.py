#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ujson as json
import urllib
import tornado.web
import ltsvlogger
import logging
import os
import datetime



class FinishedHandler(tornado.web.RequestHandler):
    def initialize(self, conf):
        self.ses = self.connect_ses(conf)

    def connect_ses(self, conf):
        conn = boto.ses.connect_to_region(conf['aws']['ses_region'])

        return q

    def post(self):
        conf = self.application.settings['config']
        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())

        args = {'email': self.get_argument("email", None),
                'token': self.get_argument("token", None)
        }

        if args['email'] is None:
            self.send_error(400)
            return

        if self.auth(args['email'], args['token']) is False:
            self.send_error(403)
            return

        # Saving to tempfile
        fileinfo = self.request.files['pdf'][0]
        path = tempfile.mkdtemp(dir=conf['app']['htdocroot'])
        fname = "src.pdf"
        fh = open(os.path.join(path, fname),  'wb')
        fh.write(fileinfo['body'])

        # post task
        ret = worker.make_pdf(args)
        ret.forget()

        result_encoded = json.dumps((True, "success"))
        self.write(result_encoded)
        self.finish()
        return
