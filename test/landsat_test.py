from landsat.LSTRetriever import LSTRetriever


if __name__ == '__main__':

    lst_retriever = LSTRetriever(metadata_file=r'D:\binarywz\data\landsat\LC08_L1TP_122034_20240128_20240128\LC08_L1TP_122034_20240128_20240128_02_RT_MTL.txt',
                                LSE_mode='auto-ndvi-raw',
                                temp_dir='./temp_dir',
                                window_size=15)

    lst_retriever.cloudprobthreshold = 60
    lst_retriever.get_lst_as_gtiff('./LST_20180512.tif')