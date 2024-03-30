from landsat.LSTRetriever import LSTRetriever
import utils.tkinter_utils as tku
import utils.zip_utils as zipu

"""
Landsat8反演地表温度
1.解压文件
2.选择metadata
3.反演指标
"""
if __name__ == '__main__':

    # 解压文件
    tarFile = tku.select_file_or_folder()
    print("tarFile: ", tarFile)
    if tarFile is not None:
        zipu.unTar(tarFile, "./temp_dir/unzip")

    metadataFile = tku.select_file_or_folder()
    print("metadataFile: ", metadataFile)

    lstRetriever = LSTRetriever(metadata_file=metadataFile,
                                LSE_mode='auto-ndvi-raw',
                                temp_dir='./temp_dir',
                                window_size=15)

    lstRetriever.cloudprobthreshold = 60
    lstFileName: str = metadataFile.split("/")[-1].replace(".txt", "") + ".tif"
    print("lstFileName: ", lstFileName)
    lstRetriever.get_lst_as_gtiff(lstFileName)