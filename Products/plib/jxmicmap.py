#!/usr/bin/env python
# -*- coding: utf-8 -*-


import shapefile as shp
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnchoredOffsetbox, TextArea
import json, os, ConfigParser


class DrawMap(object):
    """
    'levels': 等值线分级值，浮点型数组，如小时雨量可以赋值[0.01,2,4,6,8,10,20,50,200]，0.01到2之间是一个等级.
    'colors': 等值线每一级颜色，字符型数组，如小时雨量可以赋值['#9CF790','#37A600','#67B4F8','#0002FE','#03714E','#FA03F0','#DE5000', '#710100'].
    'cheight': 颜色条的长度占比，浮点型， 如0.75,0.25.
    'unit': 数据单位，字符串，如雨量可以赋值"mm",温度可以赋值"°C".
    'titles'：标题内容，字典数组，如[{"title":"江西省逐小时降水3月14日19时-20时", "loc":"left"},{"title":"2018年03月14日20时制作", "loc":"right"}],
                其中loc标识标题的方位，可以取值"left","right","center".
    'statistics': 统计信息，字符数组，["极大值：5mm","极小值：0mm"],一个字符一行.
    'save_name': 产品文件保存路径，如"E:\\ex.png"或者"filepath\\ex.png"
    """
    def __init__(self, levels, colors, cheight, unit, titles, statistics, save_name):
        self.levels = levels
        self.colors = colors
        self.cheight = cheight
        self.unit = unit
        self.titles = titles
        self.statistics= statistics
        self.save_name=save_name

    def draw_scala_map(self, x, y, z):
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.read('config.txt')
        fig = plt.figure(figsize=(7,8), frameon=False, edgecolor='none')
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
        # ax.stock_img()
        # ax.coastlines()
        # cmap = plt.cm.get_cmap('RdYlBu_r')
        # lvs = [0.01,2,4,6,8,10,20,50,200]
        # colorarray = ['#9CF790','#37A600','#67B4F8','#0002FE','#03714E','#FA03F0','#DE5000', '#710100']
        # cmap = colors.ListedColormap(colorarray)
        # cs = ax.contourf(x, y, dataArray, levels=lvs, transform=ccrs.PlateCarree(), cmap=cmap, boundaries=[-48]+lvs +[48], extend='both')
        cs = ax.contourf(x, y, z, levels=self.levels, transform=ccrs.PlateCarree(), colors=self.colors)

        #设置无边距
        # plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        #设置产品标题坐标等，需要有边距
        plt.subplots_adjust(left=0.045, bottom=0.03, right=0.97, top=0.97, wspace=0, hspace=0)

        #设置colorbar
        axins = inset_axes(ax,
                           width="1.2%",
                           height=self.cheight,
                           loc=4,
                           borderpad=5)

        # orientation="horizontal"
        cbar = fig.colorbar(cs,cax=axins, ticks=self.levels[1:-1])
        cbar.ax.tick_params(labelsize='10', direction='in')
        cbar.ax.set_title(u'图例(' + self.unit + ')', fontsize=10)

        #投影边界到地图上
        mapcities=['jiangxi_all']
        mapconties=['jx_xianjie']
        for cityname in mapcities:
            adm1_shapes = list(shpreader.Reader(os.path.join(config.get('Path', 'MAPDATA_PATH'), cityname+".shp")).geometries())
            ax.add_geometries(adm1_shapes, ccrs.PlateCarree(),
                              edgecolor='black', facecolor='', alpha=0.4)
        for cityname in mapconties:
            adm1_shapes = list(shpreader.Reader(os.path.join(config.get('Path', 'MAPDATA_PATH'), cityname+".shp")).geometries())
            ax.add_geometries(adm1_shapes, ccrs.PlateCarree(),
                              edgecolor='black', facecolor='', alpha=0.2)

        #使用边界切出边界包围的部分
        sjz = shp.Reader(os.path.join("mapdata", "jx_outer.shp"))
        vertices = []
        codes = []
        for shape_rec in sjz.shapeRecords():
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
        path = Path(vertices, codes)
        patch = PathPatch(path, facecolor='none', transform=ccrs.PlateCarree())
        ax.add_patch(patch)
        # ax.set_boundary(path, transform=ccrs.PlateCarree())
        for collection in cs.collections:
            # collection.set_clip_on(True)
            collection.set_clip_path(patch)

        #设置经纬度标识
        ax.set_extent([113.3, 118.7, 24.4, 30.2], crs=ccrs.PlateCarree())
        ax.set_xticks([114, 115, 116, 117, 118], crs=ccrs.PlateCarree())
        ax.set_yticks([25, 26, 27, 28, 29, 30], crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter(number_format='g',dateline_direction_label=True)
        lat_formatter = LatitudeFormatter(number_format='g')
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.tick_params(labelsize='9')

        #设置标题
        for t in self.titles:
            ax.set_title(t["title"], loc=t["loc"])


        #设置相关统计信息
        statics_str = ""
        for info in self.statistics:
            statics_str = statics_str + info + "\n"
        textbox = TextArea(statics_str)
        anchored_text_box = AnchoredOffsetbox(loc=4,
                                              child=textbox, pad=0.0,
                                              frameon=False,
                                              bbox_to_anchor=(0.8, 0.15),
                                              bbox_transform=ax.transAxes,
                                              borderpad=0
                                              )
        ax.add_artist(anchored_text_box)


        #加信息中心LOGO
        jximg = mpimg.imread('jmic.png')
        imagebox = OffsetImage(jximg, zoom=0.2)
        anchored_image_box = AnchoredOffsetbox(loc=4,
                                         child=imagebox, pad=0.6,
                                         frameon=False,
                                         bbox_to_anchor=(1, 0),
                                         bbox_transform=ax.transAxes,
                                         borderpad=0.,
                                         )
        ax.add_artist(anchored_image_box)
        # axjx = fig.add_axes([0.59, -0.06, 0.3, 0.3], frameon=False)
        # axjx.imshow(jximg)
        # axjx.set_xticks([])
        # axjx.set_yticks([])

        # plt.table(cellText=[[1],[2]],
        #                       rowLabels=["最高温","最低温"],
        #                       loc=4)


        #地市名
        with open(os.path.join(config.get('Path', 'MAPDATA_PATH'), "CityLL.json"),'r') as json_file:
            citylls=json.load(json_file)
            for cll in citylls:
                clon = float(cll["Lon"])
                clat = float(cll["Lat"])
                ax.plot(clon, clat, ".k", transform=ccrs.PlateCarree(), markersize=3, alpha=0.6)
                #地名在点上、在点左、在点右、在点下
                if cll["Station_Name"] in ["南昌", "浮梁", "上饶县", "赣县", "大余", "石城"]:
                    ax.text(clon, clat+0.02, cll["Station_Name"], fontsize=7, alpha=0.6,
                            verticalalignment='bottom', horizontalalignment='center',
                            transform=ccrs.PlateCarree())
                elif cll["Station_Name"] in ["九江县", "新建","瑞昌"]:
                    ax.text(clon-0.01, clat, cll["Station_Name"], fontsize=7, alpha=0.6,
                            verticalalignment='center', horizontalalignment='right',
                            transform=ccrs.PlateCarree())
                elif cll["Station_Name"] in ["定南","井冈山"]:
                    ax.text(clon+0.02, clat, cll["Station_Name"], fontsize=7, alpha=0.6,
                            verticalalignment='center', horizontalalignment='left',
                            transform=ccrs.PlateCarree())
                else:
                    ax.text(clon, clat-0.02, cll["Station_Name"], fontsize=7, alpha=0.6,
                            verticalalignment='top', horizontalalignment='center',
                            transform=ccrs.PlateCarree())
        plt.savefig(self.save_name)