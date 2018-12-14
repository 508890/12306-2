#encoding:utf-8
import sys 
import time
import random 
import json 
import base64
import re 
import requests
from urllib.parse import unquote 
from qrcode_tool import Qrcode
from residual_ticket import TrainTicket

check_qr_url = "https://kyfw.12306.cn/passport/web/checkqr"
login_url = "https://kyfw.12306.cn/otn/resources/login.html"
uamtk_url = "https://kyfw.12306.cn/passport/web/auth/uamtk-static"
qr_url = "https://kyfw.12306.cn/passport/web/create-qr64"
conf_url = "https://kyfw.12306.cn/otn/login/conf"
contact_url = "https://kyfw.12306.cn/otn/passengers/query"


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


class Login():
    
    def __init__(self, method='scan', username=None, passwd=None):
        self.method = method 
        self.qr_code = Qrcode()
        self.train_ticket = TrainTicket()
        self.session = requests.session()
        self.session.headers=Login.headers()
        self.session.get(url=login_url)
        self.session.post(url=uamtk_url,data={"appid":"otn"})

    def get_qr64(self, show='TERMINAL'):
        data = {"appid":"otn"}
        qr_res = self.session.post(url=qr_url, data=data)

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
            res = self.session.post(url=check_qr_url, data=data)
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
                    self.session.get(url="https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin")
                    verfiy = self.session.post(url="https://kyfw.12306.cn/passport/web/auth/uamtk?callback=jQuery191{}_{}".format(
                        ''.join(str(random.choice(range(10))) for _ in range(19)), int(round(time.time()*1000))), 
                                data={"appid":"otn", "_json_att":""})
                    verfiy_json = json.loads(verfiy.text.split('(')[1].split(')')[0])
                    tk = verfiy_json.get("newapptk", '')
                    self.session.post(url="https://kyfw.12306.cn/otn/uamauthclient", data={'tk':tk})
                    break
                elif code_status == "3":
                    self.print_status("二维码已过期。。。")
                else:
                    self.print_status("系统错误！")
                    break
            except Exception as e:
                print(e)
            time.sleep(2)


    def print_status(self, value):
        sys.stdout.write('\r')
        sys.stdout.write(value)
        sys.stdout.flush()

    def get_contact(self):
        data = {
            "pageIndex": "1",
            "pageSize": "10"
        }
        res = self.session.post(url=contact_url, data=data)
        try:
            contact_json = json.loads(res.text)
            if contact_json.get('status', '')==True:
                contacts = contact_json.get('data',{}).get('datas',[])
                for contact in contacts:
                    print(contact)
        except Exception as e:
            print(e)

    def ordain_ticket(self):
        start = input("请输入起点：")
        end = input("请输入终点：")
        date_str = input("请输入时间(eg:2018-12-12)：")
        show_price = input("是否需要显示票价信息(1,显示、2,不显示)：")
        ticket_info = self.train_ticket.search_ticket(start,end,date_str,show_price)
        if not ticket_info:
            print("No tickets!")

        _ = self.session.post(url="https://kyfw.12306.cn/otn/login/checkUser", data={"_json_att":""})
        print(_.status_code)
        print(_.text)
        while 1:
            choice_train_times = input("please input trains times:")
            choice_train_info = ticket_info.get(choice_train_times, '')
            if not choice_train_info:
                print("input error!please retry!")
            else:
                break


        data = {
            "secretStr": unquote(choice_train_info[0]),
            "train_date": date_str,
            "back_train_date": "2018-12-14",
            "tour_flag": "dc",
            "purpose_codes": "ADULT",
            "query_from_station_name": choice_train_info[2],
            "query_to_station_name": choice_train_info[3],
            "undefined":"" 
        }

        a = self.session.post(url="https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest", data=data)
        print(a.text)

        b = self.session.post(url="https://kyfw.12306.cn/otn/confirmPassenger/initDc", data={"_json_att":""})
        # print(b.text)
        rst_re = re.search(r"(?<=RepeatSubmitToken\s=\s\').+?(?=\';)", b.text)
        RepeatSubmitToken = rst_re.group() if rst_re else ""

        c = self.session.post(url="https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs", 
        data={"_json_att":"", "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken})
        print(c.text)
        passsenger_data = json.loads(c.text)
        if passsenger_data.get('status', '') == True:
            normal_passengers = passsenger_data.get('normal_passengers',[])
            for passsenger in normal_passengers:
                print(passsenger)


        check_order_data = {
            "cancel_flag": "2",
            "bed_level_order_num": "000000000000000000000000000000",
                                #座位类型,0,票类型,乘客名,证件类型,证件号,手机号码,保存常用联系人(Y或N)
            "passengerTicketStr": "1,0,3,何思贤,1,511324199712182332,14781275573,N",
                                # 乘客名,证件类型,证件号,乘客类型
            "oldPassengerStr": "何思贤,1,511324199712182332,3_",
            "tour_flag": "dc",
            "randCode": "",
            "whatsSelect": "1",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken
        }
        self.session.post(url="https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo", data=check_order_data)

        GMT_FORMAT = '%a %b %d %Y 00:00:00 GMT+0800 (China Standard Time)'
        queue_count_data = {
            "train_date": time.strftime(GMT_FORMAT, time.localtime()),
            "train_no": "760000K1130D",
            "stationTrainCode": "K113",
            "seatType": "1",
            "fromStationTelecode": "CDW",
            "toStationTelecode": "ECW",
            "leftTicket": "Wmy83lFVAhWWVO1Op5NUdo8iBPOlXyPN7zFg%2FfdmKFuIFca6A8pcA7yyarc%3D",
            "purpose_codes": "00",
            "train_location": "W1",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken
        }
        self.session.post(url="https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount", data=queue_count_data)

        confirm_queue_data = {
            "passengerTicketStr": "1,0,3,何思贤,1,511324199712182332,14781275573,N",
            "oldPassengerStr": "何思贤,1,511324199712182332,3_",
            "randCode": "",
            "purpose_codes": "00",
            "key_check_isChange": "D9DCF91FC78A440393B07BC4A19EC934E355EF75AC3880555EA16766",
            "leftTicketStr": "Wmy83lFVAhWWVO1Op5NUdo8iBPOlXyPN7zFg%2FfdmKFuIFca6A8pcA7yyarc%3D",
            "train_location": "W1",
            "choose_seats":"" , #选座？？？
            "seatDetailType": "000",
            "whatsSelect": "1",
            "roomType": "00",
            "dwAll": "N",
            "_json_att":"", 
            "REPEAT_SUBMIT_TOKEN": "a27d644aaee56e7b435307b2ab4b94e8"
        }
        self.session.post(url="https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue",data=confirm_queue_data)

        order_dc_queue_data = {
            "orderSequence_no": "E267766727",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": "a27d644aaee56e7b435307b2ab4b94e8"
        }
        self.session.post(url="https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue", data=order_dc_queue_data)

        self.session.post(url="https://kyfw.12306.cn/otn//payOrder/init?random=1544712281252", data=order_dc_queue_data)

    def keep_online(self):
        self.session.get(url="")

    def start(self):
        if self.method == 'scan':
            uid = self.get_qr64()
            if uid:
                self.check_qr(uid)
            # self.get_contact()
            self.ordain_ticket()
    
    @staticmethod
    def headers(remark=None):
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "kyfw.12306.cn",
            "If-Modified-Since": "0",
            "Referer":"https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        # if "checkUser" in remark:
        #     header["Referer"] = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
        # elif "submitOrderRequest" in remark:
        #     header["Referer"] = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
        return header

if __name__ == "__main__":
    log = Login()
    log.start()
