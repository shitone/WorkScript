#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, json, ConfigParser, socket, datetime, os


def get_jx_multi_h(hrs, type1h, timestr):
    x=[]
    y=[]
    z=[]
    now = datetime.datetime.strptime(timestr, "%Y%m%d%H0000")
    f = urllib.urlopen('http://10.116.32.88/stationinfo/index.php/Api/stationInfoJiangXi?type=json')
    stdata = f.read()
    st = json.loads(stdata)
    st_map = {}
    for stno in st:
        value = ['NA' for i in range(hrs)]
        st_map[stno] = {}
        st_map[stno]["lontiude"] = float(st[stno]["lontiude"])
        st_map[stno]["lattiude"] = float(st[stno]["lattiude"])
        st_map[stno]["value"] = value
    for hr in range(hrs):
        ago = now - datetime.timedelta(hours=hr)
        cdata = _get_cimiss_data_json(type1h, ago.strftime("%Y%m%d%H0000"))
        for row in cdata:
            if row["Station_Id_C"] in st_map:
                st_map[row["Station_Id_C"]]["value"][hr] = float(row[type1h])
    for stno in st_map:
        temp_v = st_map[stno]["value"]
        if 'NA' not in temp_v:
            x.append(float(st_map[stno]["lontiude"]))
            y.append(float(st_map[stno]["lattiude"]))
            if 'PRE' in type1h:
                z.append(sum(temp_v))
            elif 'TEM' in type1h:
                z.append(sum(temp_v)/hrs)
            elif 'TEM_Max' in type1h:
                z.append(max(temp_v))
            elif 'TEM_Min' in type1h:
                z.append(min(temp_v))
    return x, y, z

def get_jx_1h(type, timestr):
    x=[]
    y=[]
    z=[]
    f = urllib.urlopen('http://10.116.32.88/stationinfo/index.php/Api/stationInfoJiangXi?type=json')
    stdata = f.read()
    st = json.loads(stdata)

    cdata = _get_cimiss_data_json(type, timestr)
    for row in cdata:
        stno = row["Station_Id_C"]
        if stno in st:
            xx = float(st[stno]["lontiude"])
            yy = float(st[stno]["lattiude"])
            if xx not in x and yy not in y:
                x.append(xx)
                y.append(yy)
                z.append(float(row[type]))

    return x, y, z


def _get_cimiss_data_json(type, timestr):
    data_json = []
    cf = ConfigParser.RawConfigParser(allow_no_value=True)
    cf.read( 'config.txt')
    baseUrl="http://" + cf.get('CIMISS', 'IP') + "/cimiss-web/api?userId=" + cf.get('CIMISS', 'User') + "&pwd=" + cf.get('CIMISS', 'PassWord')
    scala_type=['TEM','TEM_Max','PRE_1h','TEM_Min','RHU','RHU_Min','PRS','PRS_Sea','PRS_Max','PRS_Min']
    if type in scala_type:
        baseUrl += "&interfaceId=getSurfEleInRegionByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,"+ type + \
                  "&times=" + timestr + "&adminCodes=360000" \
                  "&eleValueRanges=Q_"+type+":0,3,4"

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

if __name__ == '__main__' :
    x, y, z = get_jx_1h('PRE_1h', '20120101000000')