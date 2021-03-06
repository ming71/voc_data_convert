import dota_utils as util
import os
import sys
import cv2
import math
import json
import numpy as np
from utils import *

from PIL import Image
from tqdm import tqdm


classnames = ['car', 'airplane']

def UCAS_AOD2COCOTrain(srcpath, destfile, cls_names, train_set_file):
    imageparent = os.path.join(srcpath, 'AllImages')
    labelparent = os.path.join(srcpath, 'Annotations')

    data_dict = {}
    info = { 'contributor': 'ming71',
             'data_created': '2020',
             'description': 'UCAS_AOD',
             'url': 'sss',
             'version': '1.0',
             'year': 2014}
    data_dict['info'] = info
    data_dict['images'] = []
    data_dict['categories'] = []
    data_dict['annotations'] = []
    for idex, name in enumerate(cls_names):
        single_cat = {'id': idex + 1, 'name': name, 'supercategory': name}
        data_dict['categories'].append(single_cat)

    inst_count = 1
    image_id = 1
    with open(train_set_file, 'r') as f_set:
        filenames = [x.strip('\n') for x in f_set.readlines()]
        # import ipdb;ipdb.set_trace()

    with open(destfile, 'w') as f_out:
        # filenames = util.GetFileFromThisRootDir(labelparent)
        pbar = tqdm(filenames)
        for filename in pbar:
            pbar.set_description("UCAS_AOD2COCOTrain")
            imagepath = os.path.join(imageparent, filename + '.png')

            img = Image.open(imagepath)
            height = img.height
            width = img.width

            single_image = {}
            single_image['file_name'] = filename + '.png'
            single_image['id'] = image_id
            single_image['width'] = width
            single_image['height'] = height
            data_dict['images'].append(single_image)

            # annotations
            objects = parse_txt_poly2(os.path.join(labelparent, filename+'.txt'))
            for obj in objects:
                single_obj = {}
                single_obj['area'] = obj['area']
                single_obj['category_id'] = cls_names.index(obj['name']) + 1
                single_obj['segmentation'] = []
                single_obj['segmentation'].append(obj['poly'])
                single_obj['iscrowd'] = 0
                xmin, ymin, xmax, ymax = min(obj['poly'][0::2]), min(obj['poly'][1::2]), \
                                         max(obj['poly'][0::2]), max(obj['poly'][1::2])

                width, height = xmax - xmin, ymax - ymin
                single_obj['bbox'] = xmin, ymin, width, height
                single_obj['image_id'] = image_id
                data_dict['annotations'].append(single_obj)
                single_obj['id'] = inst_count
                inst_count = inst_count + 1
            image_id = image_id + 1
        json.dump(data_dict, f_out)

def UCAS_AOD2COCOTest(srcpath, destfile, cls_names, test_set_file):
    imageparent = os.path.join(srcpath, 'AllImages')
    data_dict = {}
    info = { 'contributor': 'ming71',
             'data_created': '2020',
             'description': 'UCAS_AOD',
             'url': 'sss',
             'version': '1.0',
             'year': 2014}
    data_dict['info'] = info
    data_dict['images'] = []
    data_dict['categories'] = []
    for idex, name in enumerate(cls_names):
        single_cat = {'id': idex + 1, 'name': name, 'supercategory': name}
        data_dict['categories'].append(single_cat)
    
    with open(test_set_file, 'r') as f_set:
        filenames = [x.strip('\n') for x in f_set.readlines()]

    inst_count = 1
    image_id = 1
    with open(destfile, 'w') as f_out:
        # filenames = util.GetFileFromThisRootDir(imageparent)
        pbar = tqdm(filenames)
        for filename in pbar:
            pbar.set_description("UCAS_AOD2COCOTest")
            # image_id = int(basename[1:])
            imagepath = os.path.join(imageparent, filename + '.png')
            # img = cv2.imread(imagepath)
            img = Image.open(imagepath)
            # height, width, c = img.shape
            height = img.height
            width = img.width

            single_image = {}
            single_image['file_name'] = filename + '.png'
            single_image['id'] = image_id
            single_image['width'] = width
            single_image['height'] = height
            data_dict['images'].append(single_image)

            image_id = image_id + 1
        json.dump(data_dict, f_out)




def parse_txt_poly(filename):
    objects = []
    #print('filename:', filename)
    f = []
    if (sys.version_info >= (3, 5)):
        fd = open(filename, 'r',encoding='UTF-8-sig')
        f = fd
    elif (sys.version_info >= 2.7):
        fd = codecs.open(filename, 'r')
        f = fd
    count = 0
    while True:
        line = f.readline()
        count = count + 1
        # if count < 2:
        #     continue
        if line:
            splitlines = line.strip().split()
            object_struct = {}
            object_struct['name'] = splitlines[0]
            object_struct['difficult'] = '0' 
            object_struct['poly'] = [(float(splitlines[1]), float(splitlines[2])),
                                     (float(splitlines[3]), float(splitlines[4])),
                                     (float(splitlines[5]), float(splitlines[6])),
                                     (float(splitlines[7]), float(splitlines[8]))
                                     ]
            gtpoly = shgeo.Polygon(object_struct['poly'])
            object_struct['area'] = gtpoly.area
            poly = list(map(lambda x:np.array(x), object_struct['poly']))
            object_struct['long-axis'] = max(distance(poly[0], poly[1]), distance(poly[1], poly[2]))
            object_struct['short-axis'] = min(distance(poly[0], poly[1]), distance(poly[1], poly[2]))
            if (object_struct['long-axis'] < 15):
                object_struct['difficult'] = '1'
                global small_count
                small_count = small_count + 1
            objects.append(object_struct)
        else:
            break
    return objects

def parse_txt_poly2(filename):
    objects = parse_txt_poly(filename)
    for obj in objects:
        obj['poly'] = TuplePoly2Poly(obj['poly'])
        obj['poly'] = list(map(int, obj['poly']))
    return objects

if __name__ == '__main__':

    UCAS_AOD2COCOTrain(r'/data-input/AerialDetection-master/data/UCAS_AOD',
                   r'/data-input/AerialDetection-master/data/UCAS_AOD/train.json',
                   classnames,
                   r'/data-input/AerialDetection-master/data/UCAS_AOD/ImageSets/train.txt')
    UCAS_AOD2COCOTrain(r'/data-input/AerialDetection-master/data/UCAS_AOD',
                   r'/data-input/AerialDetection-master/data/UCAS_AOD/val.json',
                   classnames,
                   r'/data-input/AerialDetection-master/data/UCAS_AOD/ImageSets/val.txt')
   
    UCAS_AOD2COCOTest(r'/data-input/AerialDetection-master/data/UCAS_AOD',
                  r'/data-input/AerialDetection-master/data/UCAS_AOD/test.json',
                  classnames,
                  r'/data-input/AerialDetection-master/data/UCAS_AOD/ImageSets/test.txt')





