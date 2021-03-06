#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil, os, math, re, ConfigParser
from matplotlib.mlab import griddata
import numpy as np
from scipy.interpolate import griddata as scigird
from math import radians, atan, sin, cos, tan, acos
import urllib2


def force_move_file(from_path, to_path, file_name):
    if not os.path.exists(os.path.join(from_path, file_name)):
        return False
    if not os.path.exists(to_path):
        try:
            os.mkdir(to_path)
        except:
            return False
    if os.path.exists(os.path.join(to_path, file_name)):
        try:
            os.remove(os.path.join(to_path, file_name))
        except:
            return False
    try:
        shutil.move(os.path.join(from_path, file_name), os.path.join(to_path, file_name))
        return True
    except:
        return False


def _distance(Lat_A, Lng_A, Lat_B, Lng_B):
    if Lat_A == Lat_B and Lng_A == Lng_B:
        return 999999
    ra = 6378.140
    rb = 6356.755
    flatten = (ra - rb) / ra
    rad_lat_A = radians(Lat_A)
    rad_lng_A = radians(Lng_A)
    rad_lat_B = radians(Lat_B)
    rad_lng_B = radians(Lng_B)
    pA = atan(rb / ra * tan(rad_lat_A))
    pB = atan(rb / ra * tan(rad_lat_B))
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (xx + dr)
    return distance


def scala_nearest_value(x, y, z, x1, y1):
    t_distance =999999
    value = 0
    for d in zip(x, y, z):
        if _distance(d[1], d[0], y1, x1) < t_distance:
            value = d[2]
    return value


def vector_nearest_value(x, y, u, v,  x1, y1):
    t_distance =999999
    u_value = 0
    v_value = 0
    for d in zip(x, y, u, v):
        if _distance(d[1], d[0], y1, x1) < t_distance:
            u_value = d[2]
            v_value = d[3]
    return u_value, v_value


def scala_net_grid(x, y, z, g, interp, lat_lon):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.txt')
    latlon = list(eval(config.get('Draw', lat_lon)))
    maxLon = latlon[3]
    minLon = latlon[1]
    maxLat = latlon[2]
    minLat = latlon[0]
    diffLon = math.ceil(maxLon-minLon)
    diffLat = math.ceil(maxLat-minLat)
    ngridx = diffLon*g[0]
    ngridy = diffLat*g[1]
    xi = np.linspace(minLon,maxLon,ngridx)
    yi = np.linspace(minLat,maxLat,ngridy)
    for yy in yi:
        xx = xi[0]
        zz = scala_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        xx = xi[-1]
        zz = scala_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
    for xx in xi:
        yy = yi[0]
        zz = scala_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        yy = yi[-1]
        zz = scala_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
    zi = griddata(x,y,z,xi,yi, interp)
    return xi, yi, zi


def vector_net_grid(x, y, z, angle,  g, interp, lat_lon):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.txt')
    latlon = list(eval(config.get('Draw', lat_lon)))
    maxLon = latlon[3]
    minLon = latlon[1]
    maxLat = latlon[2]
    minLat = latlon[0]
    diffLon = math.ceil(maxLon-minLon)
    diffLat = math.ceil(maxLat-minLat)
    ngridx = diffLon*g[0]
    ngridy = diffLat*g[1]
    xi = np.linspace(minLon, maxLon, ngridx)
    yi = np.linspace(minLat, maxLat, ngridy)
    for yy in yi:
        xx = xi[0]
        zz, aa = vector_nearest_value(x, y, z, angle, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        angle.append(aa)
        xx = xi[-1]
        zz, aa = vector_nearest_value(x, y, z, angle, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        angle.append(aa)
    for xx in xi:
        yy = yi[0]
        zz, aa = vector_nearest_value(x, y, z, angle, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        angle.append(aa)
        yy = yi[-1]
        zz, aa = vector_nearest_value(x, y, z, angle, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        angle.append(aa)
    u = (-np.array(z) * np.sin(np.deg2rad(np.array(angle)))).tolist()
    v = (-np.array(z) * np.cos(np.deg2rad(np.array(angle)))).tolist()
    ui = griddata(x, y, u, xi, yi, interp)
    vi = griddata(x, y, v, xi, yi, interp)
    return xi, yi, ui, vi


# def scala_net_grid(x, y, z, g, interp, lat_lon):
#     pts = []
#     for pt in zip(x, y):
#         pts.append(list(pt))
#     config = ConfigParser.RawConfigParser(allow_no_value=True)
#     config.read('config.txt')
#     latlon = list(eval(config.get('Draw', lat_lon)))
#     maxLon = latlon[3]
#     minLon = latlon[1]
#     maxLat = latlon[2]
#     minLat = latlon[0]
#     diffLon = math.ceil(maxLon-minLon)
#     diffLat = math.ceil(maxLat-minLat)
#     ngridx = diffLon * g[0]
#     ngridy = diffLat * g[1]
#     xi = np.linspace(minLon,maxLon,ngridx)
#     yi = np.linspace(minLat,maxLat,ngridy)
#     for yy in yi:
#         xx = xi[0]
#         zz = scala_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#         xx = xi[-1]
#         zz = scala_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#     for xx in xi:
#         yy = yi[0]
#         zz = scala_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#         yy = yi[-1]
#         zz = scala_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#     pts = np.array(pts)
#     z = np.array(z)
#     ngridx = complex(0, diffLon*g[0])
#     ngridy = complex(0, diffLat*g[1])
#     xi, yi = np.mgrid[minLon:maxLon:ngridx, minLat:maxLat:ngridy]
#     zi = scigird(pts, z, (xi, yi), method='linear')
#     return xi, yi, zi


def get_upload_path_from_file(file_name):
    file_list = str.split(file_name, '_')
    pathstr = '~/'
    if 'KOR' in file_list:
        list_len = len(file_list)
        file_list = file_list[0:list_len-2]
        for child_path in file_list:
            pathstr = pathstr + child_path + '/'
        return pathstr
    for child_path in file_list:
        if re.search(r'(\d{14})', child_path):
            break
        else:
            pathstr = pathstr + child_path + '/'
    return pathstr


def download_from_url(url, save_path, file_name):
    try:
        u = urllib2.urlopen(url, timeout=10)
        f = open(os.path.join(save_path, file_name+'.tmp'), 'wb')
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            f.write(buffer)
        f.close()
        os.rename(os.path.join(save_path, file_name+'.tmp'), os.path.join(save_path, file_name))
        return True
    except Exception,e:
        return False


if __name__=='__main__':
    # download_from_url('http://web.kma.go.kr/repositary/image/cht/img/up85_2018060212.png', 'D:\PycharmProjects\WorkScript\Products\source', 'test.png')
    print get_upload_path_from_file('NAFP_KOR_SURF_3H_20180522030000.png')