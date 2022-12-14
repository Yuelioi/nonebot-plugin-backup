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

## 用途

备份群文件, 只会备份文件夹里的, 因为随手传个视频 大图也会进群文件

会检索是否已备份, 所以请放心使用

会备份到 robot 安装目录/qqgroup/qq 群号

## 用法

配置文件`.env.*`中添加：

```python
COMMAND_START=["/", ""]  # 别忘了设置指令前缀，这里只是提醒一下，如果你不知道这个有什么用，请阅读nonebot文档

backup_group=["<QQ群号>"]  # 启用插件的群
backup_command="备份群文件" # 设置插件触发命令（默认`link`）
backup_maxsize=300 # 超过多少M的文件不备份, 会在后面提醒哪些没备份
```

### 使用方法

直接打 `备份群文件` 或者自定义的触发命令即可

## 参考来源

[DirectLinker](https://github.com/ninthseason/nonebot-plugin-directlinker)

因为我想备份群文件, 防止炸群, 然后发现只有这一个类似的~ 无奈只能魔改下
