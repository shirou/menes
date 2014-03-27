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
                msgs = self.queue.get_messages()

                try:
                    if len(msgs) == 0:
                        continue
                    m = msgs[0]
                    req = json.loads(m.get_body())
                except ValueError, e:
                    import traceback
                    m = {"e": str(e),
                         "trace": traceback.format_exc().replace("\n", " | ")}
                    self.log.error("parse sqs message failed", **m)
                    continue

                ret = self.make_pdf(req, self.conf)

                self.queue.delete_message(msgs[0])

            except Exception, e:
                import traceback
                m = {"e": str(e),
                     "trace": traceback.format_exc().replace("\n", " | ")}
                self.log.error("uncaught exception", **m)
                continue

    def make_pdf(self, req, conf):
        url = "/".join([conf['worker']['menes_url'], "api", "download", req['url']])

        zipfile_path = self.get_zipfile(url, conf['app']['internaltoken'],
                                        conf['worker']['build_root'])
        if zipfile_path is False:
            return False

        path = self.extract(zipfile_path, conf['worker']['build_root'])
        status, pdf_path = self.do_sphinx(path, req, conf)

        finished_url = "/".join([conf['worker']['menes_url'], "api", "finished"])
        m = {"url": finished_url}
        self.log.info("finished", **m)
        self.push(pdf_path, finished_url,
                  req['email'], req['token'], status)

    def do_sphinx(self, root, req, conf):
        if os.path.exists(root) is False or os.path.isdir(root) is False:
            return (False, "{0} is not exists.".format(root))

        if "command" in req:
            # for security reason, only latexpdfja or latexpdf can be accepted
            if "latexpdf" == req['command']:
                command = "make latexpdf"
            else:
                command = "make latexpdfja"
        else:
            command = "make latexpdfja"

        m = {"root": root, "command": command}
        self.log.info("do_sphinx started", **m)

        # append texlive_path to PATH
        env = os.environ.copy()
        env["PATH"] += ":" + conf['worker']['texlive_bin_path']

        args = shlex.split(command)
        p = subprocess.Popen(args, cwd=root, 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        rc = p.returncode

        m = {"retcode": rc}
        self.log.info("do_sphinx finished", **m)

        if rc != 0:
            error_retfile = tempfile.mkstemp(prefix="buildlog_")[1]
            m = {"retcode": rc, "error_retfile": error_retfile}
            with open(error_retfile, "w") as fp:
                fp.write(out)

            self.log.info("do_sphinx finished but failed", **m)
            return (False, error_retfile)

        pdfpath = self.find_result_pdf(root)

        if pdfpath is False:
            m = {"root": root}
            self.log.error("could not find generated pdf", **m)
            return (False, "")
        return (True, pdfpath)

    def find_result_pdf(self, root):
        nonsep = os.path.join(root, "build", "latex")
        sep = os.path.join(root, "_build", "latex")
        if os.path.exists(sep):
            d = sep
        elif os.path.exists(nonsep):
            d = nonsep
        else:
            self.log.error("could not find build dir")
            return False

        for filename in os.listdir(d):
            if filename.endswith(".pdf"):
                return os.path.join(d, filename)
        return False


    def push(self, pdf_path, url, email, token, status):
        files = {'file': open(pdf_path, 'rb')}

        p = {'token': token,
             'email': email,
             'result': status}
        r = requests.post(url, files=files, params=p)

    def get_zipfile(self, url, token, extract_root):
        chunk_size = 1024

        p = {'token': token}
        m = {"url": url, "token": token, "extract_root": extract_root}
        self.log.debug("get_zipfile", **m)
        r = requests.get(url, params=p)

        if r.status_code != 200:
            m = {"url": url, "token": token, "extract_root": extract_root,
                 "statuscode": r.status_code}
            self.log.warning("get_zipfile failed", **m)
            return False

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
