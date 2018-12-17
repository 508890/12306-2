#12306 余票查询
import json
import random
import time
import requests
import sendSMS
from city_code import CityCode
from prettytable import PrettyTable

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

class TrainTicket():
    def __init__(self):
        self.city_code = CityCode()
        self.seat_code = ["A1","A3","A4","A6","A9","F","M","O"]
        self.index = "https://www.12306.cn/index/index.html"
        self.tickets_api = ("https://kyfw.12306.cn/otn/leftTicket/query?"
                        "leftTicketDTO.train_date={}"         #2018-12-13"
                        "&leftTicketDTO.from_station={}"      #SYT"
                        "&leftTicketDTO.to_station={}"        #NCW"
                        "&purpose_codes={}")                  #ADULT
        self.price_api = ("https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?"
                            "train_no={}"         #240000K1171K
                            "&from_station_no={}" #21
                            "&to_station_no={}"   #29
                            "&seat_types={}"      #1413
                            "&train_date={}")     #2018-12014
        table_header = ["车次","始发站-终点站", "出发站/出发时间","到达站/到达时间","历时", 
                "商务座/特等座", "一等座", "二等座", "高级软卧", "软卧", "动卧",
                "硬卧", "软座", "硬座", "无座", "其他", "是否可购","备注"]
        self.table = PrettyTable(table_header)
        self.table.hrules = 1

    def search_ticket(self, START_STATION, END_STATION, DATE=None, search_price='1', TICKET_TYPE='ADULT'):
        if not DATE:
            DATE = time.strftime("%Y-%m-%d", time.localtime())
        start_station_data = self.city_code.get_code_by_city(START_STATION)
        end_station_data = self.city_code.get_code_by_city(END_STATION)
        if start_station_data.get('code') == 0:
            return {"status":False,"data":"No such as start station!"}
        if end_station_data.get('code') == 0:
            return {"status":False,"data":"No such as end station!"}
        start_station_name, start_station_code = list(start_station_data.get('result',{}).items())[0]
        end_station_name, end_station_code = list(end_station_data.get('result', {}).items())[0]
        query_url = self.tickets_api.format(DATE, start_station_code, end_station_code, TICKET_TYPE)
        res = requests.get(url=query_url, headers=TrainTicket._headers())
        try:
            tickets_data = self.parser_ticket_data(json.loads(res.text), start_station_name, end_station_name, DATE, search_price)
            return tickets_data
        except:
            return {"status":False}

   
    def parser_ticket_data(self, ticket_data, start_station, end_station, date, search_price):
        train_ticket_data = {} 
        station_map = ticket_data.get('data',{}).get('map',{})
        result = ticket_data.get('data',{}).get('result', [])
        if result:
            total_train_num = len(result)
            self.table.title = "{}-->{}{}共计{}车次".format(start_station, end_station,date,total_train_num)
            for train_times in result:
                ticket_info = train_times.split('|')
                secretStr = ticket_info[0]
                buttonTextInfo = ticket_info[1]
                train_no = ticket_info[2]
                train_num = ticket_info[3]
                start_station_telecode = ticket_info[4]
                end_station_telecode = ticket_info[5]
                from_station_telecode = ticket_info[6]
                to_station_telecode = ticket_info[7]
                start_time = ticket_info[8]
                arrive_time = ticket_info[9]
                lishi = ticket_info[10]
                canWebBuy = ticket_info[11]
                yp_info = ticket_info[12]
                start_train_date = ticket_info[13]
                train_seat_feature = ticket_info[14]
                location_code = ticket_info[15]
                from_station_no = ticket_info[16]
                to_station_no = ticket_info[17]
                is_support_card = ticket_info[18]
                controlled_train_flag = ticket_info[19]
                gg_num = ticket_info[20] if ticket_info[20] else "--" #
                gr_num = ticket_info[21] if ticket_info[21] else "--" #gaojiruanwo
                qt_num = ticket_info[22] if ticket_info[22] else "--" #qita(i guess)
                rw_num = ticket_info[23] if ticket_info[23] else "--" #ruanwo
                rz_num = ticket_info[24] if ticket_info[24] else "--" #ruanzuo
                tz_num = ticket_info[25] if ticket_info[25] else "--" #tedengzuo
                wz_num = ticket_info[26] if ticket_info[26] else "--" #wuzuo
                yb_num = ticket_info[27] if ticket_info[27] else "--" #
                yw_num = ticket_info[28] if ticket_info[28] else "--" #yingwo
                yz_num = ticket_info[29] if ticket_info[29] else "--" #yingzuo
                ze_num = ticket_info[30] if ticket_info[30] else "--" #erdengzuo
                zy_num = ticket_info[31] if ticket_info[31] else "--" #yidengzuo
                swz_num = ticket_info[32] if ticket_info[32] else "--" #shangwuzuo
                srrb_num = ticket_info[33] if ticket_info[33] else "--" #dongwo
                yp_ex = ticket_info[34]
                seat_types = ticket_info[35]
                exchange_train_flag = ticket_info[36]
                from_station_name = station_map.get(ticket_info[6],'')
                to_station_name = station_map.get(ticket_info[7], '')
                sw_tz_num = "{}/{}".format(swz_num,tz_num)
                
                if search_price == '1':
                    ticket_price = self.get_ticket_price(train_no, from_station_no, 
                                                    to_station_no,seat_types, date)
                    if ticket_price:
                        for scode in ticket_price:
                            # if scode == "WZ":
                                # wz_num = "{}\n{}".format(wz_num, ticket_price.get(scode, ''))
                            if scode == "A1":
                                yz_num = "{}\n{}".format(yz_num, ticket_price.get(scode, ''))
                                wz_num = "{}\n{}".format(wz_num, ticket_price.get(scode, ''))
                            elif scode == "A3":
                                yw_num = "{}\n{}".format(yw_num, ticket_price.get(scode, ''))
                            elif scode == "A4":
                                rw_num = "{}\n{}".format(rw_num, ticket_price.get(scode, ''))
                            elif scode == "A6":
                                gr_num = "{}\n{}".format(gr_num, ticket_price.get(scode, ''))
                            elif scode == "A9":
                                sw_tz_num = "{}\n{}".format(sw_tz_num, ticket_price.get(scode, ''))
                            elif scode == "F":
                                srrb_num = "{}\n{}".format(srrb_num, ticket_price.get(scode, ''))
                            elif scode == "M":
                                zy_num = "{}\n{}".format(zy_num, ticket_price.get(scode, ''))
                            elif scode == "O":
                                ze_num = "{}\n{}".format(ze_num, ticket_price.get(scode, ''))
                    else:
                        buttonTextInfo = "{}\n{}".format(buttonTextInfo, "票价查询失败")
                train_ticket_data[train_num] = ticket_info #[secretStr,train_no,train_num, 
                            # from_station_name, to_station_name, from_station_telecode,to_station_telecode,canWebBuy,date,yp_info,
                            # location_code,train_seat_feature,yp_ex, swz_num,tz_num, zy_num, ze_num, gr_num, rw_num, srrb_num, 
                            # yw_num,rz_num, yz_num, wz_num,  
                            # qt_num]        
                
                self.table.add_row([train_num, "{}-{}".format(self.city_code.code_name_dict.get(start_station_telecode,''),
                                    self.city_code.code_name_dict.get(end_station_telecode,'')), 
                            "{}\n{}".format(from_station_name, start_time), "{}\n{}".format(to_station_name, arrive_time),lishi, 
                            sw_tz_num, zy_num, ze_num, gr_num, rw_num, srrb_num, yw_num,rz_num, yz_num, wz_num, 
                            qt_num,canWebBuy, buttonTextInfo])
            print(self.table)
        else:
            print("No tickets")
        return train_ticket_data


    def get_ticket_price(self,train_no, from_s_no, to_s_no, seat_type, train_date):
        seat_price = dict()
        price_api = self.price_api.format(train_no, from_s_no,to_s_no, seat_type, train_date)
        res = requests.get(url=price_api, headers=TrainTicket._headers())
        try:
            res_dict = json.loads(res.text)
            if res_dict.get('status', '') == True:
                price_data = res_dict.get('data', {})
                seats = list(set(self.seat_code).intersection(set(list(price_data.keys()))))
                for s in seats:
                    seat_price[s] = price_data.get(s, '')
                return seat_price
        except Exception as e:
            print("Data Error",e)
            return 
            
    @staticmethod
    def _headers():
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "kyfw.12306.cn",
            "If-Modified-Since": "0",
            "User-Agent":random.choice(user_agent),
            "X-Requested-With": "XMLHttpRequest"
        }
        return headers


if __name__ == "__main__":
    ticket = TrainTicket()
    # start = input("请输入起点：")
    # end = input("请输入终点：")
    # date_str = input("请输入时间(eg:2018-12-12)：")
    # # tickect_type = input("请输入类型：")
    # show_price = input("是否需要显示票价信息(1,显示、2,不显示)：")
    start = "沈阳"
    end = "南充"
    date_str = "2019-01-15"
    # tickect_type = input("请输入类型：")
    show_price = 2
    train_no = "K388"
    
    while 1:
        train_tickets = ticket.search_ticket(start,end,date_str,show_price)
        ticket_data = train_tickets.get(train_no, [])
        if ticket_data:
            yw = ticket_data[28]
            yz = ticket_data[29]
            notice_times = 1
            if yw:
                notice_str = "你好，{} {}至{}的{}列车的硬卧还有票，请抓紧时间购票！这是第{}次通知！".format(date_str,start,end,train_no, notice_times)
                notice_times+=1
                sendSMS.sendGroupTemplateSMS(notice=notice_str)
                if notice_times>3:
                    break  
        time.sleep(int(str(random.uniform(30,50))[:2]))

