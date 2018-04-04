#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil, os, math, re, ConfigParser
from matplotlib.mlab import griddata
import numpy as np
from scipy.interpolate import griddata as scigird
from math import radians, atan, sin, cos, tan, acos

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


def get_nearest_value(x, y, z, x1, y1):
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
    t_distance =999999
    value = 0
    for d in zip(x, y, z):
        if _distance(d[1], d[0], y1, x1) < t_distance:
            value = d[2]
    return value


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
        zz = get_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        xx = xi[-1]
        zz = get_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
    for xx in xi:
        yy = yi[0]
        zz = get_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
        yy = yi[-1]
        zz = get_nearest_value(x, y, z, xx, yy)
        x.append(xx)
        y.append(yy)
        z.append(zz)
    zi = griddata(x,y,z,xi,yi, interp)
    return xi, yi, zi


# def scala_net_grid(x, y, z, g, interp, lat_lon):
#
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
#         zz = get_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#         xx = xi[-1]
#         zz = get_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#     for xx in xi:
#         yy = yi[0]
#         zz = get_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#         yy = yi[-1]
#         zz = get_nearest_value(x, y, z, xx, yy)
#         pts.append([xx, yy])
#         z.append(zz)
#     pts = np.array(pts)
#     z = np.array(z)
#     ngridx = complex(0, diffLon*g[0])
#     ngridy = complex(0, diffLat*g[1])
#     xi, yi = np.mgrid[minLon:maxLon:ngridx, minLat:maxLat:ngridy]
#     # xi, yi = np.meshgrid(xi, yi)
#     zi = scigird(pts, z, (xi, yi), method='nearest')
#     # rbf = Rbf(x, y, z, epsilon=2)
#     # zi = rbf(xi, yi)
#     return xi, yi, zi


def get_upload_path_from_file(file_name):
    file_list = str.split(file_name, '_')
    pathstr = '~/'
    for child_path in file_list:
        if re.search(r'(\d{14})', child_path):
            break
        else:
            pathstr = pathstr + child_path + '/'
    return pathstr




if __name__=='__main__':
    get_upload_path_from_file('SURF_PRE_1H_20180328020000.png')