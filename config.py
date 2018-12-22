#encoding:utf-8
import configparser

class config():
    def __init__(self):
        self.ticket_conf_filed = set(["from_station", "to_station", "date", 
                                    "train_no","seat_type", "passenger_name"])
        self.conf = configparser.ConfigParser()
        self.conf.read('journey.conf')
        self.section = self.conf.sections()
        self.ticket_sections = [s for s in self.section if "ticket" in s]

    def ticket_conf(self):
        train_ticket_config = dict()
        for ticket_no in self.ticket_sections:
            tf = {}
            options = self.conf.options(ticket_no)
            for option in options:
                tf[option] =  self.conf.get(ticket_no, option)
                if option in ["date", "train_no", "seat_type", "passenger_name"]:
                    tf[option] =  self.conf.get(ticket_no, option).split(',')
            train_ticket_config[ticket_no] = tf
        return train_ticket_config

    def general_conf(self):
        refresh_interval = self.conf.get("general", "refresh_ticket_interval")
        notice_level = self.conf.get("general", "notice_level")
        email = self.conf.get("contact", "e-mail").split(',')
        phone = self.conf.get("contact", "phone_num").split(',')
        general_config = {
            "refresh_interval" : refresh_interval,
            "notice_level" : notice_level,
            "email" : email,
            "phone" : phone
            }
        return general_config

    def proxy_conf(self):
        proxy = {}
        http_proxy = self.conf.get("proxy", "http")
        https_proxy = self.conf.get("proxy", "https")
        proxy["http"] = http_proxy
        proxy["https"] = https_proxy
        proxy = dict((k,v) for k,v in proxy.items() if v)
        if proxy:
            return proxy
        return 

    def check_conf(self):
        if self.ticket_conf_filed.issubset(self.ticket_sections):
            print("YES")

if __name__ == "__main__":
    conf = config()
    print(conf.check_conf())
    ticket_config = conf.ticket_conf()
    print(ticket_config)