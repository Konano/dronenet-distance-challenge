# dronenet-distance-challenge

## 查询从某一 Portal 出发最远飞行距离和方案

首先下载数据压缩包文件（[Mega](https://mega.nz/file/PsYnkCoD#ujlASFyomu1ZT8WZXi1_57ogH3pneGRXT2EC156u-lg) or [bjres](http://bjres.net/downloads/portaldata.zip)）并解压到项目当前文件夹内，其解压后的文件夹名为 `data`。

接着运行以下命令：

```bash
pip install -r requirements.txt
python path.py [latitude] [longitude]
```

其中 `latitude` 和 `longitude` 是你想要查询的起始 Portal 的经纬度坐标，可从 Ingress IITC 上获知。

如在使用方面出现问题请联系作者。
