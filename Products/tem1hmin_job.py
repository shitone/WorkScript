#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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
    title1 = u'江西省小时最低温' + bjnow.strftime(u'%m月%d日') + bjnow.strftime(u'%H时')  #修改相应标题
    title2 = bjnow.strftime(u'%Y年%m月%d日%H时')+u'制作'
    filehead="SURF_TEM_1HMIN_"     #修改相应文件名头
    st=filehead.split("_")
    fn = filehead + timestr + ".png"
    # x, y, z = cimissdata.get_jx_pre_1h(timestr)
    x, y, z = cimissdata.get_jx_1h('TEM_Min',timestr)
    maxtem = max(z)
    mintem = min(z)
    x, y, z = puntil.scala_net_grid(x, y, z, [50, 50], 'linear')
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.txt')
    drawmap = DrawMap(levels=list(eval(config.get('Draw', 'TEM_LEVELS'))),
                    colors=list(eval(config.get('Draw', 'TEM_COLORS'))),
                    cheight="40%",
                    unit=config.get('Draw', 'TEM_UNIT'),
                    titles=[{"title":title1, "loc":u"left"},
                            {"title":title2, "loc":u"right"}],
                    statistics=[u"极大值："+ str(maxtem) +"°C",
                             u"极小值："+ str(mintem) + "°C"],
                    save_name=os.path.join(config.get('Path', 'SOURCE_PATH'), fn))
    drawmap.draw_scala_map(x, y, z)
    is_success = False
    pftp = ProductFTP(ip=config.get('FTP', 'IP'), port=config.getint('FTP', 'Port'), user=config.get('FTP', 'User'), pwd=config.get('FTP', 'PassWord'))
    if pftp.connect():
       if pftp.upload(upload_path=st[0]+'/'+st[1]+'/'+st[2]+'/', local_path=config.get('Path', 'SOURCE_PATH'), upload_file=fn):
          is_success = True
       pftp.dis_connect()
    if is_success:
        os.remove(os.path.join(config.get('Path', 'SOURCE_PATH'), fn))
    else:
        puntil.force_move_file(config.get('Path', 'SOURCE_PATH'), 'failed', fn)


if __name__ == '__main__' :
    now = datetime.datetime.utcnow()
    if len(sys.argv) > 1:
        now = datetime.datetime.strptime(sys.argv[1], '%Y%m%d%H0000')
    _job(now)


