# __author: linle
# __date: 2019/12/5


from lib.util import common
import requests
import json
from datetime import datetime
from os import system, path
import os


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
        _download_msg = {'url': 'https://raw.githubusercontent.com/lurkera/FileOperator/master/conf/versioninfo.json'}
        filepath = r'..\conf\versioninfo.json'
        print(os.getcwd())
        with open(filepath) as f:
            local = json.load(f)
        try:
            rsp = requests.get(_download_msg['url'], timeout=10)
            git = json.loads(rsp.content)
            msg = []
            if rsp.status_code == 200:
                if git['name'] == local['name']:
                    timegit = datetime.strptime(git['publishtime'], '%Y-%m-%d')
                    timelocal = datetime.strptime(local['publishtime'], '%Y-%m-%d')
                    if git['version'] != local['version'] or (timegit - timelocal).days > 0:
                        msg.append('工具有更新，请按照下面链接下载最新版本：')
                        msg.append(git['downloadurl'])
                        common.print_list_formating(msg, 1)
                    else:
                        msg.append('  已使用最新版本...  ')
                        common.print_list_formating(msg, 1)
            return True
        except Exception as e:
            print('github连接超时...')
            system('pause')
