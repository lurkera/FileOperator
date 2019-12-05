# __author: linle
# __date: 2019/12/5

from conf import settings
from lib.util import common
import requests
import json
from datetime import datetime
from os import system, path


class Help():

    def __init__(self):
        self.name = '软件更新和帮助'
        self.opt_help = [
            {'title': '检查更新', 'funcname': 'check_update'},
            {'title': '联系作者', 'funcname': 'abount_author'}
        ]

    def run(self):
        while True:
            common.print_title(self.opt_help)
            inputstr = f'[{self.name}]请输入操作选项>>>'
            choice = input(inputstr).strip()
            if choice:
                if choice.lower() == 'q': exit()
                if choice.lower() == 'b': return
                if choice.isdigit():
                    choice = int(choice) - 1
                    if choice in range(0, len(self.opt_help)):
                        self.optname = self.opt_help[choice]['title']
                        funcname = self.opt_help[choice]['funcname']
                        return getattr(self, funcname)()
                    else:
                        print('输入错误，请重新输入！')
                else:
                    print('输入内容非数字，请重新输入！')

    def abount_author(self):
        author_msg = ['author : linle',
                      'email : linle861021@163.com',
                      'QQ : 595848436'
                      ]
        common.print_list_formating(author_msg, 1)
        return True

    def check_update(self):
        _download_mesg = {
            'url': r'https://raw.githubusercontent.com/lurekera/filesoperator/master/softwareinfo.json',
            'filename': 'versioninfo.json'}
        try:
            from bin.run import BASEDIR
            filepath = path.join(BASEDIR, r'lib\help\softwareinfo.json')
            with open(filepath) as f:
                j = json.load(f)
            rsp = requests.get(_download_mesg['url'], timeout=3)
            jurl = json.loads(rsp.content)
            msg = []
            if rsp.status_code == 200:
                for ju in jurl:
                    if ju['name'] == j['name']:
                        timeurl = datetime.strptime(ju['publishtime'], '%Y-%m-%d')
                        timelocal = datetime.strptime(j['publishtime'], '%Y-%m-%d')
                        if ju['version'] != j['version'] or (timeurl - timelocal).days > 0:
                            msg.append('工具有更新，请按照下面链接下载最新版本：')
                            msg.append(ju['download_url'])
                            printer.print_list_formating(msg, 1)
                        else:
                            msg.append('您已使用最新版本')
                            printer.print_list_formating(msg, 1)
            return True
        except Exception as e:
            print(e)
