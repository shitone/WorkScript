#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib, platform
if platform.system() == 'Linux':
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
    abspath = os.path.abspath('.')
    bjnow = now + datetime.timedelta(hours=8)
    timestr = now.strftime("%Y%m%d%H0000")
    title1 = u'江西省极大风速风向' + (bjnow-datetime.timedelta(hours=1)).strftime(u'%m月%d日%H时-') + bjnow.strftime(u'%m月%d日%H时')
    title2 = u'' + bjnow.strftime(u'%Y年%m月%d日%H时制作')
    x, y, z, angle = cimissdata.get_jx_1h('WIN_Inst_Max', timestr)
    maxpre = max(z)
    minpre = min(z)
    x, y, u, v = puntil.vector_net_grid(x, y, z, angle, [20, 20], 'nn', 'JX_Lat_Lon')
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read(os.path.join(abspath, 'config.txt'))
    source_path = os.path.join(abspath, config.get('Path', 'SOURCE_PATH'))
    failed_path = os.path.join(abspath, config.get('Path', 'FAILED_PATH'))
    fn = "SURF_WIND_INSTMAX_" + timestr + "_STREAM.png"
    drawmap = DrawMap(levels=list(eval(config.get('Draw', 'WIND_LEVELS'))),
                    colors=list(eval(config.get('Draw', 'WIND_COLORS'))),
                    cheight="45%",
                    unit=config.get('Draw', 'WIND_UNIT'),
                    titles=[{"title":title1, "loc":u"left"},
                            {"title":title2, "loc":u"right"}],
                    statistics=[],
                    save_name=os.path.join(source_path, fn),
                    vector_type='stream')
    drawmap.draw_vector_map(x, y, u, v)
    is_success = False
    pftp = ProductFTP(ip=config.get('FTP', 'IP'), port=config.getint('FTP', 'Port'), user=config.get('FTP', 'User'), pwd=config.get('FTP', 'PassWord'))
    if pftp.connect():
        if pftp.upload(upload_path='SURF/WIND/INSTMAX/', local_path=source_path, upload_file=fn):
            is_success = True
        pftp.dis_connect()
    if is_success:
        os.remove(os.path.join(source_path, fn))
    else:
        puntil.force_move_file(source_path, failed_path, fn)

    fn = "SURF_WIND_INSTMAX_" + timestr + "_BARB.png"
    drawmap.save_name = os.path.join(source_path, fn)
    drawmap.vector_type = 'barb'
    drawmap.draw_vector_map(x, y, u, v)
    is_success = False
    if pftp.connect():
        if pftp.upload(upload_path='SURF/WIND/INSTMAX/', local_path=source_path, upload_file=fn):
            is_success = True
        pftp.dis_connect()
    if is_success:
        os.remove(os.path.join(source_path, fn))
    else:
        puntil.force_move_file(source_path, failed_path, fn)


if __name__ == '__main__' :
    now = datetime.datetime.utcnow()
    if len(sys.argv) == 2:
        if re.match(r'^(\w{14})$', sys.argv[1]):
            now = datetime.datetime.strptime(sys.argv[1], '%Y%m%d%H0000')
        elif os.path.isabs(sys.argv[1]):
            os.chdir(sys.argv[1])
    _job(now)