# 前言

目前国内使用docker还是需要比较好的加速源，为了一劳永逸，直接写一个脚本并设置定时任务执行

还有一个问题就是docker在拉取镜像时，由于网络问题，一些文件的库文件就没有下载下来，但这时候程序也不会报错，会在后续你执行的时候给你报错无法执行，也没办法判断什么问题......在笔者的深度研究下，发现就是缺少库文件导致的，就很无语

# 配置

将docker_mirror_updater.py，放入/usr/local/bin/下，加下权限

```
chmod +x /usr/local/bin/docker_mirror_undater.py
```

手动执行

```
/usr/local/bin/docker_mirror_updater.py
```

设置定时任务

```
crontab -e
# 每周一凌晨3点自动更新Docker镜像源
0 3 * * 1 /usr/local/bin/docker_mirror_updater.py >> /var/log/docker_mirror_updater_cron.log 2>&1
```

检测是否设置定时任务成功

```
crontab -l
```

# 🐖

![](https://s2.loli.net/2025/06/15/8CJGZE9Dh7dKIaT.png)

这一块是爬取的网站，如果发现更好的可以实时更新
