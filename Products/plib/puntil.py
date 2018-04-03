#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil, os, math, re, ConfigParser
from matplotlib.mlab import griddata
import numpy as np
from scipy.interpolate import griddata as scigird


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


def scala_net_grid(x, y, z, g, interp):
    maxLon = max(x)
    minLon = min(x)
    maxLat = max(y)
    minLat = min(y)
    diffLon = math.ceil(maxLon-minLon)
    diffLat = math.ceil(maxLat-minLat)
    ngridx = diffLon*g[0]
    ngridy = diffLat*g[1]
    xi = np.linspace(minLon,maxLon,ngridx)
    yi = np.linspace(minLat,maxLat,ngridy)
    zi = griddata(x,y,z,xi,yi, interp)
    return xi, yi, zi


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
#     ngridx = diffLon*g[0]
#     ngridy = diffLat*g[1]
#     xi = np.linspace(minLon,maxLon,ngridx)
#     yi = np.linspace(minLat,maxLat,ngridy)
#     xi, yi = np.meshgrid(xi, yi)
#     zi = scigird(pts, z, (xi, yi), method='nearest')
#     # zi = griddata(x,y,z,xi,yi, interp)
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