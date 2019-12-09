#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re, sqlite3

import plib.puntil as puntil
from plib.productftp import ProductFTP
import ConfigParser


def _failed_job():
    abspath = os.path.abspath('.')
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(os.path.join(abspath, 'config.txt'))
    failed_path = os.path.join(abspath, config.get('Path', 'FAILED_PATH'))
    pftp = ProductFTP(ip="10.116.32.113", port=21, user="xxzxftp", pwd="123456", timeout=5)
    if pftp.connect():
        for fn in os.listdir(failed_path):
            if (not fn.endswith('tmp')) and pftp.upload(upload_path=puntil.get_upload_path_from_file(fn), local_path=failed_path, upload_file=fn):
                os.remove(os.path.join(failed_path, fn))
        pftp.dis_connect()


def _failed_download():
    abspath = os.path.abspath('.')
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(os.path.join(abspath, 'config.txt'))
    conn = sqlite3.connect(os.path.join(abspath, 'failed.db'))
    c = conn.cursor()
    failstr = "select * from download"
    c.execute(failstr)
    rows = c.fetchall()
    for row in rows:
        new_fn = row[0]
        url = row[1]
        if puntil.download_from_url(url, os.path.join(abspath, config.get('Path', 'FAILED_PATH')), new_fn):
            sqlstr = "delete from download where filename='%s'" % (new_fn)
            c.execute(sqlstr)
    conn.commit()
    c.close()
    conn.close()




if __name__ == '__main__' :
    if len(sys.argv) == 2:
        if os.path.isabs(sys.argv[1]):
            os.chdir(sys.argv[1])
    _failed_job()
    _failed_download()