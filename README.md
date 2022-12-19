<div align="center">

# nonebot backup group files

✨ 一个基于 [NoneBot2](https://github.com/nonebot/nonebot2) 的插件，用于备份 QQ 群文件 ✨

</div>

<p align="center">
  
  <a href="https://github.com/ninthseason/nonebot-plugin-directlinker/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-GPL3.0-informational">
  </a>
  
  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot-v2-green">
  </a>
  
  <a href="https://github.com/Mrs4s/go-cqhttp">
    <img src="https://img.shields.io/badge/go--cqhttp-v1.0.0-red">
  </a>
  
  <a href="">
    <img src="https://img.shields.io/badge/release-v1.0-orange">
  </a>
  
</p>

## 术语介绍

`临时文件`: 不在文件夹内的文件(因为随手传个视频 大图也会进群文件,并且不在文件夹里的)

## 用途

备份群文件

会检索是否已备份, 所以请放心使用

会备份到 robot 安装目录/qqgroup/qq 群号

## 用法

配置文件`.env.*`中添加：

```python
backup_group=["<QQ群号>"]  # 启用插件的群, 默认为[],代表所有群
backup_command="备份群文件" # 设置插件触发命令
backup_maxsize=300        # 超过多少M的文件不备份, 会在后面提醒哪些没备份

backup_temp_files = True  # 是否备份`临时文件`,默认备份
backup_temp_file_ignore = [".gif", ".png", ".jpg", ".mp4"] # 忽略`临时文件`哪些文件后缀
```

### 使用方法

直接打 `备份群文件` 或者自定义的触发命令即可

## TODO

过滤`临时文件`文件后缀

## 参考来源

[DirectLinker](https://github.com/ninthseason/nonebot-plugin-directlinker)

因为我想备份群文件, 防止炸群, 然后发现只有这一个类似的~ 无奈只能魔改下
