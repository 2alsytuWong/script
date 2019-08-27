import numpy as np 
import cv2
import os
from tqdm import tqdm
try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

xml_dir = '/workspace/mnt/group/algorithm/wangxunyan/voc_data/chendan/xuhui_Data/Nomotor20190726/Annotations'
img_dir = '/workspace/mnt/group/algorithm/wangxunyan/voc_data/chendan/xuhui_Data/Nomotor20190726/JPEGImages'
output_img_dir = '/workspace/mnt/group/algorithm/wangxunyan/crop_voc_data'
xml_list = os.listdir(xml_dir)

for xml_name in tqdm(xml_list):
	if xml_name.split('.')[-1] == 'xml':
		xml_file = os.path.join(xml_dir, xml_name)
	else:
		continue
	parser = et.parse(xml_file)
	root = parser.getroot()
	img_name = xml_name.replace('.xml','.jpg')
	img_path = os.path.join(img_dir, img_name)
	size = root.find('size')
	img_width = int(size.find('width').text)
	img_height = int(size.find('height').text)
	img_depth = int(size.find('depth').text)
	print(img_path)
	img = cv2.imread(img_path)
	H, W = img.shape[:2]
	crop_idx = 0

	for obj in root.findall('object'):
		label = obj.find('name').text
		if label != 'non-motor':
			continue
		crop_idx += crop_idx
		bbox = obj.find('bndbox')
		xmin = int(bbox.find('xmin').text)
		ymin = int(bbox.find('ymin').text)
		xmax = int(bbox.find('xmax').text)
		ymax = int(bbox.find('ymax').text)
		assert(xmax>xmin)
		assert(ymax>ymin)
		o_width = abs(xmax - xmin)
		o_height = abs(ymax - ymin)

		crop_img = img[ymin:ymax, xmin:xmax]

		cv2.imwrite(os.path.join(output_img_dir, '{}_{}.jpg'.format(img_name.replace('.jpg', ''), crop_idx)),
                        crop_img)






















