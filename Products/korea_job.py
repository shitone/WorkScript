#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plib import puntil
from plib.productftp import ProductFTP
import datetime, os, ConfigParser, sys, re

base_url = "http://web.kma.go.kr/repositary/image/cht/img/"
korea_dic = {
    "sfc3": "SURF_3H",
    "surf": "SURF_12H",
    "ghmd_s24": "SURF_24H",
    "up10" : "UPAR_100hPa",
    "up20" : "UPAR_200hPa",
    "up30" : "UPAR_300hPa",
    "up50" : "UPAR_500hPa",
    "up70" : "UPAR_700hPa",
    "up85" : "UPAR_850hPa",
    "up92" : "UPAR_925hPa",
}

def _job(now):
    abspath = os.path.abspath('.')
    for key in korea_dic:
        if (now.hour % 3 == 0 and key == "sfc3") or (now.hour % 12 == 0 and (key in ["surf", "ghmd_s24", "up10", "up20", "up30", "up50", "up70", "up85", "up92"])):
            ori_fn = key + "_" + now.strftime("%Y%m%d%H") + ".png"
            new_fn = "NAFP_KOR_" + korea_dic[key] + "_" + now.strftime("%Y%m%d%H0000") + ".png"
            config = ConfigParser.RawConfigParser(allow_no_value=True)
            config.read(os.path.join(abspath, 'config.txt'))
            source_path = os.path.join(abspath, config.get('Path', 'SOURCE_PATH'))
            failed_path = os.path.join(abspath, config.get('Path', 'FAILED_PATH'))
            puntil.download_from_url(base_url+ori_fn, source_path, new_fn)
            pftp = ProductFTP(ip=config.get('FTP', 'IP'), port=config.getint('FTP', 'Port'), user=config.get('FTP', 'User'),
                              pwd=config.get('FTP', 'PassWord'))
            pftp.upload_or_failed(source_path, puntil.get_upload_path_from_file(new_fn), failed_path, new_fn)


if __name__ == '__main__' :
    now = datetime.datetime.utcnow()
    if len(sys.argv) == 2:
        if re.match(r'^(\w{14})$', sys.argv[1]):
            now = datetime.datetime.strptime(sys.argv[1], '%Y%m%d%H0000')
        elif os.path.isabs(sys.argv[1]):
            os.chdir(sys.argv[1])
    _job(now)