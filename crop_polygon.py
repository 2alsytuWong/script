import json
import numpy as np
import cv2
import os

# input_json_path = '/workspace/mnt/group/ocr/qiutairu/code/maskrcnn/save/models_0401/inference/ArT_test/result.json'
input_json_path = '/workspace/mnt/group/ocr/wangxunyan/maskscoring_rcnn/result_decv.json'
img_path = ''
output_img_path = ''
conf_threshold = 0


if __name__ == '__main__':
    # load json file as dict
    with open(input_json_path, 'r') as f:
        input_dict = json.load(f)

    # ensure output_img_path existed
    if not os.path.exists(output_img_path):
        os.mkdir(output_img_path)

    for idx, (key, value) in enumerate(input_dict.items()):
        print("[ {} ]/[ {} ]".format(idx+1, len(input_dict)))
        img_name = key.replace('res', 'gt') + '.jpg'
        img = cv2.imread(os.path.join(img_path, img_name))
        H, W = img.shape[:2]

        # sort by conf
        def getConf(elem):
            return float(elem['confidence'])
        value.sort(key=getConf, reverse=True)

        for poly_idx, polygon in enumerate(value, 1):
            pts = polygon['points']
            conf = polygon['confidence']

            # filter low conf result
            if conf < conf_threshold:
                continue

            x, y, w, h = cv2.boundingRect(np.array(pts).astype(np.int32))
            # type1: origin
            crop_img = img[y:y+h, x:x+w]
            # type2: padding
            # x_pad = 5     # int(0.02 * w)
            # y_pad = 5     # int(0.02 * h)
            # new_x_min = max(0, x - x_pad)
            # new_y_min = max(0, y - y_pad)
            # new_x_max = min(W-1, x+w + x_pad)
            # new_y_max = min(H-1, y+h + y_pad)
            # crop_img = img[new_y_min:new_y_max, new_x_min:new_x_max]

            cv2.imwrite(os.path.join(output_img_path, '{}_{}.jpg'.format(img_name.replace('.jpg', ''), poly_idx)),
                        crop_img)
