from operator import concat
import cv2
from anpr import DataTrafficOCR
import os
import json
import shutil
import base64

def crop_image(img_path):
    img = cv2.imread(img_path)
    img = img[:405, ]

    cv2.imwrite(img_path, img)

def rename_image(img_name, name_concat):
    file_name, extension = img_name.split(".")

    new_name = file_name+'_'+name_concat+"."+extension

    return new_name

def save_file(src, dst):
    shutil.move(src, dst)

def get_ocr(dir_path):
    ocr = DataTrafficOCR('generated', "lib")

    for root, _, files in os.walk(dir_path):
        for file in files:
            img_abs = os.path.join(root, file)

            crop_image(img_abs)

            val = ocr.ocr(img_abs)
            
            result = json.loads(val)

            if len(result['result']) > 1:

                plate = str(result['result'])
                print(plate)

                img_new_abs = rename_image(img_abs, plate)
            else:
                img_new_abs = rename_image(img_abs, "NULL")

            save_file(img_abs, img_new_abs)


if __name__ == "__main__":
    get_ocr("/home/willian/dest/")