import os
import sys
import json
import shutil
import xmltodict
import numpy as np
import os.path as osp
from tqdm import tqdm

sys.path.append("..")

classname = 'text'

def generate_txt_labels(root_path):
    img_path = osp.join(root_path, 'images')
    label_path = osp.join(root_path, 'labels')
    label_txt_path = osp.join(root_path, 'labelTxt')
    if  osp.exists(label_txt_path):
        shutil.rmtree(label_txt_path)
    os.mkdir(label_txt_path)

    img_names = [osp.splitext(img_name.strip())[0] for img_name in os.listdir(img_path)]
    pbar = tqdm(img_names)
    for img_name in pbar:
        pbar.set_description("ICDAR15 generate_txt in {}".format(root_path))
        label = osp.join(label_path, 'gt_' + img_name+'.txt')
        label_txt = osp.join(label_txt_path, img_name+'.txt')
        f_label = open(label, encoding='UTF-8-sig')
        lines = f_label.readlines()
        s = ''
        for line in lines:
            box = line.strip().split(',')[:8]
            s += ' '.join(box) + ' ' + classname + ' 0\n' 
        f_label.close()
        with open(label_txt, 'w') as fw_label:
            fw_label.write(s)

if __name__ == '__main__':
    generate_txt_labels('/data-input/RotationDet/data/ICDAR2015/train')
    print('done!')
