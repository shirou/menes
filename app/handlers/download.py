#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ujson as json
import urllib
import tornado.web
import ltsvlogger
import logging
import os
import datetime


logger = logging.getLogger(__name__)


class ZipDownloadHandler(tornado.web.RequestHandler):
    def get(self, filename, md5):
        conf = self.application.settings['config']

        log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())

        fileext = os.path.splitext(filename)[1]
        if not fileext:
            m = {"fileext": fileext}
            log.info("invalid fileext", **m)
            self.send_error(400)
            return

        token = self.get_argument("token", None)

        m = {"fileext": fileext, "token": token, "filename": filename}
        log.debug("download requested", **m)

        validtoken = conf['app']['internaltoken']
        # zip file is only downloadable from internal request with auth token
        if fileext == ".zip":
            if token is None or token != validtoken:
                log.info("zip fileext selected but token is none or invalid")
                self.send_error(403)
                return

        if fileext == ".zip":
            self.set_header('Content-Type', 'application/zip')
        elif fileext == '.pdf':
            self.set_header('Content-Type', 'application/zip')
        else:
            m = {"fileext": fileext}
            log.info("invalid fileext", **m)
            self.send_error(400)
            return

        download_root = conf['app']['download_root']

        filepath = os.path.join(download_root, filename)
        if os.path.exists(filepath) is False:
            m = {"fileext": fileext, "filepath": filepath}
            log.info("requested file is not found", **m)
            self.send_error(404)
            return

        f = open(filepath, "r")

        self.set_header('Content-Disposition', "attachment; filename=''".format(filename))
        self.write(f.read())
