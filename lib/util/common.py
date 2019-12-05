# __author: linle
# __date: 2019/12/4
from os import path, scandir, remove
import cchardet
from re import sub
from win32api import GetFileAttributes
from multiprocessing import Process, cpu_count, Manager
from xlrd import open_workbook
from csv import writer
import pandas as pd
from math import ceil, floor


# 获取文件路径
def get_file(optname):
    while True:
        inputstr = f'[{optname}]请输入文件路径>>>'
        f = input(inputstr).strip()
        if f:
            if path.isfile(f):
                if path.exists(f):
                    return f
                else:
                    print('文件不存在，请重新输入！')
            elif f.lower() == 'b':
                return
            elif f.lower() == 'q':
                exit()
            else:
                print('输入错误，请重新输入！')


# 获取文件编码方式
def get_file_encode(fn):
    with open(fn, 'rb') as f:
        msg = f.read()
    return cchardet.detect(msg)['encoding']


# 将非法字符替换为下划线
def sub_invalid_symbol(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]."  # '/ \ : * ? " < > |'
    new_title = sub(rstr, "_", title)  # 替换为下划线
    return new_title


# 计算字符串实际打印长度
def get_str_len(s):
    return len(s.encode('gbk'))


# 搜索文件夹，返回文件列表
def get_files(filepath, filetypes):
    files = []
    for item in scandir(filepath):
        f = item.path
        if path.isdir(f):
            files = files + get_files(f, filetypes)
        elif path.isfile(f):
            if GetFileAttributes(f) < 34:
                (fpath, fbasename) = path.split(f)
                (fname, fextension) = path.splitext(fbasename)
                if fextension in filetypes: files.append(f)
    return files


# 调用多进程，通过xls_to_csv将.xls .xlsx文件另存为csv格式
def trans_files(fp, transtype):
    if not path.exists(fp): return  # 若路径不存在则终止
    files_xlsx = []
    if path.isdir(fp):
        files_xlsx = get_files(fp, transtype)
    elif path.isfile(fp):
        files_xlsx = [fp]
    len_files_xlsx = len(files_xlsx)
    if len_files_xlsx == 0: return  # 若需要转换的xls文件为空则终止
    p_list = []
    trans_list = Manager().list()
    new_split_file_xlsx = []
    for i in range(0, cpu_count()):
        new_split_file_xlsx.append(
            [files_xlsx[t] for t in range(0, len(files_xlsx)) if t % cpu_count() == i])
    for flist in new_split_file_xlsx:
        t = Process(target=xls_to_csv, args=(flist, trans_list))
        t.start()
        p_list.append(t)
    for p in p_list:
        p.join()
    return trans_list


# 将xls另存为csv
def xls_to_csv(fns, trans_list):
    for fn in fns:
        (fpath, fbasename) = path.split(fn)
        print(f'change file {fbasename} to csv...')
        try:
            wb = open_workbook(fn)
            for ws in wb.sheets():
                (savename, saveextension) = path.splitext(fbasename)
                sheetname = sub_invalid_symbol(ws.name)
                savename = savename + '_' + sheetname + '.csv'
                savefn = path.join(fpath, savename)
                if path.exists(savefn): remove(savefn)
                if ws.visibility == 0:
                    if ws.nrows > 0 and ws.ncols > 0:
                        trans_list.append(savefn)
                        with open(savefn, 'a', encoding='gbk', newline='') as f:
                            w = writer(f)
                            for i in range(ws.nrows):
                                w.writerow(ws.row_values(i))
        except KeyboardInterrupt as k:
            pass


# 大数据按行分割读取
def trunk_file_byrow(fn, encode, chunkline=500000, skiprow=0):
    reader = pd.read_csv(fn, skiprows=skiprow, encoding=encode, error_bad_lines=False, low_memory=False,
                         chunksize=chunkline, keep_default_na=False)
    n = 0
    for chunk in reader:
        # obj_list = list(chunk.select_dtypes(include='object'))
        # chunk[obj_list] = chunk[obj_list].astype('category')
        yield chunk


# 打印title
def print_title(d):
    n = 50
    left_black = int(n * 0.3)
    print('+' + '-' * n + '+')
    for index, value in enumerate(d):
        print('|' + ' ' * n + '|')
        s = str(index + 1) + '、' + value['title']
        slen = len(s.encode('gbk'))
        news = '|' + ' ' * left_black + s + ' ' * (n - left_black - slen) + '|'
        print(news)
    print('|' + ' ' * n + '|')
    print('+' + '-' * n + '+')


def get_floder(optname):
    while True:
        inputstr = f'[{optname}]请输入目录路径>>>'
        fp = input(inputstr).strip()
        if fp:
            if fp.lower() == 'q': exit()
            if fp.lower() == 'b': return
            if path.isdir(fp):
                if path.exists(fp):
                    return fp
                else:
                    print('目录不存在，请重新输入！')
            else:
                print('输入内容非有效路径，请重新输入！')


def get_need_head(optname):
    while True:
        inputstr = f'[{optname}]请输入是否包含表头(0:不包含,1:包含)>>>'
        choice = input(inputstr).strip()
        if choice:
            if choice.lower() == 'b': return
            if choice.lower() == 'q': exit()
            if choice.isdigit():
                choice = int(choice)
                if choice in [0, 1]:
                    return choice
                else:
                    print('输入错误，请重新输入！')
            else:
                print('输入非数字，请重新输入！')


def get_skip_row(optname):
    while True:
        inputstr = f'[{optname}]请输入跳过行数>>>'
        choice = input(inputstr).strip()
        if choice:
            if choice.lower() == 'b': return
            if choice.lower() == 'q': exit()
            if choice.isdigit():
                return int(choice)
            else:
                print('输入非数字，请重新输入！')


def print_rateofprogress(current, total, barlen=35):
    j = floor((current * barlen) / total)
    s = '>' * j + "." * (barlen - j)
    percent = round((current / total) * 100, 2)
    print('\r%s%s%%' % (s, percent), end='')


def trunk_csv_bysize(fp, needtitle, chunksize=100 * 1024 * 1024, skiprow=0):
    f = open(fp, 'rb')
    buf = None
    title = None
    lenbuf = 0
    if skiprow > 0:
        for i in range(skiprow):
            f.readline()
    if needtitle == 1:
        title = f.readline()
    while True:
        buf = f.read(chunksize)
        if buf:
            yield title, buf, len(buf)
        else:
            f.close()
            break


def print_list_formating(print_list, step=4):
    print()
    print_list = [' ' + str(i + 1) + '、' + print_list[i] + ' ' for i in range(len(print_list))]
    line_len = 0
    for i in range(0, step):
        max_len = 0
        for j in range(i, len(print_list), step):
            len_str = len(print_list[j].encode('gbk'))
            if max_len < len_str: max_len = len_str
        for j in range(i, len(print_list), step):
            len_str = len(print_list[j].encode('gbk'))
            print_list[j] = print_list[j] + ' ' * (max_len - len_str)
        line_len += max_len
    print('+' + '-' * line_len + '+')
    for i in range(0, len(print_list), step):
        list1 = print_list[i:i + step]
        print('|' + ''.join(list1) + '|')
    print('+' + '-' * line_len + '+')
    print()
