import tarfile

def unTar(tarFile: str, destDir: str) -> None:
    """
    解压tar包
    """
    # 打开tar文件
    with tarfile.open(tarFile, 'r') as tar:
        # 解压到指定目录下
        tar.extractall(path=destDir)