from nonebot import get_driver, logger, on_shell_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from collections import deque

import requests
import os
import time
from pathlib import Path


backup_group = get_driver().config.dict().get('backup_group', [])
if not backup_group:
    logger.warning('请在配置文件中设置应用群聊: backup_group=[\'群号\']')

backup_command = get_driver().config.dict().get('backup_command', "")
if not backup_command:
    backup_command = "备份群文件"

backup_maxsize = get_driver().config.dict().get('backup_maxsize', "")
if not backup_maxsize:
    backup_maxsize = 300

backup_normal_files = get_driver().config.dict().get('backup_maxsize', "")
if not backup_normal_files:
    backup_normal_files = True

linker_parser = ArgumentParser(add_help=False)
linker = on_shell_command(backup_command, parser=linker_parser, priority=1)


class EventInfo:
    fdindex = -1
    fsuccess = fjump = fsizes = 0
    fdtoolarge = []
    fbroken = []
    fdnames = []

    def __init__(self) -> None:
        ...

    def init(self) -> None:
        self.fdindex = -1
        self.fsuccess = self.fjump = self.fsizes = 0
        self.fdtoolarge = []
        self.fbroken = []
        self.fdnames = []


async def SaveToDisk(bot, ff, fdpath, EIF, gid):
    fname = ff["file_name"]
    fid = ff["file_id"]
    fbusid = ff["busid"]
    fsize = ff["file_size"]
    fpath = Path(fdpath, fname)

    if fsize/1024/1024 > backup_maxsize:
        EIF.fdtoolarge.append(
            EIF.fdnames[EI.fdindex] + "/" + fname)
        return

    if not Path(fpath).exists():
        try:

            finfo = await bot.get_group_file_url(group_id=gid, file_id=str(fid), bus_id=int(fbusid))
            url = finfo['url']
            req = requests.get(url)

            if not Path(fdpath).exists():
                os.makedirs(fdpath)
            with open(fpath, 'wb') as mfile:
                mfile.write(req.content)
            EIF.fsizes += fsize
            EIF.fsuccess += 1
        except Exception as e:
            EIF.fbroken.append(fdpath + "/" + fname)
            print(e)
            logger.debug("文件获取不到/已损坏:" + fdpath + "/" + fname)
    else:
        EIF.fsizes += Path(fpath).stat().st_size
        EIF.fjump += 1
EI = EventInfo()


@linker.handle()
async def link(bot: Bot, event: GroupMessageEvent, state: T_State):
    EI.init()
    gid = event.group_id
    if str(gid) in backup_group:
        args = vars(state.get("_args"))
        logger.debug(args)

        await bot.send(event, "备份中,请稍后…(不会备份根目录文件,请把重要文件放文件夹里)")
        tstart = time.time()
        root = await bot.get_group_root_files(group_id=gid)
        folders = root.get("folders")
        if backup_normal_files:
            files = root.get("files")
            fdpath = "./qqgroup/" + str(event.group_id)
            for ff in files:
                await SaveToDisk(bot, ff, fdpath, EI, gid)

        # 广度优先搜索
        dq = deque()

        if folders:
            dq.extend([i["folder_id"] for i in folders])
            EI.fdnames.extend([i["folder_name"] for i in folders])

        while dq:
            EI.fdindex += 1
            _ = dq.popleft()
            logger.debug("下一个搜索的文件夹：" + _)
            root = await bot.get_group_files_by_folder(group_id=gid, folder_id=_)

            fdpath = "./qqgroup/" + \
                str(event.group_id) + "/" + EI.fdnames[EI.fdindex]

            file = root.get("files")

            if file:
                for ff in file:
                    await SaveToDisk(bot, ff, fdpath, EI, gid)

        if len(EI.fdtoolarge) == 0:
            EI.fdtoolarge = "无"
        else:
            EI.fdtoolarge = "\n".join(EI.fdtoolarge)

        if len(EI.fbroken) == 0:
            EI.fbroken = ""
        else:
            EI.fbroken = "检测到损坏文件:" + '\n'.join(EI.fbroken)

        EI.fsizes = round(EI.fsizes/1024/1024, 2)
        tsum = round(time.time()-tstart, 2)

        await linker.finish("此次备份耗时%2d秒; 共备份%d个文件,跳过已备份%d个文件, 累计备份大小%.2f M,\n未备份大文件列表(>%dm):\n%s\n%s" % (tsum, EI.fsuccess, EI.fjump, EI.fsizes, backup_maxsize, EI.fdtoolarge, EI.fbroken))
