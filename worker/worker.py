#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import datetime
import logging
import urlparse
from ConfigParser import SafeConfigParser
import zipfile
import tempfile
import shutil
import shlex
import subprocess

import ltsvlogger
import ujson as json
import requests
import boto
from boto import sqs
from boto.sqs.message import Message

LOG_LEVEL = logging.INFO


class Worker(object):

    def __init__(self, conf):
        self.log = ltsvlogger.LTSVLoggerAdapter(logging.getLogger())
        self.queue = self.connect_sqs(conf)
        self.conf = conf

    def connect_sqs(self, conf):
        conn = sqs.connect_to_region(conf['aws']['sqs_region'])
        q = conn.create_queue(conf['aws']['sqs_queue_name'])
        # Long Polling Setting
        q.set_attribute('ReceiveMessageWaitTimeSeconds', 20)

        return q

    def main_loop(self):
        while True:
            try:
                msgs = q.get_messages()

                try:
                    m = msgs[0]
                    req = json.loads(m.get_body())
                except ValueError, e:
                    import traceback
                    m = {"e": str(e),
                         "trace": traceback.format_exc().replace("\n", " | ")}
                    self.log.error("parse sqs message failed", **m)
                    continue

                self.make_pdf(req, self.conf)

                queue.delete_message(msgs[0])

            except Exception, e:
                import traceback
                m = {"e": str(e),
                     "trace": traceback.format_exc().replace("\n", " | ")}
                self.log.error("uncaught exception", **m)
                continue

    def make_pdf(self, req, conf):
        zipfile_path = self.get_zipfile(req['url'], conf['app']['internaltoken'],
                                        conf['worker']['build_root'])

        path = self.extract(zipfile_path, conf['worker'['build_root']])
        status, ret = self.do_sphinx(path, req, conf)
        push(pdf_path, conf['worker']['finished_url'],
             req['email'], req['token'])

    def do_sphinx(self, root, req, conf):
        if os.path.exists(root) is False or os.path.isdir(root) is False:
            return (False, "{0} is not exists.".format(root))

        if "command" in req:
            # for security reason, only latexpdfja or latexpdf can be accepted
            if "latexpdfja" in req['command']:
                command = "make latexpdfja"
            else:
                command = "make latexpdf"
        else:
            command = "make latexpdf"

        args = shlex.split(command)
        p = subprocess.call(args, cwd=root)
        print "retcode", p

        if p != 0:
            error_retfile = "/"
            return (False, error_retfile)

        if os.path.exists(os.path.join(root, "build", "latex", "pdf")):
            pass

        return (True, pdfpath)

    def push(self, pdf_path, url, email, token):
        files = {'file': open(pdf_path, 'rb')}

        p = {'token': token,
             'email': email}
        r = requests.post(url, files=files, params=p)

    def get_zipfile(self, url, token, extract_root):
        chunk_size = 1024

        p = {'token': token}
        r = requests.get(url, params=p)

        urlpath = urlparse.urlparse(url).path
        filename = os.path.join(extract_root, os.path.basename(urlpath))

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

        return filename

    def get_config(self, url):
        r = requests.get(url)
        return r.json()

    def extract(self, zipfile_path, extract_root):
        dest_dir = tempfile.mkdtemp(dir=extract_root)
        with zipfile.ZipFile(zipfile_path) as zf:
            zf.extractall(dest_dir)

        return dest_dir


def set_logger(conf):
    log_dir = conf['worker']['log_directory']
    log_file_name = conf['worker']['log_filename']
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


def parse_options():
    parser = argparse.ArgumentParser(description='menes web server')
    parser.add_argument('-c', '--conf', metavar="CONFFILE", dest="file",
                        type=str, nargs=1, help='config file path',
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

    set_logger(conf)
    ensure_directory(conf['worker']['build_root'])

    w = Worker(conf)
    w.main_loop()

if __name__ == '__main__':
    main()
