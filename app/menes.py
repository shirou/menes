#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import sys
import argparse
import ltsvlogger
import logging
import ujson as json
import datetime
from ConfigParser import SafeConfigParser


### Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen

from handlers.apply import ApplyHandler
from handlers.finished import FinishedHandler
from handlers.download import ZipDownloadHandler
from handlers.webhook import WebHookHandler


DEBUG = True
N_SERVERS = 1

LOG_LEVEL = logging.INFO


class Top(tornado.web.RequestHandler):
    def get(self):
        self.render("top.html")


def log_func(handler):
    status = handler.get_status()
    if status < 400:
        log_method = logging.info
    elif status < 500:
        log_method = logging.warn
    else:
        log_method = logging.error

    request_time = 1000.0 * handler.request.request_time()
    buf = ["status:" + str(status), "method:" + handler.request.method, "uri:" + handler.request.uri,
        "ua:" + handler.request.headers['User-Agent'],
        "host:" + handler.request.remote_ip, "reqtime:%.2fms" % request_time
    ]
    log_message = "\t".join(buf)
    log_method(log_message)


def get_application(conf, logger):
    handlers = [
        (r"/api/apply", ApplyHandler, dict(conf=conf)),
        (r"/api/finished", FinishedHandler, dict(conf=conf)),
        (r"/api/download/((.*).pdf)", tornado.web.StaticFileHandler, {"path": conf['app']['download_root']}),
        (r"/api/download/((.*).zip)", ZipDownloadHandler),
        (r"/api/webhook", WebHookHandler),
    ]

    settings = {
        "template_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "templates")),
        "static_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "static")),
        "debug": DEBUG,
        "gzip": True,
        "config": conf,
        "logger": logger,
        "log_function": log_func
        }

    application = tornado.web.Application(
        handlers, **settings
    )
    return application


def set_logger(conf):
    log_dir = conf['app']['log_directory']
    log_file_name = conf['app']['log_filename']
    log_file_path = os.sep.join([log_dir, log_file_name])
    formatter = ltsvlogger.LTSVFormatter(
        'time:%(asctime)s\tlv:%(levelname)s\tmsg:%(msg)s')

    handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        encoding='utf-8',
        when='midnight',
        backupCount=60
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    return logger

def server_start(conf):
    logger = set_logger(conf)

    ### start
    application = get_application(conf, logger)
    server = tornado.httpserver.HTTPServer(application, no_keep_alive=True)
    server.bind(int(conf['app']['port']))
    server.start(N_SERVERS)

    tornado.ioloop.IOLoop.instance().start()


def parse_options():
    parser = argparse.ArgumentParser(description='menes web server')
    parser.add_argument('-c', '--conf', metavar="CONFFILE", dest="file",
                        type=str, nargs=1, help='config file path',
                        required=True)
    parser.add_argument('-p', '--port', metavar="PORT", dest="port",
                        type=int, nargs=1, help='port number',
                        required=True)

    return parser.parse_args()


def ensure_directory(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except OSError, e:
            print e


def parse_configfile(path):
    parser = SafeConfigParser()
    parser.read(path)

    ret = {}
    for section in parser.sections():
        ret[section] = {}
        for option in parser.options(section):
            ret[section][option] = parser.get(section, option)

    return ret

def main():
    args = parse_options()
    conf = parse_configfile(args.file[0])
    conf['app']['port'] = args.port[0]

    ensure_directory(conf['app']['log_directory'])
    ensure_directory(conf['app']['download_root'])

    server_start(conf)


if __name__ == '__main__':
    main()

