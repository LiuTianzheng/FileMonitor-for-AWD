import os
import sys
import hashlib
import shutil
import random
import string
import time

def generate_random_str(randomlength=16):
    #生成一个指定长度的随机字符串
    #string.digits=0123456789
    #string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def get_filelist(dir, Filelist):
    # 遍历文件夹及其子文件夹中的文件，并存储在一个列表中
    # 输入文件夹路径、空文件列表[]
    # 返回 文件列表Filelist,包含文件名（完整路径）
    newDir = dir
    if os.path.isfile(dir):
        Filelist.append(dir)
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            if s == 'bak':
                pass
#                print('Notice: "bak" is already exist!')
            else:
                newDir=os.path.join(dir,s)
                get_filelist(newDir, Filelist)
        return Filelist

def get_dirlist(dir, Dirlist):
    # 遍历当前目录下所有子目录
    # 输入当前目录路径，空目录列表[]
    # 返回 目录列表Dirlist，包含当前目录下包含的所有目录及子目录
    newDir = dir
    for i in os.listdir(dir):
        newDir = os.path.join(dir,i)
        if os.path.isdir(newDir):
            if newDir == './bak':
                print('Notice: "./bak" is already exist!')
            else:
                Dirlist.append(newDir)
                get_dirlist(newDir, Dirlist)
    return Dirlist

def get_md5(dir_list,File_md5_list):
    # 获取文件MD5值，并和其路径进行拼接
    # 输入文件列表、空MD5列表[]
    # 返回 MD5列表File_md5_list，包含所有文件路径和MD5值：filepath:MD5
    for i in range(len(dir_list)):
        file_name = dir_list[i]
        with open(file_name, 'rb') as fp:
            data = fp.read()

        file_md5 = hashlib.md5(data).hexdigest()
        #print(file_name)
        #print(file_md5)
        File_md5_list.append(str(file_name) + ':' + str(file_md5))

    return File_md5_list

def backupfiles(source_list,bak_list,File_md5_list,Dirlist):
    # 备份所有文件到指定目录
    # 先判断'./bak'目录是否存在，若存在删除'./bak'目录及其目录下所有文件，并重新执行backupfiles()
    # 若'./bak'目录不存在，创建'./bak'目录
    target_dir = './bak/'
    if os.path.isdir(target_dir):
        print('Notice: target_dir is already exist!')
        shutil.rmtree('./bak')
        backupfiles(source_list,bak_list,File_md5_list,Dirlist)

    else:
        os.makedirs(target_dir)
        print('Notice: target_dir created successful!')
        for b in range(len(Dirlist)):
            tmp_dir = './bak' + str(Dirlist[b])[1:]
            os.makedirs(tmp_dir)

    # 创建filename_list列表，截取File_md5_list列表元素，并存储到对应下标的filename_list列表
    filename_list = []
    for j in File_md5_list:
        tmp = j[1:-33]
        filename_list.append(tmp)
#        print(filename_list)

    # 构造备份文件路径，并将文件备份到指定位置
    for i in filename_list:
        source = str(i)
#        print(source)
        target_file_dir = os.path.join(target_dir, source[1:])
#        print(target_file_dir)
        bak_list.append(target_file_dir)
        #备份文件到指定目录
        source_tmp = '.' + str(source)
#        print(source_tmp)
#        print(target_file_dir)
#        os.system('cp ' + str(source_tmp) + ' ' + str(target_file_dir))
#        shutil.copy(source_tmp,target_file_dir)
        if os.path.isdir(source_tmp):
            os.makedirs(target_file_dir)
            print('Notice: create ' + str(target_file_dir) + ' successful!')
        shutil.copy(source_tmp,target_file_dir)

    return bak_list, filename_list

def check_newfiles(old_list, path, filename_tmp):
    # 检测新文件，将新文件后缀重命名并移动到'./drop'目录下
    # 输入原始文件列表，监控目录，（原始文件路径列表，备份文件路径列表）用来恢复文件
    drop_dir = './bak/drop'
    if os.path.isdir(drop_dir):
        pass
    else:
        os.makedirs(drop_dir)

    new_list = get_filelist(path, [])
    for i in new_list:
        if old_list.count(i) == 0:
            tmp_str = generate_random_str()
            tmp_name = str(i) + ".drop" + str(tmp_str)
            os.rename(i,tmp_name)
            shutil.move(tmp_name,drop_dir)

    file_rec(old_list, path, filename_tmp)

def file_list_tmp(filename_list, filename_tmp):
    # 生成原始文件路径
    # 输入原始文件列表
    # 在列表每个元素前加'.'
    for j in filename_list:
        tmp = '.' + str(j)
        filename_tmp.append(tmp)
    return filename_tmp

def file_rec(old_list_1, path, filename_tmp):
    # 检测被删除和被修改的文件，并将其从备份文件中还原
    # 输入原始文件列表，原始目录，原始文件路径，备份文件路径
    new_list_1 = get_filelist(path, [])
    #print(filename_tmp)
    for i in old_list_1:
        if new_list_1.count(i) == 0:
            tmp_idx = filename_tmp.index(i)
            #print('tmp_idx  >>>>>>  ',tmp_idx)
            #print('target_file_dir[tmp_idx]  >>>>>>   ',target_file_dir[tmp_idx])
            tar_file_dir = './bak' + str(i)[1:]
            shutil.copy(tar_file_dir,i)

    new_md5_list = get_md5(new_list_1, [])
    for b in File_md5_list:
        if new_md5_list.count(b) == 0:
            tmp_dir_str = b[:-33]
            tmp_md5_idx = filename_tmp.index(tmp_dir_str)
            #print(target_file_dir[tmp_md5_idx])
            tar_file_dir = './bak' + str(tmp_dir_str)[1:]
            os.remove(tmp_dir_str)
            shutil.copy(tar_file_dir,tmp_dir_str)


if __name__ == '__main__' :
    path = r'./'
    a_list = get_filelist(path, [])
#    print(list)

    dirlist_tmp = get_dirlist(path,[])
#    print(dirlist_tmp)

    File_md5_list = get_md5(a_list,[])
#    print(File_md5_list)

    backup_list,filename_list = backupfiles(a_list,[],File_md5_list,dirlist_tmp)
#    print(target_file_dir)

    filename_tmp = file_list_tmp(filename_list, [])
#    print(filename_tmp)

    while True:
        check_newfiles(a_list, path, filename_tmp)
        time.sleep(2)
