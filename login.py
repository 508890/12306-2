#encoding:utf-8
import sys 
import time
import random 
import json 
import base64
import requests
from qrcode_tool import Qrcode

check_qr_url = "https://kyfw.12306.cn/passport/web/checkqr"
login_url = "https://kyfw.12306.cn/otn/resources/login.html"
uamtk_url = "https://kyfw.12306.cn/passport/web/auth/uamtk-static"
qr_url = "https://kyfw.12306.cn/passport/web/create-qr64"
conf_url = "https://kyfw.12306.cn/otn/login/conf"

def headers(ref=None):
    user_agent = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
        "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
        "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2"
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
    ]
    header = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "kyfw.12306.cn",
        "If-Modified-Since": "0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    if ref:
        header["Refere"] = "https://kyfw.12306.cn/otn/resources/login.html"
    return header

class Login():
    
    def __init__(self, method='scan', username=None, passwd=None):
        self.method = method 
        self.qr_code = Qrcode()
        self.session = requests.session()
        self.session.get(url=login_url, headers=headers())
        self.session.post(url=uamtk_url,data={"appid":"otn"}, headers=headers())

    def get_qr64(self, show='TERMINAL'):
        data = {"appid":"otn"}
        qr_res = self.session.post(url=qr_url, data=data, headers=headers(ref='1'))

        try:
            qr_json = json.loads(qr_res.text)
            if qr_json.get("result_message", '') == "生成二维码成功":
                qr64_data = qr_json.get('image', '')
                qr_img = base64.b64decode(qr64_data)
                with open('login_qrcode.png', 'wb') as qf:
                    qf.write(qr_img)
                if show == "TERMINAL":
                    self.qr_code.print_to_terminal(image='login_qrcode.png',version=1)
                uid = qr_json.get('uuid', '')
                # self.session.post(url=conf_url)
                return uid
            return
        except Exception as e:
            print(e)
            return 

    def check_qr(self, uid):
        data = {
            "uuid": uid,
            "appid": "otn"
        }
        times = 0
        while 1:
            res = self.session.post(url=check_qr_url, data=data, headers=headers())
            try:
                res_json = json.loads(res.text)
                code_status = res_json.get('result_code', '')
                times += 1 
                if code_status == "0":
                    self.print_status("等待扫描{}".format("。"*(times%4)))
                elif code_status == "1":
                    self.print_status("扫描成功，请确认{}".format("。"*(times%4)))
                elif code_status == "2":
                    self.print_status("确认成功，即将登录。。。")
                    sys.stdout.write('\n')
                    break
                elif code_status == "3":
                    self.print_status("二维码已过期。。。")
                else:
                    self.print_status("系统错误！")
            except Exception as e:
                print(e)
            time.sleep(2)

    def print_status(self, value):
        sys.stdout.write('\r')
        sys.stdout.write(value)
        sys.stdout.flush()

    def start(self):
        if self.method == 'scan':
            uid = self.get_qr64()
            if uid:
                self.check_qr(uid)

if __name__ == "__main__":
    log = Login()
    log.start()
