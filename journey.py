#encoding:utf-8
import re
import sys 
import time
import random 
import json 
import base64 
import requests
from urllib.parse import unquote 
from prettytable import PrettyTable
from qrcode_tool import Qrcode
from residual_ticket import TrainTicket
from urls import urls_dict as url


# conf_url = "https://kyfw.12306.cn/otn/login/conf"
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

class TrainJourney():
    
    def __init__(self, method='scan', username=None, passwd=None):
        self.host = "https://kyfw.12306.cn"
        self.method = method 
        self.qr_code = Qrcode()
        self.train_ticket = TrainTicket()
        self.session = requests.session()
        self.session.headers = self.headers()
        self.session.get(url=self.host+url['login']['url'], 
                    headers=self.headers(url['login']['referer']))
        self.session.post(url=self.host+url['uamtk']['url'], data={"appid":"otn"}, 
                    headers=self.headers(url['uamtk']['referer']))
        self.contact_table = PrettyTable(["编号","姓名","性别","证件类型","证件号","乘客类型","手机号","邮箱"])

    def get_qr64(self, show='TERMINAL'):
        '''
        get qrcode picture, return params uid
        '''
        data = {"appid":"otn"}
        qr_res = self.session.post(url=self.host+url['create_qr']['url'], data=data, headers=url['create_qr']['referer'])
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
        '''
        check qrcode status
        '''
        times = 0
        data = {"uuid": uid, "appid": "otn"}
        while 1:
            res = self.session.post(url=self.host+url['check_qr']['url'], data=data, headers=self.headers(url['check_qr']['referer']))
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
                    self.session.get(url=self.host+url['user_login']['url'], headers=self.headers(url['user_login']['referer']))
                    uamtk_url = self.host+url['uamtk']['url'].format(''.join(str(random.choice(range(10))) for _ in range(19)), 
                                int(round(time.time()*1000)))
                    verfiy = self.session.post(url=uamtk_url, data={"appid":"otn", "_json_att":""}, headers=self.headers(url['uamtk']['referer']))
                    try:
                        verfiy_json = json.loads(verfiy.text.split('(')[1].split(')')[0])
                        tk = verfiy_json.get("newapptk", '')
                    except:
                        print("获取tk参数错误！")
                    self.session.post(url=self.host+url['uamauth_client']['url'], data={'tk':tk}, headers=self.headers(url['uamauth_client']['referer']))
                    break
                elif code_status == "3":
                    self.print_status("二维码已过期。。。")
                else:
                    self.print_status("系统错误！")
                    break
            except Exception as e:
                print(e)
            time.sleep(2)

    def ordain_ticket(self, method='auto'):
        start = input("请输入起点：")
        end = input("请输入终点：")
        date_str = input("请输入时间(eg:2018-12-12)：")
        show_price = input("是否需要显示票价信息(1,显示、2,不显示)：")
        ticket_info = self.train_ticket.search_ticket(start,end,date_str,show_price)
        if not ticket_info:
            print("No tickets!")

        while 1:
            choice_train_times = input("please input trains times:")
            choice_train_info = ticket_info.get(choice_train_times, '')
            if not choice_train_info:
                print("input error!please retry!")
            else:
                break
        
        self.__check_user()
        
        self.__submit_order(choice_train_info)

        init_dc_params = self.__init_dc()
        RepeatSubmitToken, key_check_isChange, leftTicketStr = init_dc_params
        print_contact = True if method!='auto' else False
        contact_data = self.__get_passenger(RepeatSubmitToken, print_contact)

        while 1:
            choice_passenger = input("请选择乘客名或者乘客编号：")
            passenger_info = contact_data.get(choice_passenger, '')
            if not passenger_info:
                for p in contact_data.values():
                    if choice_passenger == p[0]:
                        passenger_info = p
            if passenger_info:
                break 
            else:
                print("你输入的选项有误，请重新输入！")

        choice_seat_type = input("请选择座位类型：")

        #座位类型,0,票类型,乘客名,证件类型,证件号,手机号码,保存常用联系人(Y或N)
        passenger_ticket_str = ",".join([choice_seat_type, passenger_info[5], passenger_info[4], passenger_info[0],
                                    passenger_info[2],passenger_info[3],passenger_info[6],'N'])
        old_passenger_str = ",".join([passenger_info[0], passenger_info[2],passenger_info[3],passenger_info[4]+"_"])
        
        self.__check_order_info(choice_train_info, passenger_ticket_str, old_passenger_str, RepeatSubmitToken)

        self.__get_queue_count(choice_train_info, leftTicketStr, RepeatSubmitToken)

        train_location = choice_train_info[15]
        self.__confirm_queue(passenger_ticket_str,old_passenger_str,key_check_isChange,
                                    leftTicketStr,train_location, RepeatSubmitToken)

        orderSequence_no = self.__get_order_id(RepeatSubmitToken)

        self.__result_order(orderSequence_no, RepeatSubmitToken)

    def keep_online(self):
        online = 1
        if online:
            return online
        return

    def print_status(self, value):
        sys.stdout.write('\r')
        sys.stdout.write(value)
        sys.stdout.flush()

    def get_contact(self):
        contact_url = "https://kyfw.12306.cn/otn/passengers/query"
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

    def start(self):
        if self.method == 'scan':
            uid = self.get_qr64()
            if uid:
                self.check_qr(uid)
            # self.get_contact()
            self.ordain_ticket()

    def __check_user(self):
        r_check_user = self.session.post(url=self.host+url['check_user']['url'], data={"_json_att":""}, 
                            headers=self.headers(self.host+url['check_user']['referer']))
        j_check_user = json.loads(r_check_user.text)
        print(r_check_user.text)

    def __submit_order(self, train_info):
        data = {
            "secretStr": unquote(train_info[0]),
            "train_date": "{}-{}-{}".format(train_info[:4], train_info[4:6], train_info[-2:]),
            "back_train_date": time.strftime("%Y-%m-%d", time.localtime()),
            "tour_flag": "dc", #单程
            "purpose_codes": "ADULT",
            "query_from_station_name": train_info[37],
            "query_to_station_name": train_info[38],
            "undefined":"" 
        }
        r_submit_order = self.session.post(url=self.host+url['submit_order']['url'], data=data, 
                            headers=self.headers(url['submit_order']['referer']))
        print(r_submit_order.text)

    def __init_dc(self):
        b = self.session.post(url=self.host+url['init_dc']['url'], data={"_json_att":""}, 
                    headers=self.headers(url['init_dc']['referer']))
        rst_re = re.search(r"(?<=RepeatSubmitToken\s=\s\').+?(?=\';)", b.text)
        kci_re = re.search(r"(?<=key_check_isChange\':\').+?(?=\',)", b.text)
        lts_re = re.search(r"(?<=leftTicketStr\':\').+?(?=\',)", b.text)
        RepeatSubmitToken = rst_re.group() if rst_re else ""
        key_check_isChange = kci_re.group() if kci_re else ""
        leftTicketStr = lts_re.group() if lts_re else ""
        return [RepeatSubmitToken,key_check_isChange,leftTicketStr]

    def __get_passenger(self,RepeatSubmitToken, print_contact=False):
        r_passenger = self.session.post(url=self.host+url['get_passenger']['url'], 
                data={"_json_att":"", "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken}, 
                headers=self.headers(url['get_passenger']['referer']))
        passsenger_data = json.loads(r_passenger.text)
        if passsenger_data.get('status', '') == True:
            contact_data = {}
            normal_passengers = passsenger_data.get('data',{}).get('normal_passengers',[])
            if not normal_passengers:
                print("你的账号里没有联系人，请添加联系人后再试！")
            for passenger in normal_passengers:
                passenger_code = passenger.get('code', '')
                passenger_name = passenger.get('passenger_name', '')
                sex_code = passenger.get('sex_code', '')
                sex_name = passenger.get('sex_name', '')
                passenger_id_type_code = passenger.get('passenger_id_type_code', '')
                passenger_id_type_name = passenger.get('passenger_id_type_name', '')
                passenger_id_no = passenger.get('passenger_id_no', '')
                passenger_type = passenger.get('passenger_type', '')
                passenger_type_name = passenger.get('passenger_type_name', '')
                passenger_flag = passenger.get('passenger_flag', '')
                mobile_no = passenger.get('mobile_no', '')
                email = passenger.get('email', '')
                "编号","姓名","性别","证件类型","证件号","乘客类型","手机号","邮箱"
                self.contact_table.add_row([passenger_code, passenger_name, sex_name, passenger_id_type_name,
                passenger_id_no,passenger_type_name, mobile_no, email])
                contact_data[passenger_code] = [passenger_name, sex_code, passenger_id_type_code, 
                            passenger_id_no, passenger_type, passenger_flag, mobile_no]
            if print_contact:
                print(self.contact_table)
            return contact_data
        else:
            return

    def __check_order_info(self,seat_type,  passenger_ticket_str,
                                    old_passenger_str,RepeatSubmitToken):
        check_order_data = {
            "cancel_flag": "2",
            "bed_level_order_num": "000000000000000000000000000000",
            "passengerTicketStr": passenger_ticket_str,
            "oldPassengerStr": old_passenger_str,
            "tour_flag": "dc",
            "randCode": "",
            "whatsSelect": "1",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken
        }
        r_check_order = self.session.post(url=self.host+url['check_order']['url'] , data=check_order_data, 
                        headers=self.headers(url['check_order']['referer']))
        print(r_check_order.text)

    def __get_queue_count(self,train_info,leftTicketStr,RepeatSubmitToken):
        GMT_FORMAT = '%a %b %d %Y 00:00:00 GMT+0800 (China Standard Time)'
        queue_count_data = {
            "train_date": time.strftime(GMT_FORMAT, time.localtime()),
            "train_no": train_info[2],
            "stationTrainCode": train_info[3],
            "seatType": "1",
            "fromStationTelecode": train_info[6],
            "toStationTelecode": train_info[7],
            "leftTicket": leftTicketStr,
            "purpose_codes": "00",
            "train_location": train_info[15],
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken
        }
        r_queue_count = self.session.post(url=self.host+url['get_queue_count']['url'], data=queue_count_data, 
                    headers=self.headers(url['get_queue_count']['referer']))
        print(r_queue_count.text)

    def __confirm_queue(self,passenger_ticket_str,old_passenger_str,
            key_check_isChange, leftTicketStr,train_location, RepeatSubmitToken):
        confirm_queue_data = {
            "passengerTicketStr": passenger_ticket_str,
            "oldPassengerStr": old_passenger_str,
            "randCode": "",
            "purpose_codes": "00",
            "key_check_isChange": key_check_isChange,
            "leftTicketStr": leftTicketStr,
            "train_location": train_location,
            "choose_seats":"" , #选座？？？
            "seatDetailType": "000",
            "whatsSelect": "1",
            "roomType": "00",
            "dwAll": "N",
            "_json_att":"", 
            "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken
        }
        r_confirm_queue = self.session.post(url=self.host+url['confirm_single']['url'], data=confirm_queue_data, 
                    headers=self.headers(url['confirm_single']['referer']))
        print(r_confirm_queue.text)

    def __get_order_id(self,RepeatSubmitToken):
        get_orderid_url = self.host+url['query_order_wait_time']['url'].format(int(round(time.time()*1000)), RepeatSubmitToken)
        r_order_id = self.session.get(url=get_orderid_url, headers=self.headers(url['query_order_wait_time']['referer']))
        print(r_order_id.text)
        try:
            orderSequence_no = json.loads(r_order_id.text).get('data',{}).get('orderId','')
            return orderSequence_no
        except:
            print("发生了错误！")
            return 

    def __result_order(self,orderSequence_no,RepeatSubmitToken):
        order_dc_queue_data = {
            "orderSequence_no": orderSequence_no,
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": RepeatSubmitToken
        }
        r_result_order = self.session.post(url=self.host+url['result_order']['url'], data=order_dc_queue_data, 
                headers=self.headers(url['result_order']['referer']))
        print(r_result_order.text)

        pay_order_url = self.host+url['pay_order']['url'].format(int(round(time.time()*1000)))
        r_pay_order = self.session.post(url=pay_order_url, data=order_dc_queue_data)
        print(r_pay_order.text)
    
    def headers(self, referer=None):
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "kyfw.12306.cn",
            "If-Modified-Since": "0",
            "Referer":"https://kyfw.12306.cn/otn/leftTicket/init",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        if referer:
            header['Referer'] = referer
        return header

if __name__ == "__main__":
    trainticket = TrainJourney()
    trainticket.start()
