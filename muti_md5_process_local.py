# -*- coding:utf-8 -*-
# created 2018/03/29 @Riheng
# 从本地读取图片，计算图片的md5值


from __future__ import print_function

'''
Version:
    - V1.0 initialization 03/29/18
    - V1.1 support compare md5 value with a md5 depot 10/23/18

Todo:
    - support multiprocess 
    - merge md5_process_inter.py

    从本地读取图片，计算图片的md5值,并将重复的图片去除:
        -input, --inputImagesPath  [required]
        -dup, --duplicationDir  [optional]
        -mv whether to move the duplication image, store_true [optional]
 
'''

import os
import sys
import argparse
import hashlib
import json
import imagehash
from PIL import Image
from tqdm import tqdm
from multiprocessing import Pool
import contextlib

def parse_args():
    parser = argparse.ArgumentParser(description="md5 process check image")
    parser.add_argument('-i', '--inputImagesPath', dest='inputImagesPath')
    parser.add_argument('-dup', '--duplicationDir', dest='duplicationDir')
    parser.add_argument('-dep', '--depot',
                        help='set -dep to support compare md5 value with a md5 depot', type=str)
    parser.add_argument(
        '-mv', '--move', help='whether to move the duplication image', action='store_true')
    # save md5 file
    parser.add_argument('-s', '--save', dest='save',
                        action='store_true', help='set -s to save md5 value')
    parser.add_argument('-t', '--type', help="choose md5 or phash", choices=['md5', 'phash', 'ahash', 'dhash'], default='md5')
    return parser.parse_args()


def checkFileIsImags(filePath):
    if ('JPEG' in filePath.upper()) or ('JPG' in filePath.upper()) \
            or ('PNG' in filePath.upper()) or ('BMP' in filePath.upper()):
        return True
    return True


def getAllImages(basePath=None):
    allImageList = []
    for parent, dirnames, filenames in os.walk(basePath):
        for file in filenames:
            imagePathName = os.path.join(parent, file)
            if checkFileIsImags(imagePathName):
                allImageList.append(imagePathName)
            else:
                # print("%s isn't image"%(imagePathName))
                pass
    return allImageList


def md5_process(image=None):
    hash_md5 = hashlib.md5()
    with open(image, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_hash(imgfile):
    if args.type == 'md5':
        md5_key = md5_process(imgfile)
    elif args.type == 'ahash':
        image = Image.open(imgfile)
        md5_key = imagehash.average_hash(image)
    elif args.type == 'dhash':
        image = Image.open(imgfile)
        md5_key = imagehash.dhash(image)
    elif args.type == 'phash':
        image = Image.open(imgfile)
        md5_key = imagehash.phash(image)
    return md5_key


def mv_same_md5_file(one, two, duplicationDir):
    if(os.path.exists(duplicationDir)) == False:
        os.makedirs(duplicationDir)
    cmdStr = "mv %s %s" % (two, duplicationDir)
    result_flag = os.system(cmdStr)
    #print(cmdStr)


def write_json(md5_imagaPath_dict, output):
    # 输出到文件中
    with open(output, 'w') as fi:
        for md5_key, url in md5_imagaPath_dict.items():
            temp = {md5_key: url}
            json.dump(temp, fi)
            fi.write('\n')

        #json.dump(hash_dic, f)  # 不使用indent


args = parse_args()

def main():
    allImagesPathList = getAllImages(basePath=args.inputImagesPath)
    md5_imagaPath_dict = {}

    if args.depot:
        with open(args.depot, 'r') as fi:
            for line in fi:
                md5_imagaPath = json.loads(line.strip())
                md5_imagaPath_dict.update(md5_imagaPath)

    dep_init_num = len(md5_imagaPath_dict)

    with contextlib.closing(Pool(8)) as pool:
        results = list(tqdm(pool.imap(gethash, allImagesPathList)))
            

    for imagePath in tqdm(allImagesPathList):
        try:
            md5_key = get_hash(imagePath)

            if md5_key in md5_imagaPath_dict:
                print("%s --- %s same md5_key" %
                      (imagePath, md5_imagaPath_dict.get(md5_key)))
                if args.move:
                    mv_same_md5_file(one=md5_imagaPath_dict.get(
                        md5_key), two=imagePath, duplicationDir=args.duplicationDir)
            else:
                md5_imagaPath_dict[md5_key] = imagePath
        except Exception as e:
            print("Error: {}".format(e))

    # md5值存储
    if args.save:
        output = os.path.join(args.inputImagesPath, 'md5ofBM.json')
        write_json(md5_imagaPath_dict, output)
        print("Generate %s with success" % (output))

    img_num = len(allImagesPathList)
    dup_num = len(allImagesPathList) + dep_init_num - len(md5_imagaPath_dict)
    print("Images number: %d" % img_num)
    print("Duplication images number: %d " % dup_num)
    print("Images number after deduplication: %d " % (img_num - dup_num))


if __name__ == '__main__':
    print('Start processing')
    main()
    print ('End ...')
