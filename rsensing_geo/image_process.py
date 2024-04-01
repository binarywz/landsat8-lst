from osgeo import gdal
import os
import uuid
import logging
import numpy as np


def clipRSensingImage(imagePath: str, outPath: str, size: int, metricType="INT"):
    """
    拼接遥感影像
    :param imagePath: 原始遥感影像
    :param outPath: 输出路径
    :param size: 裁剪图像尺寸
    """
    # clip the image to sizexsize
    in_ds = gdal.Open(imagePath)       # 读取要切的原图

    width = in_ds.RasterXSize       # 获取数据宽度
    height = in_ds.RasterYSize      # 获取数据高度
    bands = in_ds.RasterCount       # 获取数据波段数

    col_num = int(width / size)     # 宽度可以分成几块
    row_num = int(height / size)    # 高度可以分成几块
    if width % size != 0:
        col_num += 1
    if height % size != 0:
        row_num += 1

    logging.debug("row_num: {}, col_num: {}".format(row_num, col_num))
    fileNameList = []
    for i in range(row_num):
        for j in range(col_num):
            logging.debug("i: {}, j: {}".format(i, j))
            offset_x = j * size
            offset_y = i * size
            # 从每个波段中切需要的矩形框内的数据(注意读取的矩形框不能超过原图大小)
            b_xsize = min(width - offset_x, size)
            b_ysize = min(height - offset_y, size)

            # 获取Tif的驱动，为创建切出来的图文件做准备
            gtif_driver = gdal.GetDriverByName("GTiff")
            tifName: str = ''.join(str(uuid.uuid1()).split('-'))
            outFile = outPath + "{}.tif".format(tifName)

            # 创建切出来的要存的文件
            if metricType == "INT":
                out_ds = gtif_driver.Create(outFile, b_xsize, b_ysize, bands=bands, eType=gdal.GDT_Int32)
            else:
                out_ds = gtif_driver.Create(outFile, b_xsize, b_ysize, bands=bands, eType=gdal.GDT_Float32)

            # 获取原图的原点坐标信息
            ori_transform = in_ds.GetGeoTransform()

            # 读取原图仿射变换参数值
            top_left_x = ori_transform[0]               # 左上角x坐标
            w_e_pixel_resolution = ori_transform[1]     # 东西方向像素分辨率
            top_left_y = ori_transform[3]               # 左上角y坐标
            n_s_pixel_resolution = ori_transform[5]     # 南北方向像素分辨率

            # 根据反射变换参数计算新图的原点坐标
            top_left_x = top_left_x + offset_x * w_e_pixel_resolution
            top_left_y = top_left_y + offset_y * n_s_pixel_resolution

            # 将计算后的值组装为一个元组，以方便设置
            dst_transform = (
                top_left_x, ori_transform[1], ori_transform[2], top_left_y, ori_transform[4], ori_transform[5])

            # 设置裁剪出来图的原点坐标
            out_ds.SetGeoTransform(dst_transform)

            # 设置SRS属性（投影信息）
            out_ds.SetProjection(in_ds.GetProjection())

            # 写入目标文件
            array_band = []
            for k in range(1, bands + 1):
                if metricType == "INT":
                    array_band = in_ds.GetRasterBand(k).ReadAsArray(offset_x, offset_y, b_xsize, b_ysize).astype(np.int32)
                else:
                    array_band = in_ds.GetRasterBand(k).ReadAsArray(offset_x, offset_y, b_xsize, b_ysize).astype(np.float32)
                out_ds.GetRasterBand(k).WriteArray(array_band)  # 将每个波段写入新的文件中

            # 将缓存写入磁盘
            out_ds.FlushCache()
            del out_ds
            if array_band.any() == 0:
                logging.debug("此幅影像为空值，已删除！")
                os.remove(outFile)
            else:
                fileNameList.append("{}.tif".format(tifName))
    print("Length of fileNameList: {}".format(len(fileNameList)))
    return fileNameList

def mosaicRSensingImage(imageUrlList: list, outPath: str) -> str:
    """
    拼接遥感影像
    :param imageUrlList: 拼接影像列表
    :param outPath: 输出路径
    :return mosaicImagePath: 拼接影像路径
    """
    if len(imageUrlList) < 2:
        return imageUrlList[0]
    mosaicImageList: list = []
    mosaicImagePath: str = gdalWarp(imageUrlList[0], imageUrlList[1], outPath)
    if len(imageUrlList) == 2:
        return mosaicImagePath
    mosaicImageList.append(mosaicImagePath)
    for i in range(2, len(imageUrlList)):
        mosaicImagePath = gdalWarp(mosaicImagePath, imageUrlList[i], outPath)
        mosaicImageList.append(mosaicImagePath)
    # TODO 此处可修改为异步
    for i in range(len(mosaicImageList) - 1):
        os.remove(mosaicImageList[i])
    return mosaicImagePath

def gdalWarp(srcPath: str, destPath: str, outPath: str):
    srcImage = gdal.Open(srcPath, gdal.GA_ReadOnly)
    descImage = gdal.Open(destPath, gdal.GA_ReadOnly)
    proj = descImage.GetProjection()
    options = gdal.WarpOptions(srcSRS=proj, dstSRS=proj, format='GTiff',
                               resampleAlg=gdal.GRA_NearestNeighbour)
    mosaicImageName: str = ''.join(str(uuid.uuid1()).split('-'))
    # 输入投影，输出投影，输出格式，重采样方法
    mosaicImagePath = outPath + "{}.tif".format(mosaicImageName)
    gdal.Warp(mosaicImagePath, [srcImage, descImage], options=options)  # 输出路径，需要镶嵌的数据，参数配置
    srcImage = None
    descImage = None
    del srcImage, descImage
    return mosaicImagePath