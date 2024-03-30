# landsat8-lst

### 安装
```bash
conda create --name lst python=3.8.2
conda install -c conda-forge -n lst python-fmask
conda activate lst
```

## 使用步骤
```
1.运行gen_lst.py，获取地表温度指标文件
2.运行clip_to_database.py，裁剪影像并入库
```