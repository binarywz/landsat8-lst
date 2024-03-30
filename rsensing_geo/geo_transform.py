# -*- encoding: utf-8 -*-
from osgeo import gdal
from osgeo import osr
import numpy as np


def getSRSPair(dataset: gdal.Dataset):
    """
    获得给定数据的投影参考系和地理参考系
    :param dataset: GDAL地理数据
    :return: 投影参考系和地理参考系
    """
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs


def lonlat2Geo(dataset: gdal.Dataset, lon, lat):
    """
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lat, lon)对应的投影坐标
    """
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    # 见https://github.com/OSGeo/gdal/issues/1546
    coords = ct.TransformPoint(lat, lon)
    return coords[:2]


def geo2lonlat(dataset: gdal.Dataset, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lat, lon)
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]


def lonlat2Idx(dataset: gdal.Dataset, lonlat):
    """
    计算经纬度坐标对应遥感图像中的像素点
    :param lonlat: 经纬度坐标
    :type dataset: gdal.Dataset
    """
    geotransform = dataset.GetGeoTransform()
    # 获取栅格影像的左上角起始坐标，像元大小
    xOrigin = geotransform[0]       # 左上角x坐标
    yOrigin = geotransform[3]       # 左上角y坐标
    pixelWidth = geotransform[1]    # 像元宽度
    pixelHeight = geotransform[5]   # 像元高度
    # 小于90为纬度，大于90为经度
    lat, lon = lonlat
    coords = lonlat2Geo(dataset, lon, lat)
    # 计算坐标与tif起始坐标差了多少行和列
    idx_x = int((coords[0] - float(xOrigin)) / pixelWidth)
    idx_y = int((coords[1] - float(yOrigin)) / pixelHeight)
    return idx_x, idx_y


def imagexy2geo(dataset, row, col):
    '''
    根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
    :param dataset: GDAL地理数据
    :param row: 像素的行号
    :param col: 像素的列号
    :return: 行列号(row, col)对应的投影坐标或地理坐标(x, y)
    '''
    trans = dataset.GetGeoTransform()
    px = trans[0] + col * trans[1] + row * trans[2]
    py = trans[3] + col * trans[4] + row * trans[5]
    return px, py


def geo2imagexy(dataset, x, y):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param dataset: GDAL地理数据
    :param x: 投影或地理坐标x
    :param y: 投影或地理坐标y
    :return: 影坐标或地理坐标(x, y)对应的影像图上行列号(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解


def imagexy2lonlat(dataset: gdal.Dataset, row, col):
    """
    将图像中的行跟列转换成经纬度
    :param dataset:
    :param row:
    :param col:
    :return:
    """
    px, py = imagexy2geo(dataset, row, col)
    return geo2lonlat(dataset, px, py)


def calcVertexGeoAndLonlat(dataset: gdal.Dataset):
    """
    计算遥感影像顶点的投影坐标和经纬度
    :param dataset:
    :return:
    """
    rows, cols = dataset.RasterYSize, dataset.RasterXSize
    # lt_xy, rt_xy, lb_xy, rb_xy
    xyList = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
    geoList, lonlatList = [], []
    for xy in xyList:
        px, py = imagexy2geo(dataset, xy[0], xy[1])
        geoList.append((px, py))
        coords = geo2lonlat(dataset, px, py)
        lonlatList.append(coords)
    return geoList, lonlatList