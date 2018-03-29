#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import plib.puntil as puntil
from plib.productftp import ProductFTP
import ConfigParser


def _failed_job():
    pftp = ProductFTP(ip="10.116.32.113", port=21, user="xxzxftp", pwd="123456", timeout=5)
    if pftp.connect():
        for fn in os.listdir('failed'):
            if pftp.upload(upload_path=puntil.get_upload_path_from_file(fn), local_path='failed', upload_file=fn):
                os.remove(os.path.join('failed', fn))
        pftp.dis_connect()