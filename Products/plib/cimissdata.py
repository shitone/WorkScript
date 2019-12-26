#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, json, ConfigParser, socket, datetime, os


scala_type = {'SURF':
                  ['TEM', 'TEM_Max', 'PRE_1h', 'TEM_Min', 'RHU', 'RHU_Min', 'PRS', 'PRS_Sea', 'PRS_Max', 'PRS_Min',
                   'GST','GST_Max', 'GST_Min', 'GST_5cm', 'GST_10cm', 'GST_15cm', 'GST_20cm', 'GST_40cm', 'GST_80cm', 'GST_160cm', 'GST_320cm'],
              'AGME':
                  ['SRHU_10','SRHU_20','SRHU_30','SRHU_40','SRHU_50','SRHU_60','SRHU_70','SRHU_80','SRHU_90','SRHU_100']
              }
vector_type = {
    'WIN_Avg_2mi': ['WIN_S_Avg_2mi', 'WIN_D_Avg_2mi'],
    'WIN_Avg_10mi': ['WIN_S_Avg_10mi', 'WIN_D_Avg_10mi'],
    'WIND_Max': ['WIN_S_Max', 'WIN_D_S_Max'],
    'WIN_Inst': ['WIN_S_INST', 'WIN_D_INST'],
    'WIN_Inst_Max': ['WIN_S_Inst_Max', 'WIN_D_INST_Max']
}


def get_jx_multi_h(hrs, type1h, timestr, step=1):
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
        ago = now - datetime.timedelta(hours=hr*step)
        cdata = _get_cimiss_data_json(type1h, ago.strftime("%Y%m%d%H0000"))
        for row in cdata:
            if row["Station_Id_C"] in st_map:
                st_map[row["Station_Id_C"]]["value"][hr] = float(row[type1h])
    for stno in st_map:
        temp_v = st_map[stno]["value"]
        if 'NA' not in temp_v:
            xx = float(st_map[stno]["lontiude"])
            yy = float(st_map[stno]["lattiude"])
            if xx not in x and yy not in y and xx >= 113.5 and xx <= 118.5 and yy >= 24.4 and yy <= 30.1:
                x.append(xx)
                y.append(yy)
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
    x = []
    y = []
    z = []
    angle = []
    global scala_type, vector_type
    f = urllib.urlopen('http://10.116.32.88/stationinfo/index.php/Api/stationInfoJiangXi?type=json')
    stdata = f.read()
    st = json.loads(stdata)

    cdata = _get_cimiss_data_json(type, timestr)
    for row in cdata:
        stno = row["Station_Id_C"]
        if stno in st:
            xx = float(st[stno]["lontiude"])
            yy = float(st[stno]["lattiude"])
            if xx not in x and yy not in y and xx >= 113.5 and xx <= 118.5 and yy >= 24.4 and yy <= 30.1:
                x.append(xx)
                y.append(yy)
                if type in scala_type['SURF']:
                    z.append(float(row[type]))
                elif type in scala_type['AGME']:
                    z.append(float(row[type.split('_')[0]]))
                elif type in vector_type:
                    z.append(float(row[vector_type[type][0]]))
                    angle.append(float(row[vector_type[type][1]]))

    return x, y, z, angle


def _get_cimiss_data_json(type, timestr):
    data_json = []
    cf = ConfigParser.RawConfigParser(allow_no_value=True)
    cf.read( 'config.txt')
    baseUrl="http://" + cf.get('CIMISS', 'IP') + "/cimiss-web/api?userId=" + cf.get('CIMISS', 'User') + "&pwd=" + cf.get('CIMISS', 'PassWord')
    global scala_type, vector_type
    if type in scala_type['SURF']:
        baseUrl += "&interfaceId=getSurfEleInRegionByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,"+ type + \
                  "&times=" + timestr + "&adminCodes=360000" \
                  "&eleValueRanges=Q_"+type+":0,3,4"
        baseUrl += _add_value_range(type)
    elif type in scala_type['AGME']:
        baseUrl += "&interfaceId=getAgmeEleInRegionByTime" \
                  "&dataCode=AGME_CHN_SOIL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,"+ type[0:4] + \
                  "&times=" + timestr + "&adminCodes=360000" \
                  "&eleValueRanges=Soil_Depth_BelS:"+type[5:7] + ";"+type[0:4]+":[0,100]"
    elif type in vector_type:
        baseUrl += "&interfaceId=getSurfEleInRegionByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,"+ vector_type[type][0] + "," + vector_type[type][1] + \
                  "&times=" + timestr + "&adminCodes=360000" \
                  "&eleValueRanges=Q_" + vector_type[type][0] + ":0,3,4;Q_" + vector_type[type][1] + ":0,3,4"
    baseUrl += "&dataFormat=json"

    socket.setdefaulttimeout(20)
    for i in range(3):
        req = urllib.urlopen(baseUrl)
        data = req.read()
        data = data.replace(",fieldNames=", ",\"fieldNames\":")
        data = data.replace(",fieldUnits=", ",\"fieldUnits\":")
        root = json.loads(data)
        if root['returnCode'] == str(0):
            data_json = root['DS']
        if len(data_json) > 0:
            break
    return data_json


def _add_value_range(type):
    new_url = ""
    if 'RHU' in type:
        new_url = ";" + type + ":(0,100]"
    elif ('TEM' in type) or ('GST' in type):
        new_url = ";" + type + ":(-273,990000)"
    elif ('PRE' in type) or ('PRS' in type):
        new_url = ";" + type + ":[0,990000)"
    else:
        pass
    return new_url


if __name__ == '__main__' :
    x, y, z = get_jx_1h('PRE_1h', '20120101000000')