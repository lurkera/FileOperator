# __author: linle
# __date: 2019/12/4

from lib.util import common
from os import path, remove
from math import ceil
from re import sub, split, findall
import pandas as pd


class FileSplit():

    def __init__(self):
        self.name = '文件分割操作'
        self.opt = [{'title': '按照行数分割', 'funcname': 'split_byrow'},
                    {'title': '按照大小分割', 'funcname': 'split_bysize'},
                    {'title': '按照列内容分割', 'funcname': 'split_bycolumn'}
                    ]
        self.filetypes = ('.txt', '.csv')
        self.transtypes = ('.xlsx', '.xls', '.xlsm')

    def run(self):
        while True:
            common.print_title(self.opt)
            choice = input('[' + self.name + ']请输入操作选项>>>').strip()
            if choice:
                if choice.lower() == 'q': exit()
                if choice.lower() == 'b': return
                choice = int(choice) - 1
                funcname = self.opt[choice]['funcname']
                if getattr(self, funcname)(choice): return True

    def split_byrow(self, choice):
        fp = common.get_file(self.opt[choice]['title'])
        if not fp: return
        need_title = common.get_need_head(self.opt[choice]['title'])
        if need_title is None: return
        split_line = self.__get_split_row(self.opt[choice]['title'])
        if split_line is None: return
        skip_row = common.get_skip_row(self.opt[choice]['title'])
        if skip_row is None: return
        trance_list = []
        print('\n---------------开始分割文件---------------\n')
        if fp.endswith(self.transtypes):
            trance_list = common.trans_files(fp, self.transtypes)
            if not trance_list: raise Exception('文件内容为空')
            split_file_list = trance_list
        else:
            split_file_list = [fp]
        allsize = sum([path.getsize(x) for x in split_file_list])
        currentsize = 0
        for f in split_file_list:
            fid = 0
            (savepath, fbasename) = path.split(f)
            with open(f, mode='rb') as fobj:
                for i in range(skip_row):
                    currentsize += len(fobj.readline())
                if need_title == 1:
                    title = fobj.readline()
                    currentsize += len(title)
                while True:
                    fid += 1
                    (savename, saveextension) = path.splitext(fbasename)
                    savename = savename + '_' + str(fid) + saveextension
                    savefn = path.join(savepath, savename)
                    fobj1 = open(savefn, 'wb')
                    if need_title: fobj1.write(title)
                    for i in range(split_line):
                        line = fobj.readline()
                        if not line: break
                        fobj1.write(line)
                        currentsize += len(line)
                        common.print_rateofprogress(currentsize, allsize)
                    fobj1.close()
                    if currentsize == allsize: break
        if trance_list: [remove(x) for x in trance_list]
        print('\n\n---------------完成分割文件---------------\n')
        return True

    '''
    split_bysize:按大小分割文件逻辑
    为支持大数据的分割，引入chunksize,split_size是输入的最终需要分割成的文件大小
    通过split_size//chunksize 计算最多可以按照chunksize的大小chunk多少次，
    剩余量split-chunksize*n，再最后read一次
    如果split_size<chunksize,则split_size//chunksize=0,则跳过chunk直接在最后一步一次性读取
    '''

    def split_bysize(self, choice):
        fp = common.get_file(self.opt[choice]['title'])
        if fp is None: return
        need_title = common.get_need_head(self.opt[choice]['title'])
        if need_title is None: return
        split_size = self.__get_split_size(self.opt[choice]['title'])
        if split_size is None: return
        trance_list = []
        print('\n---------------开始分割文件---------------\n')
        if fp.endswith(self.transtypes):
            trance_list = common.trans_files(fp, self.transtypes)
            if not trance_list: raise Exception('文件内容为空...')
            split_file_list = trance_list
        else:
            split_file_list = [fp]
        chunksize = 50 * 1024 * 1024
        allsize = sum([path.getsize(x) for x in split_file_list])
        currentsize = 0  # 记录整体已分割大小
        for f in split_file_list:
            fid = 0
            (savepath, fbasename) = path.split(f)
            fsize = path.getsize(f)
            with open(f, mode='rb') as fobj:
                if need_title == 1:
                    title = fobj.readline()
                    currentsize += len(title)
                chunknum = split_size // chunksize  # 计算chunk次数
                splitnum = ceil(fsize / split_size)  # 计算分割次数
                for i in range(splitnum):
                    fid += 1
                    (savename, saveextension) = path.splitext(fbasename)
                    savename = savename + '_' + str(fid) + saveextension
                    savefn = path.join(savepath, savename)
                    fobj1 = open(savefn, 'wb')
                    if need_title: fobj1.write(title)
                    havechunk = 0
                    for j in range(chunknum):
                        lines = fobj.readlines(chunksize)
                        fobj1.writelines(lines)
                        fobj1.flush()
                        len_lines = sum([len(x) for x in lines])
                        havechunk += len_lines
                        currentsize += len_lines
                        common.print_rateofprogress(currentsize, allsize)
                    if split_size - havechunk > 0:
                        lines = fobj.readlines(split_size - havechunk)
                        fobj1.writelines(lines)
                        currentsize += sum([len(x) for x in lines])
                        common.print_rateofprogress(currentsize, allsize)
                        fobj1.flush()
                    fobj1.close()
        if trance_list: [remove(x) for x in trance_list]
        print('\n\n---------------完成分割文件---------------\n')
        return True

    def split_bycolumn(self, choice):
        fp = common.get_file(self.opt[choice]['title'])
        if fp is None: return
        trans_list = []
        print('\n---------------开始处理文件---------------\n')
        if fp.endswith(self.transtypes):
            trans_list = common.trans_files(fp, self.transtypes)
            if trans_list is None: raise Exception('文件内容为空')
            split_file_list = trans_list
        else:
            split_file_list = [fp]
        chunkline = 500000
        for f in split_file_list:
            (savepath, fbasename) = path.split(f)
            (savename, saveextension) = path.splitext(fbasename)
            skip_row = common.get_skip_row(self.opt[choice]['title'])
            if skip_row is None: return
            split_header = self.__get_split_header(f,self.opt[choice]['title'],skip_row)
            if not split_header: return
            encode = common.get_file_encode(f)
            for t in common.trunk_file_byrow(f, encode, chunkline,skip_row):
                print(f'------正在生成文件------')
                t_group = t.groupby(by=split_header)
                for index, value in t_group:
                    savename_tail = str(index) if len(split_header) == 1 else '_'.join(
                        [str(x) for x in index])
                    savename_tail = sub(r"[\/\\\:\*\?\"\<\>\|.]", "_", savename_tail)
                    new_savename = savename + '_' + savename_tail + '.csv'
                    savefn = path.join(savepath, new_savename)
                    print(f'...{savefn}')
                    value.to_csv(savefn, index=False, encoding='gbk', mode='a', header=True)
        if trans_list: [remove(x) for x in trans_list]
        print('\n\n---------------完成分割文件---------------\n')
        return True

    def __get_split_row(self, optname):
        while True:
            inputstr = f'[{optname}]请输入分割行数>>>'
            choice = input(inputstr).strip()
            if choice:
                if choice.lower() == 'q': exit()
                if choice.lower() == 'b': return
                if choice.isdigit():
                    ret = int(choice)
                    if ret > 0:
                        return ret
                    else:
                        print('输入数字不能为0，请重新输入!')
                else:
                    print('输入非数字，请重新输入！')

    def __get_split_size(self, optname):
        while True:
            inputstr = f'[{optname}]请输入分割大小(MB)>>>'
            choice = input(inputstr).strip()
            if choice:
                if choice.lower() == 'q': exit()
                if choice.lower() == 'b': return
                ret = ceil(float(choice) * 1024 * 1024)
                if ret > 0:
                    return ret
                else:
                    print('输入数字不能为0，请重新输入!')


    def __get_split_header(self, f, optname,skiprow=0):
        try:
            encode = common.get_file_encode(f)
            tb_title = pd.read_csv(f, skiprows=skiprow,header=0, encoding=encode, error_bad_lines=False, low_memory=False,
                                   nrows=0, keep_default_na=False)
            tb_title_columns_list = list(tb_title.columns)
        except Exception as e:
            print(e)
            return
        while True:
            common.print_list_formating(tb_title_columns_list, 4)
            iptstr = f'[{optname}]请输入[分割字段]>>>'
            column_input = input(iptstr).strip()
            if column_input:
                if column_input.lower() == 'q': exit()
                if column_input.lower() == 'b': return
                sp = split('\[|\]', column_input)
                inp_list = []
                for s in sp:
                    if s != '' and s != ',': inp_list.append(s)
                for i in range(0, len(inp_list)):
                    s = inp_list[i]
                    m = r'[1-9]\d*-[1-9]\d*'
                    results = findall(m, inp_list[i])
                    newlist = []
                    if len(results) > 0:
                        for r in results:
                            r1 = r.split('-')
                            istrart = int(r1[0])
                            iend = int(r1[1]) + 1
                            for j in range(istrart, iend):
                                newlist.append(j)
                            s = s.replace(r, '')
                    m = r'[1-9]\d*'
                    results = findall(m, s)
                    if len(results) > 0:
                        for r in results:
                            newlist.append(int(r))
                    inp_list[i] = list(set(newlist))
                if len(inp_list) > 0:
                    return [tb_title_columns_list[i - 1] for i in inp_list[0]]
                else:
                    print('输入错误，请重新输入！')

