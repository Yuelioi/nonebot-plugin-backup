from nonebot import get_driver, logger, on_shell_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from collections import deque

import requests
import os
import time


backup_group = get_driver().config.dict().get('backup_group', [])
if not backup_group:
    logger.warning('请在配置文件中设置应用群聊: backup_group=[\'群号\']')

backup_command = get_driver().config.dict().get('backup_command', "")
if not backup_command:
    backup_command = "备份群文件"

linker_parser = ArgumentParser(add_help=False)
linker = on_shell_command(backup_command, parser=linker_parser, priority=1)


@linker.handle()
async def link(bot: Bot, event: GroupMessageEvent, state: T_State):
    gid = event.group_id
    fdindex = -1
    fsuccess = 0
    fjump = 0
    fsizes = 0
    fdtoolarge = []
    fdnames = []

    if gid in backup_group:
        args = vars(state.get("_args"))
        logger.debug(args)

        await bot.send(event, "备份中,请稍后…(不会备份根目录文件,请把重要文件放文件夹里)")
        tstart = time.time()
        root = await bot.get_group_root_files(group_id=gid)
        folders = root.get("folders")

        # 广度优先搜索
        dq = deque()

        if folders:
            print(folders)
            dq.extend([i["folder_id"] for i in folders])
            fdnames.extend([i["folder_name"] for i in folders])

        while dq:
            fdindex += 1
            _ = dq.popleft()
            logger.debug("下一个搜索的文件夹：" + _)
            root = await bot.get_group_files_by_folder(group_id=gid, folder_id=_)

            folder_path = "./qqgroup/" + \
                str(event.group_id) + "/" + fdnames[fdindex]

            file = root.get("files")

            if file:
                for i in file:
                    file_name = i["file_name"]
                    fid = i["file_id"]
                    fbusid = i["busid"]
                    fsize = i["file_size"]
                    fpath = os.path.join(folder_path, file_name)

                    if fsize/1024/1024 > 300:
                        fdtoolarge.append(file_name)
                        continue

                    if not os.path.exists(fpath):
                        finfo = await bot.get_group_file_url(group_id=gid, file_id=str(fid), bus_id=int(fbusid))
                        url = finfo['url']
                        req = requests.get(url)

                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                        with open(fpath, 'wb') as mfile:
                            mfile.write(req.content)

                        fsizes += fsize
                        fsuccess += 1
                    else:
                        fjump += 1

        if len(fdtoolarge) == 0:
            fdtoolarge = "无"
        else:
            fdtoolarge = "\n".join(fdtoolarge)

        fsizes = round(fsizes/1024/1024, 2)
        tsum = round(time.time()-tstart, 2)

        await linker.finish("此次备份耗时%2d秒; 共备份%d个文件,跳过已备份%d个文件, 累计备份大小%.2f M,\n未备份大文件列表(>300m):\n%s" % (tsum, fsuccess, fjump, fsizes, fdtoolarge))
