#encoding:utf-8
import sys
import qrcode 
import requests
import platform
from io import BytesIO
import pyzbar.pyzbar as pyzbar 
from PIL import Image,ImageEnhance


class Qrcode():
    def __init__(self):
        pass
    
    def identify(self, image=None, image_url=None):
        if image and image_url:
            print("only choice image or url!")
            return 
        elif image_url:
            try:
                img = Image.open(BytesIO(requests.get(image_url, headers=HEADERS).content))
            except Exception as e:
                print(e)
                return 
        elif image: 
            try:
                img = Image.open(image)
            except Exception as e:
                print(e)
                return
        else:
            print("must choice one of image or image_url!")
            return 
        #img = ImageEnhance.Brightness(img).enhance(2.0)#增加亮度
        #img = ImageEnhance.Sharpness(img).enhance(17.0)#锐利化
        #img = ImageEnhance.Contrast(img).enhance(4.0)#增加对比度
        #img = img.convert('L')#灰度化
        #img.show()
        decode_result = pyzbar.decode(img)
        if decode_result:
            result = [str(dr.data, encoding='utf-8') for dr in decode_result]
            return result 
        return 

    def print_to_terminal(self, string=None, image=None,version=1):
        if string and image:
            return "only choice string or image!"
        elif string:
            self.create(string, version)
        elif image:
            qr_result = self.identify(image=image)
            if qr_result:
                for qr in qr_result:
                    self.create(qr, version)
            else:
                print("can not identify this picture!")
        else:
            print("you must choice one of imge of string!") 
    
    def create(self, string, pic_name='qrcode.png', show_terminal=1, version=1):
        qr_img = qrcode.QRCode(version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr_img.add_data(string)
        qr_img.make()
        # pic = qr_img.make_image()
        # pic.save(pic_name)
        # img = Image.open(pic_name)
        # img.show()
        if show_terminal:
            qr_img.print_tty()


if __name__ == "__main__":
    qr = Qrcode()
    s = input("请输入字符串：")
    qr.create(string=s, show_terminal=1)
