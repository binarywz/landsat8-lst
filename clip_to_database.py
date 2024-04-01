import logging
import os
import time

from elasticsearch import Elasticsearch
from osgeo import gdal

import rsensing_geo.geo_transform as rgt
import rsensing_geo.image_process as rgi
import utils.tkinter_utils as rtk

"""
Landsat8影像
遥感影像裁剪入库

filePath: LC08_L1TP_121035_20240309_20240316_02_T1_MTL.tif
"""
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    gdal.AllRegister()


    filePath = rtk.select_file_or_folder()
    print("filePath: ", filePath)

    fileDate: str = filePath.split("_")[4]
    fileDate: str = fileDate[:4] + "-" + fileDate[4:6] + "-" + fileDate[6:8]

    basePath: str = r"D:/binarywz"
    dataPath: str = r"/data/rsensing/ndvi/" + fileDate + "/0533/"
    dirPath = basePath + dataPath
    print("dirPath: ", dirPath)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    # 裁剪影像
    fileNameList = rgi.clipRSensingImage(filePath, dirPath, 512, metricType="FLOAT")

    address = {
        "host": "192.168.46.10",
        "port": 9200
    }
    es = Elasticsearch([address])

    image_template = {
        "created_by": "cuiwenzhi",
        "created_time": "2024-01-19 16:18:10",
        "img": "",
        "max_lat": 0,
        "max_lon": 0,
        "min_lat": 0,
        "min_lon": 0,
        "phase_time": "2024-01-19"
    }

    cityCode: str = "0533"
    for fileName in fileNameList:
        path = os.path.join(dirPath, fileName)
        print('File {} loaded'.format(path))
        dataset = gdal.Open(path, gdal.GA_ReadOnly)
        _, lonlatList = rgt.calcVertexGeoAndLonlat(dataset)
        # (lat, lon)
        lt, rt, lb, rb = lonlatList
        image_mapping = image_template.copy()
        image_mapping["img"] = dataPath + fileName
        image_mapping["created_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        image_mapping["phase_time"] = fileDate
        image_mapping["max_lon"] = rb[1]
        image_mapping["min_lon"] = lt[1]
        image_mapping["max_lat"] = rt[0]
        image_mapping["min_lat"] = rb[0]
        print("Image mapping: {}".format(image_mapping))
        es.index(index = "rs_ndvi_" + cityCode, body = image_mapping)