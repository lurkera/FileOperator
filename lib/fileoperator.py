# __author: linle
# __date: 2019/12/4

from conf import settings
from importlib import import_module
from lib.util import common
from os import system


def start():
    while True:
        common.print_title(settings.modules)
        try:
            choice = input('[文件操作]请输入操作选项>>>').strip()
            if choice:
                if choice.lower() == 'q': exit()
                if choice.lower() == 'b': start()
                choice = int(choice) - 1
                modulename = settings.modules[choice]['module']
                classname = settings.modules[choice]['class']
                m = import_module(modulename)
                optclass = getattr(m, classname)
                opt = optclass()
                if opt.run(): system('pause')
        except KeyboardInterrupt as k:
            print('程序终止......')
            system('pause')
        except Exception as e:
            print(e)
            system('pause')
