#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, json, ConfigParser, socket


def get_jx_1h(type, timestr):
    x=[]
    y=[]
    z=[]
    f = urllib.urlopen('http://10.116.32.88/stationinfo/index.php/Api/stationInfoLast?type=json')
    stdata = f.read()
    st = json.loads(stdata)

    cdata = _get_cimiss_data_json(type, timestr)


    for row in cdata:
        stno = row["Station_Id_C"]
        if stno in st:
            x.append(float(st[stno]["lontiude"]))
            y.append(float(st[stno]["lattiude"]))
            z.append(float(row[type]))

    return x, y, z


def _get_cimiss_data_json(type, timestr):
    data_json = []
    cf = ConfigParser.RawConfigParser(allow_no_value=True)
    cf.read('config.txt')
    baseUrl="http://" + cf.get('CIMISS', 'IP') + "/cimiss-web/api?userId=" + cf.get('CIMISS', 'User') + "&pwd=" + cf.get('CIMISS', 'PassWord')

    if type=='PRE_1h':
        baseUrl += "&interfaceId=getSurfEleInRegionByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,PRE_1h,Q_PRE_1h" \
                  "&times=" + timestr + "&adminCodes=360000" \
                  "&eleValueRanges=Q_PRE_1h:0,3,4"

    elif type=='TEM':
        baseUrl += "&interfaceId=getSurfEleInRectByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,TEM" \
                  "&times=" + timestr + \
                  "&minLat=24.2811" \
                  "&minLon=112.53" \
                  "&maxLat=30.4333" \
                  "&maxLon=119.9297" \
                  "&eleValueRanges=TEM:(-25,50)"

    baseUrl += "&dataFormat=json"

    socket.setdefaulttimeout(20)
    for i in range(3):
        req = urllib.urlopen(baseUrl)
        data = req.read()
        data = data.replace(",fieldNames=", ",\"fieldNames\":");
        data = data.replace(",fieldUnits=", ",\"fieldUnits\":");
        root = json.loads(data)
        if root['returnCode'] == str(0):
            data_json = root['DS']
        if len(data_json) > 0:
            break
    return data_json