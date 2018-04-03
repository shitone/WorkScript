#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import sys, re
import plib.cimissdata as cimissdata
import matplotlib.pyplot as plt
from plib.jxmicmap import DrawMap
import ConfigParser, datetime, os
from plib import puntil
from plib.productftp import ProductFTP

reload(sys)
sys.setdefaultencoding('utf-8')
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号


def _job(now):
    bjnow = now + datetime.timedelta(hours=8)
    timestr = now.strftime("%Y%m%d%H0000")
    title1 = u'江西省逐24小时降水' + bjnow.strftime(u'%m月%d日') + (bjnow-datetime.timedelta(hours=12)).strftime(u'%H时-') + bjnow.strftime(u'%H时')
    title2 = bjnow.strftime(u'%Y年%m月%d日%H时制作')
    fn = "SURF_PRE_24H_" + timestr + ".png"
    x, y, z = cimissdata.get_jx_multi_h(24, 'PRE_1h', timestr)
    maxpre = max(z)
    minpre = min(z)
    x, y, z = puntil.scala_net_grid(x, y, z, [50, 50], 'linear')
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.txt')
    drawmap = DrawMap(levels=list(eval(config.get('Draw', 'PRE_24H_LEVELS'))),
                    colors=list(eval(config.get('Draw', 'PRE_24H_COLORS'))),
                    cheight="25%",
                    unit=config.get('Draw', 'PRE_24H_UNIT'),
                    titles=[{"title":title1, "loc":u"left"},
                            {"title":title2, "loc":u"right"}],
                    statistics=[u"极大值："+ str(maxpre) +"mm",
                                u"极小值："+ str(minpre) + "mm"],
                    save_name=os.path.join(config.get('Path', 'SOURCE_PATH'), fn))
    drawmap.draw_scala_map(x, y, z)
    is_success = False
    pftp = ProductFTP(ip=config.get('FTP', 'IP'), port=config.getint('FTP', 'Port'), user=config.get('FTP', 'User'), pwd=config.get('FTP', 'PassWord'))
    if pftp.connect():
        for fn in os.listdir('source'):
            tmp_path = os.path.join('source', fn)
            if pftp.upload(upload_path='SURF/PRE/24H/', local_path='source', upload_file=fn):
                is_success = True
        pftp.dis_connect()
    if is_success:
        os.remove(os.path.join('source', fn))
    else:
        puntil.force_move_file('source', 'failed', fn)

    #日降水08-08 20-20
    if now.hour == 0 or now.hour == 12:
        title1 = (bjnow - datetime.timedelta(hours=24)).strftime(u'江西省%H时') + bjnow.strftime(u'-%H时降水%m月%d日') + bjnow.strftime(u'%m月%d日')
        title2 = bjnow.strftime(u'%Y年%m月%d日%H时制作')
        fn = "SURF_PRE_" + (bjnow - datetime.timedelta(hours=24)).strftime("%H") + bjnow.strftime("%H") + "H_" + timestr + ".png"
        drawmap = DrawMap(levels=list(eval(config.get('Draw', 'PRE_24H_LEVELS'))),
                          colors=list(eval(config.get('Draw', 'PRE_24H_COLORS'))),
                          cheight="25%",
                          unit=config.get('Draw', 'PRE_24H_UNIT'),
                          titles=[{"title": title1, "loc": u"left"},
                                  {"title": title2, "loc": u"right"}],
                          statistics=[u"极大值：" + str(maxpre) + "mm",
                                      u"极小值：" + str(minpre) + "mm"],
                          save_name=os.path.join(config.get('Path', 'SOURCE_PATH'), fn))
        drawmap.draw_scala_map(x, y, z)
        is_success = False
        pftp = ProductFTP(ip=config.get('FTP', 'IP'), port=config.getint('FTP', 'Port'), user=config.get('FTP', 'User'),
                          pwd=config.get('FTP', 'PassWord'))
        if pftp.connect():
            for fn in os.listdir('source'):
                tmp_path = os.path.join('source', fn)
                if pftp.upload(upload_path=puntil.get_upload_path_from_file(fn), local_path='source', upload_file=fn):
                    is_success = True
            pftp.dis_connect()
        if is_success:
            os.remove(os.path.join('source', fn))
        else:
            puntil.force_move_file('source', 'failed', fn)


if __name__ == '__main__' :
    now = datetime.datetime.utcnow()
    if len(sys.argv) == 2:
        if re.match(r'^(\w{14})$', sys.argv[1]):
            now = datetime.datetime.strptime(sys.argv[1], '%Y%m%d%H0000')
        elif os.path.isabs(sys.argv[1]):
            os.chdir(sys.argv[1])
    _job(now)