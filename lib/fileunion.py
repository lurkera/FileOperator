# __author: linle
# __date: 2019/12/4

from lib.util import common
from os import system, path, remove
from time import strftime, localtime
import pandas as pd


class FileUnion:

    def __init__(self):
        self.name = '文件合并操作'
        self.opt = [{'title': '简单文件合并', 'funcname': 'simple_file_union'},
                    {'title': '复杂文件合并', 'funcname': 'complex_file_union'}]
        self.filetypes = ['.txt', '.csv']
        self.transtypes = ['.xlsx', '.xls', 'xlsm']

    def run(self):
        while True:
            common.print_title(self.opt)
            choice = input('[' + self.name + ']请输入操作选项>>>').strip()
            if choice:
                if choice.lower() == 'q': exit()
                if choice.lower() == 'b': return
                choice = int(choice) - 1
                funcname = self.opt[choice]['funcname']
                return getattr(self, funcname)(choice)

    def simple_file_union(self, choice):
        fp = common.get_floder(self.opt[choice]['title'])
        if not fp: return
        need_title = common.get_need_head(self.opt[choice]['title'])
        if not need_title: return
        start_row = common.get_start_row(self.opt[choice]['title'])
        print('\n---------------开始合并文件---------------\n')
        trans_list = common.trans_files(fp, self.transtypes)  # 将excel转换为csv
        files_csv = common.get_files(fp, self.filetypes)  # 查找目录下的所有文本文件
        if len(files_csv) == 0: raise Exception('无可合并文件!')
        savefn = path.join(fp, 'Result_UnionTable' + strftime("%Y%m%d%H%M%S", localtime()) + '.csv')
        chunksize = 100 * 1024 * 1024
        fsize = sum([path.getsize(x) for x in files_csv])
        havechunk = 0
        with open(savefn, 'ab+') as f0:
            title = None
            for f in files_csv:
                with open(f, 'rb') as f1:
                    if start_row > 1:
                        for i in range(start_row - 1):
                            tmp = f1.readline()
                            havechunk += len(tmp)
                    if need_title == 1:
                        if not title:
                            title = f1.readline()
                            f0.write(title)
                            havechunk += len(title)
                        else:
                            tmp = f1.readline()
                            havechunk += len(tmp)
                    while True:
                        lines = f1.read(chunksize)
                        if not lines: break
                        f0.write(lines)
                        f0.flush()
                        havechunk += len(lines)
                        common.print_rateofprogress(havechunk, fsize)
                if f0.read(1) != '\n': f0.write(b'\n')
        if trans_list: [remove(x) for x in trans_list]
        print('\n\n---------------完成文件合并---------------\n')
        return True

    def complex_file_union(self, choice):
        fp = common.get_floder(self.opt[choice]['title'])
        if not fp: return
        start_row = common.get_start_row(self.opt[choice]['title'])
        print('\n---------------开始合并文件---------------\n')
        trans_list = common.trans_files(fp, self.transtypes)
        files_csv = common.get_files(fp, self.filetypes)
        if len(files_csv) == 0: raise Exception("无可合并文件！")
        savefn = path.join(fp, 'Result_UnionTable' + strftime("%Y%m%d%H%M%S", localtime()) + '.csv')
        title = self.__read_title(files_csv, start_row)
        fsize = sum([path.getsize(x) for x in files_csv])
        chunkline = 500000
        havechunk = 0
        for f in files_csv:
            encode = common.get_file_encode(f)
            df1 = common.trunk_file_byrow(f, encode, chunkline, start_row)
            for d in df1:
                d_save = pd.concat([title, d], axis=0, sort=False)
                header = not path.exists(savefn)
                d_save.to_csv(savefn, mode='a', header=header, index=False, encoding='gbk')
            havechunk += path.getsize(f)
            common.print_rateofprogress(havechunk, fsize)
        if trans_list: [remove(x) for x in trans_list]
        print('\n\n---------------开始合并文件---------------\n')
        return True

    def __read_title(self, filelist, start_row):
        title = pd.DataFrame()
        for f in filelist:
            encode = common.get_file_encode(f)
            t = pd.read_csv(f, encoding=encode, low_memory=False, skiprows=start_row - 1, nrows=0)
            title = pd.concat([title, t], axis=0, sort=False)
        return title
