#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, json


def get_jx_1h(type,timestr):
    # baseUrl = "http://10.116.89.55/cimiss-web/api?userId=BENC_XXZX_product" \
    #           "&pwd=123456" \
    #           "&interfaceId=getSurfEleInRegionByTime" \
    #           "&dataCode=SURF_CHN_MUL_HOR" \
    #           "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,PRE_1h,Q_PRE_1h" \
    #           "&times=" + timestr + "&adminCodes=360000" \
    #           "&eleValueRanges=Q_PRE_1h:0,3,4" \
    #           "&dataFormat=json";
    baseUrl=get_url(type, timestr)

    req = urllib.urlopen(baseUrl)
    data = req.read()
    data = data.replace(",fieldNames=", ",\"fieldNames\":");
    data = data.replace(",fieldUnits=", ",\"fieldUnits\":");
    root = json.loads(data)
    x=[]
    y=[]
    z=[]

    f = urllib.urlopen('http://10.116.32.88/stationinfo/index.php/Api/stationInfoLast?type=json')
    stdata = f.read()
    st = json.loads(stdata)

    if root['returnCode'] == str(0):
        for row in root['DS']:
            stno = row["Station_Id_C"]
            if stno in st:
                x.append(float(st[stno]["lontiude"]))
                y.append(float(st[stno]["lattiude"]))
                z.append(float(row[type]))

    return x, y, z

def get_url(type,timestr):
    baseUrl=''
    if type=='PRE_1h':
        baseUrl = "http://10.116.89.55/cimiss-web/api?userId=BENC_XXZX_product" \
                  "&pwd=123456" \
                  "&interfaceId=getSurfEleInRegionByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,PRE_1h,Q_PRE_1h" \
                  "&times=" + timestr + "&adminCodes=360000" \
                  "&eleValueRanges=Q_PRE_1h:0,3,4" \
                  "&dataFormat=json";
    elif type=='TEM':
        baseUrl = "http://10.116.89.55/cimiss-web/api?userId=BENC_XXZX_product" \
                  "&pwd=123456" \
                  "&interfaceId=getSurfEleInRectByTime" \
                  "&dataCode=SURF_CHN_MUL_HOR" \
                  "&elements=Station_Id_C,Lon,Lat,Year,Mon,Day,Hour,TEM" \
                  "&times=" + timestr + \
                  "&minLat=24.2811" \
                  "&minLon=112.53" \
                  "&maxLat=30.4333" \
                  "&maxLon=119.9297" \
                  "&eleValueRanges=TEM:(-25,50)" \
                  "&dataFormat=json";
    return baseUrl
